from pytz import timezone
import mysql.connector
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# import locale

# # Set the locale for Indian or Nepali currency formatting
# locale.setlocale(locale.LC_ALL, 'en_IN.UTF-8')  # For Indian locale

# Load environment variables
load_dotenv()

nepal_tz = timezone('Asia/Kathmandu')

def monthly_report():
    try:
        # Connect to MySQL
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password'),
            database=os.getenv('database')
        )
        cursor = mydb.cursor(dictionary=True)  # Fetch results as dictionaries

        # # Get current date and calculate the last 3 months (including this month)
        # today = datetime.now().date()
        # first_day_this_month = today.replace(day=1)
        # first_day_two_months_ago = (first_day_this_month - timedelta(days=1)).replace(day=1)
        # first_day_three_months_ago = (first_day_two_months_ago - timedelta(days=1)).replace(day=1)

        # today_date = today.strftime("%Y-%m-%d")
        # first_day_three_months_ago_date = first_day_three_months_ago.strftime("%Y-%m-%d")

        # Get current date
        today = datetime.now().date()

        # Get the first day of the current month
        first_day_this_month = today.replace(day=1)
        # Get the first day of the last three full months
        first_day_last_month = (first_day_this_month - timedelta(days=1)).replace(day=1)  # Previous month
        first_day_two_months_ago = (first_day_last_month - timedelta(days=1)).replace(day=1)  # 2 months ago
        first_day_three_months_ago = (first_day_two_months_ago - timedelta(days=1)).replace(day=1)  # 3 months ago

        # Convert to string format
        today_date = first_day_this_month.strftime("%Y-%m-%d")  # Start date (first day of current month)
        first_day_three_months_ago_date = first_day_three_months_ago.strftime("%Y-%m-%d")  # 3 months ago

        stats_sql = """
            SELECT 
                DATE_FORMAT(Date, '%Y %b') AS Month,
                Outlet_Name,

                -- Total sales (excluding invalid bill_no)
                SUM(CASE WHEN bill_no != '' THEN Total ELSE 0 END) AS TotalSales,

                -- Dine-In sales
                SUM(CASE WHEN bill_no != '' AND Type = 'Dine-In' THEN Total ELSE 0 END) AS DineInSales,

                -- Tab sales
                SUM(CASE WHEN bill_no != '' AND Type = 'Tab' THEN Total ELSE 0 END) AS TabSales,

                -- Net total sales (excluding invalid bill_no)
                SUM(CASE WHEN bill_no != '' THEN Total - VAT - serviceCharge ELSE 0 END) AS NetTotalSales,

                -- Net Dine-In sales
                SUM(CASE WHEN bill_no != '' AND Type = 'Dine-In' THEN Total - VAT - serviceCharge ELSE 0 END) AS NetDineInSales,

                -- Net Tab sales
                SUM(CASE WHEN bill_no != '' AND Type = 'Tab' THEN Total - VAT - serviceCharge ELSE 0 END) AS NetTabSales,

                -- Total VAT (excluding invalid bill_no)
                SUM(CASE WHEN bill_no != '' THEN VAT ELSE 0 END) AS TotalVat,

                -- Total guests (excluding invalid bill_no)
                SUM(CASE WHEN bill_no != '' THEN NoOfGuests ELSE 0 END) AS TotalGuests,

                -- Disount (excluding invalid bill_no)
                SUM(CASE WHEN bill_no != '' THEN DiscountAmt ELSE 0 END) AS Discount,



                -- Payment Modes (Include all orders, including bill_no = '')
                SUM(CASE WHEN PaymentMode = 'Cash' THEN Total ELSE 0 END) AS Cash,
                SUM(CASE WHEN PaymentMode = 'Credit Card' THEN Total ELSE 0 END) AS CreditCard,
                SUM(CASE WHEN PaymentMode = 'Mobile Payment' THEN Total ELSE 0 END) AS MobilePayment,
                SUM(CASE WHEN PaymentMode = 'Complimentary' THEN Total ELSE 0 END) AS Complimentary,
                SUM(CASE WHEN PaymentMode = 'Non Chargeable' THEN Total ELSE 0 END) AS NonChargeable,
                SUM(CASE WHEN PaymentMode = 'Split' THEN Total ELSE 0 END) AS Split,
                SUM(CASE WHEN PaymentMode = 'Credit' THEN Total ELSE 0 END) AS Credit,

                -- Start and End Bill numbers (converted to integers)
                MIN(CASE WHEN bill_no != '' THEN CAST(bill_no AS UNSIGNED) ELSE NULL END) AS StartBill,
                MAX(CASE WHEN bill_no != '' THEN CAST(bill_no AS UNSIGNED) ELSE NULL END) AS EndBill

            FROM tblorderhistory

            -- Get the last three months (including current month) using calculated date range
            WHERE Date >= %s AND Date < %s

            GROUP BY Month, Outlet_Name
            ORDER BY Month DESC, Outlet_Name;
        """

        cursor.execute(stats_sql, (first_day_three_months_ago_date, today_date,))
        stats_results = cursor.fetchall()

        if not stats_results:
            print("No sales data found for the last three months.")
            return

        print(stats_results)
        # Extract distinct months and outlet names
        months_set = set(row['Month'] for row in stats_results)
        months = sorted(months_set, key=lambda x: datetime.strptime(x, "%Y %b"))
        print(f"months {months}")
        outlets = sorted(set(row['Outlet_Name'] for row in stats_results))

        # Initialize data structure for each outlet
        outlet_data = {outlet: {month: {
            "Total Sales": 0,
            "Net Sales": 0,
            "Vat": 0,
            "DineIn Sales": 0,
            "Tab Sales": 0,
            "Net DineIn Sales": 0,
            "Net Tab Sales": 0,
            "Total Guests": 0,
            "Rev. Per Guest": 0,
            "Discount": 0,
            "Cash": 0,
            "Credit": 0,
            "Credit Card": 0,
            "Mobile Payment": 0,
            "Complimentary": 0,
            "Non Chargeable": 0,
            "Split": 0,
            "Start Bill": 0,
            "End Bill": 0,
        } for month in months} for outlet in outlets}

        # Populate the outlet_data dictionary
        for row in stats_results:
            outlet = row['Outlet_Name']
            month = row['Month']
            outlet_data[outlet][month] = {
                "Total Sales": f"{row['TotalSales']:,.2f}",
                "Net Sales": f"{row['NetTotalSales']:,.2f}",
                "Vat": f"{row['TotalVat']:,.2f}",
                "DineIn Sales": f"{row['DineInSales']:,.2f}",
                "Tab Sales": f"{row['TabSales']:,.2f}",
                "Net DineIn Sales": f"{row['NetDineInSales']:,.2f}",
                "Net Tab Sales": f"{row['NetTabSales']:,.2f}",
                "Total Guests": f"{row['TotalGuests']:,}",
                "Rev. Per Guest": f"{row['NetTotalSales']/row['TotalGuests']:,.2f}",
                "Discount": f"{row['Discount']:,.2f}",
                "Cash": f"{row['Cash']:,.2f}",
                "Credit": f"{row['Credit']:,.2f}",
                "Credit Card": f"{row['CreditCard']:,.2f}",
                "Mobile Payment": f"{row['MobilePayment']:,.2f}",
                "Complimentary": f"{row['Complimentary']:,.2f}",
                "Non Chargeable": f"{row['NonChargeable']:,.2f}",
                "Split": f"{row['Split']:,.2f}",
                "Start Bill": row['StartBill'],
                "End Bill": row['EndBill'],
                # "TotalSales": locale.format_string("%0.2f", row['TotalSales'], grouping=True),
                # "NetSales": locale.format_string("%0.2f", row['NetTotalSales'], grouping=True),
                # "Vat": locale.format_string("%0.2f", row['TotalVat'], grouping=True),
                # "DineInSales": locale.format_string("%0.2f", row['DineInSales'], grouping=True),
                # "TabSales": locale.format_string("%0.2f", row['TabSales'], grouping=True),
                # "NetDineInSales": locale.format_string("%0.2f", row['NetDineInSales'], grouping=True),
                # "NetTabSales": locale.format_string("%0.2f", row['NetTabSales'], grouping=True),
                # "TotalGuests": locale.format_string("%0d", row['TotalGuests'], grouping=True),
                # "Cash": locale.format_string("%0.2f", row['Cash'], grouping=True),
                # "Credit": locale.format_string("%0.2f", row['Credit'], grouping=True),
                # "CreditCard": locale.format_string("%0.2f", row['CreditCard'], grouping=True),
                # "MobilePayment": locale.format_string("%0.2f", row['MobilePayment'], grouping=True),
                # "Complimentary": locale.format_string("%0.2f", row['Complimentary'], grouping=True),
                # "NonChargeable": locale.format_string("%0.2f", row['NonChargeable'], grouping=True),
                # "Split": locale.format_string("%0.2f", row['Split'], grouping=True)
            }


        # Start creating the HTML report
        report = """
        <html>
        <body>
        <h2>Last 3 Months Sales Report (All Outlets)</h2>
        <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse; width: 100%;">
            <thead>
                <tr>
                    <th rowspan="2">Metric</th>  <!-- Metric header spanning 2 rows -->
        """

        # Dynamically create column headers for each outlet
        for outlet in outlets:
            report += f"<th colspan='{len(months)}'>{outlet}</th>"
        report += "</tr><tr>"

        # Add month subheaders under each outlet
        for outlet in outlets:
            for month in months:
                report += f"<th>{month}</th>"
        report += "</tr></thead><tbody>"

        # List of metrics to display
        metrics = [
            "Total Sales", "Net Sales", "Vat", "DineIn Sales", "Tab Sales",
            "Net DineIn Sales", "Net Tab Sales", "Total Guests", "Rev. Per Guest", "Discount",
            "Cash", "Credit", "Credit Card", "Mobile Payment",
            "Complimentary", "Non Chargeable", "Split", "Start Bill", "End Bill"
        ]

        # Add each metric row
        for metric in metrics:
            report += f"<tr><td>{metric}</td>"
            for outlet in outlets:
                for month in months:
                    report += f"<td>{outlet_data[outlet][month][metric]}</td>"
            report += "</tr>"

        # Close table and HTML
        report += """
            </tbody>
        </table>
        </body>
        </html>
        """

        # Fetch email recipients and return report
        query = """SELECT email FROM mailrecipient WHERE status = TRUE;"""
        cursor.execute(query)
        rows = cursor.fetchall()
        recipients = [row['email'] for row in rows]

        return report, recipients

    except Exception as error:
        print(f"Error in sending report: {error}")

# monthly_report()