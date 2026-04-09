# from flask import Blueprint, jsonify, request
# import mysql.connector
# import os
# from dotenv import load_dotenv
# from flask_cors import cross_origin
# from root.auth.check import token_auth
# from decimal import Decimal, ROUND_HALF_UP
# from datetime import datetime

# load_dotenv()

# app_file116 = Blueprint('app_file116', __name__)

# def get_db_connection():
#     return mysql.connector.connect(
#         host=os.getenv("host"),
#         user=os.getenv("user"),
#         password=os.getenv("password"),
#         database=os.getenv("database")
#     )

# @app_file116.route("/save-inventory-snapshot", methods=["POST"])
# @cross_origin()
# def save_inventory_snapshot():
#     try:
#         data = request.get_json()
#         token = data.get("token")
#         if not token or not token_auth(token):
#             return jsonify({"error": "Invalid or missing token."}), 400

#         items = data.get("items")
#         outlet = data.get("outlet")
#         start_date = data.get("start_date")
#         end_date = data.get("end_date")
#         food_total_items = data.get("food_total_items")
#         beverage_total_items = data.get("beverage_total_items")
#         food_accuracy = data.get("food_accuracy")
#         beverage_accuracy = data.get("beverage_accuracy")

#         if not all([items, outlet, start_date, end_date]):
#             return jsonify({"error": "Missing required fields."}), 400

#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)

#         today = datetime.now().date()
#         cursor.execute("""
#             SELECT id FROM inventory_snapshot_master
#             WHERE outlet_name = %s AND DATE(created_at) = %s
#         """, (outlet, today))

#         is_opening = False
#         if cursor.fetchone():
#             cursor.close()
#             conn.close()
#             return jsonify({"error": f"Inventory snapshot has already been saved for {outlet} today."}), 400

#         cursor.execute("""
#             SELECT COUNT(*) AS count FROM inventory_snapshot_master
#             WHERE outlet_name = %s
#         """, (outlet,))
#         if cursor.fetchone()["count"] == 0:
#             is_opening = True

#         # Insert master record
#         cursor.execute("""
#             INSERT INTO inventory_snapshot_master (
#                 outlet_name, start_date, end_date, created_at,
#                 food_total_items, beverage_total_items,
#                 food_accuracy, beverage_accuracy
#             ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
#         """, (
#             outlet, start_date, end_date, datetime.now(),
#             food_total_items, beverage_total_items,
#             food_accuracy, beverage_accuracy
#         ))

#         snapshot_id = cursor.lastrowid

#         insert_item_sql = """
#             INSERT INTO inventory_snapshot_items (
#                 snapshot_id, item_name, item_type, group_name,
#                 uom, new_uom, total_consumed, total_received,
#                 closing_balance, closing_count, opening_count,
#                 wastage_count, physical_count, discrepancy_count,
#                 received_cost, consumption_cost, wastage_cost, rate,actual_consumption_cost,opening_cost, physical_cost
#             ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#         """

#         for item in items:
#             item_name = item.get("name")

#             # Get consumption cost
#             cursor.execute("""
#                 SELECT SUM(consumed_quantity * rate) AS total_consumption_cost
#                 FROM consumption_tracker
#                 WHERE item_name = %s AND outlet = %s AND order_date BETWEEN %s AND %s
#             """, (item_name, outlet, start_date, end_date))
#             consumption_cost = float(cursor.fetchone()["total_consumption_cost"] or 0)

#             # Get received cost
#             # cursor.execute("""
#             #     SELECT SUM(quantity * price) AS total_received_cost
#             #     FROM received_items
#             #     WHERE item_name = %s AND outlet_name = %s AND received_date BETWEEN %s AND %s
#             # """, (item_name, outlet, start_date, end_date))

#             # Get received cost from store requisition tables
#             cursor.execute("""
#                 SELECT SUM(d.Amount * d.Rate) AS total_received_cost
#                 FROM intblstorereqdetails d
#                 JOIN intblstorerequisition r ON d.StoreReqID = r.idintblStoreRequisition
#                 WHERE d.ItemName = %s 
#                     AND r.Outlet = %s 
#                     AND DATE(r.Date) BETWEEN %s AND %s
#             """, (item_name, outlet, start_date, end_date))
#             received_cost = float(cursor.fetchone()["total_received_cost"] or 0)

#             # Get wastage cost
#             cursor.execute("""
#                 SELECT SUM(price) AS total_wastage_cost
#                 FROM wastage_items
#                 WHERE item_name = %s AND outlet_name = %s AND received_date BETWEEN %s AND %s
#             """, (item_name, outlet, start_date, end_date))
#             wastage_cost = float(cursor.fetchone()["total_wastage_cost"] or 0)

#             # Get closing quantity (from frontend input)
#             closing_count = float(Decimal(item.get("closing_balance", 0)).quantize(Decimal('0.01'), ROUND_HALF_UP))

#             # Get previous closing balance to calculate opening cost
#             cursor.execute("""
#                 SELECT isi.rate, isi.closing_balance
#                 FROM inventory_snapshot_items isi
#                 JOIN inventory_snapshot_master ism ON isi.snapshot_id = ism.id
#                 WHERE ism.outlet_name = %s AND isi.item_name = %s AND ism.end_date < %s
#                 ORDER BY ism.end_date DESC LIMIT 1
#             """, (outlet, item_name, start_date))
#             prev = cursor.fetchone()
#             opening_cost = 0
#             if prev:
#                 opening_cost = float(prev["closing_balance"] or 0)
#             else:
#                 cursor.execute("""
#                     SELECT Rate FROM stock_statement
#                     WHERE ItemName = %s AND OutletName = %s
#                 """, (item_name, outlet))
#                 opening_rate_result = cursor.fetchone()
#                 if not opening_rate_result:
#                     print(f"{item_name} didnt have stockstatement")
#                     # continue
#                     opening_cost = 0
#                 else:
#                     opening_rate = float(opening_rate_result["Rate"])
#                     opening_cost = opening_rate * float(item.get("opening_count", 0))

#             # Total cost = opening + received - wastage - consumption
#             total_cost = opening_cost + received_cost - wastage_cost - consumption_cost

#             # Step 1: Get physical_count from frontend
#             physical_count = float(Decimal(item.get("physical_count", 0)).quantize(Decimal('0.01'), ROUND_HALF_UP))
#             remaining_physical_qty = physical_count
#             physical_cost = 0.0

#             # Step 2: Fetch from item_current_level in **LIFO** order
#             cursor.execute("""
#                 SELECT quantity, rate FROM item_current_level
#                 WHERE itemname = %s AND outlet = %s AND quantity > 0
#                 ORDER BY id DESC
#             """, (item_name, outlet))
#             stock_rows = cursor.fetchall()

#             last_rate = 0.0

#             # Step 3: LIFO calculation
#             for row in stock_rows:
#                 available_qty = float(row["quantity"])
#                 rate = float(row["rate"])
#                 last_rate = rate  # update last seen rate

#                 if remaining_physical_qty <= 0:
#                     break

#                 used_qty = min(available_qty, remaining_physical_qty)
#                 physical_cost += used_qty * rate
#                 remaining_physical_qty -= used_qty

#             # Step 4: If there's still remaining quantity, use the last known rate
#             if remaining_physical_qty > 0 and last_rate > 0:
#                 physical_cost += remaining_physical_qty * last_rate



#             actual_consumption_cost = opening_cost + received_cost + wastage_cost - physical_cost

#             if is_opening == False:

#                 rate = round(total_cost / physical_count, 4) if physical_count > 0 else 0
#                 closing_balance = round(physical_count * rate, 2)
            
#             else:
#                 cursor.execute("""
#                     SELECT Rate FROM stock_statement
#                     WHERE ItemName = %s AND OutletName = %s
#                 """, (item_name, outlet))
#                 noopening_rate_result = cursor.fetchone()
#                 if not opening_rate_result:
#                     print(f"{item_name} didnt have stockstatement")
#                 else:
#                     noopening_rate = float(noopening_rate_result["Rate"])
#                     closing_cost = noopening_rate * physical_count
#                     closing_balance = closing_cost
#                     rate = noopening_rate

#             # Insert record
#             cursor.execute(insert_item_sql, (
#                 snapshot_id,
#                 item_name,
#                 item.get("type"),
#                 item.get("group_name"),
#                 item.get("uom"),
#                 item.get("new_uom"),
#                 float(Decimal(item.get("total_consumed", 0)).quantize(Decimal('0.01'), ROUND_HALF_UP)),
#                 float(Decimal(item.get("total_received", 0)).quantize(Decimal('0.01'), ROUND_HALF_UP)),
#                 closing_balance,
#                 closing_count,
#                 float(Decimal(item.get("opening_count", 0)).quantize(Decimal('0.01'), ROUND_HALF_UP)),
#                 float(Decimal(item.get("total_wastage", 0)).quantize(Decimal('0.01'), ROUND_HALF_UP)),
#                 float(Decimal(item.get("physical_count", 0)).quantize(Decimal('0.01'), ROUND_HALF_UP)),
#                 float(Decimal(item.get("discrepancy_count", 0)).quantize(Decimal('0.01'), ROUND_HALF_UP)),
#                 round(received_cost, 2),
#                 round(consumption_cost, 2),
#                 round(wastage_cost, 2),
#                 rate,
#                 round(actual_consumption_cost, 2),
#                 round(opening_cost, 2),
#                 round(physical_cost, 2)
#             ))

#             # Opening stock insert (if first snapshot)
#             if is_opening:
#                 cursor.execute("""
#                     SELECT Rate FROM stock_statement
#                     WHERE ItemName = %s AND OutletName = %s
#                 """, (item_name, outlet))
#                 rate_result = cursor.fetchone()
#                 if not rate_result:
#                     continue
#                 opening_rate = float(rate_result["Rate"])

#                 # Always insert a new row for opening stock (sequentially)
#                 cursor.execute("""
#                     INSERT INTO item_current_level (itemname, quantity, rate, outlet)
#                     VALUES (%s, %s, %s, %s)
#                 """, (item_name, closing_count, opening_rate, outlet))


#         conn.commit()
#         cursor.close()
#         conn.close()

#         return jsonify({"status": "success", "snapshot_id": snapshot_id}), 200

#     except Exception as e:
#         if 'conn' in locals():
#             conn.rollback()
#             conn.close()
#         return jsonify({"error": str(e)}), 500



from flask import Blueprint, jsonify, request
import mysql.connector
import os
from dotenv import load_dotenv
from flask_cors import cross_origin
from root.auth.check import token_auth
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime

load_dotenv()

app_file116 = Blueprint('app_file116', __name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("host"),
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )

@app_file116.route("/save-inventory-snapshot", methods=["POST"])
@cross_origin()
def save_inventory_snapshot():
    try:
        data = request.get_json()
        token = data.get("token")
        if not token or not token_auth(token):
            return jsonify({"error": "Invalid or missing token."}), 400

        items = data.get("items")
        outlet = data.get("outlet")
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        food_total_items = data.get("food_total_items")
        beverage_total_items = data.get("beverage_total_items")
        food_accuracy = data.get("food_accuracy")
        beverage_accuracy = data.get("beverage_accuracy")

        if not all([items, outlet, start_date, end_date]):
            return jsonify({"error": "Missing required fields."}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        today = datetime.now().date()
        cursor.execute("""
            SELECT id FROM inventory_snapshot_master
            WHERE outlet_name = %s AND DATE(created_at) = %s
        """, (outlet, today))

        is_opening = False
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": f"Inventory snapshot has already been saved for {outlet} today."}), 400

        cursor.execute("""
            SELECT COUNT(*) AS count FROM inventory_snapshot_master
            WHERE outlet_name = %s
        """, (outlet,))
        if cursor.fetchone()["count"] == 0:
            is_opening = True

        # Insert master record
        cursor.execute("""
            INSERT INTO inventory_snapshot_master (
                outlet_name, start_date, end_date, created_at,
                food_total_items, beverage_total_items,
                food_accuracy, beverage_accuracy
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            outlet, start_date, end_date, datetime.now(),
            food_total_items, beverage_total_items,
            food_accuracy, beverage_accuracy
        ))

        snapshot_id = cursor.lastrowid

        insert_item_sql = """
            INSERT INTO inventory_snapshot_items (
                snapshot_id, item_name, item_type, group_name,
                uom, new_uom, total_consumed, total_received,
                closing_balance, closing_count, opening_count,
                wastage_count, physical_count, discrepancy_count,
                received_cost, consumption_cost, wastage_cost, rate,actual_consumption_cost,opening_cost, physical_cost
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        for item in items:
            item_name = item.get("name")

            # Get consumption cost
            cursor.execute("""
                SELECT SUM(consumed_quantity * rate) AS total_consumption_cost
                FROM consumption_tracker
                WHERE item_name = %s AND outlet = %s AND order_date BETWEEN %s AND %s
            """, (item_name, outlet, start_date, end_date))
            consumption_cost = float(cursor.fetchone()["total_consumption_cost"] or 0)

            # # Get received cost
            # cursor.execute("""
            #     SELECT SUM(quantity * price) AS total_received_cost
            #     FROM received_items
            #     WHERE item_name = %s AND outlet_name = %s AND received_date BETWEEN %s AND %s
            # """, (item_name, outlet, start_date, end_date))

            # Get received cost from store requisition tables
            cursor.execute("""
                SELECT SUM(d.Amount * d.Rate) AS total_received_cost
                FROM intblstorereqdetails d
                JOIN intblstorerequisition r ON d.StoreReqID = r.idintblStoreRequisition
                WHERE d.ItemName = %s 
                    AND r.Outlet = %s 
                    AND DATE(r.Date) BETWEEN %s AND %s
            """, (item_name, outlet, start_date, end_date))

            received_cost = float(cursor.fetchone()["total_received_cost"] or 0)

            # Get wastage cost
            cursor.execute("""
                SELECT SUM(price) AS total_wastage_cost
                FROM wastage_items
                WHERE item_name = %s AND outlet_name = %s AND received_date BETWEEN %s AND %s
            """, (item_name, outlet, start_date, end_date))
            wastage_cost = float(cursor.fetchone()["total_wastage_cost"] or 0)

            # Get closing quantity (from frontend input)
            closing_count = float(Decimal(item.get("closing_balance", 0)).quantize(Decimal('0.01'), ROUND_HALF_UP))

            # Get previous closing balance to calculate opening cost
            cursor.execute("""
                SELECT isi.rate, isi.closing_balance
                FROM inventory_snapshot_items isi
                JOIN inventory_snapshot_master ism ON isi.snapshot_id = ism.id
                WHERE ism.outlet_name = %s AND isi.item_name = %s AND ism.end_date < %s
                ORDER BY ism.end_date DESC LIMIT 1
            """, (outlet, item_name, start_date))
            prev = cursor.fetchone()
            opening_cost = 0
            if prev:
                opening_cost = float(prev["closing_balance"] or 0)
            else:
                cursor.execute("""
                    SELECT Rate FROM stock_statement
                    WHERE ItemName = %s AND OutletName = %s
                """, (item_name, outlet))
                opening_rate_result = cursor.fetchone()
                if not opening_rate_result:
                    print(f"{item_name} didnt have stockstatement")
                    # continue
                    opening_cost = 0
                else:
                    opening_rate = float(opening_rate_result["Rate"])
                    opening_cost = opening_rate * float(item.get("opening_count", 0))

            # Total cost = opening + received - wastage - consumption
            total_cost = opening_cost + received_cost - wastage_cost - consumption_cost

            # Step 1: Get physical_count from frontend
            physical_count = float(Decimal(item.get("physical_count", 0)).quantize(Decimal('0.01'), ROUND_HALF_UP))
            remaining_physical_qty = physical_count
            physical_cost = 0.0

            # Step 2: Fetch from item_current_level in **LIFO** order
            cursor.execute("""
                SELECT quantity, rate FROM item_current_level
                WHERE itemname = %s AND outlet = %s AND quantity > 0
                ORDER BY id DESC
            """, (item_name, outlet))
            stock_rows = cursor.fetchall()

            last_rate = 0.0

            # Step 3: LIFO calculation
            for row in stock_rows:
                available_qty = float(row["quantity"])
                rate = float(row["rate"])
                last_rate = rate  # update last seen rate

                if remaining_physical_qty <= 0:
                    break

                used_qty = min(available_qty, remaining_physical_qty)
                physical_cost += used_qty * rate
                remaining_physical_qty -= used_qty

            # Step 4: If there's still remaining quantity, use the last known rate
            if remaining_physical_qty > 0 and last_rate > 0:
                physical_cost += remaining_physical_qty * last_rate



            actual_consumption_cost = opening_cost + received_cost + wastage_cost - physical_cost

            if is_opening == False:

                rate = round(total_cost / physical_count, 4) if physical_count > 0 else 0
                closing_balance = round(physical_count * rate, 2)
            
            else:
                cursor.execute("""
                    SELECT Rate FROM stock_statement
                    WHERE ItemName = %s AND OutletName = %s
                """, (item_name, outlet))
                noopening_rate_result = cursor.fetchone()
                if not opening_rate_result:
                    print(f"{item_name} didnt have stockstatement")
                else:
                    noopening_rate = float(noopening_rate_result["Rate"])
                    closing_cost = noopening_rate * physical_count
                    closing_balance = closing_cost
                    rate = noopening_rate

            # Insert record
            cursor.execute(insert_item_sql, (
                snapshot_id,
                item_name,
                item.get("type"),
                item.get("group_name"),
                item.get("uom"),
                item.get("new_uom"),
                float(Decimal(item.get("total_consumed", 0)).quantize(Decimal('0.01'), ROUND_HALF_UP)),
                float(Decimal(item.get("total_received", 0)).quantize(Decimal('0.01'), ROUND_HALF_UP)),
                closing_balance,
                closing_count,
                float(Decimal(item.get("opening_count", 0)).quantize(Decimal('0.01'), ROUND_HALF_UP)),
                float(Decimal(item.get("total_wastage", 0)).quantize(Decimal('0.01'), ROUND_HALF_UP)),
                float(Decimal(item.get("physical_count", 0)).quantize(Decimal('0.01'), ROUND_HALF_UP)),
                float(Decimal(item.get("discrepancy_count", 0)).quantize(Decimal('0.01'), ROUND_HALF_UP)),
                round(received_cost, 2),
                round(consumption_cost, 2),
                round(wastage_cost, 2),
                rate,
                round(actual_consumption_cost, 2),
                round(opening_cost, 2),
                round(physical_cost, 2)
            ))

            # Opening stock insert (if first snapshot)
            if is_opening:
                cursor.execute("""
                    SELECT Rate FROM stock_statement
                    WHERE ItemName = %s AND OutletName = %s
                """, (item_name, outlet))
                rate_result = cursor.fetchone()
                if not rate_result:
                    continue
                opening_rate = float(rate_result["Rate"])

                # Always insert a new row for opening stock (sequentially)
                cursor.execute("""
                    INSERT INTO item_current_level (itemname, quantity, rate, outlet)
                    VALUES (%s, %s, %s, %s)
                """, (item_name, closing_count, opening_rate, outlet))


        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"status": "success", "snapshot_id": snapshot_id}), 200

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return jsonify({"error": str(e)}), 500



@app_file116.route("/save-inventory-snapshot-food", methods=["POST"])
@cross_origin()
def save_inventory_snapshot_food():
    try:
        data = request.get_json()
        token = data.get("token")
        if not token or not token_auth(token):
            return jsonify({"error": "Invalid or missing token."}), 400

        items = data.get("items")
        outlet = data.get("outlet")
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        food_total_items = data.get("food_total_items")
        food_accuracy = data.get("food_accuracy")

        if not all([items, outlet, start_date, end_date]):
            return jsonify({"error": "Missing required fields."}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        today = datetime.now().date()
        cursor.execute("""
            SELECT id FROM inventory_snapshot_master_food
            WHERE outlet_name = %s AND DATE(created_at) = %s
        """, (outlet, today))

        is_opening = False
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": f"Inventory snapshot for food has already been saved for {outlet} today."}), 400

        cursor.execute("""
            SELECT COUNT(*) AS count FROM inventory_snapshot_master_food
            WHERE outlet_name = %s
        """, (outlet,))
        if cursor.fetchone()["count"] == 0:
            is_opening = True

        # Insert master record
        cursor.execute("""
            INSERT INTO inventory_snapshot_master_food (
                outlet_name, start_date, end_date, created_at,
                food_total_items,
                food_accuracy
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            outlet, start_date, end_date, datetime.now(),
            food_total_items, 
            food_accuracy
        ))

        snapshot_id = cursor.lastrowid

        insert_item_sql = """
            INSERT INTO inventory_snapshot_items_food (
                snapshot_id, item_name, item_type, group_name,
                uom, new_uom, total_consumed, total_received,
                closing_balance, closing_count, opening_count,
                wastage_count, physical_count, discrepancy_count,
                received_cost, consumption_cost, wastage_cost, rate,actual_consumption_cost,opening_cost, physical_cost
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        for item in items:
            item_name = item.get("name")

            # Get consumption cost
            cursor.execute("""
                SELECT SUM(consumed_quantity * rate) AS total_consumption_cost
                FROM consumption_tracker
                WHERE item_name = %s AND outlet = %s AND order_date BETWEEN %s AND %s
            """, (item_name, outlet, start_date, end_date))
            consumption_cost = float(cursor.fetchone()["total_consumption_cost"] or 0)

            # # Get received cost
            # cursor.execute("""
            #     SELECT SUM(quantity * price) AS total_received_cost
            #     FROM received_items
            #     WHERE item_name = %s AND outlet_name = %s AND received_date BETWEEN %s AND %s
            # """, (item_name, outlet, start_date, end_date))

            # Get received cost from store requisition tables
            cursor.execute("""
                SELECT SUM(d.Amount * d.Rate) AS total_received_cost
                FROM intblstorereqdetails d
                JOIN intblstorerequisition r ON d.StoreReqID = r.idintblStoreRequisition
                WHERE d.ItemName = %s 
                    AND r.Outlet = %s 
                    AND DATE(r.Date) BETWEEN %s AND %s
            """, (item_name, outlet, start_date, end_date))

            received_cost = float(cursor.fetchone()["total_received_cost"] or 0)

            # Get wastage cost
            cursor.execute("""
                SELECT SUM(price) AS total_wastage_cost
                FROM wastage_items
                WHERE item_name = %s AND outlet_name = %s AND received_date BETWEEN %s AND %s
            """, (item_name, outlet, start_date, end_date))
            wastage_cost = float(cursor.fetchone()["total_wastage_cost"] or 0)

            # Get closing quantity (from frontend input)
            closing_count = float(Decimal(item.get("closing_balance", 0)).quantize(Decimal('0.01'), ROUND_HALF_UP))

            # Get previous closing balance to calculate opening cost
            cursor.execute("""
                SELECT isi.rate, isi.closing_balance
                FROM inventory_snapshot_items_food isi
                JOIN inventory_snapshot_master_food ism ON isi.snapshot_id = ism.id
                WHERE ism.outlet_name = %s AND isi.item_name = %s AND ism.end_date < %s
                ORDER BY ism.end_date DESC LIMIT 1
            """, (outlet, item_name, start_date))
            prev = cursor.fetchone()
            opening_cost = 0
            if prev:
                opening_cost = float(prev["closing_balance"] or 0)
            else:
                cursor.execute("""
                    SELECT Rate FROM stock_statement
                    WHERE ItemName = %s AND OutletName = %s
                """, (item_name, outlet))
                opening_rate_result = cursor.fetchone()
                if not opening_rate_result:
                    print(f"{item_name} didnt have stockstatement")
                    # continue
                    opening_cost = 0
                else:
                    opening_rate = float(opening_rate_result["Rate"])
                    opening_cost = opening_rate * float(item.get("opening_count", 0))

            # Total cost = opening + received - wastage - consumption
            total_cost = opening_cost + received_cost - wastage_cost - consumption_cost

            # Step 1: Get physical_count from frontend
            physical_count = float(Decimal(item.get("physical_count", 0)).quantize(Decimal('0.01'), ROUND_HALF_UP))
            remaining_physical_qty = physical_count
            physical_cost = 0.0

            # Step 2: Fetch from item_current_level in **LIFO** order
            cursor.execute("""
                SELECT quantity, rate FROM item_current_level
                WHERE itemname = %s AND outlet = %s AND quantity > 0
                ORDER BY id DESC
            """, (item_name, outlet))
            stock_rows = cursor.fetchall()

            last_rate = 0.0

            # Step 3: LIFO calculation
            for row in stock_rows:
                available_qty = float(row["quantity"])
                rate = float(row["rate"])
                last_rate = rate  # update last seen rate

                if remaining_physical_qty <= 0:
                    break

                used_qty = min(available_qty, remaining_physical_qty)
                physical_cost += used_qty * rate
                remaining_physical_qty -= used_qty

            # Step 4: If there's still remaining quantity, use the last known rate
            if remaining_physical_qty > 0 and last_rate > 0:
                physical_cost += remaining_physical_qty * last_rate



            actual_consumption_cost = opening_cost + received_cost + wastage_cost - physical_cost

            if is_opening == False:

                rate = round(total_cost / physical_count, 4) if physical_count > 0 else 0
                closing_balance = round(physical_count * rate, 2)
            
            else:
                cursor.execute("""
                    SELECT Rate FROM stock_statement
                    WHERE ItemName = %s AND OutletName = %s
                """, (item_name, outlet))
                noopening_rate_result = cursor.fetchone()
                if not opening_rate_result:
                    print(f"{item_name} didnt have stockstatement")
                else:
                    noopening_rate = float(noopening_rate_result["Rate"])
                    closing_cost = noopening_rate * physical_count
                    closing_balance = closing_cost
                    rate = noopening_rate

            # Insert record
            cursor.execute(insert_item_sql, (
                snapshot_id,
                item_name,
                item.get("type"),
                item.get("group_name"),
                item.get("uom"),
                item.get("new_uom"),
                float(Decimal(item.get("total_consumed", 0)).quantize(Decimal('0.01'), ROUND_HALF_UP)),
                float(Decimal(item.get("total_received", 0)).quantize(Decimal('0.01'), ROUND_HALF_UP)),
                closing_balance,
                closing_count,
                float(Decimal(item.get("opening_count", 0)).quantize(Decimal('0.01'), ROUND_HALF_UP)),
                float(Decimal(item.get("total_wastage", 0)).quantize(Decimal('0.01'), ROUND_HALF_UP)),
                float(Decimal(item.get("physical_count", 0)).quantize(Decimal('0.01'), ROUND_HALF_UP)),
                float(Decimal(item.get("discrepancy_count", 0)).quantize(Decimal('0.01'), ROUND_HALF_UP)),
                round(received_cost, 2),
                round(consumption_cost, 2),
                round(wastage_cost, 2),
                rate,
                round(actual_consumption_cost, 2),
                round(opening_cost, 2),
                round(physical_cost, 2)
            ))

            # Opening stock insert (if first snapshot)
            if is_opening:
                cursor.execute("""
                    SELECT Rate FROM stock_statement
                    WHERE ItemName = %s AND OutletName = %s
                """, (item_name, outlet))
                rate_result = cursor.fetchone()
                if not rate_result:
                    continue
                opening_rate = float(rate_result["Rate"])

                # Always insert a new row for opening stock (sequentially)
                cursor.execute("""
                    INSERT INTO item_current_level (itemname, quantity, rate, outlet)
                    VALUES (%s, %s, %s, %s)
                """, (item_name, closing_count, opening_rate, outlet))


        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"status": "success", "snapshot_id": snapshot_id}), 200

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return jsonify({"error": str(e)}), 500


@app_file116.route("/save-inventory-snapshot-beverage", methods=["POST"])
@cross_origin()
def save_inventory_snapshot_beverage():
    try:
        data = request.get_json()
        token = data.get("token")
        if not token or not token_auth(token):
            return jsonify({"error": "Invalid or missing token."}), 400

        items = data.get("items")
        outlet = data.get("outlet")
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        beverage_total_items = data.get("beverage_total_items")
        beverage_accuracy = data.get("beverage_accuracy")

        if not all([items, outlet, start_date, end_date]):
            return jsonify({"error": "Missing required fields."}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        today = datetime.now().date()
        cursor.execute("""
            SELECT id FROM inventory_snapshot_master_beverage
            WHERE outlet_name = %s AND DATE(created_at) = %s
        """, (outlet, today))

        is_opening = False
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": f"Inventory snapshot for beverage has already been saved for {outlet} today."}), 400

        cursor.execute("""
            SELECT COUNT(*) AS count FROM inventory_snapshot_master_beverage
            WHERE outlet_name = %s
        """, (outlet,))
        if cursor.fetchone()["count"] == 0:
            is_opening = True

        # Insert master record
        cursor.execute("""
            INSERT INTO inventory_snapshot_master_beverage (
                outlet_name, start_date, end_date, created_at,
                beverage_total_items,
                beverage_accuracy
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            outlet, start_date, end_date, datetime.now(),
            beverage_total_items, 
            beverage_accuracy
        ))

        snapshot_id = cursor.lastrowid

        insert_item_sql = """
            INSERT INTO inventory_snapshot_items_beverage (
                snapshot_id, item_name, item_type, group_name,
                uom, new_uom, total_consumed, total_received,
                closing_balance, closing_count, opening_count,
                wastage_count, physical_count, discrepancy_count,
                received_cost, consumption_cost, wastage_cost, rate,actual_consumption_cost,opening_cost, physical_cost
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        for item in items:
            item_name = item.get("name")

            # Get consumption cost
            cursor.execute("""
                SELECT SUM(consumed_quantity * rate) AS total_consumption_cost
                FROM consumption_tracker
                WHERE item_name = %s AND outlet = %s AND order_date BETWEEN %s AND %s
            """, (item_name, outlet, start_date, end_date))
            consumption_cost = float(cursor.fetchone()["total_consumption_cost"] or 0)

            # # Get received cost
            # cursor.execute("""
            #     SELECT SUM(quantity * price) AS total_received_cost
            #     FROM received_items
            #     WHERE item_name = %s AND outlet_name = %s AND received_date BETWEEN %s AND %s
            # """, (item_name, outlet, start_date, end_date))

            # Get received cost from store requisition tables
            cursor.execute("""
                SELECT SUM(d.Amount * d.Rate) AS total_received_cost
                FROM intblstorereqdetails d
                JOIN intblstorerequisition r ON d.StoreReqID = r.idintblStoreRequisition
                WHERE d.ItemName = %s 
                    AND r.Outlet = %s 
                    AND DATE(r.Date) BETWEEN %s AND %s
            """, (item_name, outlet, start_date, end_date))

            received_cost = float(cursor.fetchone()["total_received_cost"] or 0)

            # Get wastage cost
            cursor.execute("""
                SELECT SUM(price) AS total_wastage_cost
                FROM wastage_items
                WHERE item_name = %s AND outlet_name = %s AND received_date BETWEEN %s AND %s
            """, (item_name, outlet, start_date, end_date))
            wastage_cost = float(cursor.fetchone()["total_wastage_cost"] or 0)

            # Get closing quantity (from frontend input)
            closing_count = float(Decimal(item.get("closing_balance", 0)).quantize(Decimal('0.01'), ROUND_HALF_UP))

            # Get previous closing balance to calculate opening cost
            cursor.execute("""
                SELECT isi.rate, isi.closing_balance
                FROM inventory_snapshot_items_beverage isi
                JOIN inventory_snapshot_master_beverage ism ON isi.snapshot_id = ism.id
                WHERE ism.outlet_name = %s AND isi.item_name = %s AND ism.end_date < %s
                ORDER BY ism.end_date DESC LIMIT 1
            """, (outlet, item_name, start_date))
            prev = cursor.fetchone()
            opening_cost = 0
            if prev:
                opening_cost = float(prev["closing_balance"] or 0)
            else:
                cursor.execute("""
                    SELECT Rate FROM stock_statement
                    WHERE ItemName = %s AND OutletName = %s
                """, (item_name, outlet))
                opening_rate_result = cursor.fetchone()
                if not opening_rate_result:
                    print(f"{item_name} didnt have stockstatement")
                    # continue
                    opening_cost = 0
                else:
                    opening_rate = float(opening_rate_result["Rate"])
                    opening_cost = opening_rate * float(item.get("opening_count", 0))

            # Total cost = opening + received - wastage - consumption
            total_cost = opening_cost + received_cost - wastage_cost - consumption_cost

            # Step 1: Get physical_count from frontend
            physical_count = float(Decimal(item.get("physical_count", 0)).quantize(Decimal('0.01'), ROUND_HALF_UP))
            remaining_physical_qty = physical_count
            physical_cost = 0.0

            # Step 2: Fetch from item_current_level in **LIFO** order
            cursor.execute("""
                SELECT quantity, rate FROM item_current_level
                WHERE itemname = %s AND outlet = %s AND quantity > 0
                ORDER BY id DESC
            """, (item_name, outlet))
            stock_rows = cursor.fetchall()

            last_rate = 0.0

            # Step 3: LIFO calculation
            for row in stock_rows:
                available_qty = float(row["quantity"])
                rate = float(row["rate"])
                last_rate = rate  # update last seen rate

                if remaining_physical_qty <= 0:
                    break

                used_qty = min(available_qty, remaining_physical_qty)
                physical_cost += used_qty * rate
                remaining_physical_qty -= used_qty

            # Step 4: If there's still remaining quantity, use the last known rate
            if remaining_physical_qty > 0 and last_rate > 0:
                physical_cost += remaining_physical_qty * last_rate



            actual_consumption_cost = opening_cost + received_cost + wastage_cost - physical_cost

            if is_opening == False:

                rate = round(total_cost / physical_count, 4) if physical_count > 0 else 0
                closing_balance = round(physical_count * rate, 2)
            
            else:
                cursor.execute("""
                    SELECT Rate FROM stock_statement
                    WHERE ItemName = %s AND OutletName = %s
                """, (item_name, outlet))
                noopening_rate_result = cursor.fetchone()
                if not opening_rate_result:
                    print(f"{item_name} didnt have stockstatement")
                else:
                    noopening_rate = float(noopening_rate_result["Rate"])
                    closing_cost = noopening_rate * physical_count
                    closing_balance = closing_cost
                    rate = noopening_rate

            # Insert record
            cursor.execute(insert_item_sql, (
                snapshot_id,
                item_name,
                item.get("type"),
                item.get("group_name"),
                item.get("uom"),
                item.get("new_uom"),
                float(Decimal(item.get("total_consumed", 0)).quantize(Decimal('0.01'), ROUND_HALF_UP)),
                float(Decimal(item.get("total_received", 0)).quantize(Decimal('0.01'), ROUND_HALF_UP)),
                closing_balance,
                closing_count,
                float(Decimal(item.get("opening_count", 0)).quantize(Decimal('0.01'), ROUND_HALF_UP)),
                float(Decimal(item.get("total_wastage", 0)).quantize(Decimal('0.01'), ROUND_HALF_UP)),
                float(Decimal(item.get("physical_count", 0)).quantize(Decimal('0.01'), ROUND_HALF_UP)),
                float(Decimal(item.get("discrepancy_count", 0)).quantize(Decimal('0.01'), ROUND_HALF_UP)),
                round(received_cost, 2),
                round(consumption_cost, 2),
                round(wastage_cost, 2),
                rate,
                round(actual_consumption_cost, 2),
                round(opening_cost, 2),
                round(physical_cost, 2)
            ))

            # Opening stock insert (if first snapshot)
            if is_opening:
                cursor.execute("""
                    SELECT Rate FROM stock_statement
                    WHERE ItemName = %s AND OutletName = %s
                """, (item_name, outlet))
                rate_result = cursor.fetchone()
                if not rate_result:
                    continue
                opening_rate = float(rate_result["Rate"])

                # Always insert a new row for opening stock (sequentially)
                cursor.execute("""
                    INSERT INTO item_current_level (itemname, quantity, rate, outlet)
                    VALUES (%s, %s, %s, %s)
                """, (item_name, closing_count, opening_rate, outlet))


        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"status": "success", "snapshot_id": snapshot_id}), 200

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return jsonify({"error": str(e)}), 500