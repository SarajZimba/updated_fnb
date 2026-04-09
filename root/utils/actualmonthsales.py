from flask import Blueprint
import mysql.connector
import os
from dotenv import load_dotenv
from datetime import datetime
import pytz
load_dotenv()

def get_actualmonthsales(outlet, posted_date):
    try:
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password'),
            database=os.getenv('database')
        )
        cursor = mydb.cursor(buffered=True)
        nepal_tz = pytz.timezone('Asia/Kathmandu')
        
        # Convert posted_date to datetime and extract the year and month
        posted_date_obj = datetime.strptime(posted_date, '%Y-%m-%d')
        year_month = posted_date_obj.strftime('%Y-%m')  # Format as 'YYYY-MM'

        # Modify the SQL query to calculate the sales for the month of posted_date
        stats_sql = """
            SELECT COALESCE(SUM(total), 0)
            FROM tblorderhistory 
            WHERE bill_no != '' 
            AND DATE_FORMAT(Date, '%Y-%m') = %s
            AND Outlet_Name = %s
        """
        cursor.execute(stats_sql, (year_month, outlet))
        sales_data = cursor.fetchone()  # fetchone since we only expect a single row result

        # The total sales value
        total_sales = sales_data[0] if sales_data else 0.0

        # Return the total sales in the desired format
        return {"total_sales": total_sales}
    
    except Exception as e:
        print("Error extracting monthly sales:", str(e))
        return {"error": str(e)}
