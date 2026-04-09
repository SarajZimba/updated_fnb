from flask import Blueprint, jsonify, request
import mysql.connector
import os
from dotenv import load_dotenv
from flask_cors import cross_origin
from root.auth.check import token_auth

load_dotenv()
app_file104 = Blueprint('app_file104', __name__)

@app_file104.route("/employee-analytics", methods=["POST"])
@cross_origin()
def get_employee_sales():
    try:
        data = request.get_json()

        if not data or "token" not in data or not data["token"]:
            return jsonify({"error": "No token provided."}), 400

        if not token_auth(data["token"]):
            return jsonify({"error": "Invalid token."}), 400

        dateStart = data.get("startDate")
        dateEnd = data.get("endDate")
        outlet = data.get("outlet")

        if not dateStart or not dateEnd or not outlet:
            return jsonify({"error": "Missing fields"}), 400

        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password'),
            database=os.getenv('database')
        )
        cursor = mydb.cursor(dictionary=True)

        # ================================
        # 1️⃣ MAIN EMPLOYEE TOTALS
        # ================================
        cursor.execute("""
            SELECT 
                Employee,
                SUM(CASE WHEN PaymentMode IN ('Complimentary','Non Chargeable') THEN Total ELSE 0 END) AS Complimentary_Sales,
                SUM(CASE WHEN Type='Banquet' THEN Total ELSE 0 END) AS Banquet_Sales,
                SUM(CASE WHEN bill_no!='' THEN DiscountAmt ELSE 0 END) AS Discounts_Sales,
                SUM(NoOfGuests) AS noOfGuests,
                SUM(CASE WHEN Type='Dine-In' AND bill_no!='' THEN (Total-VAT-serviceCharge) ELSE 0 END) AS DineInSales,
                SUM(CASE WHEN Type='Order' AND bill_no!='' THEN (Total-VAT-serviceCharge) ELSE 0 END) AS TakeawaySales,
                SUM(CASE WHEN Type='Banquet' AND bill_no!='' THEN (Total-VAT-serviceCharge) ELSE 0 END) AS BanquetSales,
                SUM(Total-VAT-serviceCharge) AS netTotalSales,
                COUNT(DISTINCT idtblorderHistory) AS TotalOrders
            FROM tblorderhistory
            WHERE Employee!=''
              AND Outlet_Name=%s
              AND Date BETWEEN %s AND %s
              AND bill_no!=''
            GROUP BY Employee
        """, (outlet, dateStart, dateEnd))

        employee_rows = cursor.fetchall()

        # ================================
        # 2️⃣ ITEM TOTALS + TYPE TOTALS (MERGED QUERY)
        # ================================
        cursor.execute("""
            SELECT 
                oh.Employee,
                od.ItemName,
                COALESCE(od.ItemType,'Other') AS ItemType,
                SUM(od.count) AS TotalQuantity,
                SUM(od.Total) AS TotalAmount,
                MAX(od.itemRate) AS ItemRate,
                MAX(od.Description) AS `Group`
            FROM tblorderhistory oh
            JOIN tblorder_detailshistory od 
                ON od.order_ID = oh.idtblorderHistory
            WHERE oh.Employee!=''
              AND oh.Outlet_Name=%s
              AND oh.Date BETWEEN %s AND %s
              AND oh.bill_no!=''
            GROUP BY oh.Employee, od.ItemName, od.ItemType
        """, (outlet, dateStart, dateEnd))

        item_rows = cursor.fetchall()

        # Build item structure + type totals together
        employee_items = {}
        type_totals = {}

        for r in item_rows:
            emp = r["Employee"]
            itype = r["ItemType"] or "Other"

            if emp not in employee_items:
                employee_items[emp] = {"Food": [], "Beverage": [], "Other": []}
                type_totals[emp] = {"Food": 0, "Beverage": 0, "Other": 0}

            employee_items[emp][itype].append({
                "ItemName": r["ItemName"],
                "TotalQuantity": int(r["TotalQuantity"]),
                "TotalAmount": round(float(r["TotalAmount"]),2),
                "ItemRate": round(float(r["ItemRate"]),2),
                "Group": r["Group"]
            })

            type_totals[emp][itype] += float(r["TotalAmount"])

        # ================================
        # 3️⃣ VOID COUNTS
        # ================================
        cursor.execute("""
            SELECT tt.Employee,
                   COUNT(td.idtblorderTracker_Details) AS void_count
            FROM tblorderTracker tt
            JOIN tblorderTracker_Details td 
                 ON tt.idtblorderTracker = td.orderTrackerID
            WHERE td.completedAt='VOID'
              AND tt.outlet_Name=%s
              AND tt.Date BETWEEN %s AND %s
              AND tt.Employee!=''
            GROUP BY tt.Employee
        """, (outlet, dateStart, dateEnd))

        void_map = {r["Employee"]: r["void_count"] for r in cursor.fetchall()}

        # ================================
        # 4️⃣ FINAL RESPONSE
        # ================================
        result = []

        for row in employee_rows:

            emp = row["Employee"]
            total_sales = float(row["netTotalSales"] or 0)
            dine = float(row["DineInSales"] or 0)
            take = float(row["TakeawaySales"] or 0)
            banq = float(row["BanquetSales"] or 0)
            guests = int(row["noOfGuests"] or 0)
            orders = int(row["TotalOrders"] or 0)

            items_sold = employee_items.get(emp, {"Food": [], "Beverage": [], "Other": []})
            types = type_totals.get(emp, {"Food":0,"Beverage":0,"Other":0})

            result.append({
                "Employee": emp,
                "Total_Sales": round(total_sales,2),
                "Complimentary_Sales": round(float(row["Complimentary_Sales"]),2),
                "Banquet_Sales": round(float(row["Banquet_Sales"]),2),
                "Discounts_Sales": round(float(row["Discounts_Sales"]),2),

                "Food_Sales": round(types["Food"],2),
                "Beverage_Sales": round(types["Beverage"],2),

                "noOfGuests": guests,
                "DineInSales": round(dine,2),
                "TakeawaySales": round(take,2),
                "BanquetSales": round(banq,2),

                "DineInSalesPercent": round((dine/total_sales)*100,2) if total_sales else 0,
                "TakeawaySalesPercent": round((take/total_sales)*100,2) if total_sales else 0,
                "BanquetSalesPercent": round((banq/total_sales)*100,2) if total_sales else 0,

                "avgSales": round(total_sales/orders,2) if orders else 0,
                "RevperGuest": round(total_sales/guests,2) if guests else 0,

                "Void_Order_Count": void_map.get(emp,0),
                "Items_Sold": items_sold
            })

        cursor.close()
        mydb.close()

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 400
