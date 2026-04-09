# from flask import  Blueprint,request, jsonify
# import mysql.connector
# from flask_cors import  cross_origin
# import os
# from dotenv import load_dotenv
# load_dotenv()
# app_file30 = Blueprint('app_file30',__name__)
# from root.auth.check import token_auth
# import pytz
# from datetime import datetime
# import re
# from collections import defaultdict

# def valid_date(datestring):
#         try:
#                 regex = re.compile("^(\d{4})-(0[1-9]|1[0-2]|[1-9])-([1-9]|0[1-9]|[1-2]\d|3[0-1])$")
#                 match = re.match(regex, datestring)
#                 if match is not None:
#                     return True
#         except ValueError:
#             return False
#         return False

# @app_file30.route("/item-lists", methods=["POST"])
# @cross_origin()
# def stats():
#     try:
#         mydb = mysql.connector.connect(host=os.getenv('host'), user=os.getenv('user'), password=os.getenv('password'))
#         cursor = mydb.cursor(buffered=True)
#         database_sql = "USE {};".format(os.getenv('database'))
#         cursor.execute(database_sql)
#         json = request.get_json()
#         if "token" not in json  or not any([json["token"]])  or json["token"]=="":
#             data = {"error":"No token provided."}
#             return data,400
#         token = json["token"]
#         if "outlet" not in json  or not any([json["outlet"]])  or json["outlet"]=="":
#             data = {"error":"No outlet provided."}
#             return data,400
#         outlet = json["outlet"]
#         if not token_auth(token):
#             data = {"error":"Invalid token."}
#             return data,400
#         menu_query = """SELECT Name, Description, Type, Price, Restaurant, state, discountExempt, serviceChargeExempt FROM tblmenu where Restaurant=%s"""
#         cursor.execute(menu_query, (outlet,))
#         menus = cursor.fetchall()

#         # Group data by Type and then by Description
#         grouped_data = defaultdict(lambda: defaultdict(list))

#         for menu in menus:
#             menu_data = {
#                 "Name": menu[0],
#                 "Description": menu[1],
#                 "Type": menu[2],
#                 "Price": str(menu[3]),  # Convert price to string for JSON serialization
#                 "Restaurant": menu[4],
#                 "state": menu[5],
#                 "discountExempt": menu[6],
#                 "serviceChargeExempt": menu[7]
#             }
#             type_lower = menu[1].lower()
#             grouped_data[menu[2]][type_lower].append(menu_data)


#         print(grouped_data)
#         # Prepare the response data in the required format
#         response_data = []
#         for menu_type, descriptions in grouped_data.items():
#             type_group = {'Type': menu_type, 'items': []}
#             for desc, items in descriptions.items():
#                 menu_group = {'Description': desc.title(), 'items': items}
#                 type_group['items'].append(menu_group)
#             response_data.append(type_group)

#         return response_data, 200

        

#     except mysql.connector.Error as db_error:
#         return jsonify({"error": f"Database error: {str(db_error)}"}), 500
#     except Exception as error:
#         return jsonify({"error": f"Internal server error: {str(error)}"}), 500
#     finally:
#         # Ensure the cursor and connection are closed
#         if cursor:
#             cursor.close()
#         if mydb:
#             mydb.close()

from flask import Blueprint, request, jsonify
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv
from root.auth.check import token_auth
import re
from collections import defaultdict

load_dotenv()

app_file30 = Blueprint('app_file30', __name__)

def valid_date(datestring):
    try:
        regex = re.compile(r"^(\d{4})-(0[1-9]|1[0-2]|[1-9])-([1-9]|0[1-9]|[1-2]\d|3[0-1])$")
        return re.match(regex, datestring) is not None
    except ValueError:
        return False

@app_file30.route("/item-lists", methods=["POST"])
@cross_origin()
def stats():
    try:
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password')
        )
        cursor = mydb.cursor(buffered=True)
        cursor.execute(f"USE {os.getenv('database')}")

        json_data = request.get_json()

        token = json_data.get("token")
        outlet = json_data.get("outlet")

        if not token:
            return {"error": "No token provided."}, 400
        if not outlet:
            return {"error": "No outlet provided."}, 400
        if not token_auth(token):
            return {"error": "Invalid token."}, 400

        # Fetch all recipes for current outlet
        recipe_query = "SELECT name FROM recipe WHERE outlet = %s"
        cursor.execute(recipe_query, (outlet,))
        recipe_names = set(row[0].strip().lower() for row in cursor.fetchall() if row[0])

        # Fetch all menus for the outlet
        menu_query = """
            SELECT Name, Description, Type, Price, Restaurant, state, discountExempt, serviceChargeExempt
            FROM tblmenu
            WHERE Restaurant = %s
        """
        cursor.execute(menu_query, (outlet,))
        menus = cursor.fetchall()

        grouped_data = defaultdict(lambda: defaultdict(list))

        for menu in menus:
            name = menu[0].strip() if menu[0] else ""
            has_recipe = name.lower() in recipe_names

            menu_data = {
                "Name": name,
                "Description": menu[1],
                "Type": menu[2],
                "Price": str(menu[3]),
                "Restaurant": menu[4],
                "state": menu[5],
                "discountExempt": menu[6],
                "serviceChargeExempt": menu[7],
                "hasRecipe": has_recipe
            }

            desc_key = menu[1].lower() if menu[1] else "undefined"
            grouped_data[menu[2]][desc_key].append(menu_data)

        response_data = []
        for menu_type, descriptions in grouped_data.items():
            type_group = {'Type': menu_type, 'items': []}
            for desc, items in descriptions.items():
                menu_group = {'Description': desc.title(), 'items': items}
                type_group['items'].append(menu_group)
            response_data.append(type_group)

        return jsonify(response_data), 200

    except mysql.connector.Error as db_error:
        return jsonify({"error": f"Database error: {str(db_error)}"}), 500
    except Exception as error:
        return jsonify({"error": f"Internal server error: {str(error)}"}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'mydb' in locals():
            mydb.close()

