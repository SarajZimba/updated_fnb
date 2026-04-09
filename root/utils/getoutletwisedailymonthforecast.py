import mysql.connector
import os
from dotenv import load_dotenv
import json
from datetime import datetime, timedelta

from root.utils.monthlysalesforecast import get_current_month_prediction

load_dotenv()

def getmonthlysaleForecastdatewise():
    try:
        mydb = mysql.connector.connect(
            user=os.getenv('user'), 
            password=os.getenv('password'), 
            host=os.getenv('host'),
            database=os.getenv('database')
        )
        cursor = mydb.cursor(dictionary=True)

        # Get today's date
        today_date = datetime.today().date()
        start_date = today_date - timedelta(weeks=2)  # 2 weeks from today
        print(start_date)
        print(today_date)
        # Fetch all outlets
        cursor.execute("SELECT Outlet FROM outetNames")
        outlets = cursor.fetchall()

        if not outlets:
            return {"error": "No outlets found"}, 404
        
        # Generate the full list of dates within the range
        date_list = [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(15)]  # 14 days + today


        # Prepare forecast data for each outlet
        forecast_data = {}

        for outlet in outlets:
            outlet_name = outlet["Outlet"]

            # Fetch forecast data for the next 2 weeks from today
            query = """
                SELECT date, monthlyforecast 
                FROM trackmonthlyforecast 
                WHERE date BETWEEN %s AND %s and outlet = %s
                ORDER BY date ASC
            """
            cursor.execute(query, (start_date, today_date, outlet_name,))
            forecast_results = {row["date"].strftime("%Y-%m-%d"): float(row["monthlyforecast"]) for row in cursor.fetchall()}

            current_month_prediction = get_current_month_prediction(outlet_name)
            # If the function returns a JSON string, convert it to a dictionary
            if isinstance(current_month_prediction, str):
                current_month_prediction = json.loads(current_month_prediction)
            current_day_value = current_month_prediction["yhat"]
            print(current_day_value)
            # Fill missing dates with 0
            forecast_data[outlet_name] = [
                {"date": date, "monthlyforecast": forecast_results.get(date, current_day_value if date == today_date.strftime("%Y-%m-%d") else 0.0)} for date in date_list
                # {"date": date, "monthlyforecast": forecast_results.get(date, 0.0)} for date in date_list
            ]


            # forecast_data[outlet_name] = forecast_results

        return {"forecast": forecast_data}

    except Exception as e:
        return {"error": str(e)}, 500

    finally:
        if mydb.is_connected():
            cursor.close()
            mydb.close()