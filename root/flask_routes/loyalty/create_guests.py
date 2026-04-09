from flask import Blueprint, jsonify, request
import mysql.connector
import os
from dotenv import load_dotenv
from flask_cors import cross_origin
from root.auth.check import token_auth
import uuid

load_dotenv()

app_file96 = Blueprint('app_file96', __name__)

@app_file96.route("/create-guests", methods=["POST"])
@cross_origin()
def check_or_create_guest():
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

        # Get guest details
        phone_no = data.get("phone_no")
        guest_name = data.get("guest_name")
        guest_email = data.get("guest_email")
        guest_address = data.get("guest_address")
        outlet_name = data.get("outlet_name")

        if not phone_no:
            return jsonify({"error": "Missing phone_no"}), 400

        # Check if guest already exists
        cursor.execute("SELECT * FROM guest WHERE guestPhone = %s", (phone_no,))
        guest = cursor.fetchone()

        if guest:
            return jsonify({
                "guest_exists": True,
                "message": "Guest already exists."
            }), 200
        else:
            # Create new guest
            new_guest_id = str(uuid.uuid4())[:8]  # simple unique guest ID
            cursor.execute("""
                INSERT INTO guest (guestID, guestPhone, guestEmail, guestAddress, Outlet_Name, GuestName)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (new_guest_id, phone_no, guest_email, guest_address, outlet_name, guest_name))
            mydb.commit()

            return jsonify({
                "guest_exists": False,
                "message": "New guest created successfully.",
                "guestID": new_guest_id
            }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
