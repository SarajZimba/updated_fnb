# import os
# os.environ["OPENBLAS_NUM_THREADS"] = "1"

# from datetime import datetime
# import pandas as pd
# from prophet import Prophet
# import json
# from .getdailyreport import get_dailyreport

# from prophet import Prophet
# import pandas as pd
# import json
# from root.utils.getconfidencelevel import getconfidencelevel

# def  get_monthly_prediction(outlet_name, posted_date):
#     # Fetch daily sales data
#     print(f"{posted_date} posted_date")
#     dailysales_result = get_dailyreport(outlet_name)  # Assuming this function fetches the daily sales data
#     df = pd.DataFrame(dailysales_result, columns=['date', 'sales'])

#     # Convert 'date' column to datetime format
#     df['date'] = pd.to_datetime(df['date'])

#     # Aggregate sales data by month
#     df['month'] = df['date'].dt.to_period('M')  # Convert to year-month period
#     df_monthly = df.groupby('month').agg({'sales': 'sum'}).reset_index()
    
#     # Convert 'month' back to datetime format for Prophet
#     df_monthly['month'] = df_monthly['month'].dt.to_timestamp()

#     # Get the current month (excluding the current month from data)
#     current_month = pd.to_datetime(datetime.now()).to_period('M')

#     # # Filter out the current month data
#     # df_monthly = df_monthly[df_monthly['month'] != current_month]
    
#     # Prepare data for Prophet
#     df_prophet = df_monthly.rename(columns={'month': 'ds', 'sales': 'y'})
#     confidencelevel = getconfidencelevel(outlet_name)

#     # Fit the Prophet model
#     model = Prophet(interval_width=confidencelevel)
#     model.fit(df_prophet)

#     # Convert posted_date to datetime format and extract the first day of that month
#     posted_date = pd.to_datetime(posted_date)
#     posted_month = posted_date.replace(day=1)

#     # Generate a date range (6 months before and 6 months after posted_date)
#     prediction_dates = pd.date_range(start=posted_month - pd.DateOffset(months=6),
#                                      end=posted_month + pd.DateOffset(months=6),
#                                      freq='MS')  # 'MS' means Month Start

#     # Create a DataFrame with these dates
#     future = pd.DataFrame({'ds': prediction_dates})

#     # Make predictions for the date range
#     forecast = model.predict(future)

#     # Extract relevant forecast data
#     forecast_data = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()

#     # Round predictions to avoid too many decimal places
#     forecast_data['yhat'] = forecast_data['yhat'].round(2)
#     forecast_data['yhat_lower'] = forecast_data['yhat_lower'].round(2)
#     forecast_data['yhat_upper'] = forecast_data['yhat_upper'].round(2)

#     # Convert 'ds' to a string formatted as YYYY-MM
#     forecast_data['ds'] = forecast_data['ds'].dt.strftime('%Y-%m')

#     # Convert the DataFrame to a list of dicts
#     forecast_data_dict = forecast_data.to_dict(orient='records')

#     # Return the data in JSON format
#     return json.dumps(forecast_data_dict, indent=4)


# # def get_current_month_prediction(outlet_name):
# #     full_date = datetime.now().strftime('%Y-%m-%d')
# #     all_monthly_prediction = get_monthly_prediction(outlet_name, full_date)
# #     today_formatted = datetime.now().strftime('%Y-%m')
# #     yhat = 0.0

# #     for month in json.loads(all_monthly_prediction):  # Convert JSON string to a Python list
# #         if month["ds"] == today_formatted:
# #             yhat = month["yhat"]
# #             break

# #     month_data = {
# #             "yhat": yhat,
# #             "ds": today_formatted
# #         }
    

# #     return json.dumps(month_data, indent=4)  # Convert list to JSON string

# # from root.utils.getsaleforecastbydaterange_util import getsaleforecastBydaterangeutil
# # from datetime import datetime, timedelta
# # import calendar
# # def get_current_month_prediction(outlet_name):

# #     now = datetime.now()
# #     # full_date = datetime.now().strftime('%Y-%m-%d')
# #     # all_monthly_prediction = get_monthly_prediction(outlet_name, full_date)
# #     today_formatted = datetime.now().strftime('%Y-%m')
# #     yhat = 0.0
# #     # Determine the first and last day of the current month
# #     dateStart = now.replace(day=1).strftime('%Y-%m-%d')
# #     last_day = calendar.monthrange(now.year, now.month)[1]  # Get last day of the month
# #     dateEnd = now.replace(day=last_day).strftime('%Y-%m-%d')

# #     results = get_prediction_daterange(outlet_name, dateStart, dateEnd)

# #     # Convert JSON results into Python objects
# #     data = json.loads(results)

# #     # for month in json.loads(all_monthly_prediction):  # Convert JSON string to a Python list
# #     #     if month["ds"] == today_formatted:
# #     #         yhat = month["yhat"]
# #     #         break
# #     for datum in data:
# #         yhat += datum["yhat"]




# #     month_data = {
# #             "yhat": yhat,
# #             "ds": today_formatted
# #         }
    

# #     return json.dumps(month_data, indent=4)  # Convert list to JSON string

# from root.utils.getsaleforecastbydaterange_util import getsaleforecastBydaterangeutil
# from datetime import datetime, timedelta
# import calendar
# def get_current_month_prediction(outlet_name):

#     now = datetime.now()
#     # full_date = datetime.now().strftime('%Y-%m-%d')
#     # all_monthly_prediction = get_monthly_prediction(outlet_name, full_date)
#     today_formatted = datetime.now().strftime('%Y-%m')
#     yhat = 0.0
#     # Determine the first and last day of the current month
#     dateStart = now.replace(day=1).strftime('%Y-%m-%d')
#     last_day = calendar.monthrange(now.year, now.month)[1]  # Get last day of the month
#     dateEnd = now.replace(day=last_day).strftime('%Y-%m-%d')

#     results, special_date_data = getsaleforecastBydaterangeutil(outlet_name, dateStart, dateEnd)

#     # Convert JSON results into Python objects
#     data = results

#     for datum in data:
#         yhat += datum["yhat"]

#     # yesterday = datetime.now() - timedelta(days=1)

#     # # Format it as 'YYYY-MM-DD'
#     # yesterday_formatted = yesterday.strftime('%Y-%m-%d')

#     # yesterday_monthlysaleforeacst = get_yesterday_monthlyforecast(yesterday_formatted)

#     # month_data = {
#     #         "yhat": yhat,
#     #         "ds": today_formatted,
#     #         "yesterday_monthlyforecast" : yesterday_monthlysaleforeacst
#     #     }
    

#     # return json.dumps(month_data, indent=4)  # Convert list to JSON string

#     yesterday = datetime.now() - timedelta(days=1)

#     # Format it as 'YYYY-MM-DD'
#     yesterday_formatted = yesterday.strftime('%Y-%m-%d')

#     yesterday_monthlysaleforeacast = get_yesterday_monthlyforecast(yesterday_formatted, outlet_name)

#     previousweek_date = datetime.now() - timedelta(days=7)


#     # Format it as 'YYYY-MM-DD'
#     oneweek_formatted = previousweek_date.strftime('%Y-%m-%d')

#     oneweek_monthlysaleforeacast = get_yesterday_monthlyforecast(oneweek_formatted, outlet_name)

#     # Get the first day of the current month
#     first_day_of_current_month = datetime.now().replace(day=1)

#     # Format it as 'YYYY-MM-DD'
#     firsatday_of_current_month_formatted = first_day_of_current_month.strftime('%Y-%m-%d')

#     firstday_monthlysaleforeacast = get_yesterday_monthlyforecast(firsatday_of_current_month_formatted, outlet_name)

#     month_data = {
#             "yhat": yhat,
#             "ds": today_formatted,
#             "yesterday_monthlyforecast" :{
#                 "date": yesterday_formatted,
#                 "value" : yesterday_monthlysaleforeacast
#             },
#             "oneweek_monthlyforecast" : {
#                 "date" : oneweek_formatted,
#                 "value" : oneweek_monthlysaleforeacast
#             },
#             "firstday_of_monthlyforecast": {
#                 "date" : firsatday_of_current_month_formatted,
#                 "value" : firstday_monthlysaleforeacast

#             }
#         }
    

#     return json.dumps(month_data, indent=4)  # Convert list to JSON string

# import mysql.connector
# import os
# def get_yesterday_monthlyforecast(yesterday_formatted, outlet_name):

#     mydb = mysql.connector.connect(host=os.getenv('host'), user=os.getenv('user'), password=os.getenv('password'))
#     cursor = mydb.cursor(buffered=True)
#     database_sql = "USE {};".format(os.getenv('database'))
#     cursor.execute(database_sql)

#     # SQL Query: Get monthlyforecast for yesterday, default to 0 if no data
#     query = """
#         SELECT IFNULL((monthlyforecast), 0) 
#         FROM trackmonthlyforecast 
#         WHERE date = %s and outlet = %s
#     """
    
#     cursor.execute(query, (yesterday_formatted,outlet_name,))
#     result = cursor.fetchone()
#     monthly_forecast = result[0] if result else 0

#     return float(monthly_forecast)