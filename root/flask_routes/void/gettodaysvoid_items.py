from flask import Flask, request, jsonify
import mysql.connector
from flask import  Blueprint,request
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv
load_dotenv()
app_file84 = Blueprint('app_file84',__name__)

def get_void_orders(start_date, end_date, outlet_name):
    mydb = mysql.connector.connect(host=os.getenv('host'), user=os.getenv('user'), password=os.getenv('password'))
    cursor = mydb.cursor(dictionary=True)
    database_sql = "USE {};".format(os.getenv('database'))
    cursor.execute(database_sql)

    query = """
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
        ORDER BY t.idtblorderTracker, d.idtblorderTracker_Details;
    """
    
    cursor.execute(query, (start_date, end_date, outlet_name))
    rows = cursor.fetchall()
    mydb.close()

    orders = {}
    for row in rows:
        order_id = row["order_id"]
        if order_id not in orders:
            orders[order_id] = {
                "Date": row["Date"],
                "Employee": row["Employee"],
                "KOTID": row["KOTID"],
                "OrderType": row["orderType"],
                "OrderedAt": row["orderedAt"],
                "Outlet_orderID": row["outlet_orderID"],
                "TableNum": row["tableNum"],
                "TotalTime": row["orderTotalTime"],
                "items": []
            }
        
        orders[order_id]["items"].append({
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

    return list(orders.values())

@app_file84.route("/void-orders-today", methods=["POST"])
def void_orders():
    data = request.get_json()
    start_date = data.get("startDate")
    end_date = data.get("endDate")
    outlet_name = data.get("outletName")

    if not start_date or not end_date or not outlet_name:
        return jsonify({"error": "Missing parameters"}), 400

    orders = get_void_orders(start_date, end_date, outlet_name)
    return jsonify({"orders": orders})

