# from flask import Flask, Blueprint, request, jsonify
# import mysql.connector
# from flask_cors import cross_origin

# import os

# from dotenv import load_dotenv

# load_dotenv()
# import json

# app_file76 = Blueprint('appfile_76', __name__)

# from root.utils.getyearlyprediction import get_yearly_prediction
# from datetime import datetime
# import calendar
# @app_file76.route('/getyearlysaleforecast', methods=["POST"])
# @cross_origin()


# def getmonthlyprediction():
#     try:
#         mydb = mysql.connector.connect(
#             user=os.getenv('user'), 
#             password=os.getenv('password'), 
#             host=os.getenv('host'),
#             database=os.getenv('database')
#         )
#         # cursor = mydb.cursor(buffered=True)

#         data = request.get_json()

#         # Validate input data
#         if "outlet_name" not in data or not data["outlet_name"]:
#             return jsonify({"error": "please provide the outlet_name"}), 400
#         if "date" not in data or not data["date"]:
#             return jsonify({"error": "please provide the date"}), 400

#         outlet = data.get("outlet_name")
#         posted_date = data.get("date")

#         # Get predicted monthly sales
#         yearly_results = json.loads(get_yearly_prediction(outlet, posted_date))

#         # # Fetch actual sales for each predicted month
#         # for result in monthly_results:
#         #     prediction_date = result["ds"]  # Format: "YYYY-MM"

#         #     # Extract Year and Month
#         #     year, month = prediction_date.split("-")
#         #     month_name = calendar.month_name[int(month)]  # Convert month number to name

#         #     # Query to sum daily sales for the given month
#         #     query = """
#         #         SELECT COALESCE(SUM(sales), 0) FROM tblDailySales
#         #         WHERE YEAR(date) = %s AND MONTH(date) = %s AND outlet_name = %s
#         #     """
            
#         #     cursor.execute(query, (year, month, outlet))
#         #     actual_sales = cursor.fetchone()[0]  # Get sum of sales for the month

#         #     result["actual_sales"] = round(float(actual_sales), 2)
#         #     result["name"] = month_name  # Add month name
#         #     result["event"] = ""

#         #     result["last_year_sales"] = 0.0

#         return jsonify({"data": yearly_results}), 200

#     except Exception as e:
#         return jsonify({"error": str(e)}), 400

#     finally:
#         mydb.close()


from flask import Flask, Blueprint, request, jsonify
import mysql.connector
from flask_cors import cross_origin

import os

from dotenv import load_dotenv

load_dotenv()
import json

app_file76 = Blueprint('appfile_76', __name__)

from root.utils.getyearlyprediction import get_yearly_prediction
from root.utils.monthlysalesforecast import get_current_month_prediction
from root.utils.salesforecast import get_today_prediction
from datetime import datetime
import calendar
@app_file76.route('/getyearmonthtodaysaleforecast', methods=["POST"])
@cross_origin()


def getyearmonthtodayprediction():
    try:
        mydb = mysql.connector.connect(
            user=os.getenv('user'), 
            password=os.getenv('password'), 
            host=os.getenv('host'),
            database=os.getenv('database')
        )
        # cursor = mydb.cursor(buffered=True)

        data = request.get_json()

        # Validate input data
        if "outlet_name" not in data or not data["outlet_name"]:
            return jsonify({"error": "please provide the outlet_name"}), 400

        outlet = data.get("outlet_name")

        # Get predicted monthly sales
        yearly_results = json.loads(get_yearly_prediction(outlet))

        monthly_results = json.loads(get_current_month_prediction(outlet))
        today_results = json.loads(get_today_prediction(outlet))
        # # Fetch actual sales for each predicted month
        # for result in monthly_results:
        #     prediction_date = result["ds"]  # Format: "YYYY-MM"

        #     # Extract Year and Month
        #     year, month = prediction_date.split("-")
        #     month_name = calendar.month_name[int(month)]  # Convert month number to name

        #     # Query to sum daily sales for the given month
        #     query = """
        #         SELECT COALESCE(SUM(sales), 0) FROM tblDailySales
        #         WHERE YEAR(date) = %s AND MONTH(date) = %s AND outlet_name = %s
        #     """
            
        #     cursor.execute(query, (year, month, outlet))
        #     actual_sales = cursor.fetchone()[0]  # Get sum of sales for the month

        #     result["actual_sales"] = round(float(actual_sales), 2)
        #     result["name"] = month_name  # Add month name
        #     result["event"] = ""

        #     result["last_year_sales"] = 0.0

        return jsonify({"year": yearly_results, "month": monthly_results, "today": today_results}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

    finally:
        mydb.close()
