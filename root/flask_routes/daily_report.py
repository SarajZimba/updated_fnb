# from flask import Blueprint, request
# import mysql.connector
# from flask_cors import cross_origin
# import os
# from dotenv import load_dotenv
# from datetime import datetime, timedelta
# import re

# load_dotenv()
# app_file65 = Blueprint('app_file65', __name__)
# from root.auth.check import token_auth

# from collections import defaultdict

# from decimal import Decimal
# def valid_date(datestring):
#     try:
#         regex = re.compile("^(\d{4})-(0[1-9]|1[0-2]|[1-9])-([1-9]|0[1-9]|[1-2]\d|3[0-1])$")
#         match = re.match(regex, datestring)
#         if match:
#             return True
#     except ValueError:
#         return False
#     return False


# @app_file65.route("/dailyreport", methods=["POST"])
# @cross_origin()
# def dailyreport():
#     try:
#         mydb = mysql.connector.connect(host=os.getenv('host'), user=os.getenv('user'), password=os.getenv('password'))
#         cursor = mydb.cursor(buffered=True)
#         cursor.execute(f"USE {os.getenv('database')};")

#         json = request.get_json()
#         if "token" not in json or not json["token"]:
#             return {"error": "No token provided."}, 400
        
#         token = json["token"]
#         if not token_auth(token):
#             return {"error": "Invalid token."}, 400
        
#         if "outlet" not in json or "dateStart" not in json or "dateEnd" not in json:
#             return {"error": "Some fields are missing"}, 400
        
#         outletName = json["outlet"]
#         start_Date = json["dateStart"]
#         end_Date = json["dateEnd"]

#         if not valid_date(start_Date) or not valid_date(end_Date):
#             return {"error": "Invalid date supplied."}, 400
        
#         # Convert dates to Python date objects
#         start_date_obj = datetime.strptime(start_Date, "%Y-%m-%d")
#         end_date_obj = datetime.strptime(end_Date, "%Y-%m-%d")

#         # List to store daily reports
#         daily_reports = []

#         # Iterate through each date
#         current_date = start_date_obj
#         while current_date <= end_date_obj:
#             date_str = current_date.strftime("%Y-%m-%d")

#             # Query to fetch sales data for the current day
#             statsSql = f"""
#             SELECT 
#                 (SELECT SUM(b.total) FROM tblorderhistory b WHERE b.bill_no != '' AND b.Date = %s AND b.Outlet_Name = %s) AS TOTALSALES,
#                 (SELECT SUM(b.total) FROM tblorderhistory b WHERE b.bill_no != '' AND b.Date = %s AND b.Outlet_Name = %s AND b.Type='Dine-In') AS DineInSALES,
#                 (SELECT SUM(b.total) FROM tblorderhistory b WHERE b.bill_no != '' AND b.Date = %s AND b.Outlet_Name = %s AND b.Type='Tab') AS TabSALES,
#                 (SELECT SUM(b.Total - b.serviceCharge - b.VAT) FROM tblorderhistory b WHERE b.bill_no != '' AND b.Date = %s AND b.Outlet_Name = %s) AS netTOTALSALES,
#                 (SELECT SUM(b.Total - b.serviceCharge - b.VAT) FROM tblorderhistory b WHERE b.bill_no != '' AND b.Date = %s AND b.Outlet_Name = %s AND b.Type='Dine-In') AS netDineInSALES,
#                 (SELECT SUM(b.Total - b.serviceCharge - b.VAT) FROM tblorderhistory b WHERE b.bill_no != '' AND b.Date = %s AND b.Outlet_Name = %s AND b.Type='Tab') AS netTabSALES,
#                 (SELECT SUM(b.VAT) FROM tblorderhistory b WHERE b.bill_no != '' AND b.Date = %s AND b.Outlet_Name = %s) AS TotalVat,
#                 (SELECT SUM(b.serviceCharge) FROM tblorderhistory b WHERE b.bill_no != '' AND b.Date = %s AND b.Outlet_Name = %s) AS TotalServiceCharge,
#                 (SELECT SUM(b.NoOfGuests) FROM tblorderhistory b WHERE b.bill_no != '' AND b.Date = %s AND b.Outlet_Name = %s) AS TotalGuests,
#                 (SELECT MIN(CAST(bill_no AS UNSIGNED)) FROM tblorderhistory WHERE bill_no != '' AND Date = %s AND Outlet_Name = %s) AS StartBill,
#                 (SELECT MAX(CAST(bill_no AS UNSIGNED)) FROM tblorderhistory WHERE bill_no != '' AND Date = %s AND Outlet_Name = %s) AS EndBill;
#             """
#             cursor.execute(statsSql, (date_str, outletName) * 11)
#             statsResult = cursor.fetchall()

#             if not statsResult or not statsResult[0][0]:
#                 current_date += timedelta(days=1)
#                 continue  # Skip if no data

#             row_headers = [x[0] for x in cursor.description]
#             daily_data = dict(zip(row_headers, statsResult[0]))
#             daily_data["Date"] = date_str  # Add date to response
            
#             # Fetch payment stats
#             paymentStats_Sql = """
#             SELECT CONVERT(SUM(Total), CHAR) AS Total, PaymentMode 
#             FROM tblorderhistory 
#             WHERE Date = %s AND Outlet_Name = %s 
#             GROUP BY PaymentMode
#             """
#             cursor.execute(paymentStats_Sql, (date_str, outletName))
#             paymentStatsResult = cursor.fetchall()

#             paymentStats_json_data = {}
#             row_headers = [x[0] for x in cursor.description]
#             for res in paymentStatsResult:
#                 paymentkey = dict(zip(row_headers, res))["PaymentMode"]
#                 paymentkey = paymentkey.replace(" ", "")
#                 paymentStats_json_data[paymentkey] = dict(zip(row_headers, res))["Total"]

#             # Ensure all keys exist
#             required_keys = ["Cash", "Complimentary", "CreditCard", "MobilePayment", "NonChargeable", "Split", "Credit"]
#             for key in required_keys:
#                 if key not in paymentStats_json_data:
#                     paymentStats_json_data[key] = "0"

#             # Merge Complimentary and NonChargeable
#             if "NonChargeable" in paymentStats_json_data and "Complimentary" in paymentStats_json_data:
#                 paymentStats_json_data["Complimentary"] = str(float(paymentStats_json_data["NonChargeable"]) + float(paymentStats_json_data["Complimentary"]))

#             if "NonChargeable" in paymentStats_json_data and "Complimentary" not in paymentStats_json_data:
#                 paymentStats_json_data["Complimentary"] = paymentStats_json_data["NonChargeable"]

#             daily_data["paymentStats"] = paymentStats_json_data

#             # Append to list
#             daily_reports.append(daily_data)

#             # Move to next day
#             current_date += timedelta(days=1)

#         mydb.close()

#         response_dict = {
#             "daily_data" : [],
#             "total_data": {}
#         }

#         response_dict["daily_data"] = daily_reports

#         total_data = defaultdict(Decimal)

#         for report in daily_reports:
#             for key, value in report.items():
#                 if key in ["Date", "StartBill", "EndBill", "paymentStats"]:
#                     continue

#                 if isinstance(value, str ) or value is None:
#                     value = Decimal(value) if value not in (None, "null") else Decimal(0.0)
#                 total_data[key] += value

#             for key, value in report["paymentStats"].items():
#                 if isinstance(value, str) or value is None:
#                     value = Decimal(value) if value not in (None, "null") else Decimal(0.0)
#                 total_data[key] += value

            
#         total_data = dict(total_data)


#         response_dict["total_data"] = total_data
        


#         return response_dict

#     except Exception as error:
#         return {'error': str(error)}, 400


from flask import Blueprint, request
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import re

load_dotenv()
app_file65 = Blueprint('app_file65', __name__)
from root.auth.check import token_auth

from collections import defaultdict

from decimal import Decimal
def valid_date(datestring):
    try:
        regex = re.compile("^(\d{4})-(0[1-9]|1[0-2]|[1-9])-([1-9]|0[1-9]|[1-2]\d|3[0-1])$")
        match = re.match(regex, datestring)
        if match:
            return True
    except ValueError:
        return False
    return False


@app_file65.route("/dailyreport", methods=["POST"])
@cross_origin()
def dailyreport():
    try:
        mydb = mysql.connector.connect(host=os.getenv('host'), user=os.getenv('user'), password=os.getenv('password'))
        cursor = mydb.cursor(buffered=True)
        cursor.execute(f"USE {os.getenv('database')};")

        json = request.get_json()
        if "token" not in json or not json["token"]:
            return {"error": "No token provided."}, 400
        
        token = json["token"]
        if not token_auth(token):
            return {"error": "Invalid token."}, 400
        
        if "outlet" not in json or "dateStart" not in json or "dateEnd" not in json:
            return {"error": "Some fields are missing"}, 400
        
        outletName = json["outlet"]
        start_Date = json["dateStart"]
        end_Date = json["dateEnd"]

        if not valid_date(start_Date) or not valid_date(end_Date):
            return {"error": "Invalid date supplied."}, 400
        
        # Convert dates to Python date objects
        start_date_obj = datetime.strptime(start_Date, "%Y-%m-%d")
        end_date_obj = datetime.strptime(end_Date, "%Y-%m-%d")

        # List to store daily reports
        daily_reports = []

        # Iterate through each date
        current_date = start_date_obj
        while current_date <= end_date_obj:
            date_str = current_date.strftime("%Y-%m-%d")

            # Query to fetch sales data for the current day
            statsSql = f"""
            SELECT 
                (SELECT SUM(b.total) FROM tblorderhistory b WHERE b.bill_no != '' AND b.Date = %s AND b.Outlet_Name = %s) AS TOTALSALES,
                (SELECT SUM(b.total) FROM tblorderhistory b WHERE b.bill_no != '' AND b.Date = %s AND b.Outlet_Name = %s AND b.Type='Dine-In') AS DineInSALES,
                (SELECT SUM(b.total) FROM tblorderhistory b WHERE b.bill_no != '' AND b.Date = %s AND b.Outlet_Name = %s AND b.Type='Tab') AS TabSALES,
                (SELECT SUM(b.Total - b.serviceCharge - b.VAT) FROM tblorderhistory b WHERE b.bill_no != '' AND b.Date = %s AND b.Outlet_Name = %s) AS netTOTALSALES,
                (SELECT SUM(b.Total - b.serviceCharge - b.VAT) FROM tblorderhistory b WHERE b.bill_no != '' AND b.Date = %s AND b.Outlet_Name = %s AND b.Type='Dine-In') AS netDineInSALES,
                (SELECT SUM(b.Total - b.serviceCharge - b.VAT) FROM tblorderhistory b WHERE b.bill_no != '' AND b.Date = %s AND b.Outlet_Name = %s AND b.Type='Tab') AS netTabSALES,
                (SELECT SUM(b.VAT) FROM tblorderhistory b WHERE b.bill_no != '' AND b.Date = %s AND b.Outlet_Name = %s) AS TotalVat,
                (SELECT SUM(b.serviceCharge) FROM tblorderhistory b WHERE b.bill_no != '' AND b.Date = %s AND b.Outlet_Name = %s) AS TotalServiceCharge,
                (SELECT SUM(b.NoOfGuests) FROM tblorderhistory b WHERE b.bill_no != '' AND b.Date = %s AND b.Outlet_Name = %s) AS TotalGuests,
                (SELECT MIN(CAST(bill_no AS UNSIGNED)) FROM tblorderhistory WHERE bill_no != '' AND Date = %s AND Outlet_Name = %s) AS StartBill,
                (SELECT MAX(CAST(bill_no AS UNSIGNED)) FROM tblorderhistory WHERE bill_no != '' AND Date = %s AND Outlet_Name = %s) AS EndBill,
                (SELECT SUM(b.DiscountAmt) FROM tblorderhistory b WHERE b.bill_no != '' AND b.Date = %s AND b.Outlet_Name = %s) AS DiscountAmt,
                (SELECT SUM(od.Total) FROM tblorder_detailshistory od
                WHERE od.ItemType = 'Food'
                AND od.order_ID IN (
                    SELECT idtblorderHistory 
                    FROM tblorderhistory 
                    WHERE Date = %s 
                    AND Outlet_Name = %s 
                    AND bill_no != ''
                )) AS Food_Sales,
                (SELECT SUM(od.Total) FROM tblorder_detailshistory od
                WHERE od.ItemType = 'Beverage'
                AND od.order_ID IN (
                    SELECT idtblorderHistory 
                    FROM tblorderhistory 
                    WHERE Date = %s 
                    AND Outlet_Name = %s 
                    AND bill_no != ''
                )) AS Beverage_Sales,
                (SELECT SUM(od.Total) FROM tblorder_detailshistory od
                WHERE od.ItemType = 'Other'
                AND od.order_ID IN (
                    SELECT idtblorderHistory 
                    FROM tblorderhistory 
                    WHERE Date = %s 
                    AND Outlet_Name = %s 
                    AND bill_no != ''
                )) AS Others_Sales
            """
            cursor.execute(statsSql, (date_str, outletName) * 15)
            statsResult = cursor.fetchall()

            if not statsResult or not statsResult[0][0]:
                # current_date += timedelta(days=1)
                dummy_data_for_notavailable_data = {
                    "Beverage_Sales": "0.0",
                    "Date": date_str,
                    "DineInSALES": "0.0",
                    "DiscountAmt": "0.00",
                    "EndBill": 0,
                    "Food_Sales": "0.0",
                    "Others_Sales": None,
                    "StartBill": 0,
                    "TOTALSALES": "0.0",
                    "TabSALES": None,
                    "TotalGuests": "0",
                    "TotalServiceCharge": "0.00",
                    "TotalVat": "0.0",
                    "netDineInSALES": "0.0",
                    "netTOTALSALES": "0.0",
                    "netTabSALES": None,
                    "paymentStats": {
                        "Cash": "0.00",
                        "Complimentary": "0",
                        "Credit": "0",
                        "CreditCard": "0.0",
                        "MobilePayment": "0.0",
                        "NonChargeable": "0",
                        "Split": "0"
                    }
                }
                daily_reports.append(dummy_data_for_notavailable_data)
                current_date += timedelta(days=1)

                continue  # Skip if no data

            row_headers = [x[0] for x in cursor.description]
            daily_data = dict(zip(row_headers, statsResult[0]))
            daily_data["Date"] = date_str  # Add date to response
            
            # Fetch payment stats
            paymentStats_Sql = """
            SELECT CONVERT(SUM(Total), CHAR) AS Total, PaymentMode 
            FROM tblorderhistory 
            WHERE Date = %s AND Outlet_Name = %s 
            GROUP BY PaymentMode
            """
            cursor.execute(paymentStats_Sql, (date_str, outletName))
            paymentStatsResult = cursor.fetchall()

            paymentStats_json_data = {}
            row_headers = [x[0] for x in cursor.description]
            for res in paymentStatsResult:
                paymentkey = dict(zip(row_headers, res))["PaymentMode"]
                paymentkey = paymentkey.replace(" ", "")
                paymentStats_json_data[paymentkey] = dict(zip(row_headers, res))["Total"]

            # Ensure all keys exist
            required_keys = ["Cash", "Complimentary", "CreditCard", "MobilePayment", "NonChargeable", "Split", "Credit"]
            for key in required_keys:
                if key not in paymentStats_json_data:
                    paymentStats_json_data[key] = "0"

            # # Merge Complimentary and NonChargeable
            # if "NonChargeable" in paymentStats_json_data and "Complimentary" in paymentStats_json_data:
            #     paymentStats_json_data["Complimentary"] = str(float(paymentStats_json_data["NonChargeable"]) + float(paymentStats_json_data["Complimentary"]))

            # if "NonChargeable" in paymentStats_json_data and "Complimentary" not in paymentStats_json_data:
            #     paymentStats_json_data["Complimentary"] = paymentStats_json_data["NonChargeable"]

            daily_data["paymentStats"] = paymentStats_json_data



            # Append to list
            daily_reports.append(daily_data)

            # Move to next day
            current_date += timedelta(days=1)

        mydb.close()

        response_dict = {
            "daily_data" : [],
            "total_data": {}
        }

        response_dict["daily_data"] = daily_reports

        total_data = defaultdict(Decimal)

        min_startbill = None
        max_endbill = None
        for report in daily_reports:
            start_bill = Decimal(report.get("StartBill") or 0)  # Convert None/null to 0
            end_bill = Decimal(report.get("EndBill") or 0)

            # Update min_startbill
            if min_startbill is None or start_bill < min_startbill:
                min_startbill = start_bill

            # Update max_endbill
            if max_endbill is None or end_bill > max_endbill:
                max_endbill = end_bill
            for key, value in report.items():
                if key in ["Date", "StartBill", "EndBill", "paymentStats"]:

                    continue

                # if key in ["StartBill"]:
                #     min_startbill = min(min_startbill, Decimal(value))
                

                # if key in ["StartBill"]:
                #     max_endbill = max(max_endbill, Decimal(value))


                if isinstance(value, str ) or value is None:
                    value = Decimal(value) if value not in (None, "null") else Decimal(0.0)
                total_data[key] += value

            for key, value in report["paymentStats"].items():
                if isinstance(value, str) or value is None:
                    value = Decimal(value) if value not in (None, "null") else Decimal(0.0)
                total_data[key] += value

            
        total_data = dict(total_data)

        total_data["min_startbill"] = int(min_startbill) if min_startbill else None
        total_data["max_endbill"] = int(max_endbill) if max_endbill else None
        response_dict["total_data"] = total_data
        


        return response_dict

    except Exception as error:
        return {'error': str(error)}, 400
