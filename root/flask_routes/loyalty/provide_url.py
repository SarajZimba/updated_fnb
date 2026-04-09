from flask import Blueprint, jsonify, request
import mysql.connector
import os
from dotenv import load_dotenv
from flask_cors import cross_origin
from root.auth.check import token_auth
import hashlib

load_dotenv()

app_file93 = Blueprint('app_file93', __name__)

@app_file93.route("/provide-url", methods=["POST"])
@cross_origin()
def get_guests():
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

        loyalty_url = os.getenv('loyalty_url')

        # Validate token
        token = data.get("token")
        if not token or not token_auth(token):
            return jsonify({"error": "Invalid or missing token"}), 400

        # Required fields
        outlet = data.get("outlet")
        bill_no = data.get("bill_no")
        sub_total = data.get("sub_total")
        date = data.get("date")

        if not all([outlet, bill_no, sub_total, date]):
            return jsonify({"error": "Missing required fields"}), 400

        # Create a hash based on guest_id + bill_no + outlet + date
        hash_input = f"{bill_no}{outlet}{date}"
        hash_code = hashlib.sha256(hash_input.encode()).hexdigest()

        # Insert into LoyaltyQueue without order_id
        insert_query = """
            INSERT INTO loyaltyqueue ( hash_code, status, outlet, bill_no, sub_total, date)
            VALUES (%s, 'pending', %s, %s, %s, %s)
        """
        cursor.execute(insert_query, ( hash_code, outlet, bill_no, sub_total, date))
        mydb.commit()

        cursor.close()
        mydb.close()

        return jsonify({"hash": hash_code, "url": loyalty_url, "outlet": outlet}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
