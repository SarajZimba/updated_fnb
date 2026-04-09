# from flask import Blueprint, jsonify, request
# import mysql.connector
# import os
# from dotenv import load_dotenv
# from flask_cors import cross_origin
# from root.auth.check import token_auth
# from decimal import Decimal

# load_dotenv()

# app_file117 = Blueprint('app_file117', __name__)

# def get_db_connection():
#     return mysql.connector.connect(
#         host=os.getenv("host"),
#         user=os.getenv("user"),
#         password=os.getenv("password"),
#         database=os.getenv("database")
#     )

# @app_file117.route("/wastage-items", methods=["POST"])
# @cross_origin()
# def post_wastage_items():
#     try:
#         data = request.get_json()
#         token = data.get("token")
#         if not token or not token_auth(token):
#             return jsonify({"error": "Invalid or missing token."}), 400

#         wastage_items = data.get("items", [])
#         outlet_name = data.get("outlet_name")
#         received_date = data.get("received_date")

#         if not isinstance(wastage_items, list) or not wastage_items:
#             return jsonify({"error": "No items provided or invalid format."}), 400
#         if not outlet_name or not received_date:
#             return jsonify({"error": "Missing outlet_name or received_date."}), 400

#         mydb = get_db_connection()
#         cursor = mydb.cursor(dictionary=True)

#         grouped_items = {}

#         for item in wastage_items:
#             item_name = item.get("item_name")
#             uom = item.get("uom")
#             quantity = item.get("quantity")
#             price = item.get("price")

#             if not all([item_name, uom, quantity, price]):
#                 continue

#             try:
#                 quantity = Decimal(str(quantity))
#                 price = Decimal(str(price))
#                 if quantity <= 0 or price < 0:
#                     continue

#                 # Fetch stock_statement UOM
#                 cursor.execute("SELECT uom FROM stock_statement WHERE ItemName = %s LIMIT 1", (item_name,))
#                 stock_row = cursor.fetchone()
#                 stock_uom = stock_row['uom'] if stock_row else None

#                 # Fetch unitdefinition UOM & unit
#                 cursor.execute("SELECT uom, unit FROM tblunitdefinition WHERE name = %s LIMIT 1", (item_name,))
#                 unit_row = cursor.fetchone()
#                 def_uom = unit_row['uom'] if unit_row else None
#                 def_unit = Decimal(unit_row['unit']) if unit_row else Decimal(1)

#                 # Normalize quantity to stock_uom
#                 if uom == stock_uom:
#                     normalized_qty = quantity
#                 elif uom == def_uom:
#                     normalized_qty = (1 / def_unit) * quantity
#                 else:
#                     return jsonify({"error": f"Invalid UOM for item: {item_name}"}), 400

#                 key = (item_name, stock_uom, float(price))  # group by name + uom + rate
#                 if key not in grouped_items:
#                     grouped_items[key] = {
#                         "quantity": Decimal(0),
#                         "price": Decimal(0),
#                         "uom": stock_uom,
#                         "rate": float(price)
#                     }

#                 grouped_items[key]["quantity"] += normalized_qty
#                 grouped_items[key]["price"] += price

#             except Exception:
#                 continue

#         if not grouped_items:
#             mydb.close()
#             return jsonify({"error": "No valid items to insert."}), 400

#         inserted_ids = []
#         for (item_name, uom, rate), val in grouped_items.items():
#             # Insert into wastage_items
#             cursor.execute("""
#                 INSERT INTO wastage_items 
#                 (item_name, outlet_name, quantity, price, uom, received_date)
#                 VALUES (%s, %s, %s, %s, %s, %s)
#             """, (
#                 item_name,
#                 outlet_name,
#                 float(val["quantity"]),
#                 float(val["price"]),
#                 uom,
#                 received_date
#             ))
#             inserted_ids.append(cursor.lastrowid)

#             # === FIFO Deduct from item_current_level based on item_name + outlet ===
#             total_to_deduct = val["quantity"]

#             while total_to_deduct > 0:
#                 cursor.execute("""
#                     SELECT id, quantity, rate FROM item_current_level
#                     WHERE itemname = %s AND outlet = %s AND quantity > 0
#                     ORDER BY id ASC LIMIT 1
#                 """, (item_name, outlet_name))
#                 stock_row = cursor.fetchone()

#                 if stock_row:
#                     stock_id = stock_row["id"]
#                     stock_qty = Decimal(stock_row["quantity"])

#                     if stock_qty >= total_to_deduct:
#                         new_qty = stock_qty - total_to_deduct
#                         cursor.execute("""
#                             UPDATE item_current_level SET quantity = %s WHERE id = %s
#                         """, (float(new_qty), stock_id))
#                         total_to_deduct = Decimal(0)
#                     else:
#                         # Use up the entire stock and loop
#                         cursor.execute("""
#                             UPDATE item_current_level SET quantity = 0 WHERE id = %s
#                         """, (stock_id,))
#                         total_to_deduct -= stock_qty
#                 else:
#                     # No more stock rows available
#                     break

#         mydb.commit()
#         cursor.close()
#         mydb.close()

#         return jsonify({
#             "message": f"{len(inserted_ids)} wastage items recorded and stock adjusted using FIFO.",
#             "inserted_ids": inserted_ids
#         }), 201

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
from decimal import Decimal, InvalidOperation

load_dotenv()

app_file117 = Blueprint('app_file117', __name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("host"),
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )

@app_file117.route("/wastage-items", methods=["POST"])
@cross_origin()
def post_wastage_items():
    try:
        data = request.get_json()
        token = data.get("token")
        if not token or not token_auth(token):
            return jsonify({"error": "Invalid or missing token."}), 400

        wastage_items = data.get("items", [])
        outlet_name = data.get("outlet_name")
        received_date = data.get("received_date")

        if not isinstance(wastage_items, list) or not wastage_items:
            return jsonify({"error": "No items provided or invalid format."}), 400
        if not outlet_name or not received_date:
            return jsonify({"error": "Missing outlet_name or received_date."}), 400

        mydb = get_db_connection()
        cursor = mydb.cursor(dictionary=True)

        inserted_ids = []

        for item in wastage_items:
            item_name = item.get("item_name")
            uom = item.get("uom")
            quantity = item.get("quantity")
            try:
                # We ignore API-sent price now
                if not all([item_name, uom, quantity]):
                    continue

                quantity = Decimal(str(quantity))
                if quantity <= 0:
                    continue

                # Get UOM from stock_statement
                cursor.execute("SELECT uom FROM stock_statement WHERE ItemName = %s LIMIT 1", (item_name,))
                stock_row = cursor.fetchone()
                stock_uom = stock_row['uom'] if stock_row else None

                # Get unit conversion from tblunitdefinition
                cursor.execute("SELECT uom, unit FROM tblunitdefinition WHERE name = %s LIMIT 1", (item_name,))
                unit_row = cursor.fetchone()
                def_uom = unit_row['uom'] if unit_row else None
                def_unit = Decimal(unit_row['unit']) if unit_row else Decimal(1)

                # Normalize quantity
                if uom == stock_uom:
                    normalized_qty = quantity
                elif uom == def_uom:
                    normalized_qty = quantity * (Decimal(1) / def_unit)
                else:
                    return jsonify({"error": f"Invalid UOM for item: {item_name}"}), 400

                total_to_deduct = normalized_qty

                while total_to_deduct > 0:
                    cursor.execute("""
                        SELECT id, quantity, rate FROM item_current_level
                        WHERE itemname = %s AND outlet = %s AND quantity > 0
                        ORDER BY id ASC LIMIT 1
                    """, (item_name, outlet_name))
                    stock_row = cursor.fetchone()

                    if not stock_row:
                        break  # No stock available

                    stock_id = stock_row["id"]
                    stock_qty = Decimal(stock_row["quantity"])
                    stock_rate = Decimal(stock_row["rate"])

                    if stock_qty >= total_to_deduct:
                        deduct_qty = total_to_deduct
                        new_qty = stock_qty - total_to_deduct

                        cursor.execute("""
                            UPDATE item_current_level SET quantity = %s WHERE id = %s
                        """, (float(new_qty), stock_id))

                        total_to_deduct = Decimal(0)
                    else:
                        deduct_qty = stock_qty

                        cursor.execute("""
                            UPDATE item_current_level SET quantity = 0 WHERE id = %s
                        """, (stock_id,))
                        total_to_deduct -= stock_qty

                    # Insert into wastage_items with FIFO rate
                    cursor.execute("""
                        INSERT INTO wastage_items
                        (item_name, outlet_name, quantity, price, uom, received_date)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        item_name,
                        outlet_name,
                        float(deduct_qty),
                        float(stock_rate * deduct_qty),
                        stock_uom,
                        received_date
                    ))

                    inserted_ids.append(cursor.lastrowid)

            except (InvalidOperation, Exception) as e:
                continue  # skip invalid item

        if not inserted_ids:
            mydb.close()
            return jsonify({"error": "No valid items to insert."}), 400

        mydb.commit()
        cursor.close()
        mydb.close()

        return jsonify({
            "message": f"{len(inserted_ids)} wastage items recorded using FIFO and stock adjusted.",
            "inserted_ids": inserted_ids
        }), 201

    except Exception as e:
        if 'mydb' in locals():
            mydb.rollback()
            mydb.close()
        return jsonify({"error": str(e)}), 400