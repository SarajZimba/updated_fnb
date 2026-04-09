from flask import Blueprint, request, jsonify
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv
from root.auth.check import token_auth
import re
def valid_date(datestring):
        try:
                regex = re.compile("^(\d{4})-(0[1-9]|1[0-2]|[1-9])-([1-9]|0[1-9]|[1-2]\d|3[0-1])$")
                match = re.match(regex, datestring)
                if match is not None:
                    return True
        except ValueError:
            return False
        return False

load_dotenv()
app_file214 = Blueprint('app_file214', __name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('host'),
        user=os.getenv('user'),
        password=os.getenv('password'),
        database=os.getenv('database')
    )

@app_file214.route("/heatmap/table-orders", methods=["POST"])
@cross_origin()
def table_orders_heatmap():
    try:
        data = request.get_json()

        # --- Auth ---
        if "token" not in data or not data["token"]:
            return {"error": "No token provided."}, 400
        if not token_auth(data["token"]):
            return {"error": "Invalid token."}, 400

        # --- Required ---
        required = ["outlet", "dateStart", "dateEnd"]
        if not all(k in data for k in required):
            return {"error": "outlet, dateStart, dateEnd are required."}, 400

        outlet = data["outlet"]
        startDate = data["dateStart"]
        endDate = data["dateEnd"]

        if not valid_date(startDate) or not valid_date(endDate):
            return {"error": "Invalid date supplied."}, 400

        mydb = get_db_connection()
        cursor = mydb.cursor(dictionary=True)

        sql = """
            SELECT
                t.x_coordinate AS x,
                t.y_coordinate AS y,
                COUNT(o.idtblorderHistory) AS value,
                o.Table_No AS table_no
            FROM tblorderhistory o
            JOIN tbl_table_coordinates t
                ON o.Table_No = t.table_no
               AND o.Outlet_Name = t.outlet_name
            WHERE o.Date BETWEEN %s AND %s
              AND o.Outlet_Name = %s
            GROUP BY o.Table_No
        """

        cursor.execute(sql, (startDate, endDate, outlet))
        result = cursor.fetchall()

        cursor.close()
        mydb.close()

        if not result:
            return {"error": "No heatmap data available."}, 400

        return jsonify({
            "type": "table_vs_orders",
            "outlet": outlet,
            "data": result
        }), 200

    except Exception as e:
        return {"error": str(e)}, 500
