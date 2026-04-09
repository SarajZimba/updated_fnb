from flask import Flask, Blueprint, request, jsonify
import mysql.connector
from flask_cors import cross_origin

import os

from dotenv import load_dotenv

load_dotenv()
import json

app_file74 = Blueprint('appfile_74', __name__)

from root.utils.monthlysalesforecast import get_monthly_prediction
from datetime import datetime, timedelta
import pytz
import calendar
@app_file74.route('/getmonthlysaleforecast', methods=["POST"])
@cross_origin()



def getmonthlyprediction():
    try:
        mydb = mysql.connector.connect(
            user=os.getenv('user'), 
            password=os.getenv('password'), 
            host=os.getenv('host'),
            database=os.getenv('database')
        )
        cursor = mydb.cursor(buffered=True)

        data = request.get_json()

        # Validate input data
        if "outlet_name" not in data or not data["outlet_name"]:
            return jsonify({"error": "please provide the outlet_name"}), 400
        if "type" not in data or not data["type"]:
            return jsonify({"error": "please provide the type"}), 400
        if "date" not in data or not data["date"]:
            return jsonify({"error": "please provide the date"}), 400

        outlet = data.get("outlet_name")
        posted_date = data.get("date")

        # Get predicted monthly sales
        monthly_results = json.loads(get_monthly_prediction(outlet, posted_date))

        # Fetch actual sales for each predicted month
        for result in monthly_results:
            prediction_date = result["ds"]  # Format: "YYYY-MM"

            # Extract Year and Month
            year, month = prediction_date.split("-")
            month_name = calendar.month_abbr[int(month)]  # Convert month number to name

            # Query to sum daily sales for the given month
            query = """
                SELECT COALESCE(SUM(sales), 0) FROM tblDailySales
                WHERE YEAR(date) = %s AND MONTH(date) = %s AND outlet_name = %s
            """
            
            cursor.execute(query, (year, month, outlet))
            actual_sales = cursor.fetchone()[0]  # Get sum of sales for the month

            # result["actual_sales"] = round(float(actual_sales), 2)

            nepal_tz = pytz.timezone('Asia/Kathmandu')
            nepal_time = datetime.now(nepal_tz)
            date_str = nepal_time.strftime('%Y-%m-%d')

            tomorrow_nepal_time = nepal_time + timedelta(days=1)  # Subtract 1 day
            tomorrow_date_str = tomorrow_nepal_time.strftime('%Y-%m-%d')

            # Define time range (yesterday 2:01 AM to today 2:00 AM)
            start_datetime = f"{date_str} 02:01 AM"
            end_datetime = f"{tomorrow_date_str} 02:00 AM"
            #  Fetch all outlet names
            todaysale_sql = """
                SELECT COALESCE(SUM(Total), 0) 
                FROM tblorderhistory 
                WHERE bill_no != '' 
                AND STR_TO_DATE(CONCAT(Date, ' ', Start_Time), '%Y-%m-%d %h:%i %p') 
                BETWEEN STR_TO_DATE(%s, '%Y-%m-%d %h:%i %p') 
                AND STR_TO_DATE(%s, '%Y-%m-%d %h:%i %p') 
                AND Outlet_Name = %s;
            """
            # cursor.execute(stats_sql, (date_str,))
            cursor.execute(todaysale_sql, (start_datetime, end_datetime, outlet,))
            todays_sales_data = cursor.fetchall()

            todays_sales_value = todays_sales_data[0][0] if todays_sales_data else 0

            result["actual_sales"] = round(float(actual_sales), 2) + round(float(todays_sales_value), 2)


            result["name"] = month_name + ", " + str(year) # Add month name
            result["event"] = ""
            

            result["last_year_sales"] = 0.0

        return jsonify({"data": monthly_results,"events": []}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

    finally:
        mydb.close()
