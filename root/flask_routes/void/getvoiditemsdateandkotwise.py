# from flask import Flask, request, jsonify
# import mysql.connector
# from flask import Blueprint
# from flask_cors import cross_origin
# import os
# from dotenv import load_dotenv

# load_dotenv()
# app_file85 = Blueprint('app_file85', __name__)

# def get_items_orders(start_date, end_date, outlet_name, item_name, type):
#     mydb = mysql.connector.connect(
#         host=os.getenv('host'), 
#         user=os.getenv('user'), 
#         password=os.getenv('password')
#     )
#     cursor = mydb.cursor(dictionary=True)
#     cursor.execute(f"USE {os.getenv('database')}")

#     if type == "Void":
#         query = """
#             SELECT 
#                 t.idtblorderTracker AS order_id,
#                 t.Date,
#                 t.Employee,
#                 t.KOTID,
#                 t.orderType,
#                 t.orderedAt,
#                 t.outlet_orderID,
#                 t.tableNum,
#                 t.TotalTime AS orderTotalTime,
#                 d.AvgPrepTime,
#                 d.ItemName,
#                 d.Quantity,
#                 d.TotalTime,
#                 d.completedAt,
#                 d.item_price,
#                 d.orderedAt AS itemOrderedAt,
#                 d.prepTimeDifference,
#                 d.voidAt,
#                 d.voidTotalTime
#             FROM tblorderTracker t
#             JOIN tblorderTracker_Details d ON t.idtblorderTracker = d.orderTrackerID
#             WHERE d.completedAt = 'VOID' AND d.TotalTime = 'VOID'
#             AND t.Date BETWEEN %s AND %s
#             AND t.outlet_Name = %s
#             AND d.ItemName = %s            
#             ORDER BY t.Date, t.idtblorderTracker, d.idtblorderTracker_Details;
#         """
#     if type == "Normal":
#         query = """
#             SELECT 
#                 t.idtblorderTracker AS order_id,
#                 t.Date,
#                 t.Employee,
#                 t.KOTID,
#                 t.orderType,
#                 t.orderedAt,
#                 t.outlet_orderID,
#                 t.tableNum,
#                 t.TotalTime AS orderTotalTime,
#                 d.AvgPrepTime,
#                 d.ItemName,
#                 d.Quantity,
#                 d.TotalTime,
#                 d.completedAt,
#                 d.item_price,
#                 d.orderedAt AS itemOrderedAt,
#                 d.prepTimeDifference,
#                 d.voidAt,
#                 d.voidTotalTime
#             FROM tblorderTracker t
#             JOIN tblorderTracker_Details d ON t.idtblorderTracker = d.orderTrackerID
#             WHERE t.Date BETWEEN %s AND %s
#             AND t.outlet_Name = %s
#             AND d.ItemName = %s
#             ORDER BY t.Date, t.idtblorderTracker, d.idtblorderTracker_Details;
#         """

    
#     cursor.execute(query, (start_date, end_date, outlet_name, item_name))
#     rows = cursor.fetchall()
#     mydb.close()

#     grouped_orders = {}

#     for row in rows:
#         date = row["Date"]
#         order_id = row["order_id"]

#         # Initialize date group
#         if date not in grouped_orders:
#             grouped_orders[date] = {}

#         # Initialize order tracker group within the date
#         if order_id not in grouped_orders[date]:
#             grouped_orders[date][order_id] = {
#                 "Employee": row["Employee"],
#                 "KOTID": row["KOTID"],
#                 "OrderType": row["orderType"],
#                 "OrderedAt": row["orderedAt"],
#                 "Outlet_orderID": row["outlet_orderID"],
#                 "TableNum": row["tableNum"],
#                 "TotalTime": row["orderTotalTime"],
#                 "items": []
#             }
        
#         # Append item details
#         grouped_orders[date][order_id]["items"].append({
#             "AvgPrepTime": row["AvgPrepTime"],
#             "ItemName": row["ItemName"],
#             "Quantity": str(row["Quantity"]),
#             "TotalTime": row["TotalTime"],
#             "completedAt": row["completedAt"],
#             "item_price": row["item_price"],
#             "orderedAt": row["itemOrderedAt"],
#             "prepTimeDifference": row["prepTimeDifference"],
#             "voidAt": row["voidAt"],
#             "voidTotalTime": row["voidTotalTime"]
#         })

#     # Convert to list format
#     final_output = []
#     for date, orders in grouped_orders.items():
#         final_output.append({
#             "Date": date,
#             "orders": list(orders.values())  # Convert orders dict to list
#         })

#     return final_output

# @app_file85.route("/items-orders-datewise", methods=["POST"])
# def void_orders():
#     data = request.get_json()
#     start_date = data.get("startDate")
#     end_date = data.get("endDate")
#     outlet_name = data.get("outletName")
#     item_name = data.get("itemName")
#     type = data.get("type")
#     if not start_date or not end_date or not outlet_name or not item_name or not type:
#         return jsonify({"error": "Missing parameters"}), 400

#     orders = get_items_orders(start_date, end_date, outlet_name, item_name, type)
#     return jsonify({"orders": orders})

from flask import Flask, request, jsonify
import mysql.connector
from flask import Blueprint
from flask_cors import cross_origin
import os
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()
app_file85 = Blueprint('app_file85', __name__)

def get_items_orders(start_date, end_date, outlet_name, item_name):
    mydb = mysql.connector.connect(
        host=os.getenv('host'), 
        user=os.getenv('user'), 
        password=os.getenv('password')
    )
    cursor = mydb.cursor(dictionary=True)
    cursor.execute(f"USE {os.getenv('database')}")


    void_item_query = """
            SELECT 
                t.idtblorderTracker AS order_id,
                t.Date,
                t.Employee,
                t.KOTID,
                t.orderType,
                t.orderedAt,
                t.outlet_orderID,
                t.tableNum,
                t.TotalTime AS orderTotalTime,
                d.AvgPrepTime,
                d.ItemName,
                d.Quantity,
                d.TotalTime,
                d.completedAt,
                d.item_price,
                d.orderedAt AS itemOrderedAt,
                d.prepTimeDifference,
                d.voidAt,
                d.voidTotalTime
            FROM tblorderTracker t
            JOIN tblorderTracker_Details d ON t.idtblorderTracker = d.orderTrackerID
            WHERE d.completedAt = 'VOID' AND d.TotalTime = 'VOID'
            AND t.Date BETWEEN %s AND %s
            AND t.outlet_Name = %s
            AND d.ItemName = %s            
            ORDER BY t.Date, t.idtblorderTracker, d.idtblorderTracker_Details;
        """
    
    cursor.execute(void_item_query, (start_date, end_date, outlet_name, item_name))
    voiditems_item_rows = cursor.fetchall()
    # mydb.close()

    voiditems_grouped_orders = {}

    for row in voiditems_item_rows:
        date = row["Date"]
        order_id = row["order_id"]

        # Initialize date group
        if date not in voiditems_grouped_orders:
            voiditems_grouped_orders[date] = {}

        # Initialize order tracker group within the date
        if order_id not in voiditems_grouped_orders[date]:
            voiditems_grouped_orders[date][order_id] = {
                "Employee": row["Employee"],
                "KOTID": row["KOTID"],
                "OrderType": row["orderType"],
                "OrderedAt": row["orderedAt"],
                "Outlet_orderID": row["outlet_orderID"],
                "TableNum": row["tableNum"],
                "TotalTime": row["orderTotalTime"],
                "items": []
            }
        
        # Append item details
        voiditems_grouped_orders[date][order_id]["items"].append({
            "AvgPrepTime": row["AvgPrepTime"],
            "ItemName": row["ItemName"],
            "Quantity": str(row["Quantity"]),
            "TotalTime": row["TotalTime"],
            "completedAt": row["completedAt"],
            "item_price": row["item_price"],
            "orderedAt": row["itemOrderedAt"],
            "prepTimeDifference": row["prepTimeDifference"],
            "voidAt": row["voidAt"],
            "voidTotalTime": row["voidTotalTime"]
        })

    # Convert to list format
    final_voiditems_output = []
    for date, orders in voiditems_grouped_orders.items():
        final_voiditems_output.append({
            "Date": date,
            "orders": list(orders.values())  # Convert orders dict to list
        })

    sale_item_query = """
            SELECT 
                t.idtblorderTracker AS order_id,
                t.Date,
                t.Employee,
                t.KOTID,
                t.orderType,
                t.orderedAt,
                t.outlet_orderID,
                t.tableNum,
                t.TotalTime AS orderTotalTime,
                d.AvgPrepTime,
                d.ItemName,
                d.Quantity,
                d.TotalTime,
                d.completedAt,
                d.item_price,
                d.orderedAt AS itemOrderedAt,
                d.prepTimeDifference,
                d.voidAt,
                d.voidTotalTime
            FROM tblorderTracker t
            JOIN tblorderTracker_Details d ON t.idtblorderTracker = d.orderTrackerID
            WHERE t.Date BETWEEN %s AND %s
            AND t.outlet_Name = %s
            AND d.ItemName = %s
            ORDER BY t.Date, t.idtblorderTracker, d.idtblorderTracker_Details;
        """

    
    cursor.execute(sale_item_query, (start_date, end_date, outlet_name, item_name))
    sales_item_rows = cursor.fetchall()
    mydb.close()

    sales_grouped_orders = {}

    for row in sales_item_rows:
        date = row["Date"]
        order_id = row["order_id"]

        # Initialize date group
        if date not in sales_grouped_orders:
            sales_grouped_orders[date] = {}

        # Initialize order tracker group within the date
        if order_id not in sales_grouped_orders[date]:
            sales_grouped_orders[date][order_id] = {
                "Employee": row["Employee"],
                "KOTID": row["KOTID"],
                "OrderType": row["orderType"],
                "OrderedAt": row["orderedAt"],
                "Outlet_orderID": row["outlet_orderID"],
                "TableNum": row["tableNum"],
                "TotalTime": row["orderTotalTime"],
                "items": []
            }     

        # Append item details
        sales_grouped_orders[date][order_id]["items"].append({
            "AvgPrepTime": row["AvgPrepTime"],
            "ItemName": row["ItemName"],
            "Quantity": str(row["Quantity"]),
            "TotalTime": row["TotalTime"],
            # "completedAt": row["completedAt"],
            "completedAt": change_to_12hourformat(row["completedAt"]) if row["completedAt"] != "VOID" else "VOID",
            "item_price": row["item_price"],
            # "orderedAt": row["itemOrderedAt"],
            "orderedAt": change_to_12hourformat(row["itemOrderedAt"]) if row["completedAt"] != "VOID" else "VOID",
            "prepTimeDifference": row["prepTimeDifference"],
            "voidAt": row["voidAt"],
            "voidTotalTime": row["voidTotalTime"]
        })

    # Convert to list format
    final_sale_output = []
    for date, orders in sales_grouped_orders.items():
        final_sale_output.append({
            "Date": date,
            "orders": list(orders.values())  # Convert orders dict to list
        })

    return final_sale_output,final_voiditems_output

@app_file85.route("/items-orders-datewise", methods=["POST"])
def void_orders():
    data = request.get_json()
    start_date = data.get("startDate")
    end_date = data.get("endDate")
    outlet_name = data.get("outletName")
    item_name = data.get("itemName")
    # type = data.get("type")
    if not start_date or not end_date or not outlet_name or not item_name:
        return jsonify({"error": "Missing parameters"}), 400

    orders, void_orders = get_items_orders(start_date, end_date, outlet_name, item_name)
    return jsonify({"orders": orders, "void_orders": void_orders})

def change_to_12hourformat(time):
    # Convert string to datetime object
    time_obj = datetime.strptime(time, "%H:%M:%S")

    # Convert to 12-hour format with AM/PM
    time_12 = time_obj.strftime("%I:%M %p")  # %I is for 12-hour, %p is for AM/PM

    return time_12