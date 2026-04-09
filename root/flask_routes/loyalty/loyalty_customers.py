from flask import Blueprint, jsonify, request
import mysql.connector
import os
from dotenv import load_dotenv
from flask_cors import cross_origin
from root.auth.check import token_auth  # <-- make sure this import is correct

load_dotenv()

app_file91 = Blueprint('app_file91', __name__)

@app_file91.route("/getguests", methods=["POST"])
@cross_origin()
def get_guests():
    try:
        data = request.get_json()

        # Check for token
        if not data or "token" not in data or not data["token"]:
            return jsonify({"error": "No token provided."}), 400

        token = data["token"]
        if not token_auth(token):
            return jsonify({"error": "Invalid token."}), 400

        # Check for outlet
        outlet = data.get("outlet")
        if not outlet:
            return jsonify({"error": "Missing 'outlet' in request body"}), 400

        # Connect to DB
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password'),
            database=os.getenv('database')
        )
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT * FROM guest WHERE Outlet_Name = %s", (outlet,))
        guests = cursor.fetchall()

        mydb.close()
        return jsonify(guests), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
