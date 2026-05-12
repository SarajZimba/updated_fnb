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

#         # Select the correct database
#         database_sql = "USE {};".format(os.getenv('database'))
#         cursor.execute(database_sql)

#         data = request.get_json()

#         if "outlet_name" not in data or data["outlet_name"] == "":
#             return jsonify({"error": "please provide the outlet_name"}), 400

#         outlet_name = data["outlet_name"]

#         # Updated SQL query with LEFT JOIN to tblunitdefinition
#         sql_query = """
#         SELECT 
#             ss.GroupName,
#             ss.ItemName,
#             ss.BrandName,
#             ss.UOM,
#             ss.CurrentLevel,
#             ss.Rate,
#             ss.Total,
#             tu.uom
#         FROM 
#             stock_statement ss
#         LEFT JOIN 
#             tblunitdefinition tu ON ss.ItemName = tu.name
#         WHERE 
#             ss.OutletName = %s
#         ORDER BY 
#             ss.GroupName;
#         """

#         cursor.execute(sql_query, (outlet_name,))
#         result = cursor.fetchall()

#         if not result:
#             return jsonify({"error": "No stock records found."}), 404

#         # Group results by GroupName
#         grouped_stocks = {}
#         for row in result:
#             group_name = row[0]
#             stock = {
#                 "ItemName": row[1],
#                 "BrandName": row[2],
#                 "UOM": row[3],
#                 "CurrentLevel": row[4],
#                 "Rate": row[5],
#                 "Total": row[6],
#                 "UnitdefinitionUOM": row[7] if row[7] is not None else None
#             }

#             if group_name not in grouped_stocks:
#                 grouped_stocks[group_name] = {
#                     "stocks": [],
#                     "group_total": 0.0
#                 }

#             grouped_stocks[group_name]["stocks"].append(stock)
#             grouped_stocks[group_name]["group_total"] += float(stock["Total"])

#         # Format data for response
#         formatted_data = [
#             {
#                 "group": group_name,
#                 "stocks": group_data["stocks"],
#                 "group_total": round(group_data["group_total"], 2)
#             }
#             for group_name, group_data in grouped_stocks.items()
#         ]

#         return jsonify(formatted_data), 200

#     except mysql.connector.Error as db_error:
#         return jsonify({"error": f"Database error: {str(db_error)}"}), 500
#     except Exception as e:
#         return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
#     finally:
#         if 'mydb' in locals():
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

        # Updated SQL query to fetch from storereqdetails with unitdefinition
        # No filtering by cost center - get all items received in the store
        sql_query = """
        SELECT 
            d.ItemName,
            d.GroupName,
            d.UOM,
            tu.uom AS unitdefinition_uom,
            tu.id AS unitdefinition_id,
            tu.name AS unitdefinition_name,
            tu.unit,
            tu.rate AS unit_rate,
            tu.outlet AS unit_outlet,
            '0' AS CurrentLevel,
            '0' AS Rate,
            '0' AS Total
        FROM 
            intblstorereqdetails d
        JOIN 
            intblstorerequisition r ON d.StoreReqID = r.idintblStoreRequisition
        LEFT JOIN 
            tblunitdefinition tu ON d.ItemName = tu.name
        WHERE 
            r.Outlet = %s
        GROUP BY 
            d.ItemName, d.UOM, tu.uom, tu.id, tu.name, tu.unit, tu.rate, tu.outlet, d.GroupName
        """

        cursor.execute(sql_query, (outlet_name,))
        result = cursor.fetchall()

        if not result:
            return jsonify({"error": "No stock records found."}), 404

        # Group results by GroupName
        grouped_stocks = {}
        for row in result:
            group_name = row[1] if row[1] else "Uncategorized"
            
            stock = {
                "ItemName": row[0],
                "BrandName": None,  # Not available in storereqdetails
                "UOM": row[2],
                "CurrentLevel": float(row[9]) if row[9] else 0.0,
                "Rate": float(row[10]) if row[10] else 0.0,
                "Total": float(row[11]) if row[11] else 0.0,
                "unitdefinition": {
                    "uom": row[3] if row[3] is not None else None,
                    "id": row[4] if row[4] is not None else None,
                    "name": row[5] if row[5] is not None else None,
                    "unit": float(row[6]) if row[6] is not None else None,
                    "unit_rate": float(row[7]) if row[7] is not None else None,
                    "outlet": row[8] if row[8] is not None else None
                } if row[3] is not None else None
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

@app_file46.route("/getstockstatement", methods=["POST"])
@cross_origin()
def get_stock_statement():
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
            return jsonify({"error": "Please provide the outlet_name"}), 400

        outlet_name = data["outlet_name"]

        # Fetch stock statement with all fields including new ones
        sql_query = """
        SELECT 
            `id`,
            `GroupName`,
            `ItemName`,
            `BrandName`,
            `UOM`,
            `CurrentLevel`,
            `Rate`,
            `Total`,
            `OutletName`,
            `Type` AS `Department`,
            `vendor_name` AS `Vendor`,
            `exp_date`,
            `taxable`,
            `primary_unit`,
            `secondary_unit`,
            `StockType`
        FROM 
            `stock_statement`
        WHERE 
            `OutletName` = %s
        ORDER BY 
            `GroupName`, `ItemName`
        """

        cursor.execute(sql_query, (outlet_name,))
        results = cursor.fetchall()

        if not results:
            return jsonify({"error": f"No stock records found for outlet: {outlet_name}"}), 404

        # Prepare all stock items as a flat list
        stock_items = []
        for row in results:
            # Handle date conversion
            exp_date = row[10].strftime('%Y-%m-%d') if row[10] else None
            
            # Prepare stock item
            stock = {
                "GroupName": row[0],
                "ItemName": row[1],
                "BrandName": row[2],
                "UOM": row[3],
                "CurrentLevel": float(row[4]) if row[4] is not None else 0.0,
                "Rate": float(row[5]) if row[5] is not None else 0.0,
                "Total": float(row[6]) if row[6] is not None else 0.0,
                "OutletName": row[7],
                "Department": row[8],
                "Vendor": row[9],
                "exp_date": exp_date,
                "taxable": bool(row[11]) if row[11] is not None else False,
                "primary_unit": row[12],
                "secondary_unit": row[13],
                "stocktype": row[14],
            }
            stock_items.append(stock)

        # Calculate summary totals
        total_value = sum(item["Total"] for item in stock_items)
        taxable_total = sum(item["Total"] for item in stock_items if item["taxable"])
        non_taxable_total = sum(item["Total"] for item in stock_items if not item["taxable"])

        response = {
            "outlet_name": outlet_name,
            "stock_items": stock_items,
            "summary": {
                "total_items": len(stock_items),
                "total_value": round(total_value, 2),
                "total_taxable_value": round(taxable_total, 2),
                "total_non_taxable_value": round(non_taxable_total, 2)
            }
        }

        return jsonify(response), 200

    except mysql.connector.Error as db_error:
        return jsonify({"error": f"Database error: {str(db_error)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
    finally:
        if 'mydb' in locals() and mydb.is_connected():
            mydb.close()