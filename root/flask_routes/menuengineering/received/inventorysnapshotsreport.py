from flask import Blueprint, jsonify, request
import mysql.connector
import os
from dotenv import load_dotenv
from flask_cors import cross_origin
from root.auth.check import token_auth

load_dotenv()

app_file119 = Blueprint('app_file119', __name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("host"),
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )

@app_file119.route("/inventory-snapshot-reports", methods=["POST"])
@cross_origin()
def receive_items():
    try:
        data = request.get_json()
        token = data.get("token")
        outlet = data.get("outlet")

        if not token or not token_auth(token):
            return jsonify({"error": "Invalid or missing token."}), 400

        if not outlet:
            return jsonify({"error": "Missing required parameter: outlet"}), 400

        mydb = get_db_connection()
        cursor = mydb.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, start_date, end_date, created_at, food_total_items, beverage_total_items, food_accuracy, beverage_accuracy
            FROM inventory_snapshot_master
            WHERE outlet_name = %s
            ORDER BY created_at DESC
        """, (outlet,))

        snapshots = cursor.fetchall()

        cursor.close()
        mydb.close()

        return jsonify({
            "status": "success",
            "outlet": outlet,
            "snapshot_reports": snapshots
        }), 200

    except Exception as e:
        if 'mydb' in locals():
            mydb.rollback()
            mydb.close()
        return jsonify({"error": str(e)}), 400
