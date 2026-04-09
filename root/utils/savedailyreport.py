# from flask import Blueprint
# import mysql.connector
# import os
# from dotenv import load_dotenv
# from datetime import datetime, timedelta
# import pytz

# load_dotenv()
# from root.utils.getsaleforecastbydaterange_util import getsaleforecastBydaterangeutil
# import calendar
# def save_dailyreport():
#     try:
#         mydb = mysql.connector.connect(
#             host=os.getenv('host'),
#             user=os.getenv('user'),
#             password=os.getenv('password'),
#             database=os.getenv('database')
#         )
#         cursor = mydb.cursor(buffered=True)
#         nepal_tz = pytz.timezone('Asia/Kathmandu')
#         nepal_time = datetime.now(nepal_tz)
#         date_str = nepal_time.strftime('%Y-%m-%d')

#         yesterday_nepal_time = nepal_time - timedelta(days=1)  # Subtract 1 day
#         last_date_str = yesterday_nepal_time.strftime('%Y-%m-%d')

#         # Define time range (yesterday 2:01 AM to today 2:00 AM)
#         start_datetime = f"{last_date_str} 02:01 AM"
#         end_datetime = f"{date_str} 02:00 AM"
#         #  Fetch all outlet names
#         outlet_sql = "SELECT Outlet FROM outetNames"
#         cursor.execute(outlet_sql)
#         outlets = cursor.fetchall()

#         # Convert to a set for easy lookup
#         outlet_names = {row[0] for row in outlets}

#         # #  Fetch sales data for the day
#         # stats_sql = """
#         #     SELECT Outlet_Name, COALESCE(SUM(total), 0) 
#         #     FROM tblorderhistory 
#         #     WHERE bill_no != '' AND Date = %s
#         #     GROUP BY Outlet_Name
#         # """
#         # Fetch sales data for the custom time range
#         stats_sql = """
#             SELECT Outlet_Name, COALESCE(SUM(Total), 0) 
#             FROM tblorderhistory 
#             WHERE bill_no != '' 
#             AND STR_TO_DATE(CONCAT(Date, ' ', Start_Time), '%Y-%m-%d %h:%i %p') 
#             BETWEEN STR_TO_DATE(%s, '%Y-%m-%d %h:%i %p') 
#             AND STR_TO_DATE(%s, '%Y-%m-%d %h:%i %p') 
#             GROUP BY Outlet_Name;
#         """
#         # cursor.execute(stats_sql, (date_str,))
#         cursor.execute(stats_sql, (start_datetime, end_datetime))
#         sales_data = cursor.fetchall()

#         # Convert sales data to a dictionary
#         sales_dict = {row[0]: row[1] for row in sales_data}

#         #  Ensure all outlets have an entry in tblDailySales
#         for outlet in outlet_names:
#             total_sales = sales_dict.get(outlet, 0)  # Default to 0 if no sales found

#             # Insert or update tblDailySales
#             insert_sql = """
#                 INSERT INTO tblDailySales (date, outlet_name, sales)
#                 VALUES (%s, %s, %s)
#             """
#             cursor.execute(insert_sql, (last_date_str, outlet, total_sales))

#             now = datetime.now()
#             yhat = 0.0
#             # Determine the first and last day of the current month
#             dateStart = now.replace(day=1).strftime('%Y-%m-%d')
#             last_day = calendar.monthrange(now.year, now.month)[1]  # Get last day of the month
#             dateEnd = now.replace(day=last_day).strftime('%Y-%m-%d')

#             results, special_date_data = getsaleforecastBydaterangeutil(outlet, dateStart, dateEnd)

#             # Convert JSON results into Python objects
#             data = results

#             # for month in json.loads(all_monthly_prediction):  # Convert JSON string to a Python list
#             #     if month["ds"] == today_formatted:
#             #         yhat = month["yhat"]
#             #         break
#             for datum in data:
#                 yhat += datum["yhat"]

#             # Insert or update tblDailySales
#             insert_sql = """
#                 INSERT INTO trackmonthlyforecast (date, monthlyforecast, outlet)
#                 VALUES (%s, %s, %s)
#             """
#             cursor.execute(insert_sql, (last_date_str, yhat, outlet,))

#         # Commit changes and close connection
#         mydb.commit()
#         mydb.close()
        
#         print("Daily sales report saved successfully!")

#     except Exception as e:
#         print("Error extracting daily sales:", str(e))
#         return {"error": str(e)}