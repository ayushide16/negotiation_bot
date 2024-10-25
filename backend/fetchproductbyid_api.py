from flask import Flask, jsonify
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

# Get a product by ID
@app.route('/data', methods=['GET'])
@app.route('/data/<int:product_id>', methods=['GET'])
def get_product(product_id=None):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if product_id is not None:
            cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
            row = cursor.fetchone()
            
            if row is None:
                return jsonify({"error": "Product not found"}), 404
            
            data = dict(zip([column[0] for column in cursor.description], row))
        
        else:
            cursor.execute("SELECT * FROM products")
            rows = cursor.fetchall()
            data = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
        
        cursor.close()
        conn.close()
        
        return jsonify(data), 200
    
    except psycopg2.Error as e:
        return jsonify({"error": f"Database query failed: {str(e)}"}), 500
    
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
