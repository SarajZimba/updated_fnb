from flask import Blueprint, request, jsonify
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv
from datetime import datetime
import pytz
import copy

from .cost_utils import (
    calculate_food_and_beverage_stockstatement,
    calculate_food_and_beverage_purchase,
    insert_into_tblcosttracker,
    calculate_food_and_beverage_from_newposted_stockstatement
)

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

        # Get opening stock totals
        opening_foodtotal, opening_beveragetotal = calculate_food_and_beverage_stockstatement(cursor, outlet_name)

        # Delete existing stock statement
        cursor.execute("DELETE FROM stock_statement WHERE OutletName=%s", (outlet_name,))

        # Modified INSERT statement with new fields
        sql_insert_stock = """
        INSERT INTO stock_statement (
            `GroupName`, `ItemName`, `BrandName`, `UOM`, `CurrentLevel`, `Rate`, `Total`, 
            `OutletName`, `Type`, `vendor_name`, `exp_date`, `taxable`, `primary_unit`, `secondary_unit`, `StockType`
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                stock.get('secondary_unit'),  # New field
                stock.get('StockType', 'Stockable')   # StockType
            )
            for stock in stock_data
        ]
        cursor.executemany(sql_insert_stock, stock_entries)


        # NEW: Insert into stock_current_level table
        sql_insert_current_level = """
        INSERT INTO stock_current_level (
            `name`, `outlet`, `units`, `qty`, `expiry_date`, `rate`, `total`
        ) VALUES (%s, %s,%s, %s, %s, %s, %s)
        """

        current_level_entries = [
            (
                stock.get('ItemName'),           # name
                stock.get('OutletName', outlet_name),  # outlet
                stock.get('UOM'),                 # units
                stock.get('currentLevel'),        # qty
                stock.get('exp_date'),            # expiry_date
                stock.get('Rate'),                # rate
                stock.get('Total')                # total
            )
            for stock in stock_data
        ]
        cursor.executemany(sql_insert_current_level, current_level_entries)

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

        if last_synced_date:
            purchase_foodtotal, purchase_beveragetotal = calculate_food_and_beverage_purchase(
                last_synced_date, today_date, outlet_name, cursor
            )
            closing_foodtotal, closing_beveragetotal = calculate_food_and_beverage_from_newposted_stockstatement(posted_data)

            if opening_foodtotal != 0.0:
                insert_into_tblcosttracker(today_date, purchase_foodtotal, opening_foodtotal, closing_foodtotal, outlet_name, "Food")
            if opening_beveragetotal != 0.0:
                insert_into_tblcosttracker(today_date, purchase_beveragetotal, opening_beveragetotal, closing_beveragetotal, outlet_name, "Beverage")

        # Update organization table
        if count == 0:
            cursor.execute("INSERT INTO organization (`last_synced`, `outlet_name`) VALUES (%s, %s)", (current_datetime, outlet_name))
        else:
            cursor.execute("UPDATE organization SET `last_synced` = %s WHERE outlet_name=%s", (current_datetime, outlet_name))

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


@app_file45.route('/checkAndInsertStockItems', methods=["POST"])
@cross_origin()
def check_and_insert_stock_items():
    mydb = None
    try:
        mydb = mysql.connector.connect(
            user=os.getenv('user'), 
            password=os.getenv('password'), 
            host=os.getenv('host')
        )
        cursor = mydb.cursor(buffered=True)
        database_sql = "USE {};".format(os.getenv('database'))
        cursor.execute(database_sql)
        
        data = request.get_json()
        
        # Validate input
        if not data or 'items' not in data:
            return jsonify({"error": "Invalid input. 'items' list is required."}), 400
        
        items_list = data['items']
        if not isinstance(items_list, list) or len(items_list) == 0:
            return jsonify({"error": "Items must be a non-empty list."}), 400
        
        # Track results
        existing_items = []
        inserted_items = []
        failed_items = []
        
        # SQL to check if item exists
        check_sql = """
            SELECT COUNT(*) FROM stock_statement 
            WHERE ItemName = %s AND OutletName = %s
        """
        
        # SQL to insert new item
        insert_sql = """
            INSERT INTO stock_statement (
                GroupName, ItemName, BrandName, UOM, CurrentLevel, Rate, Total, 
                OutletName, Type, vendor_name, StockType, exp_date, taxable, 
                primary_unit, secondary_unit
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        for item in items_list:
            try:
                # Validate required fields
                if 'ItemName' not in item or 'OutletName' not in item:
                    failed_items.append({
                        "item": item,
                        "reason": "Missing required field: ItemName or OutletName"
                    })
                    continue
                
                item_name = item['ItemName']
                outlet_name = item['OutletName']
                
                # Check if item exists
                cursor.execute(check_sql, (item_name, outlet_name))
                count = cursor.fetchone()[0]
                
                if count > 0:
                    existing_items.append({
                        "ItemName": item_name,
                        "OutletName": outlet_name,
                        "status": "already_exists"
                    })
                else:
                    # Prepare insert data with defaults
                    insert_data = (
                        item.get('GroupName', None),           # GroupName
                        item_name,                              # ItemName
                        item.get('BrandName', None),            # BrandName
                        item.get('UOM', None),                  # UOM
                        item.get('CurrentLevel', 0.0),          # CurrentLevel
                        item.get('Rate', 0.0),                  # Rate
                        item.get('Total', 0.0),                 # Total
                        outlet_name,                            # OutletName
                        item.get('Type', None),                 # Type
                        item.get('vendor_name', None),          # vendor_name
                        item.get('StockType', 'Stockable'),     # StockType
                        item.get('exp_date', None),             # exp_date
                        item.get('taxable'),                 # taxable
                        item.get('primary_unit', None),         # primary_unit
                        item.get('secondary_unit', None)        # secondary_unit
                    )
                    
                    cursor.execute(insert_sql, insert_data)
                    inserted_items.append({
                        "ItemName": item_name,
                        "OutletName": outlet_name,
                        "status": "inserted"
                    })
                    
            except Exception as e:
                failed_items.append({
                    "item": item,
                    "reason": str(e)
                })
                return jsonify({
                    "success": False,
                    "message": f"Processed {len(items_list)} items. Inserted: {len(inserted_items)}, Already existed: {len(existing_items)}, Failed: {len(failed_items)}",
                    "data": {
                        "inserted": inserted_items,
                        "existing": existing_items,
                        "failed": failed_items
                    }
                }), 400
        
        # Commit all inserts
        mydb.commit()
        
        return jsonify({
            "success": True,
            "message": f"Processed {len(items_list)} items. Inserted: {len(inserted_items)}, Already existed: {len(existing_items)}, Failed: {len(failed_items)}",
            "data": {
                "inserted": inserted_items,
                "existing": existing_items,
                "failed": failed_items
            }
        }), 200
        
    except Exception as e:
        if mydb:
            mydb.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        if mydb and mydb.is_connected():
            mydb.close()