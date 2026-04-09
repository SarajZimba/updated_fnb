# from flask import Blueprint, jsonify, request
# import mysql.connector
# from flask_cors import cross_origin
# import os
# from dotenv import load_dotenv
# load_dotenv()

# app_file46 = Blueprint('app_file46', __name__)

# @app_file46.route("/getstocksbygroup", methods=["POST"])
# @cross_origin()
# def get_stocks_by_group():
#     try:
#         mydb = mysql.connector.connect(
#             host=os.getenv('host'),
#             user=os.getenv('user'),
#             password=os.getenv('password')
#         )
#         cursor = mydb.cursor(buffered=True)
#         database_sql = "USE {};".format(os.getenv('database'))
#         cursor.execute(database_sql)

#         data = request.get_json()

#         if "outlet_name" not in data or data["outlet_name"] == "":
#             return jsonify({"error": "please provide the outlet_name"}), 400
#         outlet_name = data["outlet_name"]

#         # # SQL Query to get stocks grouped by GroupName
#         # sql_query = """
#         # SELECT `GroupName`, `ItemName`, `BrandName`, `UOM`, `CurrentLevel`, `Rate`, `Total`
#         # FROM stock_statement
#         # ORDER BY `GroupName`
#         # """
        
#         # SQL Query to get stocks grouped by GroupName
#         sql_query = """
#         SELECT `GroupName`, `ItemName`, `BrandName`, `UOM`, `CurrentLevel`, `Rate`, `Total`
#         FROM stock_statement WHERE `OutletName`=%s
#         ORDER BY `GroupName`
#         """

#         cursor.execute(sql_query, (outlet_name,))

#         # cursor.execute(sql_query)
#         result = cursor.fetchall()

#         if not result:
#             return jsonify({"error": "No stock records found."}), 404

#         # Group the results by GroupName
#         grouped_stocks = {}
#         for row in result:
#             group_name = row[0]
#             stock = {
#                 "ItemName": row[1],
#                 "BrandName": row[2],
#                 "UOM": row[3],
#                 "CurrentLevel": row[4],
#                 "Rate": row[5],
#                 "Total": row[6]
#             }

#             if group_name not in grouped_stocks:
#                 grouped_stocks[group_name] = {
#                     "stocks": [],
#                     "group_total": 0.0
#                 }

#             # Add stock to the group
#             grouped_stocks[group_name]["stocks"].append(stock)

#             # Increment the group total
#             grouped_stocks[group_name]["group_total"] += stock["Total"]

#         # Transform the grouped data into the desired format
#         formatted_data = [
#             {
#                 "group": group_name,
#                 "stocks": group_data["stocks"],
#                 "group_total": group_data["group_total"]
#             }
#             for group_name, group_data in grouped_stocks.items()
#         ]

#         return jsonify(formatted_data), 200

#     except mysql.connector.Error as db_error:
#         return jsonify({"error": f"Database error: {str(db_error)}"}), 500
#     except Exception as e:
#         return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
#     finally:
#         if mydb:
#             mydb.close()

from flask import Blueprint, jsonify, request
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv

load_dotenv()

app_file46 = Blueprint('app_file46', __name__)

@app_file46.route("/getstocksbygroup", methods=["POST"])
@cross_origin()
def get_stocks_by_group():
    try:
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password')
        )
        cursor = mydb.cursor(buffered=True)

        # Select the correct database
        database_sql = "USE {};".format(os.getenv('database'))
        cursor.execute(database_sql)

        data = request.get_json()

        if "outlet_name" not in data or data["outlet_name"] == "":
            return jsonify({"error": "please provide the outlet_name"}), 400

        outlet_name = data["outlet_name"]

        # Updated SQL query with LEFT JOIN to tblunitdefinition
        sql_query = """
        SELECT 
            ss.GroupName,
            ss.ItemName,
            ss.BrandName,
            ss.UOM,
            ss.CurrentLevel,
            ss.Rate,
            ss.Total,
            tu.uom
        FROM 
            stock_statement ss
        LEFT JOIN 
            tblunitdefinition tu ON ss.ItemName = tu.name
        WHERE 
            ss.OutletName = %s
        ORDER BY 
            ss.GroupName;
        """

        cursor.execute(sql_query, (outlet_name,))
        result = cursor.fetchall()

        if not result:
            return jsonify({"error": "No stock records found."}), 404

        # Group results by GroupName
        grouped_stocks = {}
        for row in result:
            group_name = row[0]
            stock = {
                "ItemName": row[1],
                "BrandName": row[2],
                "UOM": row[3],
                "CurrentLevel": row[4],
                "Rate": row[5],
                "Total": row[6],
                "UnitdefinitionUOM": row[7] if row[7] is not None else None
            }

            if group_name not in grouped_stocks:
                grouped_stocks[group_name] = {
                    "stocks": [],
                    "group_total": 0.0
                }

            grouped_stocks[group_name]["stocks"].append(stock)
            grouped_stocks[group_name]["group_total"] += float(stock["Total"])

        # Format data for response
        formatted_data = [
            {
                "group": group_name,
                "stocks": group_data["stocks"],
                "group_total": round(group_data["group_total"], 2)
            }
            for group_name, group_data in grouped_stocks.items()
        ]

        return jsonify(formatted_data), 200

    except mysql.connector.Error as db_error:
        return jsonify({"error": f"Database error: {str(db_error)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
    finally:
        if 'mydb' in locals():
            mydb.close()
