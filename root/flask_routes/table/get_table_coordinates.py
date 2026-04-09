from flask import Blueprint, request, jsonify
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv
from root.auth.check import token_auth

load_dotenv()
app_file212 = Blueprint('app_file212', __name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('host'),
        user=os.getenv('user'),
        password=os.getenv('password'),
        database=os.getenv('database')
    )

@app_file212.route("/get-table-coordinates", methods=["POST"])
@cross_origin()
def get_table_coordinates():
    try:
        data = request.get_json()

        # --- Token Validation ---
        if "token" not in data or not data["token"]:
            return {"error": "No token provided."}, 400

        if not token_auth(data["token"]):
            return {"error": "Invalid token."}, 400

        # --- Required Field ---
        if "outlet_name" not in data:
            return {"error": "outlet_name is required."}, 400

        outlet_name = data["outlet_name"]

        mydb = get_db_connection()
        cursor = mydb.cursor(dictionary=True)

        # --- Fetch Layout ---
        sql = """
            SELECT 
                table_no,
                x_coordinate,
                y_coordinate
            FROM tbl_table_coordinates
            WHERE outlet_name = %s
            ORDER BY table_no
        """
        cursor.execute(sql, (outlet_name,))
        tables = cursor.fetchall()

        cursor.close()
        mydb.close()

        return jsonify({
            "outlet_name": outlet_name,
            "tables": tables
        }), 200

    except Exception as error:
        return {"error": str(error)}, 500
