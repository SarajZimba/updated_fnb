# # test_mail_delay.py
# from tasks import send_bulk_emails

# emails = [
#     {
#         "email": "sarajgimba@gmail.com",
#         "subject": "Test Email from Celery",
#         "html": "<h1>Hello from Celery!</h1>"
#     }
# ]

# # Enqueue task asynchronously
# result = send_bulk_emails.delay(emails)

# print("Task sent to Celery, ID:", result.id)

from flask import Blueprint, request, jsonify
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv
from datetime import datetime
import pytz
import copy

# from .cost_utils import (
#     calculate_food_and_beverage_stockstatement,
#     calculate_food_and_beverage_purchase,
#     insert_into_tblcosttracker,
#     calculate_food_and_beverage_from_newposted_stockstatement
# )

load_dotenv()

app_file45 = Blueprint('app_file45', __name__)

@app_file45.route("/poststocks", methods=["POST"])
@cross_origin()
def stats():
    mydb = None
    try:
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password')
        )
        cursor = mydb.cursor(buffered=True)
        cursor.execute(f"USE {os.getenv('database')}")

        # Check if request has JSON data
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        stock_data_json = request.get_json()
        
        # Check if JSON data is None or empty
        if not stock_data_json:
            return jsonify({"error": "Empty or invalid JSON data"}), 400
        
        # Debug: Print received data (remove in production)
        print("Received JSON:", stock_data_json)
        
        posted_data = copy.deepcopy(stock_data_json)
        stock_data = stock_data_json.get("ItemDetailsList", [])

        # Check for OutletName
        if "OutletName" not in stock_data_json:
            return jsonify({"error": "OutletName is required in the root of JSON object"}), 400
        
        if not stock_data_json["OutletName"]:
            return jsonify({"error": "OutletName cannot be empty"}), 400
        
        outlet_name = stock_data_json["OutletName"]

        if not stock_data or not isinstance(stock_data, list):
            return jsonify({"error": "Invalid input. 'ItemDetailsList' must be a non-empty list."}), 400

        for idx, stock in enumerate(stock_data):
            if not stock.get('ItemName'):
                return jsonify({"error": f"ItemName is required for item at index {idx}"}), 400
            
            if not isinstance(stock.get('currentLevel'), (int, float)) or stock.get('currentLevel') < 0:
                return jsonify({"error": f"Invalid 'Current Level' for {stock.get('ItemName')}"}), 400
            if not isinstance(stock.get('Rate'), (int, float)):
                return jsonify({"error": f"Invalid 'Rate' for {stock.get('ItemName')}"}), 400
            if not isinstance(stock.get('Total'), (int, float)):
                return jsonify({"error": f"Invalid 'Total' for {stock.get('ItemName')}"}), 400
            if stock.get('Department') is None:
                return jsonify({"error": f"Missing 'Department' for {stock.get('ItemName')}"}), 400

            # New field validations
            if stock.get('exp_date'):
                try:
                    datetime.strptime(stock.get('exp_date'), '%Y-%m-%d')
                except ValueError:
                    return jsonify({"error": f"Invalid exp_date format for {stock.get('ItemName')}. Use YYYY-MM-DD"}), 400
            
            if stock.get('taxable') is not None and not isinstance(stock.get('taxable'), bool):
                return jsonify({"error": f"taxable must be true/false for {stock.get('ItemName')}"}), 400

            # Unit definition validation
            unit_def = stock.get("unitdefinition")
            if not unit_def or not isinstance(unit_def, dict):
                return jsonify({"error": f"Missing or invalid unitdefinition for item: {stock.get('ItemName')}"}), 400
            if not isinstance(unit_def.get("unit"), (int, float)) or not isinstance(unit_def.get("rate"), (int, float)) or not unit_def.get("uom"):
                return jsonify({"error": f"Invalid fields in unitdefinition for item: {stock.get('ItemName')}"}), 400


        # Delete existing stock statement
        cursor.execute("DELETE FROM stock_statement WHERE OutletName=%s", (outlet_name,))

        # Modified INSERT statement with new fields
        sql_insert_stock = """
        INSERT INTO stock_statement (
            `GroupName`, `ItemName`, `BrandName`, `UOM`, `CurrentLevel`, `Rate`, `Total`, 
            `OutletName`, `Type`, `vendor_name`, `exp_date`, `taxable`, `primary_unit`, `secondary_unit`
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        stock_entries = [
            (
                stock.get('GroupName'),
                stock.get('ItemName'),
                stock.get('BrandName'),
                stock.get('UOM'),
                stock.get('currentLevel'),
                stock.get('Rate'),
                stock.get('Total'),
                stock.get('OutletName', outlet_name),  # Use item's OutletName or fallback to root
                stock.get('Department'),
                stock.get('Vendor', None),
                stock.get('exp_date'),  # New field
                stock.get('taxable', False),  # New field, default False
                stock.get('primary_unit'),  # New field
                stock.get('secondary_unit')  # New field
            )
            for stock in stock_data
        ]
        cursor.executemany(sql_insert_stock, stock_entries)

        # Handle unitdefinition: delete existing then insert new
        sql_unitdef_delete = "DELETE FROM tblunitdefinition WHERE name = %s AND outlet = %s"
        sql_unitdef_insert = """
        INSERT INTO tblunitdefinition (name, unit, uom, rate, outlet)
        VALUES (%s, %s, %s, %s, %s)
        """
        for stock in stock_data:
            unit_def = stock["unitdefinition"]
            item_name = stock["ItemName"]
            outlet = stock.get("OutletName", outlet_name)  # Use item's OutletName or fallback to root

            cursor.execute(sql_unitdef_delete, (item_name, outlet))
            cursor.execute(sql_unitdef_insert, (item_name, unit_def["unit"], unit_def["uom"], unit_def["rate"], outlet))

        # Get current time in Nepal timezone
        nepal_tz = pytz.timezone('Asia/Kathmandu')
        current_datetime = datetime.now(nepal_tz).strftime('%Y-%m-%d %H:%M:%S')
        today_date = datetime.now(nepal_tz).strftime('%Y-%m-%d')

        # Check organization last_synced
        cursor.execute("SELECT COUNT(*), DATE(MAX(last_synced)) FROM organization WHERE outlet_name=%s", (outlet_name,))
        result = cursor.fetchone()
        count, last_synced = result[0], result[1]
        last_synced_date = last_synced.strftime('%Y-%m-%d') if last_synced else None

        mydb.commit()

        return jsonify({"success": f"Successfully updated stock statement with {len(stock_entries)} records and unit definitions."}), 200

    except mysql.connector.Error as db_error:
        if mydb:
            mydb.rollback()
        return jsonify({"error": f"Database error: {str(db_error)}"}), 500
    except Exception as e:
        if mydb:
            mydb.rollback()
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
    finally:
        if mydb and mydb.is_connected():
            mydb.close()
