from flask import Flask, Blueprint, request, jsonify

import mysql.connector

from flask_cors import cross_origin

app_file53 = Blueprint('app_file53', __name__)
import os

from dotenv import load_dotenv

load_dotenv()

from root.auth.check import token_auth

@app_file53.route('/toppurchasingvendorsfromcount', methods = ["POST"])
@cross_origin()
def get_topvendors():
    try:
        mydb = mysql.connector.connect(host=os.getenv('host'), password=os.getenv('password'), user = os.getenv('user'))

        cursor = mydb.cursor(buffered=True)
        database_sql = "USE {};".format(os.getenv('database'))

        cursor.execute(database_sql)
        json = request.get_json()

        if "token" not in json or json["token"] == "":
            return jsonify({"error": "Please provide token"}), 400
        

        token = json["token"]
        if not token_auth(token):
            return jsonify({"error": "Invalid token provided"}), 400
        
        sql_query = """select Company_Name, count(idintbl_purchaserequisition) as purchaseCount from intbl_purchaserequisition group by Company_Name order by count(idintbl_purchaserequisition) DESC""" 

        cursor.execute(sql_query)

        columns = [col[0] for col in cursor.description]

        responseJson = [dict(zip(columns, rows)) for rows in cursor.fetchall()]


        return responseJson, 200
    except mysql.connector.Error as db_error:
        mydb.rollback()  # Rollback on error
        return jsonify({"error": f"Database error: {str(db_error)}"}), 500
    except Exception as e:
        mydb.rollback()  # Rollback on unexpected error
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
    finally:
        if mydb:
            mydb.close()



