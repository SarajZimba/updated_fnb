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

# @app_file117.route("/physical-items", methods=["POST"])
# @cross_origin()
# def post_wastage_items():
#     try:
#         data = request.get_json()
#         token = data.get("token")
#         if not token or not token_auth(token):
#             return jsonify({"error": "Invalid or missing token."}), 400

#         physical_items = data.get("items", [])
#         outlet_name = data.get("outlet_name")
#         received_date = data.get("received_date")

#         if not isinstance(physical_items, list) or len(physical_items) == 0:
#             return jsonify({"error": "No items provided or invalid format."}), 400

#         if not outlet_name or not received_date:
#             return jsonify({"error": "Missing outlet_name or received_date."}), 400

#         mydb = get_db_connection()
#         cursor = mydb.cursor(dictionary=True)

#         # Validate and prepare items
#         valid_items = []
#         for item in physical_items:
#             stock_statement_uom = None
#             unitdefinition_uom = None
#             unitdefinition_unit = Decimal(1)
#             if not all(key in item for key in ['item_name', 'quantity', 'price', 'uom']):
#                 continue
            
#             try:
#                 quantity = Decimal(str(item['quantity']))
#                 cursor.execute("""
#                     SELECT uom FROM stock_statement
#                     WHERE ItemName= %s LIMIT 1
#                 """, (item['item_name'],))
#                 stock_statement_uom_result = cursor.fetchone()

#                 if stock_statement_uom_result:
#                     stock_statement_uom = stock_statement_uom_result["uom"]

#                 cursor.execute("""
#                     SELECT uom, unit FROM tblunitdefinition
#                     WHERE name= %s LIMIT 1
#                 """, (item['item_name'],))
#                 unitdefinition_uom_result = cursor.fetchone()

#                 if unitdefinition_uom_result:
#                     unitdefinition_uom = unitdefinition_uom_result["uom"]
#                     unitdefinition_unit = Decimal(unitdefinition_uom_result["unit"])

#                 if item['uom'] == stock_statement_uom:

#                     quantity = Decimal(str(item['quantity']))

#                 elif item['uom'] == unitdefinition_uom:

#                     quantity = (1/unitdefinition_unit) * Decimal(str(item['quantity']))
#                 else:
#                     return jsonify({"error": "Not a valid uom provided"}), 400


#                 price = Decimal(str(item['price']))
#                 if quantity <= 0 or price < 0:
#                     continue
                
#                 valid_items.append({
#                     'item_name': item['item_name'],
#                     'quantity': quantity,
#                     'price': price,
#                     'uom': item['uom']
#                 })
#             except:
#                 continue

#         if not valid_items:
#             mydb.close()
#             return jsonify({"error": "No valid items provided."}), 400

#         inserted_ids = []
#         for item in valid_items:
#             cursor.execute(
#                 """
#                 INSERT INTO physical_items 
#                 (item_name, outlet_name, quantity, price, uom, received_date)
#                 VALUES (%s, %s, %s, %s, %s, %s)
#                 """,
#                 (
#                     item['item_name'],
#                     outlet_name,
#                     float(item['quantity']),
#                     float(item['price']),
#                     item['uom'],
#                     received_date
#                 )
#             )
#             inserted_ids.append(cursor.lastrowid)

#         mydb.commit()
#         cursor.close()
#         mydb.close()

#         return jsonify({
#             "message": f"{len(inserted_ids)} wastage items recorded successfully.",
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
from decimal import Decimal

load_dotenv()

app_file121 = Blueprint('app_file121', __name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("host"),
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )
@app_file121.route("/physical-items", methods=["POST"])
@cross_origin()
def post_physical_items():
    try:
        data = request.get_json()
        token = data.get("token")
        if not token or not token_auth(token):
            return jsonify({"error": "Invalid or missing token."}), 400

        physical_items = data.get("items", [])
        outlet_name = data.get("outlet_name")
        received_date = data.get("received_date")

        if not isinstance(physical_items, list) or not physical_items:
            return jsonify({"error": "No items provided or invalid format."}), 400
        if not outlet_name or not received_date:
            return jsonify({"error": "Missing outlet_name or received_date."}), 400

        mydb = get_db_connection()
        cursor = mydb.cursor(dictionary=True)

        # Group and accumulate normalized items
        grouped_items = {}

        for item in physical_items:
            item_name = item.get('item_name')
            uom = item.get('uom')
            quantity = item.get('quantity')
            price = item.get('price')

            if not all([item_name, uom, quantity, price]):
                continue

            try:
                quantity = Decimal(str(quantity))
                price = Decimal(str(price))
                # if quantity < 0 or price < 0:
                #     continue

                # Get stock_statement UOM
                cursor.execute("SELECT uom FROM stock_statement WHERE ItemName = %s LIMIT 1", (item_name,))
                stock_uom_row = cursor.fetchone()
                stock_uom = stock_uom_row['uom'] if stock_uom_row else None

                # Get unitdefinition UOM + unit
                cursor.execute("SELECT uom, unit FROM tblunitdefinition WHERE name = %s LIMIT 1", (item_name,))
                unit_row = cursor.fetchone()
                def_uom = unit_row['uom'] if unit_row else None
                def_unit = Decimal(unit_row['unit']) if unit_row else Decimal(1)

                # Normalize quantity to stock_statement UOM
                if uom == stock_uom:
                    normalized_qty = quantity
                elif uom == def_uom:
                    normalized_qty = (1 / def_unit) * quantity
                else:
                    return jsonify({"error": f"Invalid UOM for item: {item_name}"}), 400

                key = (item_name, stock_uom)
                if key not in grouped_items:
                    grouped_items[key] = {"quantity": Decimal(0), "total_price": Decimal(0), "uom": stock_uom}
                grouped_items[key]["quantity"] += normalized_qty
                grouped_items[key]["total_price"] += price

            except Exception as e:
                continue

        if not grouped_items:
            mydb.close()
            return jsonify({"error": "No valid items to insert."}), 400

        inserted_ids = []
        for (item_name, uom), vals in grouped_items.items():
            cursor.execute("""
                INSERT INTO physical_items 
                (item_name, outlet_name, quantity, price, uom, received_date)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                item_name,
                outlet_name,
                float(vals["quantity"]),
                float(vals["total_price"]),
                uom,
                received_date
            ))
            inserted_ids.append(cursor.lastrowid)

        mydb.commit()
        cursor.close()
        mydb.close()

        return jsonify({
            "message": f"{len(inserted_ids)} physical items recorded successfully.",
            "inserted_ids": inserted_ids
        }), 201

    except Exception as e:
        if 'mydb' in locals():
            mydb.rollback()
            mydb.close()
        return jsonify({"error": str(e)}), 400
