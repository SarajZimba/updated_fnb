# from flask import Blueprint, jsonify, request
# import mysql.connector
# import os
# from dotenv import load_dotenv
# from flask_cors import cross_origin
# from root.auth.check import token_auth

# load_dotenv()

# app_file105 = Blueprint('app_file105', __name__)

# @app_file105.route("/employee-orders", methods=["POST"])
# @cross_origin()
# def get_employee_sales():
#     try:
#         data = request.get_json()

#         # Token validation
#         token = data.get("token")
#         if not token:
#             return jsonify({"error": "No token provided."}), 400
#         if not token_auth(token):
#             return jsonify({"error": "Invalid token."}), 400

#         # Extract and validate required fields
#         dateStart = data.get("startDate")
#         dateEnd = data.get("endDate")
#         outlet = data.get("outlet")
#         employee = data.get("employee")

#         if not all([dateStart, dateEnd, outlet, employee]):
#             return jsonify({"error": "Missing 'startDate', 'endDate', 'outlet' or 'employee'"}), 400

#         # Database connection
#         mydb = mysql.connector.connect(
#             host=os.getenv('host'),
#             user=os.getenv('user'),
#             password=os.getenv('password'),
#             database=os.getenv('database')
#         )
#         cursor = mydb.cursor(dictionary=True)

#         # Query tblorderhistory
#         cursor.execute("""
#             SELECT * FROM tblorderhistory
#             WHERE Date BETWEEN %s AND %s
#               AND Outlet_Name = %s
#               AND Employee = %s
#         """, (dateStart, dateEnd, outlet, employee))

#         orders = cursor.fetchall()

#         # Fetch order details for each order
#         for order in orders:
#             order_id = order["idtblorderHistory"]
#             cursor.execute("""
#                 SELECT * FROM tblorder_detailshistory
#                 WHERE order_ID = %s
#             """, (order_id,))
#             order_details = cursor.fetchall()
#             order["details"] = order_details

#         cursor.close()
#         mydb.close()

#         return jsonify({"orders": orders})

#     except Exception as e:
#         return jsonify({"error": str(e)}), 400


from flask import Blueprint, jsonify, request
import mysql.connector
import os
from dotenv import load_dotenv
from flask_cors import cross_origin
from root.auth.check import token_auth

load_dotenv()

app_file105 = Blueprint('app_file105', __name__)

@app_file105.route("/employee-orders", methods=["POST"])
@cross_origin()
def get_employee_sales():
    try:
        data = request.get_json()

        # Token validation
        token = data.get("token")
        if not token:
            return jsonify({"error": "No token provided."}), 400
        if not token_auth(token):
            return jsonify({"error": "Invalid token."}), 400

        # Required fields
        dateStart = data.get("startDate")
        dateEnd = data.get("endDate")
        outlet = data.get("outlet")
        employee = data.get("employee")

        if not all([dateStart, dateEnd, outlet, employee]):
            return jsonify({"error": "Missing 'startDate', 'endDate', 'outlet' or 'employee'"}), 400

        # DB connection
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password'),
            database=os.getenv('database')
        )
        cursor = mydb.cursor(dictionary=True)

        # Get orders
        cursor.execute("""
            SELECT * FROM tblorderhistory
            WHERE Date BETWEEN %s AND %s
              AND Outlet_Name = %s
              AND Employee = %s
              AND bill_no != ''
        """, (dateStart, dateEnd, outlet, employee))
        orders = cursor.fetchall()

        # Initialize aggregation structure
        aggregated_items = {
            "Food": {},
            "Beverage": {},
            "Other": {}
        }

        # Add item details to each order and collect for aggregation
        for order in orders:
            order_id = order["idtblorderHistory"]
            cursor.execute("""
                SELECT ItemName, ItemType, count, Total, itemRate, Description
                FROM tblorder_detailshistory
                WHERE order_ID = %s
            """, (order_id,))
            items = cursor.fetchall()
            order["details"] = items

            # Aggregate items
            for item in items:
                name = item["ItemName"]
                rate = item["itemRate"]
                group = item["Description"]
                qty = int(item.get("count", 0))
                total = float(item.get("Total", 0.0))
                item_type = item.get("ItemType", "Other")

                if item_type not in ["Food", "Beverage"]:
                    item_type = "Other"

                if name not in aggregated_items[item_type]:
                    aggregated_items[item_type][name] = {
                        "ItemName": name,
                        "TotalQuantity": 0,
                        "TotalAmount": 0.0,
                        "Rate":rate,
                        "Group": group,
                    }

                aggregated_items[item_type][name]["TotalQuantity"] += qty
                aggregated_items[item_type][name]["TotalAmount"] += total

        # Format aggregated result to list
        formatted_aggregated = {
            "Food": list(aggregated_items["Food"].values()),
            "Beverage": list(aggregated_items["Beverage"].values()),
            "Other": list(aggregated_items["Other"].values())
        }

        cursor.close()
        mydb.close()

        return jsonify({
            "orders": orders,
            "aggregated_items": formatted_aggregated
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400