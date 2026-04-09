from flask import Flask, Blueprint, request, jsonify
import mysql.connector
from flask_cors import cross_origin
from datetime import datetime, timedelta
import os
import pytz
from dotenv import load_dotenv

load_dotenv()

app_file80 = Blueprint('appfile_80', __name__)

from root.utils.getsaleforecastbydaterange_util import getsaleforecastBydaterangeutil
from root.utils.monthlysalesforecast import get_yesterday_monthlyforecast
@app_file80.route('/getsaleforecastbydaterange', methods=["POST"])
@cross_origin()
def getsaleforecastBydaterange():
    try:
        mydb = mysql.connector.connect(user=os.getenv('user'), password=os.getenv('password'), host=os.getenv('host'))

        cursor = mydb.cursor(buffered=True)

        # Use the correct database
        database_sql = "USE {};".format(os.getenv('database'))
        cursor.execute(database_sql)

        data = request.get_json()

        if "outlet_name" not in data or data["outlet_name"] == "":
            return jsonify({"error": "please provide the outlet_name"}), 400
        
        if "dateStart" not in data or data["dateStart"] == "":
            return jsonify({"error": "please provide the dateStart"}), 400
        if "dateEnd" not in data or data["dateEnd"] == "":
            return jsonify({"error": "please provide the dateEnd"}), 400


        outlet = data.get("outlet_name")
        dateStart = data.get("dateStart")
        dateEnd = data.get("dateEnd")

        data, special_date_data = getsaleforecastBydaterangeutil(outlet, dateStart, dateEnd)
        startDateprediction = get_yesterday_monthlyforecast(dateStart, outlet)

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

        for datum in data:
            if datum["ds"] == date_str:
                datum["actual_sales"] = round(float(todays_sales_value), 2)

        json_data =  {"data": data, "events":special_date_data, "startDatePrediciton": startDateprediction}

        return json_data, 200

    except Exception as e:
        data = {"error": str(e)}
        return data, 400

    finally:
        mydb.close()
