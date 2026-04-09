# import os
# os.environ["OPENBLAS_NUM_THREADS"] = "1"
# import pandas as pd
# from prophet import Prophet
# import matplotlib.pyplot as plt
# from datetime import datetime, timedelta
# from decimal import Decimal
# from root.utils.getdailyreport import get_dailyreport
# import json
# from root.utils.getconfidencelevel import getconfidencelevel

# def get_prediction(outlet_name, posted_date):
#     # Fetch daily sales data
#     print(f"{posted_date} posted_date")
#     dailysales_result = get_dailyreport(outlet_name)  # Assuming this function fetches the daily sales data
#     df = pd.DataFrame(dailysales_result, columns=['date', 'sales'])

#     # Convert the 'Date' column to datetime format
#     df['date'] = pd.to_datetime(df['date'])

#     # Prepare the data for Prophet
#     df_prophet = df.rename(columns={'date': 'ds', 'sales': 'y'})

#     # Ensure 'ds' is datetime and 'y' is numeric
#     df_prophet['ds'] = pd.to_datetime(df_prophet['ds'])
#     df_prophet['y'] = pd.to_numeric(df_prophet['y'], errors='coerce')

#     # Drop rows with NaN values in 'y' (if any)
#     df_prophet = df_prophet.dropna(subset=['y'])

#     confidencelevel = getconfidencelevel(outlet_name)

#     # Fit the Prophet model
#     model = Prophet(interval_width=confidencelevel)
#     model.fit(df_prophet)

#     # Convert posted_date to datetime format
#     posted_date = pd.to_datetime(posted_date)

#     # Generate a date range (7 days before and 7 days after posted_date)
#     prediction_dates = pd.date_range(start=posted_date - pd.Timedelta(days=7), 
#                                      end=posted_date + pd.Timedelta(days=7), 
#                                      freq='D')

#     # Create a DataFrame with these dates
#     future = pd.DataFrame({'ds': prediction_dates})

#     # Make predictions for the date range
#     forecast = model.predict(future)

#     # Extract relevant forecast data
#     forecast_data = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()

#     # Round the predictions to avoid too many decimal places
#     forecast_data['yhat'] = forecast_data['yhat'].round(2)
#     forecast_data['yhat_lower'] = forecast_data['yhat_lower'].round(2)
#     forecast_data['yhat_upper'] = forecast_data['yhat_upper'].round(2)

#     # Convert the 'ds' column to string (formatted as YYYY-MM-DD)
#     forecast_data['ds'] = forecast_data['ds'].dt.strftime('%Y-%m-%d')

#     # Convert the DataFrame to a list of dicts
#     forecast_data_dict = forecast_data.to_dict(orient='records')

#     # Return the data in JSON format
#     data = json.dumps(forecast_data_dict, indent=4)
#     return data


# import pandas as pd
# from prophet import Prophet
# from datetime import datetime
# from root.utils.getdailyreport import get_dailyreport
# import json
# from root.utils.getconfidencelevel import getconfidencelevel

# def get_today_prediction(outlet_name):
#     # Fetch daily sales data
#     dailysales_result = get_dailyreport(outlet_name)  
#     df = pd.DataFrame(dailysales_result, columns=['date', 'sales'])

#     # Convert the 'date' column to datetime format
#     df['date'] = pd.to_datetime(df['date'])

#     # Prepare the data for Prophet
#     df_prophet = df.rename(columns={'date': 'ds', 'sales': 'y'})

#     # Ensure 'ds' is datetime and 'y' is numeric
#     df_prophet['ds'] = pd.to_datetime(df_prophet['ds'])
#     df_prophet['y'] = pd.to_numeric(df_prophet['y'], errors='coerce')

#     # Drop rows with NaN values in 'y' (if any)
#     df_prophet = df_prophet.dropna(subset=['y'])

#     confidencelevel = getconfidencelevel(outlet_name)

#     # Fit the Prophet model
#     model = Prophet(interval_width=confidencelevel)
#     model.fit(df_prophet)

#     # Generate a DataFrame with today's date
#     today_date = datetime.today().strftime('%Y-%m-%d')
#     future = pd.DataFrame({'ds': [today_date]})

#     # Make the prediction
#     forecast = model.predict(future)

#     # Extract relevant forecast data
#     forecast_data = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()

#     # Round the predictions to avoid too many decimal places
#     forecast_data['yhat'] = forecast_data['yhat'].round(2)
#     forecast_data['yhat_lower'] = forecast_data['yhat_lower'].round(2)
#     forecast_data['yhat_upper'] = forecast_data['yhat_upper'].round(2)

#     # Convert 'ds' to string format
#     forecast_data['ds'] = forecast_data['ds'].dt.strftime('%Y-%m-%d')

#     # Convert to JSON format
#     forecast_data_dict = forecast_data.to_dict(orient='records')
#     return json.dumps(forecast_data_dict, indent=4)


# def get_prediction_daterange(outlet_name, posted_date_start, posted_date_end):
#     # Fetch daily sales data
#     dailysales_result = get_dailyreport(outlet_name)  # Assuming this function fetches the daily sales data
#     df = pd.DataFrame(dailysales_result, columns=['date', 'sales'])

#     # Convert the 'Date' column to datetime format
#     df['date'] = pd.to_datetime(df['date'])

#     # Prepare the data for Prophet
#     df_prophet = df.rename(columns={'date': 'ds', 'sales': 'y'})

#     # Ensure 'ds' is datetime and 'y' is numeric
#     df_prophet['ds'] = pd.to_datetime(df_prophet['ds'])
#     df_prophet['y'] = pd.to_numeric(df_prophet['y'], errors='coerce')

#     # Drop rows with NaN values in 'y' (if any)
#     df_prophet = df_prophet.dropna(subset=['y'])


#     confidencelevel = getconfidencelevel(outlet_name)

#     # Fit the Prophet model
#     model = Prophet(interval_width=confidencelevel)
#     model.fit(df_prophet)

#     # Convert posted_date to datetime format
#     # posted_date = pd.to_datetime(posted_date)
#     posted_date_start = pd.to_datetime(posted_date_start)
#     posted_date_end = pd.to_datetime(posted_date_end)

#     # Generate a date range (7 days before and 7 days after posted_date)
#     prediction_dates = pd.date_range(start=posted_date_start, 
#                                      end=posted_date_end, 
#                                      freq='D')

#     # Create a DataFrame with these dates
#     future = pd.DataFrame({'ds': prediction_dates})

#     # Make predictions for the date range
#     forecast = model.predict(future)

#     # Extract relevant forecast data
#     forecast_data = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()

#     # Round the predictions to avoid too many decimal places
#     forecast_data['yhat'] = forecast_data['yhat'].round(2)
#     forecast_data['yhat_lower'] = forecast_data['yhat_lower'].round(2)
#     forecast_data['yhat_upper'] = forecast_data['yhat_upper'].round(2)

#     # Convert the 'ds' column to string (formatted as YYYY-MM-DD)
#     forecast_data['ds'] = forecast_data['ds'].dt.strftime('%Y-%m-%d')

#     # Convert the DataFrame to a list of dicts
#     forecast_data_dict = forecast_data.to_dict(orient='records')

#     # Return the data in JSON format
#     data = json.dumps(forecast_data_dict, indent=4)
#     return data