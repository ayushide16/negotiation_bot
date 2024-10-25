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

# Endpoint to add new entry to the cart (directly adjusted to be accessible at /data)
@app.route('/data', methods=['POST'])
def add_to_cart():
    try:
        # Ensure the content type is JSON
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 415
        
        cart_data = request.get_json()

        # Extract required fields
        user_id = cart_data.get('user_id')
        product_id = cart_data.get('product_id')
        final_price = cart_data.get('final_price')

        # Check if all required fields are present
        if not user_id or not product_id or final_price is None:
            return jsonify({"error": "Missing required fields: 'user_id', 'product_id', and 'final_price' are mandatory"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert data into the cart table
        cursor.execute(
            "INSERT INTO cart (user_id) VALUES (%s) RETURNING cart_id",
            (user_id,)
        )
        cart_id = cursor.fetchone()[0]  # Get the newly created cart_id

        # Insert data into the purchase table with the generated cart_id
        cursor.execute(
            '''
            INSERT INTO purchase (cart_id, order_id, product_id, final_price)
            VALUES (%s, NULL, %s, %s)
            ''',
            (cart_id, product_id, final_price)
        )

        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Cart entry added successfully", "cart_id": cart_id}), 201

    except psycopg2.Error as e:
        return jsonify({"error": f"Database operation failed: {str(e)}"}), 500

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
