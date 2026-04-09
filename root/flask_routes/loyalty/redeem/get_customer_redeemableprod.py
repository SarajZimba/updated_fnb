# from flask import Blueprint, request, jsonify
# import os
# import mysql.connector
# from dotenv import load_dotenv
# from flask_cors import cross_origin
# from root.auth.check import token_auth

# load_dotenv()

# app_file99 = Blueprint('app_file99', __name__)

# @app_file99.route('/get-customer-redeemable-product', methods=['POST'])
# @cross_origin()
# def get_redeemable_product():
#     try:
#         data = request.get_json()
#         token = data.get('token')
#         guest_phone = data.get('guest_phone')  # Get guest_id from frontend
#         outlet = data.get('outlet')  # Get outlet from frontend

#         if not token or not token_auth(token):
#             return jsonify({'error': 'Invalid or missing token'}), 400

#         if not guest_phone or not outlet:
#             return jsonify({"error": "Missing required fields: guest_id or outlet"}), 400

#         mydb = mysql.connector.connect(
#             host=os.getenv('host'),
#             user=os.getenv('user'),
#             password=os.getenv('password'),
#             database=os.getenv('database')
#         )
#         cursor = mydb.cursor(dictionary=True)

#         # Fetch guest's loyalty points from the guest table
#         cursor.execute("SELECT loyalty_points FROM guest WHERE guestPhone = %s AND Outlet_Name = %s", (guest_phone, outlet))
#         guest = cursor.fetchone()

#         if not guest:
#             return jsonify({'error': 'Guest not found for the given guest_phone and outlet'}), 404

#         guest_loyalty_points = guest['loyalty_points']

#         # Fetch redeemable products for the given outlet and check points eligibility
#         sql = """
#             SELECT id, product, description, points, valid_until, is_menu_item_flag, image, status
#             FROM redeemable_products
#             WHERE outlet = %s
#         """
#         cursor.execute(sql, (outlet,))
#         products = cursor.fetchall()

#         return jsonify({'redeemable_products': products, 'points_available': guest_loyalty_points}), 200

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


from flask import Blueprint, request, jsonify
import os
import mysql.connector
from dotenv import load_dotenv
from flask_cors import cross_origin
from root.auth.check import token_auth

load_dotenv()

app_file99 = Blueprint('app_file99', __name__)

@app_file99.route('/get-customer-redeemable-product', methods=['POST'])
@cross_origin()
def get_redeemable_product():
    try:
        data = request.get_json()
        token = data.get('token')
        guest_phone = data.get('guest_phone')  # Get guest_id from frontend
        outlet = data.get('outlet')  # Get outlet from frontend

        if not token or not token_auth(token):
            return jsonify({'error': 'Invalid or missing token'}), 400

        if not guest_phone or not outlet:
            return jsonify({"error": "Missing required fields: guest_id or outlet"}), 400

        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password'),
            database=os.getenv('database')
        )
        cursor = mydb.cursor(dictionary=True)

        # Fetch guest's loyalty points from the guest table
        cursor.execute("SELECT loyalty_points, GuestName, guestAddress, guestPhone, guestEmail FROM guest WHERE guestPhone = %s AND Outlet_Name = %s", (guest_phone, outlet))
        guest = cursor.fetchone()

        if not guest:
            return jsonify({'error': 'Guest not found for the given guest_phone and outlet'}), 404

        guest_loyalty_points = guest['loyalty_points']
        guestName = guest['GuestName']
        guestAddress = guest['guestAddress']
        guestPhone = guest['guestPhone']
        guestEmail = guest['guestEmail']

        # Fetch redeemable products for the given outlet and check points eligibility
        sql = """
            SELECT id, product, description, points, valid_until, is_menu_item_flag, image, status
            FROM redeemable_products
            WHERE outlet = %s 
        """
        cursor.execute(sql, (outlet,))
        products = cursor.fetchall()

        return jsonify({'redeemable_products': products, 'points_available': guest_loyalty_points, 'guestName': guestName, 'guestAddress': guestAddress, 'guestPhone':guestPhone, 'guestEmail': guestEmail}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500