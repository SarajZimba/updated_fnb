from flask import Blueprint, jsonify, request
import mysql.connector
import os
from dotenv import load_dotenv
from flask_cors import cross_origin
from root.auth.check import token_auth
from decimal import Decimal, ROUND_HALF_UP

load_dotenv()

app_file225 = Blueprint('app_file225', __name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("host"),
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )

@app_file225.route("/calculate-physical-cost", methods=["POST"])
@cross_origin()
def calculate_physical_cost():
    try:
        data = request.get_json()

        token = data.get("token")
        if not token or not token_auth(token):
            return jsonify({"error": "Invalid or missing token."}), 400

        item_name = data.get("item_name")
        outlet = data.get("outlet")
        costcenter = data.get("costcenter")
        physical_count = data.get("physical_count")

        if not item_name or not outlet or not costcenter:
            return jsonify({"error": "Missing required fields."}), 400

        if physical_count is None:
            return jsonify({"error": "physical_count is required."}), 400

        # 🔢 Round physical count properly
        physical_count = float(
            Decimal(str(physical_count)).quantize(Decimal('0.01'), ROUND_HALF_UP)
        )

        mydb = get_db_connection()
        cursor = mydb.cursor(dictionary=True)

        # 🔥 Fetch stock in LIFO (with costcenter filter)
        cursor.execute("""
            SELECT quantity, rate 
            FROM item_current_level
            WHERE itemname = %s 
              AND outlet = %s 
              AND costcenter = %s
              AND quantity > 0
            ORDER BY id DESC
        """, (item_name, outlet, costcenter))

        stock_rows = cursor.fetchall()

        remaining_physical_qty = physical_count
        physical_cost = 0.0
        last_rate = 0.0

        # 🔁 LIFO Calculation
        for row in stock_rows:
            available_qty = float(row["quantity"])
            rate = float(row["rate"])
            last_rate = rate

            if remaining_physical_qty <= 0:
                break

            used_qty = min(available_qty, remaining_physical_qty)
            physical_cost += used_qty * rate
            remaining_physical_qty -= used_qty

        # 🔁 Handle shortage using last rate
        if remaining_physical_qty > 0 and last_rate > 0:
            physical_cost += remaining_physical_qty * last_rate

        cursor.close()
        mydb.close()

        return jsonify({
            "item_name": item_name,
            "outlet": outlet,
            "costcenter": costcenter,
            "physical_count": physical_count,
            "physical_cost": round(physical_cost, 2)
        }), 200

    except Exception as e:
        if 'mydb' in locals():
            mydb.rollback()
            mydb.close()
        return jsonify({"error": str(e)}), 400