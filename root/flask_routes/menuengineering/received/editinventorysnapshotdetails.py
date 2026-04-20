# from flask import Blueprint, request, jsonify
# import mysql.connector
# from decimal import Decimal, ROUND_HALF_UP
# from dotenv import load_dotenv
# import os
# from flask_cors import cross_origin
# from root.auth.check import token_auth

# load_dotenv()

# app_file126 = Blueprint('app_file126', __name__)

# def get_db_connection():
#     return mysql.connector.connect(
#         host=os.getenv("host"),
#         user=os.getenv("user"),
#         password=os.getenv("password"),
#         database=os.getenv("database")
#     )

# @app_file126.route("/update-physical-counts", methods=["POST"])
# @cross_origin()
# def update_physical_counts():
#     try:
#         data = request.get_json()
#         token = data.get("token")
#         updates = data.get("updates")  # List of { snapshot_detail_id, physical_count }

#         if not token or not token_auth(token):
#             return jsonify({"error": "Invalid or missing token."}), 401

#         if not updates or not isinstance(updates, list):
#             return jsonify({"error": "Missing or invalid 'updates' list."}), 400

#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)

#         results = []

#         for entry in updates:
#             snapshot_detail_id = entry.get("snapshot_detail_id")
#             new_physical_count = entry.get("physical_count")

#             if not snapshot_detail_id or new_physical_count is None:
#                 results.append({"snapshot_detail_id": snapshot_detail_id, "error": "Missing data"})
#                 continue

#             # Fetch current item record
#             cursor.execute("""
#                 SELECT isi.*, ism.outlet_name, ism.start_date, ism.end_date
#                 FROM inventory_snapshot_items isi
#                 JOIN inventory_snapshot_master ism ON ism.id = isi.snapshot_id
#                 WHERE isi.id = %s
#             """, (snapshot_detail_id,))
#             item = cursor.fetchone()

#             if not item:
#                 results.append({"snapshot_detail_id": snapshot_detail_id, "error": "Item not found"})
#                 continue

#             item_name = item["item_name"]
#             outlet = item["outlet_name"]
#             start_date = item["start_date"]
#             end_date = item["end_date"]

#             physical_count = float(Decimal(new_physical_count).quantize(Decimal('0.01'), ROUND_HALF_UP))

#             # Recalculate physical cost (LIFO)
#             cursor.execute("""
#                 SELECT quantity, rate FROM item_current_level
#                 WHERE itemname = %s AND outlet = %s AND quantity > 0
#                 ORDER BY id DESC
#             """, (item_name, outlet))
#             stock_rows = cursor.fetchall()

#             remaining_qty = physical_count
#             physical_cost = 0.0
#             last_rate = 0.0

#             for row in stock_rows:
#                 available_qty = float(row["quantity"])
#                 rate = float(row["rate"])
#                 last_rate = rate
#                 if remaining_qty <= 0:
#                     break
#                 used_qty = min(available_qty, remaining_qty)
#                 physical_cost += used_qty * rate
#                 remaining_qty -= used_qty

#             if remaining_qty > 0 and last_rate > 0:
#                 physical_cost += remaining_qty * last_rate

#             opening_cost = float(item.get("opening_cost") or 0)
#             received_cost = float(item.get("received_cost") or 0)
#             wastage_cost = float(item.get("wastage_cost") or 0)

#             actual_consumption_cost = opening_cost + received_cost + wastage_cost - physical_cost

#             total_cost = opening_cost + received_cost - wastage_cost - float(item.get("consumption_cost") or 0)
#             rate = round(total_cost / physical_count, 4) if physical_count > 0 else 0
#             closing_balance = round(physical_count * rate, 2)

#             # Update the row
#             cursor.execute("""
#                 UPDATE inventory_snapshot_items
#                 SET physical_count = %s,
#                     physical_cost = %s,
#                     actual_consumption_cost = %s,
#                     rate = %s,
#                     closing_balance = %s
#                 WHERE id = %s
#             """, (
#                 physical_count,
#                 round(physical_cost, 2),
#                 round(actual_consumption_cost, 2),
#                 rate,
#                 closing_balance,
#                 snapshot_detail_id
#             ))

#             results.append({
#                 "snapshot_detail_id": snapshot_detail_id,
#                 "status": "updated",
#                 "physical_count": physical_count,
#                 "physical_cost": round(physical_cost, 2),
#                 "actual_consumption_cost": round(actual_consumption_cost, 2),
#                 "rate": rate,
#                 "closing_balance": closing_balance
#             })

#         conn.commit()
#         cursor.close()
#         conn.close()

#         return jsonify({
#             "status": "success",
#             "results": results
#         }), 200

#     except Exception as e:
#         if 'conn' in locals():
#             conn.rollback()
#             conn.close()
#         return jsonify({"error": str(e)}), 500

from flask import Blueprint, request, jsonify
import mysql.connector
from decimal import Decimal, ROUND_HALF_UP
from dotenv import load_dotenv
import os
from flask_cors import cross_origin
from root.auth.check import token_auth

load_dotenv()

app_file126 = Blueprint('app_file126', __name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("host"),
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )

@app_file126.route("/update-physical-counts", methods=["POST"])
@cross_origin()
def update_physical_counts():
    try:
        data = request.get_json()
        token = data.get("token")
        updates = data.get("updates")  # List of { snapshot_detail_id, physical_count }

        if not token or not token_auth(token):
            return jsonify({"error": "Invalid or missing token."}), 401

        if not updates or not isinstance(updates, list):
            return jsonify({"error": "Missing or invalid 'updates' list."}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        results = []

        for entry in updates:
            snapshot_detail_id = entry.get("snapshot_detail_id")
            new_physical_count = entry.get("physical_count")

            if not snapshot_detail_id or new_physical_count is None:
                results.append({"snapshot_detail_id": snapshot_detail_id, "error": "Missing data"})
                continue

            # Fetch current item record
            cursor.execute("""
                SELECT isi.*, ism.outlet_name, ism.start_date, ism.end_date
                FROM inventory_snapshot_items isi
                JOIN inventory_snapshot_master ism ON ism.id = isi.snapshot_id
                WHERE isi.id = %s
            """, (snapshot_detail_id,))
            item = cursor.fetchone()

            if not item:
                results.append({"snapshot_detail_id": snapshot_detail_id, "error": "Item not found"})
                continue

            item_name = item["item_name"]
            outlet = item["outlet_name"]
            start_date = item["start_date"]
            end_date = item["end_date"]

            physical_count = float(Decimal(new_physical_count).quantize(Decimal('0.01'), ROUND_HALF_UP))

            # Recalculate physical cost (LIFO)
            cursor.execute("""
                SELECT quantity, rate FROM item_current_level
                WHERE itemname = %s AND outlet = %s AND quantity > 0
                ORDER BY id DESC
            """, (item_name, outlet))
            stock_rows = cursor.fetchall()

            remaining_qty = physical_count
            physical_cost = 0.0
            last_rate = 0.0

            for row in stock_rows:
                available_qty = float(row["quantity"])
                rate = float(row["rate"])
                last_rate = rate
                if remaining_qty <= 0:
                    break
                used_qty = min(available_qty, remaining_qty)
                physical_cost += used_qty * rate
                remaining_qty -= used_qty

            if remaining_qty > 0 and last_rate > 0:
                physical_cost += remaining_qty * last_rate

            opening_cost = float(item.get("opening_cost") or 0)
            received_cost = float(item.get("received_cost") or 0)
            wastage_cost = float(item.get("wastage_cost") or 0)

            actual_consumption_cost = opening_cost + received_cost + wastage_cost - physical_cost

            total_cost = opening_cost + received_cost - wastage_cost - float(item.get("consumption_cost") or 0)
            rate = round(total_cost / physical_count, 4) if physical_count > 0 else 0
            closing_balance = round(physical_count * rate, 2)

            # ... (after calculating `physical_count`)

            closing_count = float(item.get("closing_count") or 0)
            discrepancy_count = round(physical_count - closing_count, 4)
            # Update the row
            cursor.execute("""
                UPDATE inventory_snapshot_items
                SET physical_count = %s,
                    physical_cost = %s,
                    actual_consumption_cost = %s,
                    rate = %s,
                    closing_balance = %s,
                    discrepancy_count = %s
                WHERE id = %s
            """, (
                physical_count,
                round(physical_cost, 2),
                round(actual_consumption_cost, 2),
                rate,
                closing_balance,
                discrepancy_count,
                snapshot_detail_id
            ))

            results.append({
                "snapshot_detail_id": snapshot_detail_id,
                "status": "updated",
                "physical_count": physical_count,
                "physical_cost": round(physical_cost, 2),
                "actual_consumption_cost": round(actual_consumption_cost, 2),
                "rate": rate,
                "closing_balance": closing_balance
            })

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "results": results
        }), 200

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return jsonify({"error": str(e)}), 500
    

@app_file126.route("/update-physical-counts-food", methods=["POST"])
@cross_origin()
def update_physical_counts_food():
    try:
        data = request.get_json()
        token = data.get("token")
        updates = data.get("updates")  # List of { snapshot_detail_id, physical_count }

        if not token or not token_auth(token):
            return jsonify({"error": "Invalid or missing token."}), 401

        if not updates or not isinstance(updates, list):
            return jsonify({"error": "Missing or invalid 'updates' list."}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        results = []

        for entry in updates:
            snapshot_detail_id = entry.get("snapshot_detail_id")
            new_physical_count = entry.get("physical_count")

            if not snapshot_detail_id or new_physical_count is None:
                results.append({"snapshot_detail_id": snapshot_detail_id, "error": "Missing data"})
                continue

            # Fetch current item record
            cursor.execute("""
                SELECT isi.*, ism.outlet_name, ism.start_date, ism.end_date
                FROM inventory_snapshot_items_food isi
                JOIN inventory_snapshot_master_food ism ON ism.id = isi.snapshot_id
                WHERE isi.id = %s
            """, (snapshot_detail_id,))
            item = cursor.fetchone()

            if not item:
                results.append({"snapshot_detail_id": snapshot_detail_id, "error": "Item not found"})
                continue

            item_name = item["item_name"]
            outlet = item["outlet_name"]
            start_date = item["start_date"]
            end_date = item["end_date"]

            physical_count = float(Decimal(new_physical_count).quantize(Decimal('0.01'), ROUND_HALF_UP))

            # Recalculate physical cost (LIFO)
            cursor.execute("""
                SELECT quantity, rate FROM item_current_level
                WHERE itemname = %s AND outlet = %s AND quantity > 0
                ORDER BY id DESC
            """, (item_name, outlet))
            stock_rows = cursor.fetchall()

            remaining_qty = physical_count
            physical_cost = 0.0
            last_rate = 0.0

            for row in stock_rows:
                available_qty = float(row["quantity"])
                rate = float(row["rate"])
                last_rate = rate
                if remaining_qty <= 0:
                    break
                used_qty = min(available_qty, remaining_qty)
                physical_cost += used_qty * rate
                remaining_qty -= used_qty

            if remaining_qty > 0 and last_rate > 0:
                physical_cost += remaining_qty * last_rate

            opening_cost = float(item.get("opening_cost") or 0)
            received_cost = float(item.get("received_cost") or 0)
            wastage_cost = float(item.get("wastage_cost") or 0)

            actual_consumption_cost = opening_cost + received_cost + wastage_cost - physical_cost

            total_cost = opening_cost + received_cost - wastage_cost - float(item.get("consumption_cost") or 0)
            rate = round(total_cost / physical_count, 4) if physical_count > 0 else 0
            closing_balance = round(physical_count * rate, 2)

            # ... (after calculating `physical_count`)

            closing_count = float(item.get("closing_count") or 0)
            discrepancy_count = round(physical_count - closing_count, 4)
            # Update the row
            cursor.execute("""
                UPDATE inventory_snapshot_items_food
                SET physical_count = %s,
                    physical_cost = %s,
                    actual_consumption_cost = %s,
                    rate = %s,
                    closing_balance = %s,
                    discrepancy_count = %s
                WHERE id = %s
            """, (
                physical_count,
                round(physical_cost, 2),
                round(actual_consumption_cost, 2),
                rate,
                closing_balance,
                discrepancy_count,
                snapshot_detail_id
            ))

            results.append({
                "snapshot_detail_id": snapshot_detail_id,
                "status": "updated",
                "physical_count": physical_count,
                "physical_cost": round(physical_cost, 2),
                "actual_consumption_cost": round(actual_consumption_cost, 2),
                "rate": rate,
                "closing_balance": closing_balance
            })

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "results": results
        }), 200

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return jsonify({"error": str(e)}), 500
    
@app_file126.route("/update-physical-counts-beverage", methods=["POST"])
@cross_origin()
def update_physical_counts_beverage():
    try:
        data = request.get_json()
        token = data.get("token")
        updates = data.get("updates")  # List of { snapshot_detail_id, physical_count }

        if not token or not token_auth(token):
            return jsonify({"error": "Invalid or missing token."}), 401

        if not updates or not isinstance(updates, list):
            return jsonify({"error": "Missing or invalid 'updates' list."}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        results = []

        for entry in updates:
            snapshot_detail_id = entry.get("snapshot_detail_id")
            new_physical_count = entry.get("physical_count")

            if not snapshot_detail_id or new_physical_count is None:
                results.append({"snapshot_detail_id": snapshot_detail_id, "error": "Missing data"})
                continue

            # Fetch current item record
            cursor.execute("""
                SELECT isi.*, ism.outlet_name, ism.start_date, ism.end_date
                FROM inventory_snapshot_items_beverage isi
                JOIN inventory_snapshot_master_beverage ism ON ism.id = isi.snapshot_id
                WHERE isi.id = %s
            """, (snapshot_detail_id,))
            item = cursor.fetchone()

            if not item:
                results.append({"snapshot_detail_id": snapshot_detail_id, "error": "Item not found"})
                continue

            item_name = item["item_name"]
            outlet = item["outlet_name"]
            start_date = item["start_date"]
            end_date = item["end_date"]

            physical_count = float(Decimal(new_physical_count).quantize(Decimal('0.01'), ROUND_HALF_UP))

            # Recalculate physical cost (LIFO)
            cursor.execute("""
                SELECT quantity, rate FROM item_current_level
                WHERE itemname = %s AND outlet = %s AND quantity > 0
                ORDER BY id DESC
            """, (item_name, outlet))
            stock_rows = cursor.fetchall()

            remaining_qty = physical_count
            physical_cost = 0.0
            last_rate = 0.0

            for row in stock_rows:
                available_qty = float(row["quantity"])
                rate = float(row["rate"])
                last_rate = rate
                if remaining_qty <= 0:
                    break
                used_qty = min(available_qty, remaining_qty)
                physical_cost += used_qty * rate
                remaining_qty -= used_qty

            if remaining_qty > 0 and last_rate > 0:
                physical_cost += remaining_qty * last_rate

            opening_cost = float(item.get("opening_cost") or 0)
            received_cost = float(item.get("received_cost") or 0)
            wastage_cost = float(item.get("wastage_cost") or 0)

            actual_consumption_cost = opening_cost + received_cost + wastage_cost - physical_cost

            total_cost = opening_cost + received_cost - wastage_cost - float(item.get("consumption_cost") or 0)
            rate = round(total_cost / physical_count, 4) if physical_count > 0 else 0
            closing_balance = round(physical_count * rate, 2)

            # ... (after calculating `physical_count`)

            closing_count = float(item.get("closing_count") or 0)
            discrepancy_count = round(physical_count - closing_count, 4)
            # Update the row
            cursor.execute("""
                UPDATE inventory_snapshot_items_beverage
                SET physical_count = %s,
                    physical_cost = %s,
                    actual_consumption_cost = %s,
                    rate = %s,
                    closing_balance = %s,
                    discrepancy_count = %s
                WHERE id = %s
            """, (
                physical_count,
                round(physical_cost, 2),
                round(actual_consumption_cost, 2),
                rate,
                closing_balance,
                discrepancy_count,
                snapshot_detail_id
            ))

            results.append({
                "snapshot_detail_id": snapshot_detail_id,
                "status": "updated",
                "physical_count": physical_count,
                "physical_cost": round(physical_cost, 2),
                "actual_consumption_cost": round(actual_consumption_cost, 2),
                "rate": rate,
                "closing_balance": closing_balance
            })

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "results": results
        }), 200

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return jsonify({"error": str(e)}), 500