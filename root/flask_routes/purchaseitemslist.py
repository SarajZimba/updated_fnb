from flask import Flask, Blueprint, request, jsonify

import mysql.connector

import os
from root.auth.check import token_auth
from dotenv import load_dotenv

load_dotenv()

from flask_cors import cross_origin

app_file50 = Blueprint("app_file50", __name__)
@app_file50.route("/purchaseitems-list", methods = ["POST"])


@cross_origin()
def get_purchaseitems():

    try:
        mydb = mysql.connector.connect(host=os.getenv("host"), user = os.getenv("user"), password = os.getenv("password"))

        cursor = mydb.cursor(buffered=True)
        database_sql = "USE {};".format(os.getenv('database'))
        cursor.execute(database_sql)
        json = request.get_json()

        if "token" not in json or json["token"] == "":
            return {"error": "token is not provided"}, 400
        token = json["token"]
        if not token_auth(token):
            return {"error": "Invalid token provided"}, 400
        
        sql = """SELECT DISTINCT(Name) from intbl_purchaserequisition_contract"""

        cursor.execute(sql)

        # Fetch all rows
        rows = cursor.fetchall()

        # Extract names into a list
        data = [row[0] for row in rows]

        # Build the response
        responseJson = {"itemslist": data}
        return responseJson, 200
     
    except mysql.connector.Error as db_error:
        return jsonify({"error": f"Database error: {str(db_error)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
    
    finally:
        if mydb:
            mydb.close()
