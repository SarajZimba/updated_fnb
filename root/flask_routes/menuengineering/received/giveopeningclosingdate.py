# from datetime import datetime, timedelta
# from flask import Blueprint, jsonify, request
# import mysql.connector
# import os
# from dotenv import load_dotenv
# from flask_cors import cross_origin
# from root.auth.check import token_auth

# load_dotenv()

# app_file124 = Blueprint('app_file124', __name__)

# def get_db_connection():
#     return mysql.connector.connect(
#         host=os.getenv("host"),
#         user=os.getenv("user"),
#         password=os.getenv("password"),
#         database=os.getenv("database")
#     )

# @app_file124.route("/get-inventory-period", methods=["POST"])
# @cross_origin()
# def get_inventory_period():
#     try:
#         data = request.get_json()
#         token = data.get("token")
#         outlet = data.get("outlet")

#         if not token or not token_auth(token):
#             return jsonify({"error": "Invalid or missing token."}), 400

#         if not outlet:
#             return jsonify({"error": "Missing required parameter: outlet"}), 400

#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)

#         # Get the most recent snapshot
#         cursor.execute("""
#             SELECT end_date
#             FROM inventory_snapshot_master
#             WHERE outlet_name = %s
#             ORDER BY end_date DESC LIMIT 1
#         """, (outlet,))
#         snapshot = cursor.fetchone()

#         if snapshot:
#             opening_date = (snapshot["end_date"] + timedelta(days=1)).strftime("%Y-%m-%d")
#         else:
#             opening_date = "2000-01-01"

#         closing_date = datetime.today().strftime("%Y-%m-%d")

#         cursor.close()
#         conn.close()

#         return jsonify({
#             "status": "success",
#             "outlet": outlet,
#             "opening_date": opening_date,
#             "closing_date": closing_date
#         }), 200

#     except Exception as e:
#         if 'conn' in locals():
#             conn.rollback()
#             conn.close()
#         return jsonify({"error": str(e)}), 400



from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
import mysql.connector
import os
from dotenv import load_dotenv
from flask_cors import cross_origin
from root.auth.check import token_auth

load_dotenv()

app_file124 = Blueprint('app_file124', __name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("host"),
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )

@app_file124.route("/get-inventory-period", methods=["POST"])
@cross_origin()
def get_inventory_period():
    try:
        data = request.get_json()
        token = data.get("token")
        outlet = data.get("outlet")

        if not token or not token_auth(token):
            return jsonify({"error": "Invalid or missing token."}), 400

        if not outlet:
            return jsonify({"error": "Missing required parameter: outlet"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Get the most recent snapshot
        cursor.execute("""
            SELECT end_date
            FROM inventory_snapshot_master
            WHERE outlet_name = %s
            ORDER BY end_date DESC LIMIT 1
        """, (outlet,))
        snapshot = cursor.fetchone()

        if snapshot:
            opening_date = (snapshot["end_date"] + timedelta(days=1)).strftime("%Y-%m-%d")
        else:
            opening_date = "2000-01-01"

        closing_date = datetime.today().strftime("%Y-%m-%d")

        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "outlet": outlet,
            "opening_date": opening_date,
            "closing_date": closing_date
        }), 200

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return jsonify({"error": str(e)}), 400
    
@app_file124.route("/get-inventory-period-food", methods=["POST"])
@cross_origin()
def get_inventory_period_food():
    try:
        data = request.get_json()
        token = data.get("token")
        outlet = data.get("outlet")

        if not token or not token_auth(token):
            return jsonify({"error": "Invalid or missing token."}), 400

        if not outlet:
            return jsonify({"error": "Missing required parameter: outlet"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Get the most recent snapshot
        cursor.execute("""
            SELECT end_date
            FROM inventory_snapshot_master_food
            WHERE outlet_name = %s
            ORDER BY end_date DESC LIMIT 1
        """, (outlet,))
        snapshot = cursor.fetchone()

        if snapshot:
            opening_date = (snapshot["end_date"] + timedelta(days=1)).strftime("%Y-%m-%d")
        else:
            opening_date = "2000-01-01"

        closing_date = datetime.today().strftime("%Y-%m-%d")

        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "outlet": outlet,
            "opening_date": opening_date,
            "closing_date": closing_date
        }), 200

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return jsonify({"error": str(e)}), 400
    
@app_file124.route("/get-inventory-period-beverage", methods=["POST"])
@cross_origin()
def get_inventory_period_beverage():
    try:
        data = request.get_json()
        token = data.get("token")
        outlet = data.get("outlet")

        if not token or not token_auth(token):
            return jsonify({"error": "Invalid or missing token."}), 400

        if not outlet:
            return jsonify({"error": "Missing required parameter: outlet"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Get the most recent snapshot
        cursor.execute("""
            SELECT end_date
            FROM inventory_snapshot_master_beverage
            WHERE outlet_name = %s
            ORDER BY end_date DESC LIMIT 1
        """, (outlet,))
        snapshot = cursor.fetchone()

        if snapshot:
            opening_date = (snapshot["end_date"] + timedelta(days=1)).strftime("%Y-%m-%d")
        else:
            opening_date = "2000-01-01"

        closing_date = datetime.today().strftime("%Y-%m-%d")

        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "outlet": outlet,
            "opening_date": opening_date,
            "closing_date": closing_date
        }), 200

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return jsonify({"error": str(e)}), 400
