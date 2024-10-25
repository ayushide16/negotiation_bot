from flask import Flask, jsonify, request
import psycopg2
import os

app = Flask(__name__)

# PostgreSQL Database Configuration
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'RetailDB')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASS = os.getenv('DB_PASS', 'Helloworld@123')

# Establish database connection
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        return conn
    except psycopg2.Error as e:
        raise Exception(f"Database connection failed: {str(e)}")

# Endpoint to add a new user
@app.route('/data', methods=['POST'])
def add_user():
    try:
        # Ensure the content type is JSON
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 415
        
        user_data = request.get_json()

        # Extract required fields
        username = user_data.get('username')
        email = user_data.get('email')
        password = user_data.get('password')
        phone = user_data.get('phone')
        address = user_data.get('address')
        customer_type = user_data.get('customer_type')

        # Check if all required fields are present
        if not username or not email or not password:
            return jsonify({"error": "Missing required fields: 'username', 'email', and 'password' are mandatory"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert data into the users table using a parameterized query
        query = '''
            INSERT INTO users (username, email, password, phone, address, customer_type)
            VALUES (%s, %s, %s, %s, %s, %s)
        '''
        cursor.execute(query, (username, email, password, phone, address, customer_type))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"message": "User added successfully"}), 201

    except psycopg2.Error as e:
        return jsonify({"error": f"Database operation failed: {str(e)}"}), 500

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
