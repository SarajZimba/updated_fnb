# from flask import Blueprint, jsonify, request
# import mysql.connector
# import os
# from dotenv import load_dotenv
# from flask_cors import cross_origin
# from root.auth.check import token_auth

# load_dotenv()

# app_file111 = Blueprint('app_file111', __name__)

# def get_db_connection():
#     return mysql.connector.connect(
#         host=os.getenv("host"),
#         user=os.getenv("user"),
#         password=os.getenv("password"),
#         database=os.getenv("database")
#     )

# @app_file111.route("/stock-statement", methods=["POST", "GET"])
# @cross_origin()
# def manage_stock_statement():
#     try:
#         if request.method == "POST":
#             data = request.get_json()

#             token = data.get("token")
#             if not token or not token_auth(token):
#                 return jsonify({"error": "Invalid or missing token."}), 400

#             items = data.get("items")
#             if not isinstance(items, list):
#                 return jsonify({"error": "Expected 'items' to be a list."}), 400

#             mydb = get_db_connection()
#             cursor = mydb.cursor()

#             for item in items:
#                 group_name = item.get("GroupName")
#                 item_name = item.get("ItemName")
#                 brand_name = item.get("BrandName")
#                 uom = item.get("UOM")
#                 current_level = item.get("CurrentLevel")
#                 rate = item.get("Rate")
#                 total = item.get("Total")
#                 outlet_name = item.get("OutletName")
#                 item_type = item.get("Type")

#                 if not item_name:
#                     continue  # Skip rows without essential data

#                 cursor.execute("""
#                     INSERT INTO stock_statement 
#                     (GroupName, ItemName, BrandName, UOM, CurrentLevel, Rate, Total, OutletName, Type)
#                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
#                 """, (
#                     group_name, item_name, brand_name, uom, current_level,
#                     rate, total, outlet_name, item_type
#                 ))

#             mydb.commit()
#             cursor.close()
#             mydb.close()

#             return jsonify({"message": "Stock statement data inserted successfully."}), 201

#         elif request.method == "GET":
#             mydb = get_db_connection()
#             cursor = mydb.cursor(dictionary=True)

#             cursor.execute("SELECT * FROM stock_statement")
#             result = cursor.fetchall()

#             cursor.close()
#             mydb.close()
#             return jsonify(result)

#     except Exception as e:
#         return jsonify({"error": str(e)}), 400


from flask import Blueprint, jsonify, request
import mysql.connector
import os
from dotenv import load_dotenv
from flask_cors import cross_origin
from root.auth.check import token_auth

load_dotenv()

app_file111 = Blueprint('app_file111', __name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("host"),
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )

@app_file111.route("/stock-statement", methods=["POST", "GET"])
@cross_origin()
def manage_stock_statement():
    try:
        if request.method == "POST":
            data = request.get_json()

            token = data.get("token")
            if not token or not token_auth(token):
                return jsonify({"error": "Invalid or missing token."}), 400

            items = data.get("items")
            if not isinstance(items, list):
                return jsonify({"error": "Expected 'items' to be a list."}), 400

            mydb = get_db_connection()
            cursor = mydb.cursor()

            for item in items:
                group_name = item.get("GroupName")
                item_name = item.get("ItemName")
                brand_name = item.get("BrandName")
                uom = item.get("UOM")
                current_level = item.get("CurrentLevel")
                rate = item.get("Rate")
                total = item.get("Total")
                outlet_name = item.get("OutletName")
                item_type = item.get("Type")

                if not item_name:
                    continue  # Skip rows without essential data

                item_check = """Select * from stock_statement where ItemName = %s"""

                cursor.execute(item_check, (item_name,) )

                item_check = cursor.fetchone()

                if not item_check:

                    cursor.execute("""
                        INSERT INTO stock_statement 
                        (GroupName, ItemName, BrandName, UOM, CurrentLevel, Rate, Total, OutletName, Type)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        group_name, item_name, brand_name, uom, current_level,
                        rate, total, outlet_name, item_type
                    ))
                else:
                    return jsonify({"message": f"Stock statement data  already exist for this item. {item_name}"}), 400                  

            mydb.commit()
            cursor.close()
            mydb.close()

            return jsonify({"message": "Stock statement data inserted successfully."}), 201

        elif request.method == "GET":
            mydb = get_db_connection()
            cursor = mydb.cursor(dictionary=True)

            cursor.execute("SELECT * FROM stock_statement")
            result = cursor.fetchall()

            cursor.close()
            mydb.close()
            return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 400