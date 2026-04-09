# from flask import Flask, Blueprint, request, jsonify
# import mysql.connector
# from flask_cors import cross_origin

# import os

# from dotenv import load_dotenv

# load_dotenv()
# import json

# app_file73 = Blueprint('appfile_73', __name__)

# from root.utils.salesforecast import get_prediction


# @app_file73.route('/getsaleforecast', methods=["POST"])
# @cross_origin()
# def getAllStockTransfers():
#     try:
#         mydb = mysql.connector.connect(user=os.getenv('user'), password=os.getenv('password'), host=os.getenv('host'))

#         cursor = mydb.cursor(buffered=True)

#         # Use the correct database
#         database_sql = "USE {};".format(os.getenv('database'))
#         cursor.execute(database_sql)

#         data = request.get_json()

#         if "outlet_name" not in data or data["outlet_name"] == "":
#             return jsonify({"error": "please provide the outlet_name"}), 400
        
#         # if "type" not in data or data["type"] == "":
#         #     return jsonify({"error": "please provide the type"}), 400
#         if "date" not in data or data["date"] == "":
#             return jsonify({"error": "please provide the date"}), 400


#         # type = data.get("type")
#         outlet = data.get("outlet_name")
#         posted_date = data.get("date")
#         results = get_prediction(type, outlet, posted_date)

#         data = json.loads(results)

#         for result in data:
#             prediction_date = result["ds"]
#             query = """select sales from tblDailySales where date = %s and outlet_name = %s """

#             cursor.execute(query, (prediction_date, outlet,) )

#             results = cursor.fetchall()

#             sales = round(float(results[0][0]), 2) if results else 0.0

#             result["actual_sales"] = sales


#         json_data =  data

#         return json_data, 200

#     except Exception as e:
#         data = {"error": str(e)}
#         return data, 400

#     finally:
#         mydb.close()


from flask import Flask, Blueprint, request, jsonify
import mysql.connector
from flask_cors import cross_origin

import os

from dotenv import load_dotenv

load_dotenv()
import json

app_file73 = Blueprint('appfile_73', __name__)

from root.utils.salesforecast import get_prediction
from datetime import datetime

@app_file73.route('/getsaleforecast', methods=["POST"])
@cross_origin()
def getAllStockTransfers():
    try:
        mydb = mysql.connector.connect(user=os.getenv('user'), password=os.getenv('password'), host=os.getenv('host'))

        cursor = mydb.cursor(buffered=True)

        # Use the correct database
        database_sql = "USE {};".format(os.getenv('database'))
        cursor.execute(database_sql)

        data = request.get_json()

        if "outlet_name" not in data or data["outlet_name"] == "":
            return jsonify({"error": "please provide the outlet_name"}), 400
        
        # if "type" not in data or data["type"] == "":
        #     return jsonify({"error": "please provide the type"}), 400
        
        if "date" not in data or data["date"] == "":
            return jsonify({"error": "please provide the date"}), 400



        # type = data.get("type")
        outlet = data.get("outlet_name")
        posted_date = data.get("date")
        results = get_prediction(outlet, posted_date)

        # Convert JSON results into Python objects
        data = json.loads(results)

        # Fetch actual sales for predicted dates
        for result in data:
            prediction_date = result["ds"]
            query = """SELECT sales FROM tblDailySales WHERE date = %s AND outlet_name = %s"""
            
            cursor.execute(query, (prediction_date, outlet))
            results = cursor.fetchall()
            
            sales = round(float(results[0][0]), 2) if results else 0.0
            result["actual_sales"] = sales
            # Get day name from date
            day_name = datetime.strptime(prediction_date, "%Y-%m-%d").strftime("%A") 
            result["name"] = day_name
        # print("data", data)

        today_date_str = datetime.today().strftime('%Y-%m-%d')
        # Fetch special dates from database
        # special_dates_query = """SELECT * FROM tblevents where `thisyeardate` > %s order by `thisyeardate` limit 10"""
        special_dates_query = """SELECT * FROM tblevents where outlet = %s order by `thisyeardate`"""
        cursor.execute(special_dates_query, (outlet,))

        # Process special dates into a dictionary list
        results = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        special_date_data = [dict(zip(column_names, row)) for row in results]

        # print(f"special_date_data {special_date_data}")


        # Convert special_date_data to a dictionary for quick lookups
        special_dates_dict = {
            special_date["thisyeardate"].strftime('%Y-%m-%d'): {
                "event": special_date["event"],
                "lastyeardate": special_date["lastyeardate"].strftime('%Y-%m-%d')
            }
            for special_date in special_date_data
        }

        # Fetch sales for last year's special dates in one query
        last_year_dates = list(set([entry["lastyeardate"] for entry in special_dates_dict.values()]))

        if last_year_dates:
            # Handle single-element tuples properly
            if len(last_year_dates) == 1:
                last_year_query = """SELECT date, sales FROM tblDailySales WHERE date = %s AND outlet_name = %s"""
                cursor.execute(last_year_query, (last_year_dates[0], outlet))
            else:
                # last_year_query = """SELECT date, sales FROM tblDailySales WHERE date IN %s AND outlet_name = %s"""
                # cursor.execute(last_year_query, (tuple(last_year_dates), outlet))
                # Generate the placeholders for the IN clause
                placeholders = ','.join(['%s'] * len(last_year_dates))

                # Construct the query with dynamic placeholders
                last_year_query = f"""SELECT date, sales FROM tblDailySales WHERE date IN ({placeholders}) AND outlet_name = %s"""

                # Execute the query with the list of dates and the outlet name
                cursor.execute(last_year_query, (*last_year_dates, outlet))      
            
            last_year_results = cursor.fetchall()

            # Convert last_year_results to a dictionary for fast lookup
            last_year_sales_dict = {row[0].strftime('%Y-%m-%d'): round(float(row[1]), 2) for row in last_year_results}
        else:
            last_year_sales_dict = {}

        # Iterate over data and update with last year's sales and event information
        for datum in data:
            datum_date = datum["ds"]
            datum["last_year_sales"] = 0.0  # Default value if no match
            datum["event"] = ""  # Default value if no match

            if datum_date in special_dates_dict:
                special_date_info = special_dates_dict[datum_date]
                last_year_sales = last_year_sales_dict.get(special_date_info["lastyeardate"], 0.0)
                datum["last_year_sales"] = last_year_sales
                datum["event"] = special_date_info["event"]
                forecasted_sales = datum["yhat"]

                if datum["event"] != "":
                    # datum["yhat"] = (forecasted_sales  + datum["last_year_sales"])/2
                    datum["yhat"] = forecasted_sales * 0.25  + datum["last_year_sales"] *0.75

        print("Updated Data with Last Year's Sales and Events:", data)



        json_data =  {"data": data, "events":special_date_data}

        return json_data, 200

    except Exception as e:
        data = {"error": str(e)}
        return data, 400

    finally:
        mydb.close()
