from flask import Blueprint, jsonify, request
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv
import re

load_dotenv()

def valid_date(datestring):
    regex = re.compile(r"^(\d{4})-(0[1-9]|1[0-2]|[1-9])-([1-9]|0[1-9]|[1-2]\d|3[0-1])$")
    return bool(re.match(regex, datestring))

app_file82 = Blueprint('app_file82', __name__)

@app_file82.route("/post-lastyearsales", methods=["POST"])
@cross_origin()
def post_lastyearsales():
    try:
        # Database connection
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password'),
            database=os.getenv('database')  # Directly use database in connection
        )
        cursor = mydb.cursor()

        # Get JSON data from request
        data = request.get_json()

        # Input validation
        if not data.get("outlet_name"):
            return jsonify({"error": "please provide the outlet_name"}), 400
        if not data.get("last_year_date"):
            return jsonify({"error": "please provide the last_year_date"}), 400
        if not data.get("sales"):
            return jsonify({"error": "please provide the sales"}), 400

        outlet_name = data["outlet_name"]
        last_year_date = data["last_year_date"]
        sales = data["sales"]

        if not valid_date(last_year_date):
            return jsonify({"error": "Invalid date supplied."}), 400
        sql_query = """SELECT count(*) from tblDailySales where outlet_name = %s and date = %s"""

        cursor.execute(sql_query, (outlet_name, last_year_date,))
        result = cursor.fetchone()


        exists = result[0] > 0

        if exists:
            return jsonify({"error": "Data already found for the entered date"}), 400

        # SQL Query to insert data
        sql_query = """INSERT INTO tblDailySales (outlet_name, date, sales) VALUES (%s, %s, %s)"""
        cursor.execute(sql_query, (outlet_name, last_year_date, sales))
        mydb.commit()  # Commit the transaction

        return jsonify({"success": True, "message": "Data inserted successfully"}), 201

    except mysql.connector.Error as db_error:
        return jsonify({"error": f"Database error: {str(db_error)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
    finally:
        if cursor:
            cursor.close()
        if mydb:
            mydb.close()
