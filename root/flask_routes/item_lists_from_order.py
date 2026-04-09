from flask import  Blueprint,request, jsonify
import mysql.connector
from flask_cors import  cross_origin
import os
from dotenv import load_dotenv
load_dotenv()
app_file216 = Blueprint('app_file216',__name__)
from root.auth.check import token_auth
import pytz
from datetime import datetime
import re
from collections import defaultdict

def valid_date(datestring):
        try:
                regex = re.compile("^(\d{4})-(0[1-9]|1[0-2]|[1-9])-([1-9]|0[1-9]|[1-2]\d|3[0-1])$")
                match = re.match(regex, datestring)
                if match is not None:
                    return True
        except ValueError:
            return False
        return False

@app_file216.route("/item-lists-from-orders", methods=["POST"])
@cross_origin()
def stats():
    try:
        mydb = mysql.connector.connect(host=os.getenv('host'), user=os.getenv('user'), password=os.getenv('password'))
        cursor = mydb.cursor(buffered=True)
        database_sql = "USE {};".format(os.getenv('database'))
        cursor.execute(database_sql)
        json = request.get_json()
        if "token" not in json  or not any([json["token"]])  or json["token"]=="":
            data = {"error":"No token provided."}
            return data,400
        token = json["token"]
        if "outlet" not in json  or not any([json["outlet"]])  or json["outlet"]=="":
            data = {"error":"No outlet provided."}
            return data,400
        outlet = json["outlet"]
        if not token_auth(token):
            data = {"error":"Invalid token."}
            return data,400

        menu_query = """select Distinct(a.ItemName) from tblorder_detailshistory a, tblorderhistory b where a.order_ID = b.idtblorderHistory and b.Outlet_Name=%s;"""
        cursor.execute(menu_query, (outlet,))
        menus = cursor.fetchall()

        # Prepare the response data in the required format
        response_data = []
        for menu in menus:
            menu_data = {
                "Name": menu[0]
            }
            response_data.append(menu_data)



        return response_data, 200

        

    except mysql.connector.Error as db_error:
        return jsonify({"error": f"Database error: {str(db_error)}"}), 500
    except Exception as error:
        return jsonify({"error": f"Internal server error: {str(error)}"}), 500
    finally:
        # Ensure the cursor and connection are closed
        if cursor:
            cursor.close()
        if mydb:
            mydb.close()


