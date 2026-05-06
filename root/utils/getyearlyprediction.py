import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"

from prophet import Prophet
import pandas as pd
import json
from .getdailyreport import get_dailyreport
from root.utils.getconfidencelevel import getconfidencelevel
from datetime import datetime

def get_yearly_prediction(outlet_name):
    # Fetch daily sales data
    dailysales_result = get_dailyreport(outlet_name)  # Assuming this function fetches the daily sales data
    df = pd.DataFrame(dailysales_result, columns=['date', 'sales'])

    # Convert 'date' column to datetime format
    df['date'] = pd.to_datetime(df['date'])

    # Aggregate sales data by month
    df['month'] = df['date'].dt.to_period('M')  # Convert to year-month period
    df_monthly = df.groupby('month').agg({'sales': 'sum'}).reset_index()

    # Convert 'month' back to datetime format for Prophet
    df_monthly['month'] = df_monthly['month'].dt.to_timestamp()

    # Prepare data for Prophet
    df_prophet = df_monthly.rename(columns={'month': 'ds', 'sales': 'y'})

    # Fit the Prophet model
    confidencelevel = getconfidencelevel(outlet_name)
    model = Prophet(interval_width=confidencelevel)
    model.fit(df_prophet)

    # Get today's date
    today_date = datetime.today()

    # Get the current year from today's date
    current_year = today_date.year

    # Generate a date range for the entire current year (Jan 1st - Dec 31st)
    prediction_dates = pd.date_range(start=f"{current_year}-01-01", end=f"{current_year}-12-31", freq='MS')  # Monthly frequency for the entire year

    # Create a DataFrame with these dates
    future = pd.DataFrame({'ds': prediction_dates})

    # Make predictions for the entire current year (monthly predictions)
    forecast = model.predict(future)

    # Extract relevant forecast data
    forecast_data = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()

    # Round predictions to avoid too many decimal places
    forecast_data['yhat'] = forecast_data['yhat'].round(2)
    forecast_data['yhat_lower'] = forecast_data['yhat_lower'].round(2)
    forecast_data['yhat_upper'] = forecast_data['yhat_upper'].round(2)

    # Get the total prediction for the current year (sum of all monthly predictions)
    yearly_prediction = forecast_data['yhat'].sum()
    yearly_lower = forecast_data['yhat_lower'].sum()
    yearly_upper = forecast_data['yhat_upper'].sum()

    # Prepare a single block of data for the entire year prediction
    prediction_block = {
        'year': current_year,
        'yhat': round(yearly_prediction, 2),
        'yhat_lower': round(yearly_lower, 2),
        'yhat_upper': round(yearly_upper, 2)
    }

    # Return the data as JSON
    return json.dumps(prediction_block, indent=4)
