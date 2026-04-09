from flask import Blueprint, jsonify, request
import mysql.connector
import os
from flask_cors import cross_origin
from dotenv import load_dotenv
from root.auth.check import token_auth
from datetime import datetime
app_file88 = Blueprint('app_file88',__name__)

@app_file88.route('/tracker-report', methods=['POST'])

@cross_origin()
def gettracker_report():
    try:
        mydb = mysql.connector.connect(host=os.getenv('host'), user=os.getenv('user'), password=os.getenv('password'))
        cursor = mydb.cursor(buffered=True)
        database_sql = "USE {};".format(os.getenv('database'))
        cursor.execute(database_sql)
        json = request.get_json()
        if "token" not in json  or not any([json["token"]])  or json["token"]=="":
            data = {"error":"No token provided."}
            return data,400

        token = json["token"]
        if "outlet" not in json  or not any([json["outlet"]])  or json["outlet"]=="":
            data = {"error":"No outlet provided."}
            return data,400

        outlet = json["outlet"]

        today_date = datetime.today().strftime("%Y-%m-%d")



        if not token_auth(token):
            data = {"error":"Invalid token."}

        
        query = """select count(DISTINCT(t.idtblorderTracker)), IFNULL(SUM(td.Quantity), 0), IFNULL(SUM(td.Quantity * td.item_price), 0) from tblorderTracker t, tblorderTracker_Details td where t.idtblorderTracker = td.orderTrackerID  and t.currentState = %s and t.Date = %s and t.outlet_Name = %s and not td.completedAt = 'VOID'"""

        cursor.execute(query, ('Started',today_date, outlet,))

        active_orders = cursor.fetchone()

        cursor.execute(query, ('Completed', today_date, outlet,))

        completed_orders = cursor.fetchone()

        active_orders_count = active_orders[0] if active_orders else 0
        active_today_quantity = float(active_orders[1]) if active_orders else 0.0
        active_total_price = float(active_orders[2]) if active_orders and active_orders[2] else 0.0
        completed_orders_count = completed_orders[0] if completed_orders else 0
        completed_total_quantity = float(completed_orders[1]) if completed_orders else 0.0
        completed_total_price = float(completed_orders[2]) if completed_orders and completed_orders[2] else 0.0
        data = {
            "active_orders": {
                "count": active_orders_count,
                "total_quantity": active_today_quantity,
                "total_price": active_total_price
            },
            "completed_orders": {
                "count": completed_orders_count,
                "total_quantity": completed_total_quantity,
                "total_price": completed_total_price
            },
            "total":{
                "count" : active_orders_count + completed_orders_count,
                "total_quantity": active_today_quantity + completed_total_quantity,
                "total_price": active_total_price + completed_total_price
            }
        }


        return data,200
    except Exception as error:
        data ={'error':str(error)}
        return data,400
