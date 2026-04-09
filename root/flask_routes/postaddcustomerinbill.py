from flask import Blueprint, request, jsonify
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv
from root.auth.check import token_auth

load_dotenv()
app_file209 = Blueprint('app_file209', __name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('host'),
        user=os.getenv('user'),
        password=os.getenv('password'),
        database=os.getenv('database')
    )

@app_file209.route("/update-guest-info", methods=["POST"])
@cross_origin()
def update_guest_info():
    try:
        data = request.get_json()

        # --- Token Validation ---
        if "token" not in data or not data["token"]:
            return {"error": "No token provided."}, 400

        token = data["token"]
        if not token_auth(token):
            return {"error": "Invalid token."}, 400

        # --- Required Fields ---
        if "bill_id" not in data or "guest_name" not in data or "guest_pan" not in data:
            return {"error": "bill_id, guest_name, and guest_pan are required."}, 400

        bill_id = data["bill_id"]
        guest_name = data["guest_name"]
        guest_pan = data["guest_pan"]

        # --- DB Connection ---
        mydb = get_db_connection()
        cursor = mydb.cursor()

        # --- Validate bill_id ---
        check_sql = "SELECT COUNT(*) FROM tblorderhistory WHERE idtblorderHistory = %s"
        cursor.execute(check_sql, (bill_id,))
        (count,) = cursor.fetchone()

        if count == 0:
            cursor.close()
            mydb.close()
            return {"error": f"Invalid bill_id {bill_id}. Bill does not exist."}, 400

        # --- Update Guest Info ---
        update_sql = """
            UPDATE tblorderhistory
            SET GuestName = %s, guestPan = %s
            WHERE idtblorderHistory = %s
        """
        cursor.execute(update_sql, (guest_name, guest_pan, bill_id))
        mydb.commit()

        cursor.close()
        mydb.close()

        return jsonify({
            "message": "Guest information updated successfully",
            "bill_id": bill_id,
            "guest_name": guest_name,
            "guest_pan": guest_pan
        }), 200

    except Exception as error:
        return {"error": str(error)}, 500


@app_file209.route("/delete-guest-info", methods=["POST"])
@cross_origin()
def clear_guest_info():
    try:
        data = request.get_json()

        # --- Token Validation ---
        if "token" not in data or not data["token"]:
            return {"error": "No token provided."}, 400

        token = data["token"]
        if not token_auth(token):
            return {"error": "Invalid token."}, 400

        # --- Required Field ---
        if "bill_id" not in data:
            return {"error": "bill_id is required."}, 400

        bill_id = data["bill_id"]

        # --- DB Connection ---
        mydb = get_db_connection()
        cursor = mydb.cursor()

        # --- Validate bill_id ---
        check_sql = "SELECT COUNT(*) FROM tblorderhistory WHERE idtblorderHistory = %s"
        cursor.execute(check_sql, (bill_id,))
        (count,) = cursor.fetchone()

        if count == 0:
            cursor.close()
            mydb.close()
            return {"error": f"Invalid bill_id {bill_id}. Bill does not exist."}, 400

        # --- Clear Guest Info ---
        clear_sql = """
            UPDATE tblorderhistory
            SET GuestName = '', guestPan = ''
            WHERE idtblorderHistory = %s
        """
        cursor.execute(clear_sql, (bill_id,))
        mydb.commit()

        cursor.close()
        mydb.close()

        return jsonify({
            "message": "Guest information cleared successfully",
            "bill_id": bill_id
        }), 200

    except Exception as error:
        return {"error": str(error)}, 500