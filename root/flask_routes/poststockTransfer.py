# from flask import Flask, Blueprint, request, jsonify
# import mysql.connector
# from flask_cors import cross_origin

# import os

# from dotenv import load_dotenv
# from datetime import datetime

# load_dotenv()


# app_file57 = Blueprint('appfile_57', __name__)


# @app_file57.route('/poststockTransfer', methods = ["POST"])

# @cross_origin()
# def postStock():
#     try:
#         mydb = mysql.connector.connect(user=os.getenv('user'), password = os.getenv('password'), host= os.getenv('host'))

#         cursor = mydb.cursor(buffered=True)

#         database_sql = "USE {};".format(os.getenv('database'))

#         cursor.execute(database_sql)

#         json = request.get_json()

#         store_itemdetails = json.pop("ItemDetailsList", None)

#         store_requisition = json

#         # Convert the date to MySQL compatible format
#         try:
#             date_obj = datetime.strptime(store_requisition['Date'], '%Y-%m-%dT%H:%M:%S')
#             formatted_date = date_obj.strftime('%Y-%m-%d %H:%M:%S')
#         except Exception as e:
#             return jsonify({"error": "Invalid date format, expected 'YYYY-MM-DDTHH:MM:SS'"}), 400

#         insert_storerequisitionSql = """ Insert into intblstorerequisition (`Date`, `CostCenter`, `Outlet`, `OutletREQID`) values (%s,%s,%s,%s)"""

#         cursor.execute(insert_storerequisitionSql, (formatted_date,store_requisition["CostCenter"], store_requisition["OutletName"],store_requisition["Outlet_Req_ID"],))

#         # Get the id of the last inserted record in intblstorerequisition
#         store_req_id = cursor.lastrowid

#         costcenter = formatted_date,store_requisition["CostCenter"]

#         item_type = "Food"
#         if costcenter == "Kitchen":
#             item_type = "Food"

#         else:
#             item_type = "Beverage"

#         for item in store_itemdetails:

#             insert_storerequisitiondetailsSql = """ Insert into intblstorereqdetails (`ItemName`, `GroupName`, `BrandName`, `Amount`, `UOM`, `Rate`, `StoreReqID`, `itemtype`) values (%s,%s,%s,%s,%s,%s,%s,%s)"""


#             cursor.execute(insert_storerequisitiondetailsSql, (item["ItemName"], item["GroupName"], item["BrandName"], item["Amount"], item["UOM"], item["Rate"], store_req_id,item_type))


#             # Always insert new entry into item_current_level (sequential entry)
#             cursor.execute("""
#                 INSERT INTO item_current_level (itemname, quantity, rate, outlet, costcenter)
#                 VALUES (%s, %s, %s, %s)
#             """, (
#                 item['item_name'],
#                 float(item['quantity']),
#                 float(item['price']),
#                 store_requisition["OutletName"],
#                 costcenter                
#             ))

#         # Commit the transaction to save changes
#         mydb.commit()

#         # Return a success response
#         return jsonify({"status": "success", "message": "Stock transfer request added successfully!"})
    
#     except Exception as e:

#         data = {"error": str(e)}
#         return data, 400
    
#     finally:
#         mydb.close()


from flask import Flask, Blueprint, request, jsonify
import mysql.connector
from flask_cors import cross_origin

import os

from dotenv import load_dotenv
from datetime import datetime

load_dotenv()


app_file57 = Blueprint('appfile_57', __name__)


@app_file57.route('/poststockTransfer', methods = ["POST"])

@cross_origin()
def postStock():
    try:
        mydb = mysql.connector.connect(user=os.getenv('user'), password = os.getenv('password'), host= os.getenv('host'))

        cursor = mydb.cursor(buffered=True)

        database_sql = "USE {};".format(os.getenv('database'))

        cursor.execute(database_sql)

        json = request.get_json()

        store_itemdetails = json.pop("ItemDetailsList", None)

        store_requisition = json

        # Convert the date to MySQL compatible format
        try:
            date_obj = datetime.strptime(store_requisition['Date'], '%Y-%m-%dT%H:%M:%S')
            formatted_date = date_obj.strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:
            return jsonify({"error": "Invalid date format, expected 'YYYY-MM-DDTHH:MM:SS'"}), 400
        
        purchase_from = store_requisition.get("purchase_from", "c_app")

        purchase_id = store_requisition.get("purchase_id", None)


        # Generate OutletREQID based on purchase_from
        if purchase_from == "web":
            cursor.execute("""
                SELECT MAX(CAST(OutletREQID AS UNSIGNED)) 
                FROM intblstorerequisition
                WHERE Outlet = %s and purchase_from = 'web'
            """, (store_requisition["OutletName"],))
            
            max_id = cursor.fetchone()[0]
            
            if max_id is None:
                outlet_req_id = 1
            else:
                outlet_req_id = int(max_id) + 1
        else:
            outlet_req_id = store_requisition["Outlet_Req_ID"]

        insert_storerequisitionSql = """ Insert into intblstorerequisition (`Date`, `CostCenter`, `Outlet`, `OutletREQID`, `purchase_from`, `purchase_id`) values (%s,%s,%s,%s,%s,%s)"""

        cursor.execute(insert_storerequisitionSql, (formatted_date,store_requisition["CostCenter"], store_requisition["OutletName"],outlet_req_id, purchase_from, purchase_id))

        # Get the id of the last inserted record in intblstorerequisition
        store_req_id = cursor.lastrowid

        costcenter = store_requisition["CostCenter"]

        item_type = "Food"
        if costcenter == "Kitchen":
            item_type = "Food"

        elif costcenter == "Bar":
            item_type = "Beverage"

        else:
            item_type = costcenter

        for item in store_itemdetails:
            # DEDUCT FROM stock_current_level TABLE USING FIFO (EARLIEST EXPIRY FIRST)
            item_name = item["ItemName"]
            requested_qty = float(item["Amount"])
            
            # Check if sufficient stock is available
            # cursor.execute("""
            #         SELECT SUM(qty) as total_available 
            #         FROM stock_current_level 
            #         WHERE name = %s 
            #         AND qty > 0
            #         AND (expiry_date IS NULL OR expiry_date > CURDATE())
            #     """, (item_name,))
                
            # result = cursor.fetchone()
            # total_available = result[0] if result[0] else 0
                
            # if total_available < requested_qty:
            #     raise Exception(f"Insufficient stock for {item_name}. Available: {total_available}, Requested: {requested_qty}")
                
            # # Get stock batches ordered by expiry date (earliest first)
            # cursor.execute("""
            #         SELECT id, qty, total, rate, expiry_date
            #         FROM stock_current_level 
            #         WHERE name = %s 
            #         AND qty > 0
            #         AND (expiry_date IS NULL OR expiry_date > CURDATE())
            #         ORDER BY expiry_date ASC, id ASC
            #     """, (item_name,))
                
            # stock_batches = cursor.fetchall()
            # remaining_to_deduct = requested_qty
                
            # # Deduct from batches
            # for batch in stock_batches:
            #     if remaining_to_deduct <= 0:
            #         break
                        
            #     batch_id = batch[0]
            #     current_qty = float(batch[1])
            #     current_total = float(batch[2])
            #     current_rate = float(batch[3])
                    
            #     if current_qty <= remaining_to_deduct:
            #         # Remove entire batch
            #         new_qty = 0
            #         new_total = 0
            #         remaining_to_deduct -= current_qty
            #     else:
            #         # Partially deduct from this batch
            #         new_qty = current_qty - remaining_to_deduct
            #         new_total = new_qty * current_rate
            #         remaining_to_deduct = 0
                    
            #     # Update the stock_current_level
            #     cursor.execute("""
            #         UPDATE stock_current_level 
            #         SET qty = %s, total = %s 
            #         WHERE id = %s
            #     """, (new_qty, new_total, batch_id))


            # SUBTRACT FROM stock_statement (aggregated stock)
            cursor.execute("""
                SELECT CurrentLevel, Total 
                FROM stock_statement 
                WHERE ItemName = %s AND UOM = %s AND OutletName = %s
            """, (item["ItemName"], item["UOM"], store_requisition["OutletName"]))

            existing = cursor.fetchone()

            if existing:
                current_level = float(existing[0])
                current_total = float(existing[1]) if existing[1] else 0

                new_level = current_level - requested_qty
                deduction_total = requested_qty * float(item["Rate"])
                new_total = current_total - deduction_total

                # if new_level <= 0:
                #     # Optional: delete row if stock becomes zero
                #     # cursor.execute(""" 
                #     #     DELETE FROM stock_statement
                #     #     WHERE ItemName = %s AND UOM = %s AND OutletName = %s
                #     # """, (item["ItemName"], item["UOM"], store_requisition["OutletName"]))
                #     new_level = 0
                #     deduction_total = 0
                #     new_total = 0
                cursor.execute("""
                        UPDATE stock_statement
                        SET CurrentLevel = %s,
                            Total = %s
                        WHERE ItemName = %s AND UOM = %s AND OutletName = %s
                    """, (
                        new_level,
                        new_total,
                        item["ItemName"],
                        item["UOM"],
                        store_requisition["OutletName"]
                    ))
            else:
                # This should not happen ideally
                raise Exception(f"Stock statement missing for {item['ItemName']}")

            # Insert into intblstorereqdetails (original code - unchanged)
            insert_storerequisitiondetailsSql = """ Insert into intblstorereqdetails (`ItemName`, `GroupName`, `BrandName`, `Amount`, `UOM`, `Rate`, `StoreReqID`, `itemtype`) values (%s,%s,%s,%s,%s,%s,%s,%s)"""

            cursor.execute(insert_storerequisitiondetailsSql, (item["ItemName"], item["GroupName"], item["BrandName"], item["Amount"], item["UOM"], item["Rate"], store_req_id,item_type))

            # Insert into item_current_level (original code - unchanged except using negative quantity)
            cursor.execute("""
                INSERT INTO item_current_level (itemname, quantity, rate, outlet, costcenter)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                item['ItemName'],
                float(item['Amount']),  # Keep as positive as in your original
                float(item['Rate']),
                store_requisition["OutletName"],
                costcenter                
            ))

        # Commit the transaction to save changes
        mydb.commit()

        # Return a success response
        return jsonify({"status": "success", "message": "Stock transfer request added successfully!"})
    
    except Exception as e:
        mydb.rollback()
        data = {"error": str(e)}
        return data, 400
    
    finally:
        mydb.close()


@app_file57.route('/poststockTransfer_web', methods = ["POST"])
@cross_origin()
def postStock_web():
    try:
        mydb = mysql.connector.connect(
            user=os.getenv('user'), 
            password=os.getenv('password'), 
            host=os.getenv('host')
        )
        cursor = mydb.cursor(buffered=True, dictionary=True)

        database_sql = "USE {};".format(os.getenv('database'))
        cursor.execute(database_sql)

        json_data = request.get_json()

        store_itemdetails = json_data.pop("ItemDetailsList", None)
        store_requisition = json_data

        # Convert the date to MySQL compatible format
        try:
            date_obj = datetime.strptime(store_requisition['Date'], '%Y-%m-%dT%H:%M:%S')
            formatted_date = date_obj.strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:
            return jsonify({"error": "Invalid date format, expected 'YYYY-MM-DDTHH:MM:SS'"}), 400
        
        purchase_from = store_requisition.get("purchase_from", "c_app")
        purchase_id = store_requisition.get("purchase_id", None)

        # Generate OutletREQID based on purchase_from
        if purchase_from == "web":
            cursor.execute("""
                SELECT MAX(CAST(OutletREQID AS UNSIGNED)) as max_id
                FROM intblstorerequisition
                WHERE Outlet = %s and purchase_from = 'web'
            """, (store_requisition["OutletName"],))
            
            result = cursor.fetchone()
            max_id = result['max_id'] if result else None
            
            if max_id is None:
                outlet_req_id = 1
            else:
                outlet_req_id = int(max_id) + 1
        else:
            outlet_req_id = store_requisition["Outlet_Req_ID"]

        # VALIDATION: Get current stock levels for all items
        stock_info = []
        stock_validation_errors = []
        
        for item in store_itemdetails:
            requested_qty = float(item["Amount"])
            item_name = item["ItemName"]
            uom = item["UOM"]
            outlet_name = store_requisition["OutletName"]
            
            cursor.execute("""
                SELECT CurrentLevel, Total, Rate 
                FROM stock_statement 
                WHERE ItemName = %s AND UOM = %s AND OutletName = %s
            """, (item_name, uom, outlet_name))
            
            existing = cursor.fetchone()
            
            if not existing:
                stock_validation_errors.append({
                    "item": item_name,
                    "uom": uom,
                    "requested": requested_qty,
                    "available": 0,
                    "error": "Item not found in stock statement"
                })
            else:
                current_level = float(existing['CurrentLevel']) if existing['CurrentLevel'] else 0
                current_total = float(existing['Total']) if existing['Total'] else 0
                unit_price = float(existing['Rate']) if existing.get('Rate') else item.get("Rate", 0)
                
                stock_info.append({
                    "item": item_name,
                    "uom": uom,
                    "requested": requested_qty,
                    "available": current_level,
                    "unit_price": unit_price,
                    "current_total": current_total,
                    "will_remain": current_level - requested_qty,
                    "will_total": current_total - (requested_qty * unit_price)
                })
                
                if requested_qty > current_level:
                    stock_validation_errors.append({
                        "item": item_name,
                        "uom": uom,
                        "requested": requested_qty,
                        "available": current_level,
                        "shortage": requested_qty - current_level,
                        "error": f"Insufficient stock. Shortage: {requested_qty - current_level} units"
                    })
        
        # If any validation errors, return them without proceeding
        if stock_validation_errors:
            mydb.rollback()
            return jsonify({
                "status": "error",
                "message": "Stock validation failed. Some items have insufficient stock.",
                "stock_summary": stock_info,
                "errors": stock_validation_errors
            }), 400

        # Proceed with insertion
        insert_storerequisitionSql = """ INSERT INTO intblstorerequisition 
            (`Date`, `CostCenter`, `Outlet`, `OutletREQID`, `purchase_from`, `purchase_id`) 
            VALUES (%s, %s, %s, %s, %s, %s)"""

        cursor.execute(insert_storerequisitionSql, (
            formatted_date,
            store_requisition["CostCenter"], 
            store_requisition["OutletName"],
            outlet_req_id, 
            purchase_from, 
            purchase_id
        ))

        store_req_id = cursor.lastrowid

        costcenter = store_requisition["CostCenter"]

        if costcenter == "Kitchen":
            item_type = "Food"
        elif costcenter == "Bar":
            item_type = "Beverage"
        else:
            item_type = costcenter

        # Process each item
        for item, stock in zip(store_itemdetails, stock_info):
            requested_qty = float(item["Amount"])
            requested_rate = float(item["Rate"])
            item_name = item["ItemName"]
            uom = item["UOM"]
            outlet_name = store_requisition["OutletName"]

            # Update stock_statement
            cursor.execute("""
                UPDATE stock_statement
                SET CurrentLevel = %s,
                    Total = %s
                WHERE ItemName = %s AND UOM = %s AND OutletName = %s
            """, (
                stock['will_remain'],
                stock['will_total'],
                item_name,
                uom,
                outlet_name
            ))

            # Insert into intblstorereqdetails
            cursor.execute("""
                INSERT INTO intblstorereqdetails 
                (`ItemName`, `GroupName`, `BrandName`, `Amount`, `UOM`, `Rate`, `StoreReqID`, `itemtype`) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                item["ItemName"], 
                item["GroupName"], 
                item["BrandName"], 
                item["Amount"], 
                item["UOM"], 
                item["Rate"], 
                store_req_id,
                item_type
            ))

            # Insert into item_current_level
            cursor.execute("""
                INSERT INTO item_current_level (itemname, quantity, rate, outlet, costcenter)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                item['ItemName'],
                float(item['Amount']),
                float(item['Rate']),
                outlet_name,
                costcenter                
            ))

        mydb.commit()

        return jsonify({
            "status": "success", 
            "message": "Stock transfer request added successfully!",
            "outlet_req_id": outlet_req_id,
            "store_req_id": store_req_id,
            "stock_summary": stock_info
        }), 200
    
    except Exception as e:
        if mydb:
            mydb.rollback()
        return jsonify({"error": str(e)}), 400
    
    finally:
        if mydb and mydb.is_connected():
            mydb.close()


@app_file57.route('/getStorereqsByPurchaseId', methods=["POST"])
@cross_origin()
def getStorereqsByPurchaseId():
    try:
        mydb = mysql.connector.connect(
            user=os.getenv('user'),
            password=os.getenv('password'),
            host=os.getenv('host')
        )
        cursor = mydb.cursor(dictionary=True, buffered=True)

        # Select DB
        cursor.execute(f"USE {os.getenv('database')}")

        # Get request data
        data = request.get_json()

        purchase_id = data.get('purchase_id')
        outlet_name = data.get('outlet_name')

        # ✅ Validation
        if not purchase_id:
            return jsonify({"error": "purchase_id is required"}), 400

        if not outlet_name:
            return jsonify({"error": "outlet_name is required"}), 400

        # Convert purchase_id to int (safer)
        try:
            purchase_id = int(purchase_id)
        except:
            return jsonify({"error": "purchase_id must be an integer"}), 400

        # ✅ Main Query (NO DATE_FORMAT here)
        sql = """
        SELECT 
            idintblStoreRequisition,
            OutletREQID,
            Date,
            CostCenter,
            Outlet,
            purchase_from,
            purchase_id
        FROM intblstorerequisition 
        WHERE purchase_id = %s AND Outlet = %s
        ORDER BY Date DESC
        """

        cursor.execute(sql, (purchase_id, outlet_name))
        store_requisitions = cursor.fetchall()

        # ✅ Add formatted date + fetch items
        for requisition in store_requisitions:
            # Format date safely
            if requisition.get("Date"):
                requisition["formatted_date"] = requisition["Date"].strftime('%Y-%m-%d %H:%M:%S')
            else:
                requisition["formatted_date"] = None

            # Fetch item details
            items_sql = """
            SELECT 
                ItemName,
                GroupName,
                BrandName,
                Amount,
                UOM,
                Rate,
                itemtype
            FROM intblstorereqdetails 
            WHERE StoreReqID = %s
            """

            cursor.execute(items_sql, (requisition['idintblStoreRequisition'],))
            requisition['items'] = cursor.fetchall()

        mydb.close()

        return jsonify({
            "success": True,
            "purchase_id": purchase_id,
            "outlet_name": outlet_name,
            "count": len(store_requisitions),
            "data": store_requisitions
        }), 200

    except Exception as e:
        print("Error details:", str(e))
        return jsonify({"error": str(e)}), 400
    

@app_file57.route('/getDistinctCostCenters', methods=["POST"])
@cross_origin()
def get_distinct_cost_centers():
    try:
        mydb = mysql.connector.connect(
            user=os.getenv('user'),
            password=os.getenv('password'),
            host=os.getenv('host')
        )
        cursor = mydb.cursor(dictionary=True, buffered=True)

        # Select DB
        cursor.execute(f"USE {os.getenv('database')}")

        # Get request data
        data = request.get_json()
        outlet_name = data.get('outlet_name')

        # Validation
        if not outlet_name:
            return jsonify({"error": "outlet_name is required"}), 400

        # Query to get distinct cost centers
        sql = """
        SELECT DISTINCT CostCenter
        FROM intblstorerequisition 
        WHERE Outlet = %s AND CostCenter IS NOT NULL AND CostCenter != ''
        ORDER BY CostCenter ASC
        """

        cursor.execute(sql, (outlet_name,))
        cost_centers = cursor.fetchall()

        mydb.close()

        # Extract just the cost center names into a list
        cost_center_list = [center['CostCenter'] for center in cost_centers]

        return jsonify({
            "success": True,
            "outlet_name": outlet_name,
            "count": len(cost_center_list),
            "cost_centers": cost_center_list
        }), 200

    except Exception as e:
        print("Error details:", str(e))
        return jsonify({"error": str(e)}), 400
    


from datetime import datetime, timedelta

@app_file57.route('/getStorereqs', methods=["POST"])
@cross_origin()
def getStorereqs():
    try:
        mydb = mysql.connector.connect(
            user=os.getenv('user'),
            password=os.getenv('password'),
            host=os.getenv('host')
        )
        cursor = mydb.cursor(dictionary=True, buffered=True)

        # Select DB
        cursor.execute(f"USE {os.getenv('database')}")

        # Get request data
        data = request.get_json()
        outlet_name = data.get('outlet_name')
        from_date = data.get('from_date')
        to_date = data.get('to_date')
        store_req_id = data.get('storereqID')
        if not outlet_name:
            return jsonify({"error": "outlet_name is required"}), 400

        # ✅ Build dynamic query
        sql = """
        SELECT 
            idintblStoreRequisition,
            OutletREQID,
            Date,
            CostCenter,
            Outlet,
            purchase_from,
            purchase_id
        FROM intblstorerequisition 
        WHERE Outlet = %s and purchase_from = 'web'
        """

        params = [outlet_name]

        # ✅ Filter by requisition ID
        if store_req_id:
            sql += " AND idintblStoreRequisition = %s"
            params.append(store_req_id)


        # ✅ Apply date filter if provided
        if from_date and to_date:
            start = datetime.strptime(from_date, "%Y-%m-%d")
            end = datetime.strptime(to_date, "%Y-%m-%d") + timedelta(days=1)

            sql += " AND Date >= %s AND Date < %s"
            params.extend([start, end])

        sql += " ORDER BY Date DESC"

        cursor.execute(sql, tuple(params))
        store_requisitions = cursor.fetchall()

        # ✅ Add formatted date + fetch items
        for requisition in store_requisitions:
            if requisition.get("Date"):
                requisition["formatted_date"] = requisition["Date"].strftime('%Y-%m-%d %H:%M:%S')
            else:
                requisition["formatted_date"] = None

            items_sql = """
            SELECT 
                ItemName,
                GroupName,
                BrandName,
                Amount,
                UOM,
                Rate,
                itemtype
            FROM intblstorereqdetails 
            WHERE StoreReqID = %s
            """

            cursor.execute(items_sql, (requisition['idintblStoreRequisition'],))
            requisition['items'] = cursor.fetchall()

        mydb.close()

        return jsonify({
            "success": True,
            "outlet_name": outlet_name,
            "count": len(store_requisitions),
            "data": store_requisitions
        }), 200

    except Exception as e:
        print("Error details:", str(e))
        return jsonify({"error": str(e)}), 400
    

@app_file57.route('/deletestockTransfer_web', methods = ["DELETE"])
@cross_origin()
def deleteStockTransfer_web():
    try:
        mydb = mysql.connector.connect(
            user=os.getenv('user'), 
            password=os.getenv('password'), 
            host=os.getenv('host')
        )
        cursor = mydb.cursor(buffered=True, dictionary=True)

        database_sql = "USE {};".format(os.getenv('database'))
        cursor.execute(database_sql)

        # Get the store_req_id from request
        json_data = request.get_json()
        store_req_id = json_data.get("store_req_id")
        
        if not store_req_id:
            return jsonify({"error": "store_req_id is required"}), 400

        # First, get the requisition details to know which items to restore/remove
        cursor.execute("""
            SELECT sr.Outlet, sr.CostCenter, srd.ItemName, srd.UOM, srd.Amount, srd.Rate
            FROM intblstorerequisition sr
            JOIN intblstorereqdetails srd ON sr.StoreReqID = srd.StoreReqID
            WHERE sr.StoreReqID = %s
        """, (store_req_id,))
        
        requisition_items = cursor.fetchall()
        
        if not requisition_items:
            return jsonify({"error": "Store requisition not found"}), 404

        # Restore stock to stock_statement and remove from item_current_level
        restoration_details = []
        restoration_errors = []
        
        for item in requisition_items:
            item_name = item['ItemName']
            uom = item['UOM']
            outlet_name = item['Outlet']
            costcenter = item['CostCenter']
            amount_to_restore = float(item['Amount'])
            rate = float(item['Rate'])
            
            # 1. RESTORE stock_statement (add back the quantity)
            cursor.execute("""
                SELECT CurrentLevel, Total, Rate 
                FROM stock_statement 
                WHERE ItemName = %s AND UOM = %s AND OutletName = %s
            """, (item_name, uom, outlet_name))
            
            existing = cursor.fetchone()
            
            if not existing:
                restoration_errors.append({
                    "item": item_name,
                    "uom": uom,
                    "error": "Item not found in stock_statement"
                })
                continue
            
            current_level = float(existing['CurrentLevel']) if existing['CurrentLevel'] else 0
            current_total = float(existing['Total']) if existing['Total'] else 0
            unit_price = float(existing['Rate']) if existing.get('Rate') else rate
            
            # Calculate restored values (adding back)
            restored_level = current_level + amount_to_restore
            restored_total = current_total + (amount_to_restore * unit_price)
            
            # Update stock_statement with restored levels
            cursor.execute("""
                UPDATE stock_statement
                SET CurrentLevel = %s,
                    Total = %s
                WHERE ItemName = %s AND UOM = %s AND OutletName = %s
            """, (
                restored_level,
                restored_total,
                item_name,
                uom,
                outlet_name
            ))
            
            # 2. REMOVE from item_current_level (subtract the quantity)
            # First, get the current item_current_level entry for this item
            cursor.execute("""
                SELECT id, quantity, rate 
                FROM item_current_level 
                WHERE itemname = %s 
                AND outlet = %s 
                AND costcenter = %s
                ORDER BY id DESC 
                LIMIT 1
            """, (item_name, outlet_name, costcenter))
            
            current_item = cursor.fetchone()
            
            if not current_item:
                restoration_errors.append({
                    "item": item_name,
                    "uom": uom,
                    "error": "Item not found in item_current_level"
                })
                continue
            
            current_item_qty = float(current_item['quantity'])
            
            if current_item_qty < amount_to_restore:
                restoration_errors.append({
                    "item": item_name,
                    "uom": uom,
                    "error": f"Insufficient quantity in item_current_level to remove. Available: {current_item_qty}, Requested to remove: {amount_to_restore}"
                })
                continue
            
            new_item_qty = current_item_qty - amount_to_restore
            
            restoration_details.append({
                "item": item_name,
                "uom": uom,
                "amount_restored_to_stock": amount_to_restore,
                "stock_statement": {
                    "previous_level": current_level,
                    "new_level": restored_level,
                    "previous_total": current_total,
                    "new_total": restored_total
                },
                "item_current_level": {
                    "previous_quantity": current_item_qty,
                    "new_quantity": new_item_qty,
                    "rate": float(current_item['rate'])
                }
            })
            
            # Update or delete from item_current_level based on new quantity
            if new_item_qty <= 0:
                # If quantity becomes zero or negative, delete the record
                cursor.execute("""
                    DELETE FROM item_current_level 
                    WHERE id = %s
                """, (current_item['id'],))
                restoration_details[-1]["item_current_level"]["action"] = "Deleted (quantity became 0)"
            else:
                # Otherwise, update with new quantity
                cursor.execute("""
                    UPDATE item_current_level 
                    SET quantity = %s
                    WHERE id = %s
                """, (new_item_qty, current_item['id']))
                restoration_details[-1]["item_current_level"]["action"] = "Updated"
        
        # If there were errors, rollback and don't delete
        if restoration_errors:
            mydb.rollback()
            return jsonify({
                "status": "error",
                "message": "Failed to restore stock/remove from current level. Deletion cancelled.",
                "errors": restoration_errors,
                "restoration_details": restoration_details
            }), 400
        
        # Delete from intblstorereqdetails first (due to foreign key constraint)
        cursor.execute("""
            DELETE FROM intblstorereqdetails 
            WHERE StoreReqID = %s
        """, (store_req_id,))
        
        # Finally delete the main requisition record
        cursor.execute("""
            DELETE FROM intblstorerequisition 
            WHERE StoreReqID = %s
        """, (store_req_id,))
        
        mydb.commit()
        
        return jsonify({
            "status": "success",
            "message": f"Store requisition {store_req_id} deleted successfully. Stock restored and current level updated.",
            "restoration_details": restoration_details
        }), 200
    
    except Exception as e:
        if mydb:
            mydb.rollback()
        return jsonify({"error": str(e)}), 400
    
    finally:
        if mydb and mydb.is_connected():
            mydb.close()