# from flask import Blueprint, jsonify, request
# import mysql.connector
# import os
# from dotenv import load_dotenv
# from flask_cors import cross_origin
# from root.auth.check import token_auth
# from decimal import Decimal

# load_dotenv()

# app_file114 = Blueprint('app_file114', __name__)

# def get_db_connection():
#     return mysql.connector.connect(
#         host=os.getenv("host"),
#         user=os.getenv("user"),
#         password=os.getenv("password"),
#         database=os.getenv("database")
#     )

# @app_file114.route("/received-items", methods=["POST"])
# @cross_origin()
# def receive_items():
#     try:
#         data = request.get_json()
#         token = data.get("token")
#         if not token or not token_auth(token):
#             return jsonify({"error": "Invalid or missing token."}), 400

#         received_items = data.get("items", [])
#         outlet_name = data.get("outlet_name")
#         received_date = data.get("received_date")

#         if not isinstance(received_items, list) or len(received_items) == 0:
#             return jsonify({"error": "No items provided or invalid format."}), 400

#         if not outlet_name or not received_date:
#             return jsonify({"error": "Missing outlet_name or received_date."}), 400

#         mydb = get_db_connection()
#         cursor = mydb.cursor()

#         # Validate all items before processing
#         valid_items = []
#         for item in received_items:
#             if not all(key in item for key in ['item_name', 'quantity', 'price', 'uom']):
#                 continue
            
#             try:
#                 quantity = Decimal(str(item['quantity']))
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

#         # Insert all valid items
#         inserted_ids = []
#         for item in valid_items:
#             cursor.execute(
#                 """
#                 INSERT INTO received_items 
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
#             "message": f"{len(inserted_ids)} items received successfully.",
#             "received_ids": inserted_ids
#         }), 201

#     except Exception as e:
#         if 'mydb' in locals():
#             mydb.rollback()
#             mydb.close()
#         return jsonify({"error": str(e)}), 400

# from flask import Blueprint, jsonify, request
# import mysql.connector
# import os
# from dotenv import load_dotenv
# from flask_cors import cross_origin
# from root.auth.check import token_auth
# from decimal import Decimal

# load_dotenv()

# app_file114 = Blueprint('app_file114', __name__)

# def get_db_connection():
#     return mysql.connector.connect(
#         host=os.getenv("host"),
#         user=os.getenv("user"),
#         password=os.getenv("password"),
#         database=os.getenv("database")
#     )

# @app_file114.route("/received-items", methods=["POST"])
# @cross_origin()
# def receive_items():
#     try:
#         data = request.get_json()
#         token = data.get("token")
#         if not token or not token_auth(token):
#             return jsonify({"error": "Invalid or missing token."}), 400

#         received_items = data.get("items", [])
#         outlet_name = data.get("outlet_name")
#         received_date = data.get("received_date")

#         if not isinstance(received_items, list) or len(received_items) == 0:
#             return jsonify({"error": "No items provided or invalid format."}), 400

#         if not outlet_name or not received_date:
#             return jsonify({"error": "Missing outlet_name or received_date."}), 400

#         mydb = get_db_connection()
#         cursor = mydb.cursor()

#         # Validate all items before processing
#         valid_items = []
#         for item in received_items:
#             if not all(key in item for key in ['item_name', 'quantity', 'price', 'uom']):
#                 continue
            
#             try:
#                 quantity = Decimal(str(item['quantity']))
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
#             # Insert into received_items table
#             cursor.execute(
#                 """
#                 INSERT INTO received_items 
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

#             # Update or insert into item_current_level
#             cursor.execute("""
#                 SELECT id, quantity FROM item_current_level
#                 WHERE itemname = %s AND rate = %s AND outlet = %s
#             """, (item['item_name'], float(item['price']), outlet_name))
#             existing = cursor.fetchone()

#             if existing:
#                 existing_id, current_qty = existing
#                 new_qty = float(current_qty) + float(item['quantity'])

#                 # Update only the quantity
#                 cursor.execute("""
#                     UPDATE item_current_level
#                     SET quantity = %s
#                     WHERE id = %s
#                 """, (new_qty, existing_id))
#             else:
#                 # Insert new entry for different rate
#                 cursor.execute("""
#                     INSERT INTO item_current_level (itemname, quantity, rate, outlet)
#                     VALUES (%s, %s, %s, %s)
#                 """, (
#                     item['item_name'],
#                     float(item['quantity']),
#                     float(item['price']),
#                     outlet_name
#                 ))

#         mydb.commit()
#         cursor.close()
#         mydb.close()

#         return jsonify({
#             "message": f"{len(inserted_ids)} items received and stock updated successfully.",
#             "received_ids": inserted_ids
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

app_file114 = Blueprint('app_file114', __name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("host"),
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )

@app_file114.route("/received-items", methods=["POST"])
@cross_origin()
def receive_items():
    try:
        data = request.get_json()
        token = data.get("token")
        if not token or not token_auth(token):
            return jsonify({"error": "Invalid or missing token."}), 400

        received_items = data.get("items", [])
        outlet_name = data.get("outlet_name")
        received_date = data.get("received_date")

        if not isinstance(received_items, list) or len(received_items) == 0:
            return jsonify({"error": "No items provided or invalid format."}), 400

        if not outlet_name or not received_date:
            return jsonify({"error": "Missing outlet_name or received_date."}), 400

        mydb = get_db_connection()
        cursor = mydb.cursor()

        valid_items = []
        for item in received_items:
            if not all(key in item for key in ['item_name', 'quantity', 'price', 'uom']):
                continue

            try:
                quantity = Decimal(str(item['quantity']))
                price = Decimal(str(item['price']))
                if quantity <= 0 or price < 0:
                    continue

                valid_items.append({
                    'item_name': item['item_name'],
                    'quantity': quantity,
                    'price': price,
                    'uom': item['uom']
                })
            except:
                continue

        if not valid_items:
            mydb.close()
            return jsonify({"error": "No valid items provided."}), 400

        inserted_ids = []
        for item in valid_items:
            # Insert into received_items
            cursor.execute("""
                INSERT INTO received_items 
                (item_name, outlet_name, quantity, price, uom, received_date)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                item['item_name'],
                outlet_name,
                float(item['quantity']),
                float(item['price']),
                item['uom'],
                received_date
            ))
            inserted_ids.append(cursor.lastrowid)

            # Always insert new entry into item_current_level (sequential entry)
            cursor.execute("""
                INSERT INTO item_current_level (itemname, quantity, rate, outlet)
                VALUES (%s, %s, %s, %s)
            """, (
                item['item_name'],
                float(item['quantity']),
                float(item['price']),
                outlet_name
            ))

        mydb.commit()
        cursor.close()
        mydb.close()

        return jsonify({
            "message": f"{len(inserted_ids)} items received and stock entries added sequentially.",
            "received_ids": inserted_ids
        }), 201

    except Exception as e:
        if 'mydb' in locals():
            mydb.rollback()
            mydb.close()
        return jsonify({"error": str(e)}), 400