from flask import Blueprint, request, jsonify
import os
import mysql.connector
from dotenv import load_dotenv
from flask_cors import cross_origin
from root.auth.check import token_auth

load_dotenv()

app_file98 = Blueprint('app_file98', __name__)

@app_file98.route('/get-redeemable-product', methods=['POST'])
@cross_origin()
def get_redeemable_product():
    try:
        data = request.get_json()
        token = data.get('token')
        guest_id = data.get('guest_id')  # (Optional, not used here)
        outlet = data.get('outlet')

        if not token or not token_auth(token):
            return jsonify({'error': 'Invalid or missing token'}), 400
        if not outlet:
            return jsonify({"error": "Missing required fields: outlet"}), 400

        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password'),
            database=os.getenv('database')
        )
        cursor = mydb.cursor(dictionary=True)

        # Updated query to filter by outlet and where status is true
        sql = """
            SELECT id, product, description, points, valid_until, is_menu_item_flag, image, status, outlet
            FROM redeemable_products 
            WHERE outlet = %s AND status = TRUE
        """
        cursor.execute(sql, (outlet,))
        products = cursor.fetchall()

        return jsonify({'redeemable_products': products}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500




