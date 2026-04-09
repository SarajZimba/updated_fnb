# from flask import Blueprint, jsonify, request
# import mysql.connector
# import os
# from dotenv import load_dotenv
# from flask_cors import cross_origin
# from root.auth.check import token_auth

# load_dotenv()

# app_file120 = Blueprint('app_file120', __name__)

# def get_db_connection():
#     return mysql.connector.connect(
#         host=os.getenv("host"),
#         user=os.getenv("user"),
#         password=os.getenv("password"),
#         database=os.getenv("database")
#     )

# @app_file120.route("/inventory-snapshot-reports-details", methods=["POST"])
# @cross_origin()
# def receive_snapshot_details():
#     try:
#         data = request.get_json()
#         token = data.get("token")
#         snapshot_id = data.get("snapshot_id")
#         item_type = data.get("type")  # Optional: "Food", "Beverage", "Others"

#         if not token or not token_auth(token):
#             return jsonify({"error": "Invalid or missing token."}), 400

#         if not snapshot_id:
#             return jsonify({"error": "Missing required parameter: snapshot_id"}), 400

#         mydb = get_db_connection()
#         cursor = mydb.cursor(dictionary=True)

#         # Fetch snapshot info
#         cursor.execute("""
#             SELECT outlet_name, start_date, end_date 
#             FROM inventory_snapshot_master 
#             WHERE id = %s
#         """, (snapshot_id,))
#         snapshot = cursor.fetchone()
#         if not snapshot:
#             return jsonify({"error": "Snapshot not found"}), 404

#         outlet_name = snapshot['outlet_name']
#         start_date = snapshot['start_date']
#         end_date = snapshot['end_date']

#         # Fetch snapshot items with cost data
#         query = """
#             SELECT 
#                 item_name, item_type, group_name, uom, new_uom,
#                 opening_count, total_received, total_consumed,
#                 closing_balance, wastage_count, physical_count, discrepancy_count,
#                 rate, received_cost, consumption_cost, wastage_cost,
#                 (closing_balance * rate) AS closing_value
#             FROM inventory_snapshot_items
#             WHERE snapshot_id = %s
#         """
#         params = [snapshot_id]

#         if item_type:
#             query += " AND item_type = %s"
#             params.append(item_type)

#         query += " ORDER BY item_name ASC"

#         cursor.execute(query, tuple(params))
#         items = cursor.fetchall()

#         cursor.close()
#         mydb.close()

#         return jsonify({
#             "status": "success",
#             "snapshot_id": snapshot_id,
#             "outlet_name": outlet_name,
#             "start_date": str(start_date),
#             "end_date": str(end_date),
#             "filtered_by_type": item_type if item_type else "All",
#             "items": items
#         }), 200

#     except Exception as e:
#         if 'mydb' in locals():
#             mydb.rollback()
#             mydb.close()
#         return jsonify({"error": str(e)}), 400

from flask import Blueprint, jsonify, request
import mysql.connector
import os
from dotenv import load_dotenv
from flask_cors import cross_origin
from root.auth.check import token_auth

load_dotenv()

app_file120 = Blueprint('app_file120', __name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("host"),
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )

@app_file120.route("/inventory-snapshot-reports-details", methods=["POST"])
@cross_origin()
def receive_snapshot_details():
    try:
        data = request.get_json()
        token = data.get("token")
        snapshot_id = data.get("snapshot_id")
        item_type = data.get("type")  # Optional: "Food", "Beverage", "Others"

        if not token or not token_auth(token):
            return jsonify({"error": "Invalid or missing token."}), 400

        if not snapshot_id:
            return jsonify({"error": "Missing required parameter: snapshot_id"}), 400

        mydb = get_db_connection()
        cursor = mydb.cursor(dictionary=True)

        # Fetch snapshot info
        cursor.execute("""
            SELECT outlet_name, start_date, end_date 
            FROM inventory_snapshot_master 
            WHERE id = %s
        """, (snapshot_id,))
        snapshot = cursor.fetchone()
        if not snapshot:
            return jsonify({"error": "Snapshot not found"}), 404

        outlet_name = snapshot['outlet_name']
        start_date = snapshot['start_date']
        end_date = snapshot['end_date']

        # Fetch snapshot items with cost data
        query = """
            SELECT 
                id, item_name, item_type, group_name, uom, new_uom,
                opening_count, total_received, total_consumed,
                closing_balance, wastage_count, physical_count, discrepancy_count,
                rate, received_cost, consumption_cost, wastage_cost
            FROM inventory_snapshot_items
            WHERE snapshot_id = %s
        """
        params = [snapshot_id]

        if item_type:
            query += " AND item_type = %s"
            params.append(item_type)

        query += " ORDER BY item_name ASC"

        cursor.execute(query, tuple(params))
        items = cursor.fetchall()

        cursor.close()
        mydb.close()

        return jsonify({
            "status": "success",
            "snapshot_id": snapshot_id,
            "outlet_name": outlet_name,
            "start_date": str(start_date),
            "end_date": str(end_date),
            "filtered_by_type": item_type if item_type else "All",
            "items": items
        }), 200

    except Exception as e:
        if 'mydb' in locals():
            mydb.rollback()
            mydb.close()
        return jsonify({"error": str(e)}), 400