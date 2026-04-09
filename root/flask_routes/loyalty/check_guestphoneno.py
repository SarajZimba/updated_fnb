from flask import Blueprint, jsonify, request
import mysql.connector
import os
from dotenv import load_dotenv
from flask_cors import cross_origin
from root.auth.check import token_auth

load_dotenv()

app_file92 = Blueprint('app_file92', __name__)

@app_file92.route("/check-phone-num", methods=["POST"])
@cross_origin()
def check_phone_num():
    try:
        data = request.get_json()

        # Connect to DB
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password'),
            database=os.getenv('database')
        )
        cursor = mydb.cursor(dictionary=True)

        # Validate token
        token = data.get("token")
        if not token or not token_auth(token):
            return jsonify({"error": "Invalid or missing token"}), 400

        # Get phone number
        phone_no = data.get("phone_no")
        if not phone_no:
            return jsonify({"error": "Missing phone_no"}), 400
        
        # Get phone number
        hash_code = data.get("hash_code")
        if not hash_code:
            return jsonify({"error": "Missing hash_code"}), 400

        # Check if guest exists with that phone number
        cursor.execute("SELECT * FROM guest WHERE guestPhone = %s", (phone_no,))
        guest = cursor.fetchone()

        # # Step 1: Get order_id from loyaltyqueue
        # cursor.execute("SELECT order_id FROM loyaltyqueue WHERE hash_code = %s AND status != 'received'", (hash_code,))
        # order = cursor.fetchone()
        # if not order:
        #     return jsonify({"error": "Order not found"}), 404


        cursor.execute("SELECT * FROM guest WHERE guestPhone = %s", (phone_no,))

        guest = cursor.fetchone()

        if guest:
                exists = True
        else:
            exists = False

        return jsonify({
            "exists": exists 
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
