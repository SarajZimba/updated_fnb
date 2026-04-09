from flask import Blueprint, jsonify, request
import mysql.connector
import os
from dotenv import load_dotenv
from flask_cors import cross_origin
from root.auth.check import token_auth

load_dotenv()

app_file102 = Blueprint('app_file102', __name__)


@app_file102.route("/item-analytics", methods=["POST"])
@cross_origin()
def get_item_analytics():
    try:
        data = request.get_json()

        if not data or "token" not in data:
            return jsonify({"error": "No token provided"}), 400

        if not token_auth(data["token"]):
            return jsonify({"error": "Invalid token"}), 400

        item_name = data.get("itemName")
        dateStart = data.get("startDate")
        dateEnd = data.get("endDate")
        outlet = data.get("outlet")

        if not all([item_name, dateStart, dateEnd, outlet]):
            return jsonify({"error": "Missing required fields"}), 400

        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password'),
            database=os.getenv('database')
        )
        cursor = mydb.cursor(dictionary=True)

        query = """
            SELECT
                od.ItemName,
                COALESCE(od.ItemType, 'Other') AS ItemType,
                oh.Employee,
                SUM(od.count) AS TotalQuantity,
                SUM(od.Total) AS TotalAmount,
                od.itemRate AS ItemRate,
                od.Description AS `Group`
            FROM tblorderhistory oh
            JOIN tblorder_detailshistory od
                ON od.order_ID = oh.idtblorderHistory
            WHERE oh.Employee != ''
                AND oh.Outlet_Name = %s
                AND oh.Date BETWEEN %s AND %s
                AND oh.bill_no != ''
                AND od.ItemName = %s
            GROUP BY od.ItemName, oh.Employee, od.ItemType, od.itemRate, od.Description
        """

        cursor.execute(query, (outlet, dateStart, dateEnd, item_name))
        rows = cursor.fetchall()

        if not rows:
            return jsonify({"message": "No data found"}), 200

        # Build response
        total_qty = 0
        total_sales = 0.0
        employee_breakdown = []

        for row in rows:
            qty = int(row["TotalQuantity"])
            amount = float(row["TotalAmount"])

            total_qty += qty
            total_sales += amount

            employee_breakdown.append({
                "Employee": row["Employee"],
                "QuantitySold": qty,
                "TotalSales": amount
            })

        response = {
            "ItemName": item_name,
            "ItemType": rows[0]["ItemType"],
            "ItemRate": float(rows[0]["ItemRate"]),
            "Group": rows[0]["Group"],
            "TotalQuantitySold": total_qty,
            "TotalSalesAmount": round(total_sales, 2),
            "EmployeeWiseSales": employee_breakdown
        }

        cursor.close()
        mydb.close()

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# @app_file104.route("/employee-analytics", methods=["POST"])
# @cross_origin()
# def get_employee_sales():
#     try:
#         data = request.get_json()

#         if not data or "token" not in data or not data["token"]:
#             return jsonify({"error": "No token provided."}), 400

#         token = data["token"]
#         if not token_auth(token):
#             return jsonify({"error": "Invalid token."}), 400

#         dateStart = data.get("startDate")
#         dateEnd = data.get("endDate")
#         outlet = data.get("outlet")

#         if not dateStart or not dateEnd or not outlet:
#             return jsonify({"error": "Missing 'startDate', 'endDate' or 'outlet' in request body"}), 400

#         mydb = mysql.connector.connect(
#             host=os.getenv('host'),
#             user=os.getenv('user'),
#             password=os.getenv('password'),
#             database=os.getenv('database')
#         )
#         cursor = mydb.cursor(dictionary=True)

#         # Main employee sales query
#         query = """
#             SELECT 
#                 oh_data.Employee,
#                 oh_data.Complimentary_Sales,
#                 oh_data.Banquet_Sales,
#                 oh_data.Discounts_Sales,
#                 COALESCE(od_data.Food_Sales, 0) AS Food_Sales,
#                 COALESCE(od_data.Beverage_Sales, 0) AS Beverage_Sales,
#                 oh_data.noOfGuests,
#                 oh_data.DineInSales,
#                 oh_data.TakeawaySales,
#                 oh_data.BanquetSales,
#                 oh_data.netTotalSales,
#                 oh_data.TotalOrders
#             FROM (
#                 SELECT 
#                     Employee,
#                     COALESCE(SUM(CASE WHEN PaymentMode IN ('Complimentary', 'Non Chargeable') THEN Total END), 0) AS Complimentary_Sales,
#                     COALESCE(SUM(CASE WHEN Type = 'Banquet' THEN Total END), 0) AS Banquet_Sales,
#                     COALESCE(SUM(CASE WHEN bill_no != '' THEN DiscountAmt END), 0) AS Discounts_Sales,
#                     COALESCE(SUM(NoOfGuests), 0) AS noOfGuests,
#                     COALESCE(SUM(CASE WHEN Type = 'Dine-In' AND bill_no != '' THEN (Total - VAT - serviceCharge) ELSE 0 END), 0) AS DineInSales,
#                     COALESCE(SUM(CASE WHEN Type = 'Order' AND bill_no != '' THEN (Total - VAT - serviceCharge) ELSE 0 END), 0) AS TakeawaySales,
#                     COALESCE(SUM(CASE WHEN Type = 'Banquet' AND bill_no != '' THEN (Total - VAT - serviceCharge) ELSE 0 END), 0) AS BanquetSales,
#                     COALESCE(SUM(Total - VAT - serviceCharge), 0) AS netTotalSales,
#                     COUNT(DISTINCT idtblorderHistory) AS TotalOrders
#                 FROM tblorderhistory
#                 WHERE Employee != ''
#                     AND Outlet_Name = %s
#                     AND Date BETWEEN %s AND %s
#                     AND bill_no != ''
#                 GROUP BY Employee
#             ) AS oh_data
#             LEFT JOIN (
#                 SELECT 
#                     oh.Employee,
#                     COALESCE(SUM(CASE WHEN od.ItemType = 'Food' THEN od.Total END), 0) AS Food_Sales,
#                     COALESCE(SUM(CASE WHEN od.ItemType = 'Beverage' THEN od.Total END), 0) AS Beverage_Sales
#                 FROM tblorderhistory oh
#                 JOIN tblorder_detailshistory od ON od.order_ID = oh.idtblorderHistory
#                 WHERE oh.Employee != ''
#                     AND oh.Outlet_Name = %s
#                     AND oh.Date BETWEEN %s AND %s
#                     AND oh.bill_no != ''
#                 GROUP BY oh.Employee
#             ) AS od_data
#             ON oh_data.Employee = od_data.Employee
#         """
#         cursor.execute(query, (outlet, dateStart, dateEnd, outlet, dateStart, dateEnd))
#         rows = cursor.fetchall()

#         # Void order count
#         void_query = """
#             SELECT 
#                 tt.Employee,
#                 COUNT(td.idtblorderTracker_Details) AS void_count
#             FROM tblorderTracker tt
#             JOIN tblorderTracker_Details td ON tt.idtblorderTracker = td.orderTrackerID
#             WHERE td.completedAt = 'VOID'
#                 AND tt.outlet_Name = %s
#                 AND tt.Date BETWEEN %s AND %s
#                 AND tt.Employee != ''
#             GROUP BY tt.Employee
#         """
#         cursor.execute(void_query, (outlet, dateStart, dateEnd))
#         void_rows = cursor.fetchall()
#         void_map = {row["Employee"]: row["void_count"] for row in void_rows}

#         # Item-wise details (quantity and total per item, per employee)
#         cursor.execute("""
#             SELECT 
#                 oh.Employee,
#                 od.ItemName,
#                 COALESCE(od.ItemType, 'Other') AS ItemType,
#                 SUM(od.count) AS TotalQuantity,
#                 SUM(od.Total) AS TotalAmount,
#                 od.itemRate AS ItemRate,
#                 od.Description as `Group`
#             FROM tblorderhistory oh
#             JOIN tblorder_detailshistory od ON od.order_ID = oh.idtblorderHistory
#             WHERE oh.Employee != ''
#                 AND oh.Outlet_Name = %s
#                 AND oh.Date BETWEEN %s AND %s
#                 AND oh.bill_no != ''
#             GROUP BY oh.Employee, od.ItemName, od.ItemType
#         """, (outlet, dateStart, dateEnd))
#         item_rows = cursor.fetchall()

#         # Group items by employee
#         employee_items = {}
#         for item in item_rows:
#             emp = item["Employee"]
#             itype = item["ItemType"]
#             if emp not in employee_items:
#                 employee_items[emp] = {"Food": [], "Beverage": [], "Other": []}
#             employee_items[emp][itype].append({
#                 "ItemName": item["ItemName"],
#                 "TotalQuantity": int(item["TotalQuantity"]),
#                 "TotalAmount": float(item["TotalAmount"]),
#                 "ItemRate": float(item["ItemRate"]),
#                 "Group": item["Group"],

#             })

#         # Final result construction
#         result = []
#         for row in rows:
#             employee_name = row["Employee"]
#             total_sales = row["netTotalSales"]
#             dine_in = row["DineInSales"]
#             takeaway = row["TakeawaySales"]
#             banquet = row["BanquetSales"]
#             no_of_guests = row["noOfGuests"]
#             total_orders = row["TotalOrders"]

#             items_sold = employee_items.get(employee_name, {"Food": [], "Beverage": [], "Other": []})

#             result.append({
#                 "Employee": employee_name,
#                 "Total_Sales": total_sales,
#                 "Complimentary_Sales": float(row["Complimentary_Sales"]),
#                 "Banquet_Sales": float(row["Banquet_Sales"]),
#                 "Discounts_Sales": float(row["Discounts_Sales"]),
#                 "Food_Sales": float(row["Food_Sales"]),
#                 "Beverage_Sales": float(row["Beverage_Sales"]),
#                 "noOfGuests": int(no_of_guests),
#                 "DineInSales": float(dine_in),
#                 "TakeawaySales": float(takeaway),
#                 "BanquetSales": float(banquet),
#                 "DineInSalesPercent": round((dine_in / total_sales) * 100, 2) if total_sales else 0.0,
#                 "TakeawaySalesPercent": round((takeaway / total_sales) * 100, 2) if total_sales else 0.0,
#                 "BanquetSalesPercent": round((banquet / total_sales) * 100, 2) if total_sales else 0.0,
#                 "avgSales": round(total_sales / total_orders, 2) if total_orders else 0.0,
#                 "RevperGuest": round(total_sales / no_of_guests, 2) if no_of_guests else 0.0,
#                 "Void_Order_Count": void_map.get(employee_name, 0),
#                 "Items_Sold": items_sold
#             })

#         cursor.close()
#         mydb.close()
#         return jsonify(result)

#     except Exception as e:
#         return jsonify({"error": str(e)}), 400
