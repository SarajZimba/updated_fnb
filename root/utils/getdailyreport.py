from flask import Blueprint
import mysql.connector
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import pytz
load_dotenv()

def get_dailyreport(outlet):
    try:
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password'),
            database=os.getenv('database')
        )
        cursor = mydb.cursor(buffered=True)

        outlet_name = outlet
        start_Date = (datetime.today() - timedelta(days=530)).strftime('%Y-%m-%d')
        end_Date = datetime.today().strftime('%Y-%m-%d')
        #  Fetch all outlet names


        # outlet_sql = "SELECT * FROM tbldailysales"
        dailysales_sql = "SELECT date, sales FROM tblDailySales where `date` between %s and %s and outlet_name = %s order by `date`"
        cursor.execute(dailysales_sql, (start_Date, end_Date, outlet_name,))
        dailysales_reult = cursor.fetchall()
        stats_sql = """
            SELECT COALESCE(SUM(Total), 0) 
            FROM tblorderhistory 
            WHERE bill_no != '' 
            AND Date = %s and Outlet_Name = %s
        """
        cursor.execute(stats_sql, (end_Date, outlet_name,))
        total = cursor.fetchone()[0]

        # dailysales_reult.append(end_Date, total)
        dailysales_reult.append((end_Date, total))
        return dailysales_reult

    except Exception as e:
        print("Error extracting daily sales:", str(e))
        return {"error": str(e)}
    
# get_dailyreport("Feels, Jhamsikhel")
# save_dailyreport()
