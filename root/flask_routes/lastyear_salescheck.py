from flask import Blueprint, jsonify, request
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv
load_dotenv()
import re

def valid_date(datestring):
    try:
        regex = re.compile("^(\d{4})-(0[1-9]|1[0-2]|[1-9])-([1-9]|0[1-9]|[1-2]\d|3[0-1])$")
        match = re.match(regex, datestring)
        if match:
            return True
    except ValueError:
        return False
    return False

app_file81 = Blueprint('app_file81', __name__)

@app_file81.route("/check-lastyearsales", methods=["POST"])
@cross_origin()
def get_stocks_by_group():
    try:
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password')
        )
        cursor = mydb.cursor(buffered=True)
        database_sql = "USE {};".format(os.getenv('database'))
        cursor.execute(database_sql)

        # outlet_name = request.args.get("outlet_name", "")

        data = request.get_json()

        if "outlet_name" not in data or data["outlet_name"] == "":
            return jsonify({"error": "please provide the outlet_name"}), 400
        if "last_year_date" not in data or data["last_year_date"] == "":
            return jsonify({"error": "please provide the last_year_date"}), 400

        outlet_name = data["outlet_name"]
        last_year_date = data["last_year_date"]
        if not valid_date(last_year_date):
            return {"error": "Invalid date supplied."}, 400
        # SQL Query to get stocks grouped by GroupName
        sql_query = """SELECT count(*) from tblDailySales where outlet_name = %s and date = %s"""

        cursor.execute(sql_query, (outlet_name, last_year_date,))
        result = cursor.fetchone()


        exists = result[0] > 0

        return jsonify({"exists": exists}), 200

    except mysql.connector.Error as db_error:
        return jsonify({"error": f"Database error: {str(db_error)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
    finally:
        if mydb:
            mydb.close()
