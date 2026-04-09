from flask import Flask, Blueprint, request, jsonify
import mysql.connector
from flask_cors import cross_origin
from dotenv import load_dotenv
import os
from root.auth.check import token_auth
from datetime import datetime, timedelta
from calendar import monthrange
load_dotenv()

app_file54 = Blueprint('app_file54', __name__)

@app_file54.route('/salesvspurchase', methods=["POST"])
@cross_origin()
def get_sales_and_purchases():
    try:
        # Connect to the database
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            password=os.getenv('password'),
            user=os.getenv('user'),
            database=os.getenv('database')
        )
        cursor = mydb.cursor(buffered=True)

        # Get request JSON
        json_data = request.get_json()

        if "token" not in json_data or json_data["token"] == "":
            return jsonify({"error": "Please provide token"}), 400
        
        if "outlet" not in json_data or json_data["outlet"] == "":
            return jsonify({"error": "Please provide outlet"}), 400
        outlet = json_data["outlet"]
        token = json_data["token"]
        if not token_auth(token):
            return jsonify({"error": "Invalid token provided"}), 400

        # Define all months
        all_months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]

        # Calculate the start and end dates for one year range
        end_date = datetime.now().date()  # Today's date
        start_date = end_date - timedelta(days=366)  # Date one year before



        # Generate a list of months in the desired range
        def get_month_year_range(start_date, end_date):
            months = []
            current_date = start_date.replace(day=1)  # Start from the first day of the month
            while current_date <= end_date:
                months.append(f"{all_months[current_date.month - 1]} {current_date.year}")
                # Move to the first day of the next month
                if current_date.month == 12:  # December
                    current_date = current_date.replace(year=current_date.year + 1, month=1, day=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1, day=1)
            return months

        # Get the range of months
        month_year_range = get_month_year_range(start_date, end_date)

        # Initialize dictionaries for sales and purchases with the correct range
        sales_data = {
            month_year: {"Total": "0.0", "monthName": month_year}
            for month_year in month_year_range
        }

        purchases_data = {
            month_year: {"Total": "0.0", "monthName": month_year}
            for month_year in month_year_range
        }

        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")

        # Example SQL queries to fetch data (replace with actual database execution)
        sql_query_sales = """
            SELECT 
                YEAR(Date) AS year,
                MONTH(Date) AS month, 
                SUM(Total - VAT) AS totalSales 
            FROM tblorderhistory 
            WHERE Date BETWEEN %s AND %s and Outlet_Name = %s and bill_no != ''
            GROUP BY YEAR(Date), MONTH(Date)
        """
        cursor.execute(sql_query_sales, (start_date_str, end_date_str, outlet,))
        sales_results = cursor.fetchall()

        sql_query_purchases = """
            SELECT 
                YEAR(Date) AS year,
                MONTH(Date) AS month, 
                SUM(TotalAmount) AS totalPurchases 
            FROM intbl_purchaserequisition 
            WHERE Date BETWEEN %s AND %s and Outlet_Name = %s
            GROUP BY YEAR(Date), MONTH(Date)
        """
        cursor.execute(sql_query_purchases, (start_date_str, end_date_str, outlet,))
        purchases_results = cursor.fetchall()

        # Populate sales data
        for year, month, totalSales in sales_results:
            month_name = f"{all_months[month - 1]} {year}"  # Combine month and year
            if month_name in sales_data:
                sales_data[month_name] = {"Total": str(totalSales), "monthName": month_name}

        # Populate purchases data
        for year, month, totalPurchases in purchases_results:
            month_name = f"{all_months[month - 1]} {year}"  # Combine month and year
            if month_name in purchases_data:
                purchases_data[month_name] = {"Total": str(totalPurchases), "monthName": month_name}

        # Convert dictionaries to lists
        sales_json = list(sales_data.values())
        purchases_json = list(purchases_data.values())

        toppurchasingvendorsbyvolumesql_query = """select Company_Name, sum(TotalAmount) as TotalAmount , sum(TotalAmount - TaxAmount) as NetAmount from intbl_purchaserequisition where Outlet_Name=%s group by Company_Name order by TotalAmount DESC """ 

        cursor.execute(toppurchasingvendorsbyvolumesql_query, (outlet,))

        columns = [col[0] for col in cursor.description]

        toppurchasingvendorsbyvolume_responseJson = [dict(zip(columns, rows)) for rows in cursor.fetchall()]


        toppurchasingvendorsbycountsql_query = """select Company_Name, count(idintbl_purchaserequisition) as purchaseCount from intbl_purchaserequisition where Outlet_Name=%s group by Company_Name order by count(idintbl_purchaserequisition) DESC""" 

        cursor.execute(toppurchasingvendorsbycountsql_query, (outlet,))

        columns = [col[0] for col in cursor.description]

        toppurchasingvendorsbycount_responseJson = [dict(zip(columns, rows)) for rows in cursor.fetchall()]

        purchaseitembycount_sql_query = """SELECT  a.Name ,count(a.IDIntbl_PurchaseRequisition_Contract) as purchase_count from intbl_purchaserequisition_contract a, intbl_purchaserequisition b where a.PurchaseReqID = b.IDIntbl_PurchaseRequisition and Outlet_Name=%s group by a.Name order by purchase_count DESC  """ 

        cursor.execute(purchaseitembycount_sql_query, (outlet,))

        columns = [col[0] for col in cursor.description]

        purchaseitembycount_responseJson = [dict(zip(columns, rows)) for rows in cursor.fetchall()]


        purchaseitembyvolume_sql_query = """SELECT  a.Name ,sum(a.UnitsOrdered * a.Rate) as purchase_total from intbl_purchaserequisition_contract a, intbl_purchaserequisition b where a.PurchaseReqID = b.IDIntbl_PurchaseRequisition and Outlet_Name=%s group by a.Name order by purchase_total DESC  """ 

        cursor.execute(purchaseitembyvolume_sql_query, (outlet,))

        # columns = [col[0] for col in cursor.description]

        # purchaseitembyvolume_responseJson = [dict(zip(columns, rows)) for rows in cursor.fetchall()]

        purchaseitembyvolume_responseJson = []
        for rows in cursor.fetchall():
            purchaseitembyvolume_data = {
            "Name": rows[0],
            "purchase_total": round(float(rows[1]), 2)
            }

            purchaseitembyvolume_responseJson.append(purchaseitembyvolume_data)

        # Final response
        response = {
            "monthlySales": sales_json,
            "monthlyPurchases": purchases_json,
            "toppurchasingvendors_byvolume": toppurchasingvendorsbyvolume_responseJson,
            "toppurchasingvendors_bycount":toppurchasingvendorsbycount_responseJson,
            "purchaseitembycount_responseJson": purchaseitembycount_responseJson,
            "purchaseitembyvolume_responseJson": purchaseitembyvolume_responseJson,

        }

        return jsonify(response), 200

    except mysql.connector.Error as db_error:
        mydb.rollback()  # Rollback on error
        return jsonify({"error": f"Database error: {str(db_error)}"}), 500
    except Exception as e:
        mydb.rollback()  # Rollback on unexpected error
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
    finally:
        if mydb:
            mydb.close()

