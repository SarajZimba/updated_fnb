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

        cost_center = data.get("costcenter")

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

                # total_to_deduct = normalized_qty
                total_to_deduct = quantity

                while total_to_deduct > 0:
                    cursor.execute("""
                        SELECT id, quantity, rate FROM item_current_level
                        WHERE itemname = %s AND outlet = %s AND quantity > 0 AND costcenter = %s
                        ORDER BY id ASC LIMIT 1
                    """, (item_name, outlet_name, cost_center,))
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
                        (item_name, outlet_name, quantity, price, uom, received_date, costcenter)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        item_name,
                        outlet_name,
                        float(deduct_qty),
                        float(stock_rate * deduct_qty),
                        stock_uom,
                        received_date,
                        cost_center
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