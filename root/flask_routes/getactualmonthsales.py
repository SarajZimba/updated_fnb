from flask import Flask, request, jsonify, Blueprint
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv
from datetime import datetime 
load_dotenv()
from root.utils.actualmonthsales import get_actualmonthsales

app_file77 = Blueprint('app_file77', __name__)

@app_file77.route("/getactualmonthsales", methods=["POST"])
@cross_origin()
def get_actual_monthsales():
    try:
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password'),
        )
        cursor = mydb.cursor(buffered=True)
        database_sql = "USE {};".format(os.getenv('database'))
        cursor.execute(database_sql)

        data = request.get_json()

        if "outlet_name" not in data or data["outlet_name"] == "":
            return jsonify({"error": "please provide the outlet_name"}), 400
        outlet_name = data["outlet_name"]
        if "date" not in data or data["date"] == "":
            return jsonify({"error": "please provide the date"}), 400
        date = data["date"]

        actualmonthsales_data = get_actualmonthsales(outlet_name, date)


        return jsonify(actualmonthsales_data), 200

    except mysql.connector.Error as db_error:
        return jsonify({"error": f"Database error: {str(db_error)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
    finally:
        if mydb:
            mydb.close()
