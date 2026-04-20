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


@app_file119.route("/inventory-snapshot-food-beverage", methods=["POST"])
@cross_origin()
def get_food_beverage_snapshot():
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

        query = """
            SELECT 
                f.start_date,
                f.end_date,
                f.food_total_items,
                f.food_accuracy,
                f.food_missing_items,
                b.beverage_total_items,
                b.beverage_accuracy,
                b.beverage_missing_items,
                f.created_at AS food_created_at,
                b.created_at AS beverage_created_at
            FROM inventory_snapshot_master_food f
            LEFT JOIN inventory_snapshot_master_beverage b
                ON f.outlet_name = b.outlet_name
                AND f.start_date = b.start_date
                AND f.end_date = b.end_date
                AND (b.is_opening = 0 OR b.is_opening IS NULL)
            WHERE f.outlet_name = %s
            AND (f.is_opening = 0 OR f.is_opening IS NULL)
            ORDER BY f.start_date DESC, f.end_date DESC
        """
        cursor.execute(query, (outlet,))
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