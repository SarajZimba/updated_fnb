from flask import Flask, request, jsonify, Blueprint
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
load_dotenv()
import re

app_file78 = Blueprint('app_file78', __name__)




def valid_date(datestring):
    try:
        regex = re.compile("^(\d{4})-(0[1-9]|1[0-2]|[1-9])-([1-9]|0[1-9]|[1-2]\d|3[0-1])$")
        match = re.match(regex, datestring)
        if match:
            return True
    except ValueError:
        return False
    return False

@app_file78.route("/getbillno", methods=["POST"])
def get_sixtydays_dailyreport():
    try:
        mydb = mysql.connector.connect(host=os.getenv('host'), user=os.getenv('user'), password=os.getenv('password'))
        cursor = mydb.cursor(buffered=True)
        cursor.execute(f"USE {os.getenv('database')};")
        data = request.get_json()
        if "outlet_name" not in data or data["outlet_name"] == "":
            return jsonify({"error": "please provide the outlet_name"}), 400
        if "startDate" not in data or data["startDate"] == "":
            return jsonify({"error": "please provide the startDate"}), 400
        if "endDate" not in data or data["endDate"] == "":
            return jsonify({"error": "please provide the endDate"}), 400
        
        outletName = data.get("outlet_name")
        start_Date = data.get("startDate")
        end_Date = data.get("endDate")





        if not valid_date(start_Date) or not valid_date(end_Date):
            return {"error": "Invalid date supplied."}, 400
        
        query = """SELECT CAST(bill_no AS SIGNED) AS bill_no FROM tblorderhistory   
            WHERE `Date` BETWEEN %s AND %s
            AND Outlet_Name = %s
            AND bill_no != ''
            ORDER BY bill_no;"""
        cursor.execute(query, (start_Date, end_Date, outletName,))
        billnos = cursor.fetchall()  # Fetch all the bill_no records

        # Convert the results into a list of bill_no
        billno_list = [billno[0] for billno in billnos]

        mydb.close()

        # Return the billno list as JSON response
        return jsonify(billno_list), 200

    except Exception as e :
        print("Error extracting billno")
        return jsonify({"error": "Error extracting billno"}), 500
    
