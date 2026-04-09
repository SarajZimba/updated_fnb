from flask import Blueprint, request, jsonify
import os
import mysql.connector
from dotenv import load_dotenv
from flask_cors import cross_origin
from root.auth.check import token_auth

load_dotenv()

app_file100 = Blueprint('app_file100', __name__)

@app_file100.route('/product-redeemed', methods=['POST'])
@cross_origin()
def get_redeemable_product():
    try:
        data = request.get_json()
        token = data.get('token')
        phone_no = data.get('phone_no')
        outlet = data.get('outlet')
        redeemed_item_list = data.get('item_list', [])

        if not token or not token_auth(token):
            return jsonify({'error': 'Invalid or missing token'}), 400
        if not outlet or not redeemed_item_list:
            return jsonify({'error': 'Missing required fields: outlet or item_list'}), 400

        # Calculate total points redeemed
        total_points = sum(item.get('total_points', 0) for item in redeemed_item_list)

        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password'),
            database=os.getenv('database')
        )
        cursor = mydb.cursor(dictionary=True)

        # Step 1: Check guest and points
        cursor.execute("""
            SELECT id, loyalty_points FROM guest
            WHERE guestPhone = %s AND Outlet_Name = %s
        """, (phone_no, outlet))
        guest = cursor.fetchone()

        if not guest:
            cursor.close()
            mydb.close()
            return jsonify({'error': 'Guest not found'}), 404

        current_points = float(guest['loyalty_points'])

        if current_points < total_points:
            cursor.close()
            mydb.close()
            return jsonify({'error': 'Not enough loyalty points'}), 400

        # Start transaction
        cursor.execute("START TRANSACTION")

        # Step 2: Insert into tblredeemedhistory
        insert_history = """
            INSERT INTO tblredeemedhistory (phone_no, outlet, total_points)
            VALUES (%s, %s, %s)
        """
        cursor.execute(insert_history, (phone_no, outlet, total_points))
        history_id = cursor.lastrowid

        # Step 3: Insert into tblredeemeddetails
        insert_detail = """
            INSERT INTO tblredeemeddetails
            (history_id, product_id, product_name, points_per_item, quantity, total_points)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        for item in redeemed_item_list:
            cursor.execute(insert_detail, (
                history_id,
                item.get('product_id'),
                item.get('product_name'),
                item.get('points_per_item'),
                item.get('quantity'),
                item.get('total_points')
            ))

        # Step 4: Deduct points from guest
        update_points = """
            UPDATE guest SET loyalty_points = loyalty_points - %s
            WHERE id = %s
        """
        cursor.execute(update_points, (total_points, guest['id']))

        # Commit transaction
        mydb.commit()
        cursor.close()
        mydb.close()

        return jsonify({'success': True, 'message': 'Redemption recorded successfully'}), 200

    except Exception as e:
        try:
            mydb.rollback()
        except:
            pass
        return jsonify({'error': str(e)}), 500
