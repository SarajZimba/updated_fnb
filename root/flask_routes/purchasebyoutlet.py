# from flask import Blueprint, request, jsonify
# import mysql.connector
# from flask_cors import cross_origin
# import os
# from dotenv import load_dotenv
# from root.auth.check import token_auth
# load_dotenv()
# app_file217 = Blueprint('app_file217', __name__)

# @app_file217.route("/purchase-by-outlet-dept", methods=["POST"])
# @cross_origin()
# def purchase_summary_outlet_dept():
#     mydb = None
#     try:
#         mydb = mysql.connector.connect(
#             host=os.getenv('host'),
#             user=os.getenv('user'),
#             password=os.getenv('password'),
#             database=os.getenv('database')
#         )
#         cursor = mydb.cursor(dictionary=True)

#         json = request.get_json()
#         start_date = json.get("dateStart")
#         end_date = json.get("dateEnd")

#         if "token" not in json  or not any([json["token"]])  or json["token"]=="":
#             data = {"error":"No token provided."}
#             mydb.close()
#             return data,400
#         token = json["token"]
#         if not token_auth(token):
#             data = {"error":"Invalid token."}
#             mydb.close()
#             return data,400

#         # -------------------------
#         # DATE FILTER
#         # -------------------------
#         date_filter = ""
#         params = []
#         if start_date and end_date:
#             date_filter = "WHERE pr.Date BETWEEN %s AND %s"
#             params.extend([start_date, end_date])

#         # -------------------------
#         # 1️⃣ GET ALL OUTLETS
#         # -------------------------
#         cursor.execute("SELECT DISTINCT Outlet FROM outetNames")
#         outlets = [r["Outlet"] for r in cursor.fetchall()]

#         result = {}
#         for o in outlets:
#             result[o] = {
#                 "TotalPurchase": 0,
#                 "Departments": {}
#             }

#         # -------------------------
#         # 2️⃣ ITEMS TOTAL PER DEPT (NO TAX)
#         # -------------------------
#         sql_items = f"""
#         SELECT 
#             pr.Outlet_Name,
#             pc.Department,
#             SUM(pc.UnitsOrdered * pc.Rate) AS ItemsTotal
#         FROM intbl_purchaserequisition pr
#         JOIN intbl_purchaserequisition_contract pc
#             ON pc.PurchaseReqID = pr.IDIntbl_PurchaseRequisition
#         {date_filter}
#         GROUP BY pr.Outlet_Name, pc.Department
#         """
#         cursor.execute(sql_items, params)
#         rows_items = cursor.fetchall()

#         for row in rows_items:
#             outlet = row["Outlet_Name"]
#             dept = (row["Department"] or "").strip()
#             items_total = float(row["ItemsTotal"] or 0)

#             if outlet not in result:
#                 result[outlet] = {
#                     "TotalPurchase": 0,
#                     "Departments": {}
#                 }

#             result[outlet]["Departments"][dept] = round(items_total, 2)

#         # -------------------------
#         # 3️⃣ FINAL TOTAL FROM TotalAmount FIELD
#         # -------------------------
#         sql_total = f"""
#         SELECT 
#             pr.Outlet_Name,
#             SUM(pr.TotalAmount) AS OutletTotal
#         FROM intbl_purchaserequisition pr
#         {date_filter}
#         GROUP BY pr.Outlet_Name
#         """
#         cursor.execute(sql_total, params)
#         rows_total = cursor.fetchall()

#         for row in rows_total:
#             outlet = row["Outlet_Name"]
#             total = float(row["OutletTotal"] or 0)

#             if outlet not in result:
#                 result[outlet] = {
#                     "TotalPurchase": 0,
#                     "Departments": {}
#                 }

#             result[outlet]["TotalPurchase"] = round(total, 2)

#         cursor.close()
#         mydb.close()

#         return result, 200

#     except Exception as e:
#         if mydb:
#             mydb.close()
#         return {"error": str(e)}, 400


# from datetime import datetime, timedelta
# import pytz

# @app_file217.route('/getweeklypurchase', methods=["POST"])
# @cross_origin()
# def getweeklypurchase():
#     try:
#         mydb = mysql.connector.connect(
#             host=os.getenv('host'),
#             user=os.getenv('user'),
#             password=os.getenv('password'),
#             database=os.getenv('database')
#         )
#         cursor = mydb.cursor()

#         data = request.get_json() or {}

#         outlet_name = data.get("outlet_name", "ALL")
#         start_date = data.get("start_date")
#         end_date = data.get("end_date")

#         if "token" not in data  or not any([data["token"]])  or data["token"]=="":
#             data = {"error":"No token provided."}
#             mydb.close()
#             return data,400
#         token = data["token"]
#         if not token_auth(token):
#             data = {"error":"Invalid token."}
#             mydb.close()
#             return data,400


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

#         # ALL OUTLETS
#         cursor.execute("SELECT DISTINCT Outlet FROM outetNames")
#         outlets = [row[0] for row in cursor.fetchall()]

#         if not outlets:
#             return jsonify({"error": "No outlets found"}), 400

#         # PURCHASE USING TotalAmount
#         purchase_sql = """
#             SELECT 
#                 pr.Date,
#                 pr.Outlet_Name,
#                 COALESCE(SUM(pr.TotalAmount),0) AS total_purchase
#             FROM intbl_purchaserequisition pr
#             WHERE pr.Date BETWEEN %s AND %s
#             AND (%s = 'ALL' OR pr.Outlet_Name = %s)
#             GROUP BY pr.Date, pr.Outlet_Name
#             ORDER BY pr.Date ASC
#         """

#         cursor.execute(
#             purchase_sql,
#             (start_date_str, end_date_str, outlet_name, outlet_name)
#         )
#         rows = cursor.fetchall()

#         # DATE LIST
#         date_list = []
#         current = start_date
#         while current <= end_date:
#             date_list.append(current.strftime("%Y-%m-%d"))
#             current += timedelta(days=1)

#         # ZERO MATRIX
#         purchase_data = {}
#         for date in date_list:
#             purchase_data[date] = {}
#             for outlet in outlets:
#                 purchase_data[date][outlet] = 0

#         # FILL VALUES
#         for row in rows:
#             date, outlet, total = row
#             purchase_data[str(date)][outlet] = float(total)

#         response = {
#             "start_date": start_date_str,
#             "end_date": end_date_str,
#             "outlets": outlets,
#             "days": [
#                 {
#                     "date": date,
#                     "outlets": purchase_data[date]
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
# from root.auth.check import token_auth

# load_dotenv()
# app_file217 = Blueprint('app_file217', __name__)

# @app_file217.route("/purchase-by-outlet-dept", methods=["POST"])
# @cross_origin()
# def purchase_summary_outlet_dept():
#     mydb = None
#     cursor = None
#     try:
#         mydb = mysql.connector.connect(
#             host=os.getenv('host'),
#             user=os.getenv('user'),
#             password=os.getenv('password'),
#             database=os.getenv('database')
#         )
#         cursor = mydb.cursor(dictionary=True)

#         json = request.get_json()

#         # -----------------------------
#         # Validate token
#         # -----------------------------
#         token = json.get("token")
#         if not token:
#             return {"error": "No token provided."}, 400
#         if not token_auth(token):
#             return {"error": "Invalid token."}, 400

#         # -----------------------------
#         # Validate employee_id
#         # -----------------------------
#         employee_id = json.get("employee_id")
#         if not employee_id:
#             return {"error": "No employee_id provided."}, 400

#         start_date = json.get("dateStart")
#         end_date = json.get("dateEnd")

#         # -----------------------------
#         # Get outlets employee has access to
#         # -----------------------------
#         cursor.execute("""
#             SELECT o.Outlet
#             FROM outetNames o
#             JOIN employeeoutlets eo ON eo.outlet_id = o.id
#             WHERE eo.employee_id = %s AND eo.status = TRUE
#         """, (employee_id,))
#         accessible_outlet_result = cursor.fetchall()
#         accessible_outlets = [r["Outlet"] for r in accessible_outlet_result]

#         if not accessible_outlets:
#             # If user has no access to any outlet, return empty result
#             return {}, 200

#         # -----------------------------
#         # Date filter for SQL queries
#         # -----------------------------
#         date_filter = ""
#         params = []
#         if start_date and end_date:
#             date_filter = "WHERE pr.Date BETWEEN %s AND %s"
#             params.extend([start_date, end_date])

#         # -----------------------------
#         # Initialize result dict only with accessible outlets
#         # -----------------------------
#         result = {}
#         for o in accessible_outlets:
#             result[o] = {
#                 "TotalPurchase": 0,
#                 "Departments": {}
#             }

#         # -----------------------------
#         # 1️⃣ ITEMS TOTAL PER DEPT (NO TAX)
#         # -----------------------------
#         sql_items = f"""
#         SELECT 
#             pr.Outlet_Name,
#             pc.Department,
#             SUM(pc.UnitsOrdered * pc.Rate) AS ItemsTotal
#         FROM intbl_purchaserequisition pr
#         JOIN intbl_purchaserequisition_contract pc
#             ON pc.PurchaseReqID = pr.IDIntbl_PurchaseRequisition
#         {date_filter}
#         AND pr.Outlet_Name IN ({','.join(['%s'] * len(accessible_outlets))})
#         GROUP BY pr.Outlet_Name, pc.Department
#         """
#         params_items = params + accessible_outlets
#         cursor.execute(sql_items, params_items)
#         rows_items = cursor.fetchall()

#         for row in rows_items:
#             outlet = row["Outlet_Name"]
#             dept = (row["Department"] or "").strip()
#             items_total = float(row["ItemsTotal"] or 0)
#             result[outlet]["Departments"][dept] = round(items_total, 2)

#         # -----------------------------
#         # 2️⃣ FINAL TOTAL FROM TotalAmount FIELD
#         # -----------------------------
#         sql_total = f"""
#         SELECT 
#             pr.Outlet_Name,
#             SUM(pr.TotalAmount) AS OutletTotal
#         FROM intbl_purchaserequisition pr
#         {date_filter}
#         AND pr.Outlet_Name IN ({','.join(['%s'] * len(accessible_outlets))})
#         GROUP BY pr.Outlet_Name
#         """
#         params_total = params + accessible_outlets
#         cursor.execute(sql_total, params_total)
#         rows_total = cursor.fetchall()

#         for row in rows_total:
#             outlet = row["Outlet_Name"]
#             total = float(row["OutletTotal"] or 0)
#             result[outlet]["TotalPurchase"] = round(total, 2)

#         cursor.close()
#         mydb.close()
#         return result, 200

#     except Exception as e:
#         if mydb:
#             mydb.close()
#         return {"error": str(e)}, 400

from flask import Blueprint, request, jsonify
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv
from root.auth.check import token_auth

load_dotenv()
app_file217 = Blueprint('app_file217', __name__)

@app_file217.route("/purchase-by-outlet-dept", methods=["POST"])
@cross_origin()
def purchase_summary_outlet_dept():
    mydb = None
    cursor = None
    try:
        # ---------------- DB CONNECTION ----------------
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password'),
            database=os.getenv('database')
        )
        cursor = mydb.cursor(dictionary=True)

        json = request.get_json() or {}

        # ---------------- VALIDATE TOKEN ----------------
        token = json.get("token")
        if not token:
            return {"error": "No token provided."}, 400
        if not token_auth(token):
            return {"error": "Invalid token."}, 400

        # ---------------- INPUTS ----------------
        employee_id = json.get("employee_id")  # optional now
        start_date = json.get("dateStart")
        end_date = json.get("dateEnd")

        # ---------------- FETCH ACCESSIBLE OUTLETS ----------------
        if employee_id:
            # Get only outlets employee can access
            cursor.execute("""
                SELECT o.Outlet
                FROM outetNames o
                JOIN employeeoutlets eo ON eo.outlet_id = o.id
                WHERE eo.employee_id = %s AND eo.status = TRUE
            """, (employee_id,))
            accessible_outlet_result = cursor.fetchall()
            accessible_outlets = [r["Outlet"] for r in accessible_outlet_result]

            # If employee has no access, return empty result
            if not accessible_outlets:
                return {}, 200
        else:
            # No employee_id → include all outlets
            cursor.execute("SELECT Outlet FROM outetNames")
            accessible_outlet_result = cursor.fetchall()
            accessible_outlets = [r["Outlet"] for r in accessible_outlet_result]

        # ---------------- DATE FILTER ----------------
        date_filter = ""
        params = []
        if start_date and end_date:
            date_filter = "WHERE pr.Date BETWEEN %s AND %s"
            params.extend([start_date, end_date])

        # ---------------- INITIALIZE RESULT ----------------
        result = {o: {"TotalPurchase": 0, "Departments": {}} for o in accessible_outlets}

        # ---------------- ITEMS TOTAL PER DEPT ----------------
        sql_items = f"""
        SELECT 
            pr.Outlet_Name,
            pc.Department,
            SUM(pc.UnitsOrdered * pc.Rate) AS ItemsTotal
        FROM intbl_purchaserequisition pr
        JOIN intbl_purchaserequisition_contract pc
            ON pc.PurchaseReqID = pr.IDIntbl_PurchaseRequisition
        {date_filter}
        {"AND" if date_filter else "WHERE"} pr.Outlet_Name IN ({','.join(['%s'] * len(accessible_outlets))})
        GROUP BY pr.Outlet_Name, pc.Department
        """
        params_items = params + accessible_outlets
        cursor.execute(sql_items, params_items)
        rows_items = cursor.fetchall()

        for row in rows_items:
            outlet = row["Outlet_Name"]
            dept = (row["Department"] or "").strip()
            items_total = float(row["ItemsTotal"] or 0)
            result[outlet]["Departments"][dept] = round(items_total, 2)

        # ---------------- FINAL TOTAL ----------------
        sql_total = f"""
        SELECT 
            pr.Outlet_Name,
            SUM(pr.TotalAmount) AS OutletTotal
        FROM intbl_purchaserequisition pr
        {date_filter}
        {"AND" if date_filter else "WHERE"} pr.Outlet_Name IN ({','.join(['%s'] * len(accessible_outlets))})
        GROUP BY pr.Outlet_Name
        """
        params_total = params + accessible_outlets
        cursor.execute(sql_total, params_total)
        rows_total = cursor.fetchall()

        for row in rows_total:
            outlet = row["Outlet_Name"]
            total = float(row["OutletTotal"] or 0)
            result[outlet]["TotalPurchase"] = round(total, 2)

        return result, 200

    except Exception as e:
        return {"error": str(e)}, 400

    finally:
        if cursor:
            cursor.close()
        if mydb:
            mydb.close()


# from datetime import datetime, timedelta
# import pytz

# @app_file217.route('/getweeklypurchase', methods=["POST"])
# @cross_origin()
# def getweeklypurchase():
#     mydb = None
#     cursor = None
#     try:
#         mydb = mysql.connector.connect(
#             host=os.getenv('host'),
#             user=os.getenv('user'),
#             password=os.getenv('password'),
#             database=os.getenv('database')
#         )
#         cursor = mydb.cursor()

#         data = request.get_json() or {}

#         # -----------------------------
#         # Token validation
#         # -----------------------------
#         token = data.get("token")
#         if not token:
#             return {"error": "No token provided."}, 400
#         if not token_auth(token):
#             return {"error": "Invalid token."}, 400

#         # -----------------------------
#         # Employee ID validation
#         # -----------------------------
#         employee_id = data.get("employee_id")
#         if not employee_id:
#             return {"error": "No employee_id provided."}, 400

#         # -----------------------------
#         # Dates
#         # -----------------------------
#         start_date = data.get("start_date")
#         end_date = data.get("end_date")

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

#         # -----------------------------
#         # Get outlets employee has access to
#         # -----------------------------
#         cursor.execute("""
#             SELECT o.Outlet
#             FROM outetNames o
#             JOIN employeeoutlets eo ON eo.outlet_id = o.id
#             WHERE eo.employee_id = %s AND eo.status = TRUE
#         """, (employee_id,))
#         accessible_outlets_result = cursor.fetchall()
#         accessible_outlets = [row[0] for row in accessible_outlets_result]

#         if not accessible_outlets:
#             # No access, return empty result
#             return jsonify({
#                 "start_date": start_date_str,
#                 "end_date": end_date_str,
#                 "outlets": [],
#                 "days": []
#             }), 200

#         # -----------------------------
#         # Purchase SQL for only accessible outlets
#         # -----------------------------
#         purchase_sql = f"""
#             SELECT 
#                 pr.Date,
#                 pr.Outlet_Name,
#                 COALESCE(SUM(pr.TotalAmount),0) AS total_purchase
#             FROM intbl_purchaserequisition pr
#             WHERE pr.Date BETWEEN %s AND %s
#             AND pr.Outlet_Name IN ({','.join(['%s']*len(accessible_outlets))})
#             GROUP BY pr.Date, pr.Outlet_Name
#             ORDER BY pr.Date ASC
#         """
#         params = [start_date_str, end_date_str] + accessible_outlets
#         cursor.execute(purchase_sql, params)
#         rows = cursor.fetchall()

#         # -----------------------------
#         # Prepare date list
#         # -----------------------------
#         date_list = []
#         current = start_date
#         while current <= end_date:
#             date_list.append(current.strftime("%Y-%m-%d"))
#             current += timedelta(days=1)

#         # -----------------------------
#         # Initialize zero matrix
#         # -----------------------------
#         purchase_data = {}
#         for date in date_list:
#             purchase_data[date] = {}
#             for outlet in accessible_outlets:
#                 purchase_data[date][outlet] = 0

#         # -----------------------------
#         # Fill values from DB
#         # -----------------------------
#         for row in rows:
#             date, outlet, total = row
#             purchase_data[str(date)][outlet] = float(total)

#         # -----------------------------
#         # Final response
#         # -----------------------------
#         response = {
#             "start_date": start_date_str,
#             "end_date": end_date_str,
#             "outlets": accessible_outlets,
#             "days": [
#                 {
#                     "date": date,
#                     "outlets": purchase_data[date]
#                 }
#                 for date in date_list
#             ]
#         }

#         return jsonify(response), 200

#     except Exception as e:
#         return jsonify({"error": str(e)}), 400

#     finally:
#         if cursor:
#             cursor.close()
#         if mydb:
#             mydb.close()



from datetime import datetime, timedelta
import pytz

@app_file217.route('/getweeklypurchase', methods=["POST"])
@cross_origin()
def getweeklypurchase():
    mydb = None
    cursor = None
    try:
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password'),
            database=os.getenv('database')
        )
        cursor = mydb.cursor()

        data = request.get_json() or {}

        # ----------------------------- Token validation -----------------------------
        token = data.get("token")
        if not token:
            return {"error": "No token provided."}, 400
        if not token_auth(token):
            return {"error": "Invalid token."}, 400

        # ----------------------------- Employee ID -----------------------------
        employee_id = data.get("employee_id")  # now optional

        # ----------------------------- Dates -----------------------------
        start_date = data.get("start_date")
        end_date = data.get("end_date")

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

        # ----------------------------- Fetch accessible outlets -----------------------------
        if employee_id:
            # Only outlets employee has access to
            cursor.execute("""
                SELECT o.Outlet
                FROM outetNames o
                JOIN employeeoutlets eo ON eo.outlet_id = o.id
                WHERE eo.employee_id = %s AND eo.status = TRUE
            """, (employee_id,))
            accessible_outlets_result = cursor.fetchall()
            accessible_outlets = [row[0] for row in accessible_outlets_result]

            # If no access, return empty
            if not accessible_outlets:
                return jsonify({
                    "start_date": start_date_str,
                    "end_date": end_date_str,
                    "outlets": [],
                    "days": []
                }), 200
        else:
            # No employee_id → include all outlets
            cursor.execute("SELECT Outlet FROM outetNames")
            accessible_outlets_result = cursor.fetchall()
            accessible_outlets = [row[0] for row in accessible_outlets_result]

        # ----------------------------- Fetch purchase data -----------------------------
        if not accessible_outlets:
            # fallback in case table is empty
            return jsonify({
                "start_date": start_date_str,
                "end_date": end_date_str,
                "outlets": [],
                "days": []
            }), 200

        purchase_sql = f"""
            SELECT 
                pr.Date,
                pr.Outlet_Name,
                COALESCE(SUM(pr.TotalAmount), 0) AS total_purchase
            FROM intbl_purchaserequisition pr
            WHERE pr.Date BETWEEN %s AND %s
            AND pr.Outlet_Name IN ({','.join(['%s'] * len(accessible_outlets))})
            GROUP BY pr.Date, pr.Outlet_Name
            ORDER BY pr.Date ASC
        """
        params = [start_date_str, end_date_str] + accessible_outlets
        cursor.execute(purchase_sql, params)
        rows = cursor.fetchall()

        # ----------------------------- Prepare date list -----------------------------
        date_list = []
        current = start_date
        while current <= end_date:
            date_list.append(current.strftime("%Y-%m-%d"))
            current += timedelta(days=1)

        # ----------------------------- Initialize zero matrix -----------------------------
        purchase_data = {date: {o: 0 for o in accessible_outlets} for date in date_list}

        # ----------------------------- Fill actual values -----------------------------
        for row in rows:
            date, outlet, total = row
            if outlet in accessible_outlets:
                purchase_data[str(date)][outlet] = float(total)

        # ----------------------------- Prepare final response -----------------------------
        response = {
            "start_date": start_date_str,
            "end_date": end_date_str,
            "outlets": accessible_outlets,
            "days": [
                {"date": date, "outlets": purchase_data[date]}
                for date in date_list
            ]
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

    finally:
        if cursor:
            cursor.close()
        if mydb:
            mydb.close()


from datetime import datetime, timedelta
import pytz
from root.auth.check import token_auth

@app_file217.route('/getweeklypurchase_sales', methods=["POST"])
@cross_origin()
def getweeklypurchase_sales():
    mydb = None
    cursor = None
    try:
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password'),
            database=os.getenv('database')
        )
        cursor = mydb.cursor()

        data = request.get_json() or {}

        # ----------------------------- Token validation -----------------------------
        token = data.get("token")
        if not token:
            return {"error": "No token provided."}, 400
        if not token_auth(token):
            return {"error": "Invalid token."}, 400

        # ----------------------------- Employee ID -----------------------------
        employee_id = data.get("employee_id")  # now optional

        # ----------------------------- Dates -----------------------------
        start_date = data.get("start_date")
        end_date = data.get("end_date")

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

        # ----------------------------- Fetch accessible outlets -----------------------------
        if employee_id:
            # Only outlets employee has access to
            cursor.execute("""
                SELECT o.Outlet
                FROM outetNames o
                JOIN employeeoutlets eo ON eo.outlet_id = o.id
                WHERE eo.employee_id = %s AND eo.status = TRUE
            """, (employee_id,))
            accessible_outlets_result = cursor.fetchall()
            accessible_outlets = [row[0] for row in accessible_outlets_result]

            # If no access, return empty
            if not accessible_outlets:
                return jsonify({
                    "start_date": start_date_str,
                    "end_date": end_date_str,
                    "outlets": [],
                    "days": []
                }), 200
        else:
            # No employee_id → include all outlets
            cursor.execute("SELECT Outlet FROM outetNames")
            accessible_outlets_result = cursor.fetchall()
            accessible_outlets = [row[0] for row in accessible_outlets_result]

        # ----------------------------- Fetch purchase data -----------------------------
        if not accessible_outlets:
            # fallback in case table is empty
            return jsonify({
                "start_date": start_date_str,
                "end_date": end_date_str,
                "outlets": [],
                "days": []
            }), 200

        purchase_sql = f"""
            SELECT 
                pr.Date,
                pr.Outlet_Name,
                COALESCE(SUM(pr.TotalAmount), 0) AS total_purchase
            FROM intbl_purchaserequisition pr
            WHERE pr.Date BETWEEN %s AND %s
            AND pr.Outlet_Name IN ({','.join(['%s'] * len(accessible_outlets))})
            GROUP BY pr.Date, pr.Outlet_Name
            ORDER BY pr.Date ASC
        """
        params = [start_date_str, end_date_str] + accessible_outlets
        cursor.execute(purchase_sql, params)
        purchase_rows = cursor.fetchall()

        # ----------------------------- Fetch sales data -----------------------------
        sales_sql = f"""
            SELECT 
                Date,
                Outlet_Name,
                COALESCE(SUM(Total), 0) AS total_sales
            FROM tblorderhistory
            WHERE bill_no != ''
            AND Date BETWEEN %s AND %s
            AND Outlet_Name IN ({','.join(['%s'] * len(accessible_outlets))})
            GROUP BY Date, Outlet_Name
            ORDER BY Date ASC
        """
        cursor.execute(sales_sql, [start_date_str, end_date_str] + accessible_outlets)
        sales_rows = cursor.fetchall()

        # ----------------------------- Prepare date list -----------------------------
        date_list = []
        current = start_date
        while current <= end_date:
            date_list.append(current.strftime("%Y-%m-%d"))
            current += timedelta(days=1)

        # ----------------------------- Initialize zero matrices -----------------------------
        purchase_data = {date: {o: 0 for o in accessible_outlets} for date in date_list}
        sales_data = {date: {o: 0 for o in accessible_outlets} for date in date_list}

        # ----------------------------- Fill actual purchase values -----------------------------
        for row in purchase_rows:
            date, outlet, total = row
            if outlet in accessible_outlets:
                purchase_data[str(date)][outlet] = float(total)

        # ----------------------------- Fill actual sales values -----------------------------
        for row in sales_rows:
            date, outlet, total = row
            if outlet in accessible_outlets:
                sales_data[str(date)][outlet] = float(total)

        # ----------------------------- Prepare final response -----------------------------
        response = {
            "start_date": start_date_str,
            "end_date": end_date_str,
            "outlets": accessible_outlets,
            "days": [
                {
                    "date": date, 
                    "outlets": {
                        outlet: {
                            "purchase": purchase_data[date][outlet],
                            "sales": sales_data[date][outlet]
                        }
                        for outlet in accessible_outlets
                    }
                }
                for date in date_list
            ]
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

    finally:
        if cursor:
            cursor.close()
        if mydb:
            mydb.close()