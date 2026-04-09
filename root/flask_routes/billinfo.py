# from flask import Flask, Blueprint, request, jsonify
# import mysql.connector
# from flask_cors import cross_origin
# import os
# from dotenv import load_dotenv
# from root.auth.check import token_auth

# load_dotenv()

# app_file19 = Blueprint('app_file19', __name__)

# @app_file19.route("/billinfo", methods=["POST"])
# @cross_origin()
# def billinfo():
#     try:
#         # DB connection
#         mydb = mysql.connector.connect(
#             host=os.getenv('host'),
#             user=os.getenv('user'),
#             password=os.getenv('password')
#         )
#         cursor = mydb.cursor(buffered=True)
#         cursor.execute(f"USE {os.getenv('database')}")

#         # Parse request
#         data = request.get_json()
#         if "token" not in data or not data["token"]:
#             return {"error": "No token provided."}, 400
#         if not token_auth(data["token"]):
#             return {"error": "Invalid token."}, 400

#         if "Outlet_Name" not in data or "bill_id" not in data or "Date" not in data:
#             return {"error": "Some fields are missing"}, 400

#         outletName = data["Outlet_Name"]
#         # billNo = data["bill_no"]
#         billDate = data["Date"]
#         if  "bill_id" not in data:
#             data = {"error":"Bill Id missing"}
#             return data,400
#         BillId = data["bill_id"]

#         # Fetch main bill details
#         cursor.execute("""
#             SELECT bill_no, employee, Table_No, Start_Time, End_Time, Type,
#                    Date, serviceCharge, vat, total, PaymentMode, NoOfGuests, GuestName, guestPan, DiscountAmt
#             FROM tblorderhistory
#             WHERE idtblorderHistory=%s
#         """, (BillId,))
#         result = cursor.fetchall()

#         if not result:
#             return {"error": "No data available."}, 400

#         row_headers = [x[0] for x in cursor.description]
#         json_data = [dict(zip(row_headers, res)) for res in result]

#         # Fetch item details with group by (fixed with aggregation)
#         cursor.execute("""
#             SELECT 
#                 a.itemName, 
#                 SUM(a.count) AS Quantity, 
#                 MAX(a.itemrate) AS itemrate, 
#                 SUM(a.total) AS total, 
#                 MAX(a.ItemType) AS ItemType
#             FROM tblorder_detailshistory a
#             JOIN tblorderhistory b ON a.order_ID = b.idtblorderHistory
#             WHERE idtblorderHistory=%s
#             GROUP BY a.itemName
#         """, (BillId,))
#         billitemresult = cursor.fetchall()

#         if not billitemresult:
#             return {"error": "No item details available."}, 400

#         row_headers = [x[0] for x in cursor.description]
#         billItemData = {"Details": [dict(zip(row_headers, res)) for res in billitemresult]}
#         json_data[0]["details"] = billItemData["Details"]

#         # Fetch total quantity
#         cursor.execute("""
#             SELECT SUM(a.count) AS Quantity
#             FROM tblorder_detailshistory a
#             JOIN tblorderhistory b ON a.order_ID = b.idtblorderHistory
#             WHERE idtblorderHistory=%s
#         """, (BillId,))
#         total_quantity_result = cursor.fetchone()
#         json_data[0]["TotalCount"] = total_quantity_result[0] if total_quantity_result else 0

#         cursor.close()
#         mydb.close()
#         return json_data[0], 200

#     except Exception as error:
#         return {"error": str(error)}, 400


from flask import Flask, Blueprint, request, jsonify
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv
from root.auth.check import token_auth

load_dotenv()

app_file19 = Blueprint('app_file19', __name__)

@app_file19.route("/billinfo", methods=["POST"])
@cross_origin()
def billinfo():
    try:
        # ---------------- DB CONNECTION ----------------
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password'),
            database=os.getenv('database')
        )
        cursor = mydb.cursor(dictionary=True, buffered=True)

        # ---------------- REQUEST DATA ----------------
        data = request.get_json()

        if not data:
            return {"error": "Invalid JSON"}, 400

        # Token validation
        token = data.get("token")
        if not token:
            return {"error": "No token provided."}, 400
        if not token_auth(token):
            return {"error": "Invalid token."}, 400

        # Required fields
        outletName = data.get("Outlet_Name")
        BillId = data.get("bill_id")
        billDate = data.get("Date")

        if not outletName or not BillId or not billDate:
            return {"error": "Some fields are missing"}, 400

        # ---------------- GET BILL PREFIX ----------------
        cursor.execute(
            "SELECT bill_prefix FROM outetNames WHERE Outlet=%s LIMIT 1",
            (outletName,)
        )
        prefix_result = cursor.fetchone()
        bill_prefix = prefix_result["bill_prefix"] if prefix_result else "GEN"

        # ---------------- FETCH MAIN BILL ----------------
        cursor.execute("""
            SELECT bill_no, fiscal_year, employee, Table_No, Start_Time, End_Time, Type,
                   Date, serviceCharge, vat, total, PaymentMode, NoOfGuests,
                   GuestName, guestPan, DiscountAmt
            FROM tblorderhistory
            WHERE idtblorderHistory=%s
        """, (BillId,))

        result = cursor.fetchone()

        if not result:
            return {"error": "No data available."}, 400

        # ---------------- FORMAT BILL NUMBER ----------------
        bill_no = result.get("bill_no")
        fiscal_year = result.get("fiscal_year")

        if bill_no:
            result["bill_no"] = f"{bill_prefix}/{bill_no}/{fiscal_year}"
        else:
            result["bill_no"] = ""

        # ---------------- FETCH ITEM DETAILS ----------------
        cursor.execute("""
            SELECT 
                a.itemName, 
                SUM(a.count) AS Quantity, 
                MAX(a.itemrate) AS itemrate, 
                SUM(a.total) AS total, 
                MAX(a.ItemType) AS ItemType
            FROM tblorder_detailshistory a
            JOIN tblorderhistory b 
                ON a.order_ID = b.idtblorderHistory
            WHERE b.idtblorderHistory=%s
            GROUP BY a.itemName
        """, (BillId,))

        items = cursor.fetchall()

        if not items:
            result["details"] = []
        else:
            result["details"] = items

        # ---------------- TOTAL QUANTITY ----------------
        cursor.execute("""
            SELECT SUM(a.count) AS Quantity
            FROM tblorder_detailshistory a
            WHERE a.order_ID=%s
        """, (BillId,))

        total_qty = cursor.fetchone()
        result["TotalCount"] = total_qty["Quantity"] if total_qty and total_qty["Quantity"] else 0

        # ---------------- CLOSE CONNECTION ----------------
        cursor.close()
        mydb.close()

        return result, 200

    except Exception as error:
        return {"error": str(error)}, 400