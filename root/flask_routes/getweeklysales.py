# from flask import Blueprint, request, jsonify
# import mysql.connector
# from flask_cors import cross_origin
# import os
# from dotenv import load_dotenv
# from datetime import datetime, timedelta
# import pytz

# load_dotenv()

# app_file207 = Blueprint('appfile_207', __name__)

# @app_file207.route('/getweeklysales', methods=["POST"])
# @cross_origin()
# def getweeklysales():
#     try:
#         # ---------------- DB CONNECTION ----------------
#         mydb = mysql.connector.connect(
#             host=os.getenv('host'),
#             user=os.getenv('user'),
#             password=os.getenv('password'),
#             database=os.getenv('database')
#         )
#         cursor = mydb.cursor()

#         data = request.get_json() or {}

#         # ---------------- INPUTS ----------------
#         outlet_name = data.get("outlet_name", "ALL")
#         start_date = data.get("start_date")
#         end_date = data.get("end_date")

#         # ---------------- DATE RANGE (DEFAULT 7 DAYS) ----------------
#         nepal_tz = pytz.timezone("Asia/Kathmandu")
#         today = datetime.now(nepal_tz).date()

#         if not start_date or not end_date:
#             end_date = today
#             start_date = today - timedelta(days=6)
#         else:
#             start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
#             end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

#         start_date_str = start_date.strftime("%Y-%m-%d")
#         end_date_str = end_date.strftime("%Y-%m-%d")

#         # ---------------- FETCH ALL OUTLETS ----------------
#         outlet_sql = "SELECT DISTINCT Outlet FROM outetNames"
#         cursor.execute(outlet_sql)
#         outlets = [row[0] for row in cursor.fetchall()]

#         if not outlets:
#             return jsonify({"error": "No outlets found"}), 400

#         # ---------------- FETCH SALES DATA ----------------
#         sales_sql = """
#             SELECT 
#                 Date,
#                 Outlet_Name,
#                 COALESCE(SUM(Total), 0) AS total_sales
#             FROM tblorderhistory
#             WHERE bill_no != ''
#             AND Date BETWEEN %s AND %s
#             AND (%s = 'ALL' OR Outlet_Name = %s)
#             GROUP BY Date, Outlet_Name
#             ORDER BY Date ASC
#         """

#         cursor.execute(
#             sales_sql,
#             (start_date_str, end_date_str, outlet_name, outlet_name)
#         )
#         rows = cursor.fetchall()

#         # ---------------- CREATE DATE LIST ----------------
#         date_list = []
#         current = start_date
#         while current <= end_date:
#             date_list.append(current.strftime("%Y-%m-%d"))
#             current += timedelta(days=1)

#         # ---------------- INITIALIZE ZERO MATRIX ----------------
#         sales_data = {}
#         for date in date_list:
#             sales_data[date] = {}
#             for outlet in outlets:
#                 sales_data[date][outlet] = 0

#         # ---------------- FILL ACTUAL SALES ----------------
#         for row in rows:
#             date, outlet, total = row
#             date_str = str(date)   # VARCHAR safe
#             sales_data[date_str][outlet] = float(total)

#         # ---------------- FINAL RESPONSE ----------------
#         response = {
#             "start_date": start_date_str,
#             "end_date": end_date_str,
#             "outlets": outlets,
#             "days": [
#                 {
#                     "date": date,
#                     "outlets": sales_data[date]
#                 }
#                 for date in date_list
#             ]
#         }

#         return jsonify(response), 200

#     except Exception as e:
#         return jsonify({"error": str(e)}), 400

#     finally:
#         if mydb.is_connected():
#             cursor.close()
#             mydb.close()    



# from flask import Blueprint, request, jsonify
# import mysql.connector
# from flask_cors import cross_origin
# import os
# from dotenv import load_dotenv
# from datetime import datetime, timedelta
# import pytz

# load_dotenv()

# app_file207 = Blueprint('appfile_207', __name__)

# @app_file207.route('/getweeklysales', methods=["POST"])
# @cross_origin()
# def getweeklysales():
#     try:
#         # ---------------- DB CONNECTION ----------------
#         mydb = mysql.connector.connect(
#             host=os.getenv('host'),
#             user=os.getenv('user'),
#             password=os.getenv('password'),
#             database=os.getenv('database')
#         )
#         cursor = mydb.cursor()

#         data = request.get_json() or {}

#         # ---------------- INPUTS ----------------
#         employee_id = data.get("employee_id")
#         if not employee_id:
#             return jsonify({"error": "No employee_id provided"}), 400

#         outlet_name = data.get("outlet_name", "ALL")
#         start_date = data.get("start_date")
#         end_date = data.get("end_date")

#         # ---------------- DATE RANGE (DEFAULT 7 DAYS) ----------------
#         nepal_tz = pytz.timezone("Asia/Kathmandu")
#         today = datetime.now(nepal_tz).date()

#         if not start_date or not end_date:
#             end_date = today
#             start_date = today - timedelta(days=6)
#         else:
#             start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
#             end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

#         start_date_str = start_date.strftime("%Y-%m-%d")
#         end_date_str = end_date.strftime("%Y-%m-%d")

#         # ---------------- FETCH OUTLETS ACCESSIBLE TO EMPLOYEE ----------------
#         cursor.execute("""
#             SELECT o.Outlet
#             FROM outetNames o
#             JOIN employeeoutlets eo ON eo.outlet_id = o.id
#             WHERE eo.employee_id = %s AND eo.status = TRUE
#         """, (employee_id,))
#         accessible_outlet_result = cursor.fetchall()
#         accessible_outlets = {row[0] for row in accessible_outlet_result}

#         # If employee has no access, return empty report
#         if not accessible_outlets:
#             return jsonify({
#                 "start_date": start_date_str,
#                 "end_date": end_date_str,
#                 "outlets": [],
#                 "days": []
#             }), 200

#         # ---------------- FETCH SALES DATA ----------------
#         sales_sql = """
#             SELECT 
#                 Date,
#                 Outlet_Name,
#                 COALESCE(SUM(Total), 0) AS total_sales
#             FROM tblorderhistory
#             WHERE bill_no != ''
#             AND Date BETWEEN %s AND %s
#             AND (%s = 'ALL' OR Outlet_Name = %s)
#             GROUP BY Date, Outlet_Name
#             ORDER BY Date ASC
#         """
#         cursor.execute(sales_sql, (start_date_str, end_date_str, outlet_name, outlet_name))
#         rows = cursor.fetchall()

#         # ---------------- CREATE DATE LIST ----------------
#         date_list = []
#         current = start_date
#         while current <= end_date:
#             date_list.append(current.strftime("%Y-%m-%d"))
#             current += timedelta(days=1)

#         # ---------------- INITIALIZE ZERO MATRIX ----------------
#         sales_data = {date: {o: 0 for o in accessible_outlets} for date in date_list}

#         # ---------------- FILL ACTUAL SALES ----------------
#         for row in rows:
#             date, outlet, total = row
#             if outlet not in accessible_outlets:
#                 continue  # skip outlets employee has no access to
#             sales_data[str(date)][outlet] = float(total)

#         # ---------------- FINAL RESPONSE ----------------
#         response = {
#             "start_date": start_date_str,
#             "end_date": end_date_str,
#             "outlets": list(accessible_outlets),
#             "days": [
#                 {
#                     "date": date,
#                     "outlets": sales_data[date]
#                 }
#                 for date in date_list
#             ]
#         }

#         return jsonify(response), 200

#     except Exception as e:
#         return jsonify({"error": str(e)}), 400

#     finally:
#         if mydb.is_connected():
#             cursor.close()
#             mydb.close()

from flask import Blueprint, request, jsonify
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import pytz

load_dotenv()

app_file207 = Blueprint('appfile_207', __name__)

@app_file207.route('/getweeklysales', methods=["POST"])
@cross_origin()
def getweeklysales():
    mydb = None
    try:
        # ---------------- DB CONNECTION ----------------
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password'),
            database=os.getenv('database')
        )
        cursor = mydb.cursor()

        data = request.get_json() or {}

        # ---------------- INPUTS ----------------
        employee_id = data.get("employee_id")  # optional
        outlet_name = data.get("outlet_name", "ALL")
        start_date = data.get("start_date")
        end_date = data.get("end_date")

        # ---------------- DATE RANGE (DEFAULT 7 DAYS) ----------------
        nepal_tz = pytz.timezone("Asia/Kathmandu")
        today = datetime.now(nepal_tz).date()

        if not start_date or not end_date:
            end_date = today
            start_date = today - timedelta(days=6)
        else:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")

        # ---------------- FETCH ACCESSIBLE OUTLETS ----------------
        if employee_id:
            # Get only outlets this employee can access
            cursor.execute("""
                SELECT o.Outlet
                FROM outetNames o
                JOIN employeeoutlets eo ON eo.outlet_id = o.id
                WHERE eo.employee_id = %s AND eo.status = TRUE
            """, (employee_id,))
            accessible_outlet_result = cursor.fetchall()
            accessible_outlets = {row[0] for row in accessible_outlet_result}

            # If employee has no access, return empty report
            if not accessible_outlets:
                return jsonify({
                    "start_date": start_date_str,
                    "end_date": end_date_str,
                    "outlets": [],
                    "days": []
                }), 200
        else:
            # No employee_id provided → include all outlets
            cursor.execute("SELECT Outlet FROM outetNames")
            accessible_outlet_result = cursor.fetchall()
            accessible_outlets = {row[0] for row in accessible_outlet_result}

        # ---------------- FETCH SALES DATA ----------------
        sales_sql = """
            SELECT 
                Date,
                Outlet_Name,
                COALESCE(SUM(Total), 0) AS total_sales
            FROM tblorderhistory
            WHERE bill_no != ''
            AND Date BETWEEN %s AND %s
            AND (%s = 'ALL' OR Outlet_Name = %s)
            GROUP BY Date, Outlet_Name
            ORDER BY Date ASC
        """
        cursor.execute(sales_sql, (start_date_str, end_date_str, outlet_name, outlet_name))
        rows = cursor.fetchall()

        # ---------------- CREATE DATE LIST ----------------
        date_list = []
        current = start_date
        while current <= end_date:
            date_list.append(current.strftime("%Y-%m-%d"))
            current += timedelta(days=1)

        # ---------------- INITIALIZE ZERO MATRIX ----------------
        sales_data = {date: {o: 0 for o in accessible_outlets} for date in date_list}

        # ---------------- FILL ACTUAL SALES ----------------
        for row in rows:
            date, outlet, total = row
            if outlet not in accessible_outlets:
                continue
            sales_data[str(date)][outlet] = float(total)

        # ---------------- FINAL RESPONSE ----------------
        response = {
            "start_date": start_date_str,
            "end_date": end_date_str,
            "outlets": list(accessible_outlets),
            "days": [
                {
                    "date": date,
                    "outlets": sales_data[date]
                }
                for date in date_list
            ]
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

    finally:
        if mydb and mydb.is_connected():
            cursor.close()
            mydb.close()