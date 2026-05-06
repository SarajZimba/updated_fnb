# from flask import Blueprint, request
# import mysql.connector
# from flask_cors import CORS, cross_origin
# import os
# from dotenv import load_dotenv

# load_dotenv()
# app_file44 = Blueprint('app_file44', __name__)

# @app_file44.route("/deleteinventory", methods=['PUT'])
# @cross_origin()
# def delete_inventory():
#     mydb = None
#     try:
#         # Connect to the database
#         mydb = mysql.connector.connect(
#             host=os.getenv('host'),
#             user=os.getenv('user'),
#             password=os.getenv('password'),
#             database=os.getenv('database')
#         )
#         cursor = mydb.cursor(buffered=True)

#         # Parse request data
#         data = request.get_json()
#         outlet_purchase_id = data.get("PurchaseReqID")
#         outlet_name = data.get("outletName")

#         outletreq_ids = data.get("storereqIds")

#         if not outlet_purchase_id or not outlet_name:
#             return {"error": "PurchaseReqID and outletName are required."}, 400

#         # Check if the purchase exists
#         sql_check = """
#         SELECT `IDIntbl_PurchaseRequisition`
#         FROM `intbl_purchaserequisition`
#         WHERE `Outlet_PurchaseReqID` = %s AND `Outlet_Name` = %s
#         """
#         cursor.execute(sql_check, (outlet_purchase_id, outlet_name))
#         result = cursor.fetchone()

#         if not result:
#             return {"error": "No purchase found for the given PurchaseReqID and outletName."}, 404

#         purchase_id = result[0]

#         # Fetch and back up data to be deleted
#         # Fetch from `intbl_purchaserequisition`
#         sql_select_purchase = """
#         SELECT `RequisitionType`, `Date`, `TotalAmount`, `TaxAmount`, `Company_Name`, `State`, 
#                `ReceivedDate`, `purchaseBillNumber`, `DiscountAmount`, `Outlet_Name`, `GRN`, `Outlet_PurchaseReqID`
#         FROM `intbl_purchaserequisition`
#         WHERE `IDIntbl_PurchaseRequisition` = %s
#         """
#         cursor.execute(sql_select_purchase, (purchase_id,))
#         purchase_to_delete = cursor.fetchone()

#         # Insert into `deleted_purchaserequisition`
#         sql_insert_purchase = """
#         INSERT INTO `deleted_purchaserequisition`
#         (`RequisitionType`, `Date`, `TotalAmount`, `TaxAmount`, `Company_Name`, `State`,
#          `ReceivedDate`, `purchaseBillNumber`, `DiscountAmount`, `Outlet_Name`, `GRN`, `Outlet_PurchaseReqID`)
#         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#         """
#         cursor.execute(sql_insert_purchase, purchase_to_delete)
#         deleted_purchase_id = cursor.lastrowid  # Get the ID of the newly inserted record

#         # Fetch from `intbl_purchaserequisition_contract`
#         sql_select_contract = """
#         SELECT `ItemID`, `UnitsOrdered`, `PurchaseReqID`, `Rate`, `Name`, `BrandName`, `Code`, `UOM`, 
#                `StockType`, `Department`, `GroupName`, `ExpDate`, `Status`, `Taxable`
#         FROM `intbl_purchaserequisition_contract`
#         WHERE `PurchaseReqID` = %s
#         """
#         cursor.execute(sql_select_contract, (purchase_id,))
#         contracts_to_delete = cursor.fetchall()

#         # Insert into `deleted_purchaserequisition_contract`
#         sql_insert_contract = """
#         INSERT INTO `deleted_purchaserequisition_contract`
#         (`ItemID`, `UnitsOrdered`, `DeletedPurchaseReqID`, `Rate`, `Name`, `BrandName`, `Code`, `UOM`,
#          `StockType`, `Department`, `GroupName`, `ExpDate`, `Status`, `Taxable`)
#         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#         """
#         contracts_to_insert = [
#             (c[0], c[1], deleted_purchase_id, c[3], c[4], c[5], c[6], c[7], c[8], c[9], c[10], c[11], c[12], c[13])
#             for c in contracts_to_delete
#         ]
#         cursor.executemany(sql_insert_contract, contracts_to_insert)

#         # Delete from original tables
#         sql_delete_contract = "DELETE FROM `intbl_purchaserequisition_contract` WHERE `PurchaseReqID` = %s"
#         sql_delete_purchase = "DELETE FROM `intbl_purchaserequisition` WHERE `IDIntbl_PurchaseRequisition` = %s"
#         cursor.execute(sql_delete_contract, (purchase_id,))
#         cursor.execute(sql_delete_purchase, (purchase_id,))


#         if outletreq_ids:

#             for outletreq_id in outletreq_ids:
#                 # Check if the purchase exists
#                 sql_check = """
#                 SELECT `idintblStoreRequisition`
#                 FROM `intblstorerequisition`
#                 WHERE `OutletREQID` = %s AND `Outlet` = %s
#                 """
#                 cursor.execute(sql_check, (outletreq_id, outlet_name))
#                 result = cursor.fetchone()

#                 if not result:
#                     continue  # skip this outletreq_id if not found

#                 storereq_id = result[0]

#                 # Fetch from `intblstorerequisition`
#                 sql_select_purchase = """
#                 SELECT `Date`, `CostCenter`, `Outlet`, `OutletREQID`
#                 FROM `intblstorerequisition`
#                 WHERE `idintblStoreRequisition` = %s
#                 """
#                 cursor.execute(sql_select_purchase, (storereq_id,))
#                 storereq_to_delete = cursor.fetchone()

#                 # Insert into `deleted_storerequisition`
#                 sql_insert_purchase = """
#                 INSERT INTO `deleted_storerequisition`
#                 (`Date`, `CostCenter`, `Outlet`, `OutletREQID`)
#                 VALUES (%s, %s, %s, %s)
#                 """
#                 cursor.execute(sql_insert_purchase, storereq_to_delete)
#                 deleted_storereq_id = cursor.lastrowid  # Get the ID of the newly inserted record

#                 # Fetch from `intblstorereqdetails`
#                 sql_select_contract = """
#                 SELECT `ItemName`, `GroupName`, `BrandName`, `Amount`, `UOM`, `Rate`
#                 FROM `intblstorereqdetails`
#                 WHERE `StoreReqID` = %s
#                 """
#                 cursor.execute(sql_select_contract, (storereq_id,))
#                 storereqdetails_to_delete = cursor.fetchall()

#                 # Insert into `deleted_purchaserequisition_contract`
#                 sql_insert_contract = """
#                 INSERT INTO `deletedstorereqdetails`
#                 (`ItemName`, `GroupName`, `BrandName`, `Amount`, `UOM`, `Rate`, `DeletedStoreReqID`)
#                 VALUES (%s, %s, %s, %s, %s, %s, %s)
#                 """
#                 storereq_to_insert = [
#                     (c[0], c[1], c[2], c[3], c[4], c[5], deleted_storereq_id)
#                     for c in storereqdetails_to_delete
#                 ]
#                 cursor.executemany(sql_insert_contract, storereq_to_insert)

#                 # Delete from original tables
#                 sql_delete_contract = "DELETE FROM `intblstorereqdetails` WHERE `StoreReqID` = %s"
#                 sql_delete_purchase = "DELETE FROM `intblstorerequisition` WHERE `idintblStoreRequisition` = %s"
#                 cursor.execute(sql_delete_contract, (storereq_id,))
#                 cursor.execute(sql_delete_purchase, (storereq_id,)) 

#         # Commit transaction
#         mydb.commit()

#         return {"success": "Deleted record successfully."}, 200

#     except mysql.connector.Error as db_error:
#         if mydb:
#             mydb.rollback()
#         return {"error": f"Database error: {str(db_error)}"}, 500
#     except Exception as e:
#         if mydb:
#             mydb.rollback()
#         return {"error": f"An unexpected error occurred: {str(e)}"}, 500
#     finally:
#         if mydb:
#             mydb.close()

# from flask import Blueprint, request
# import mysql.connector
# from flask_cors import CORS, cross_origin
# import os
# from dotenv import load_dotenv

# load_dotenv()
# app_file44 = Blueprint('app_file44', __name__)

# @app_file44.route("/deleteinventory", methods=['PUT'])
# @cross_origin()
# def delete_inventory():
#     mydb = None
#     try:
#         # Connect to the database
#         mydb = mysql.connector.connect(
#             host=os.getenv('host'),
#             user=os.getenv('user'),
#             password=os.getenv('password'),
#             database=os.getenv('database')
#         )
#         cursor = mydb.cursor(buffered=True)

#         # Parse request data
#         data = request.get_json()
#         outlet_purchase_id = data.get("PurchaseReqID")
#         outlet_name = data.get("outletName")
#         outletreq_ids = data.get("storereqIds", [])

#         if not outlet_purchase_id or not outlet_name:
#             return {"error": "PurchaseReqID and outletName are required."}, 400

#         # Check if the purchase exists
#         sql_check = """
#         SELECT `IDIntbl_PurchaseRequisition`
#         FROM `intbl_purchaserequisition`
#         WHERE `Outlet_PurchaseReqID` = %s AND `Outlet_Name` = %s
#         """
#         cursor.execute(sql_check, (outlet_purchase_id, outlet_name))
#         result = cursor.fetchone()

#         if not result:
#             return {"error": "No purchase found for the given PurchaseReqID and outletName."}, 404

#         purchase_id = result[0]
        
#         # Check the State of the purchase
#         cursor.execute("SELECT `State` FROM `intbl_purchaserequisition` WHERE `IDIntbl_PurchaseRequisition` = %s", (purchase_id,))
#         purchase_state = cursor.fetchone()[0]

#         # ============ 1. REVERSE STORE REQUISITION OPERATIONS (if any) ============
#         if outletreq_ids:
#             for outletreq_id in outletreq_ids:
#                 # Get store requisition details
#                 sql_check_store = """
#                 SELECT `idintblStoreRequisition`, `CostCenter`
#                 FROM `intblstorerequisition`
#                 WHERE `OutletREQID` = %s AND `Outlet` = %s
#                 """
#                 cursor.execute(sql_check_store, (outletreq_id, outlet_name))
#                 store_result = cursor.fetchone()

#                 if not store_result:
#                     continue

#                 storereq_id = store_result[0]
#                 costcenter = store_result[1]
                
#                 # Get store items
#                 sql_get_store_items = """
#                 SELECT `ItemName`, `Amount`, `Rate`
#                 FROM `intblstorereqdetails`
#                 WHERE `StoreReqID` = %s
#                 """
#                 cursor.execute(sql_get_store_items, (storereq_id,))
#                 store_items = cursor.fetchall()
                
#                 # Reverse store operations: Add back to stock, remove from item_current_level
#                 for item in store_items:
#                     item_name = item[0]
#                     amount = float(item[1])
#                     rate = float(item[2])
                    
#                     # Add back to stock_current_level (reverse deduction)
#                     cursor.execute("""
#                         SELECT id, qty, total
#                         FROM stock_current_level 
#                         WHERE name = %s AND outlet = %s AND rate = %s
#                         ORDER BY expiry_date ASC, id ASC
#                         LIMIT 1
#                     """, (item_name, outlet_name, rate))
                    
#                     existing_batch = cursor.fetchone()
                    
#                     if existing_batch:
#                         batch_id = existing_batch[0]
#                         new_qty = float(existing_batch[1]) + amount
#                         new_total = new_qty * rate
#                         cursor.execute("""
#                             UPDATE stock_current_level 
#                             SET qty = %s, total = %s 
#                             WHERE id = %s
#                         """, (new_qty, new_total, batch_id))
#                     else:
#                         cursor.execute("""
#                             INSERT INTO stock_current_level (name, outlet, units, qty, expiry_date, rate, total)
#                             VALUES (%s, %s, %s, %s, %s, %s, %s)
#                         """, (item_name, outlet_name, "units", amount, None, rate, amount * rate))
                    
#                     # Remove from item_current_level (reverse addition)
#                     cursor.execute("""
#                         SELECT quantity, id
#                         FROM item_current_level
#                         WHERE itemname = %s AND outlet = %s AND costcenter = %s
#                     """, (item_name, outlet_name, costcenter))
                    
#                     current_level = cursor.fetchone()
                    
#                     if current_level:
#                         current_qty = float(current_level[0])
#                         level_id = current_level[1]
#                         new_qty = current_qty - amount
                        
#                         if new_qty <= 0:
#                             cursor.execute("DELETE FROM item_current_level WHERE id = %s", (level_id,))
#                         else:
#                             cursor.execute("""
#                                 UPDATE item_current_level 
#                                 SET quantity = %s
#                                 WHERE id = %s
#                             """, (new_qty, level_id))

#                 # Backup store requisition to deleted table
#                 sql_select_store = """
#                 SELECT `Date`, `CostCenter`, `Outlet`, `OutletREQID`
#                 FROM `intblstorerequisition`
#                 WHERE `idintblStoreRequisition` = %s
#                 """
#                 cursor.execute(sql_select_store, (storereq_id,))
#                 storereq_to_delete = cursor.fetchone()

#                 sql_insert_deleted_store = """
#                 INSERT INTO `deleted_storerequisition`
#                 (`Date`, `CostCenter`, `Outlet`, `OutletREQID`)
#                 VALUES (%s, %s, %s, %s)
#                 """
#                 cursor.execute(sql_insert_deleted_store, storereq_to_delete)
#                 deleted_storereq_id = cursor.lastrowid

#                 # Backup store details
#                 sql_select_details = """
#                 SELECT `ItemName`, `GroupName`, `BrandName`, `Amount`, `UOM`, `Rate`
#                 FROM `intblstorereqdetails`
#                 WHERE `StoreReqID` = %s
#                 """
#                 cursor.execute(sql_select_details, (storereq_id,))
#                 storereqdetails_to_delete = cursor.fetchall()

#                 sql_insert_deleted_details = """
#                 INSERT INTO `deletedstorereqdetails`
#                 (`ItemName`, `GroupName`, `BrandName`, `Amount`, `UOM`, `Rate`, `DeletedStoreReqID`)
#                 VALUES (%s, %s, %s, %s, %s, %s, %s)
#                 """
#                 storereq_to_insert = [
#                     (c[0], c[1], c[2], c[3], c[4], c[5], deleted_storereq_id)
#                     for c in storereqdetails_to_delete
#                 ]
#                 cursor.executemany(sql_insert_deleted_details, storereq_to_insert)

#                 # Delete from original tables
#                 cursor.execute("DELETE FROM `intblstorereqdetails` WHERE `StoreReqID` = %s", (storereq_id,))
#                 cursor.execute("DELETE FROM `intblstorerequisition` WHERE `idintblStoreRequisition` = %s", (storereq_id,))

#         # ============ 2. REVERSE PURCHASE REQUISITION OPERATIONS ============
#         # Always reverse purchase if State was "Received"
#         if purchase_state == "Received":
#             # Get purchase items
#             sql_get_purchase_items = """
#             SELECT `Name`, `UnitsOrdered`, `Rate`
#             FROM `intbl_purchaserequisition_contract`
#             WHERE `PurchaseReqID` = %s
#             """
#             cursor.execute(sql_get_purchase_items, (purchase_id,))
#             purchase_items = cursor.fetchall()

#             # Remove from stock_current_level (reverse the original addition)
#             for item in purchase_items:
#                 item_name = item[0]
#                 units_ordered = float(item[1])
                
#                 # Get stock batches ordered by expiry (FIFO)
#                 cursor.execute("""
#                     SELECT id, qty, total, rate
#                     FROM stock_current_level 
#                     WHERE name = %s AND outlet = %s AND qty > 0
#                     ORDER BY expiry_date ASC, id ASC
#                 """, (item_name, outlet_name))
                
#                 stock_batches = cursor.fetchall()
#                 remaining_to_remove = units_ordered
                
#                 for batch in stock_batches:
#                     if remaining_to_remove <= 0:
#                         break
                        
#                     batch_id = batch[0]
#                     current_qty = float(batch[1])
#                     current_total = float(batch[2])
#                     current_rate = float(batch[3])
                    
#                     if current_qty <= remaining_to_remove:
#                         # Remove entire batch
#                         new_qty = 0
#                         new_total = 0
#                         remaining_to_remove -= current_qty
#                     else:
#                         # Partially remove from batch
#                         new_qty = current_qty - remaining_to_remove
#                         new_total = new_qty * current_rate
#                         remaining_to_remove = 0
                    
#                     if new_qty == 0:
#                         cursor.execute("DELETE FROM stock_current_level WHERE id = %s", (batch_id,))
#                     else:
#                         cursor.execute("""
#                             UPDATE stock_current_level 
#                             SET qty = %s, total = %s 
#                             WHERE id = %s
#                         """, (new_qty, new_total, batch_id))

#         # ============ 3. BACKUP AND DELETE PURCHASE REQUISITION ============
#         # Backup purchase requisition
#         sql_select_purchase = """
#         SELECT `RequisitionType`, `Date`, `TotalAmount`, `TaxAmount`, `Company_Name`, `State`, 
#                `ReceivedDate`, `purchaseBillNumber`, `DiscountAmount`, `Outlet_Name`, `GRN`, `Outlet_PurchaseReqID`
#         FROM `intbl_purchaserequisition`
#         WHERE `IDIntbl_PurchaseRequisition` = %s
#         """
#         cursor.execute(sql_select_purchase, (purchase_id,))
#         purchase_to_delete = cursor.fetchone()

#         sql_insert_purchase = """
#         INSERT INTO `deleted_purchaserequisition`
#         (`RequisitionType`, `Date`, `TotalAmount`, `TaxAmount`, `Company_Name`, `State`,
#          `ReceivedDate`, `purchaseBillNumber`, `DiscountAmount`, `Outlet_Name`, `GRN`, `Outlet_PurchaseReqID`)
#         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#         """
#         cursor.execute(sql_insert_purchase, purchase_to_delete)
#         deleted_purchase_id = cursor.lastrowid

#         # Backup purchase contract items
#         sql_select_contract = """
#         SELECT `ItemID`, `UnitsOrdered`, `PurchaseReqID`, `Rate`, `Name`, `BrandName`, `Code`, `UOM`, 
#                `StockType`, `Department`, `GroupName`, `ExpDate`, `Status`, `Taxable`
#         FROM `intbl_purchaserequisition_contract`
#         WHERE `PurchaseReqID` = %s
#         """
#         cursor.execute(sql_select_contract, (purchase_id,))
#         contracts_to_delete = cursor.fetchall()

#         sql_insert_contract = """
#         INSERT INTO `deleted_purchaserequisition_contract`
#         (`ItemID`, `UnitsOrdered`, `DeletedPurchaseReqID`, `Rate`, `Name`, `BrandName`, `Code`, `UOM`,
#          `StockType`, `Department`, `GroupName`, `ExpDate`, `Status`, `Taxable`)
#         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#         """
#         contracts_to_insert = [
#             (c[0], c[1], deleted_purchase_id, c[3], c[4], c[5], c[6], c[7], c[8], c[9], c[10], c[11], c[12], c[13])
#             for c in contracts_to_delete
#         ]
#         cursor.executemany(sql_insert_contract, contracts_to_insert)

#         # Delete from original tables
#         cursor.execute("DELETE FROM `intbl_purchaserequisition_contract` WHERE `PurchaseReqID` = %s", (purchase_id,))
#         cursor.execute("DELETE FROM `intbl_purchaserequisition` WHERE `IDIntbl_PurchaseRequisition` = %s", (purchase_id,))

#         # Commit all changes
#         mydb.commit()

#         return {
#             "success": "Deleted record successfully. Stock levels reversed completely.",
#             "details": {
#                 "purchase_reversed": purchase_state == "Received",
#                 "store_requisitions_reversed": len(outletreq_ids) if outletreq_ids else 0
#             }
#         }, 200

#     except mysql.connector.Error as db_error:
#         if mydb:
#             mydb.rollback()
#         return {"error": f"Database error: {str(db_error)}"}, 500
#     except Exception as e:
#         if mydb:
#             mydb.rollback()
#         return {"error": f"An unexpected error occurred: {str(e)}"}, 500
#     finally:
#         if mydb:
#             mydb.close()



from flask import Blueprint, request
import mysql.connector
from flask_cors import CORS, cross_origin
import os
from dotenv import load_dotenv

load_dotenv()
app_file44 = Blueprint('app_file44', __name__)

@app_file44.route("/deleteinventory", methods=['PUT'])
@cross_origin()
def delete_inventory():
    mydb = None
    try:
        # Connect to the database
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password'),
            database=os.getenv('database')
        )
        cursor = mydb.cursor(buffered=True)

        # Parse request data
        data = request.get_json()
        outlet_purchase_id = data.get("PurchaseReqID")
        outlet_name = data.get("outletName")
        outletreq_ids = data.get("storereqIds", [])

        if not outlet_purchase_id or not outlet_name:
            return {"error": "PurchaseReqID and outletName are required."}, 400

        # Check if the purchase exists
        sql_check = """
        SELECT `IDIntbl_PurchaseRequisition`
        FROM `intbl_purchaserequisition`
        WHERE `Outlet_PurchaseReqID` = %s AND `Outlet_Name` = %s
        """
        cursor.execute(sql_check, (outlet_purchase_id, outlet_name))
        result = cursor.fetchone()

        if not result:
            return {"error": "No purchase found for the given PurchaseReqID and outletName."}, 404

        purchase_id = result[0]
        
        # Check the State of the purchase
        cursor.execute("SELECT `State` FROM `intbl_purchaserequisition` WHERE `IDIntbl_PurchaseRequisition` = %s", (purchase_id,))
        purchase_state = cursor.fetchone()[0]

        # ============ 1. REVERSE STORE REQUISITION OPERATIONS (if any) ============
        if outletreq_ids:
            for outletreq_id in outletreq_ids:
                # Get store requisition details
                sql_check_store = """
                SELECT `idintblStoreRequisition`, `CostCenter`
                FROM `intblstorerequisition`
                WHERE `OutletREQID` = %s AND `Outlet` = %s
                """
                cursor.execute(sql_check_store, (outletreq_id, outlet_name))
                store_result = cursor.fetchone()

                if not store_result:
                    continue

                storereq_id = store_result[0]
                costcenter = store_result[1]
                
                # Get store items
                sql_get_store_items = """
                SELECT `ItemName`, `Amount`, `Rate`
                FROM `intblstorereqdetails`
                WHERE `StoreReqID` = %s
                """
                cursor.execute(sql_get_store_items, (storereq_id,))
                store_items = cursor.fetchall()
                
                # Reverse store operations: Add back to stock, remove from item_current_level
                for item in store_items:
                    item_name = item[0]
                    amount = float(item[1])
                    rate = float(item[2])
                    
                    # Add back to stock_current_level (reverse deduction)
                    cursor.execute("""
                        SELECT id, qty, total
                        FROM stock_current_level 
                        WHERE name = %s AND outlet = %s AND rate = %s
                        ORDER BY expiry_date ASC, id ASC
                        LIMIT 1
                    """, (item_name, outlet_name, rate))
                    
                    existing_batch = cursor.fetchone()
                    
                    if existing_batch:
                        batch_id = existing_batch[0]
                        new_qty = float(existing_batch[1]) + amount
                        new_total = new_qty * rate
                        cursor.execute("""
                            UPDATE stock_current_level 
                            SET qty = %s, total = %s 
                            WHERE id = %s
                        """, (new_qty, new_total, batch_id))
                    else:
                        cursor.execute("""
                            INSERT INTO stock_current_level (name, outlet, units, qty, expiry_date, rate, total)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, (item_name, outlet_name, "units", amount, None, rate, amount * rate))
                    
                    # Remove from item_current_level (reverse addition)
                    cursor.execute("""
                        SELECT quantity, id
                        FROM item_current_level
                        WHERE itemname = %s AND outlet = %s AND costcenter = %s
                    """, (item_name, outlet_name, costcenter))
                    
                    current_level = cursor.fetchone()
                    
                    if current_level:
                        current_qty = float(current_level[0])
                        level_id = current_level[1]
                        new_qty = current_qty - amount
                        
                        if new_qty <= 0:
                            cursor.execute("DELETE FROM item_current_level WHERE id = %s", (level_id,))
                        else:
                            cursor.execute("""
                                UPDATE item_current_level 
                                SET quantity = %s
                                WHERE id = %s
                            """, (new_qty, level_id))
                    
                    # ============ UPDATE stock_statement (ADD BACK stock for store reversal) ============
                    cursor.execute("""
                        SELECT CurrentLevel, Total
                        FROM stock_statement
                        WHERE ItemName = %s AND OutletName = %s
                    """, (item_name, outlet_name))
                    
                    stmt = cursor.fetchone()
                    
                    if stmt:
                        current_level = float(stmt[0])
                        current_total = float(stmt[1]) if stmt[1] else 0
                        
                        add_qty = amount
                        add_total = amount * rate
                        
                        new_level = current_level + add_qty
                        new_total = current_total + add_total
                        
                        cursor.execute("""
                            UPDATE stock_statement
                            SET CurrentLevel = %s,
                                Total = %s
                            WHERE ItemName = %s AND OutletName = %s
                        """, (
                            new_level,
                            new_total,
                            item_name,
                            outlet_name
                        ))
                    else:
                        # If missing, recreate row
                        cursor.execute("""
                            INSERT INTO stock_statement
                            (ItemName, OutletName, CurrentLevel, Total, Rate)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (
                            item_name,
                            outlet_name,
                            amount,
                            amount * rate,
                            rate
                        ))

                # Backup store requisition to deleted table
                sql_select_store = """
                SELECT `Date`, `CostCenter`, `Outlet`, `OutletREQID`
                FROM `intblstorerequisition`
                WHERE `idintblStoreRequisition` = %s
                """
                cursor.execute(sql_select_store, (storereq_id,))
                storereq_to_delete = cursor.fetchone()

                sql_insert_deleted_store = """
                INSERT INTO `deleted_storerequisition`
                (`Date`, `CostCenter`, `Outlet`, `OutletREQID`)
                VALUES (%s, %s, %s, %s)
                """
                cursor.execute(sql_insert_deleted_store, storereq_to_delete)
                deleted_storereq_id = cursor.lastrowid

                # Backup store details
                sql_select_details = """
                SELECT `ItemName`, `GroupName`, `BrandName`, `Amount`, `UOM`, `Rate`
                FROM `intblstorereqdetails`
                WHERE `StoreReqID` = %s
                """
                cursor.execute(sql_select_details, (storereq_id,))
                storereqdetails_to_delete = cursor.fetchall()

                sql_insert_deleted_details = """
                INSERT INTO `deletedstorereqdetails`
                (`ItemName`, `GroupName`, `BrandName`, `Amount`, `UOM`, `Rate`, `DeletedStoreReqID`)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                storereq_to_insert = [
                    (c[0], c[1], c[2], c[3], c[4], c[5], deleted_storereq_id)
                    for c in storereqdetails_to_delete
                ]
                cursor.executemany(sql_insert_deleted_details, storereq_to_insert)

                # Delete from original tables
                cursor.execute("DELETE FROM `intblstorereqdetails` WHERE `StoreReqID` = %s", (storereq_id,))
                cursor.execute("DELETE FROM `intblstorerequisition` WHERE `idintblStoreRequisition` = %s", (storereq_id,))

        # ============ 2. REVERSE PURCHASE REQUISITION OPERATIONS ============
        # Always reverse purchase if State was "Received"
        if purchase_state == "Received":
            # Get purchase items
            sql_get_purchase_items = """
            SELECT `Name`, `UnitsOrdered`, `Rate`
            FROM `intbl_purchaserequisition_contract`
            WHERE `PurchaseReqID` = %s
            """
            cursor.execute(sql_get_purchase_items, (purchase_id,))
            purchase_items = cursor.fetchall()

            # Remove from stock_current_level (reverse the original addition)
            for item in purchase_items:
                item_name = item[0]
                units_ordered = float(item[1])
                rate = float(item[2])
                
                # Get stock batches ordered by expiry (FIFO)
                cursor.execute("""
                    SELECT id, qty, total, rate
                    FROM stock_current_level 
                    WHERE name = %s AND outlet = %s AND qty > 0
                    ORDER BY expiry_date ASC, id ASC
                """, (item_name, outlet_name))
                
                stock_batches = cursor.fetchall()
                remaining_to_remove = units_ordered
                
                for batch in stock_batches:
                    if remaining_to_remove <= 0:
                        break
                        
                    batch_id = batch[0]
                    current_qty = float(batch[1])
                    current_total = float(batch[2])
                    current_rate = float(batch[3])
                    
                    if current_qty <= remaining_to_remove:
                        # Remove entire batch
                        new_qty = 0
                        new_total = 0
                        remaining_to_remove -= current_qty
                    else:
                        # Partially remove from batch
                        new_qty = current_qty - remaining_to_remove
                        new_total = new_qty * current_rate
                        remaining_to_remove = 0
                    
                    if new_qty == 0:
                        cursor.execute("DELETE FROM stock_current_level WHERE id = %s", (batch_id,))
                    else:
                        cursor.execute("""
                            UPDATE stock_current_level 
                            SET qty = %s, total = %s 
                            WHERE id = %s
                        """, (new_qty, new_total, batch_id))
                
                # ============ UPDATE stock_statement (REMOVE stock for purchase reversal) ============
                cursor.execute("""
                    SELECT CurrentLevel, Total
                    FROM stock_statement
                    WHERE ItemName = %s AND OutletName = %s
                """, (item_name, outlet_name))
                
                stock_stmt = cursor.fetchone()
                
                if stock_stmt:
                    current_level = float(stock_stmt[0])
                    current_total = float(stock_stmt[1]) if stock_stmt[1] else 0
                    
                    qty = units_ordered
                    deduction_total = qty * rate
                    
                    new_level = current_level - qty
                    new_total = current_total - deduction_total
                    
                    if new_level <= 0:
                        new_level = 0
                        new_total = 0
                    
                    cursor.execute("""
                        UPDATE stock_statement
                        SET CurrentLevel = %s,
                            Total = %s
                        WHERE ItemName = %s AND OutletName = %s
                    """, (
                        new_level,
                        new_total,
                        item_name,
                        outlet_name
                    ))

        # ============ 3. BACKUP AND DELETE PURCHASE REQUISITION ============
        # Backup purchase requisition
        sql_select_purchase = """
        SELECT `RequisitionType`, `Date`, `TotalAmount`, `TaxAmount`, `Company_Name`, `State`, 
               `ReceivedDate`, `purchaseBillNumber`, `DiscountAmount`, `Outlet_Name`, `GRN`, `Outlet_PurchaseReqID`
        FROM `intbl_purchaserequisition`
        WHERE `IDIntbl_PurchaseRequisition` = %s
        """
        cursor.execute(sql_select_purchase, (purchase_id,))
        purchase_to_delete = cursor.fetchone()

        sql_insert_purchase = """
        INSERT INTO `deleted_purchaserequisition`
        (`RequisitionType`, `Date`, `TotalAmount`, `TaxAmount`, `Company_Name`, `State`,
         `ReceivedDate`, `purchaseBillNumber`, `DiscountAmount`, `Outlet_Name`, `GRN`, `Outlet_PurchaseReqID`)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql_insert_purchase, purchase_to_delete)
        deleted_purchase_id = cursor.lastrowid

        # Backup purchase contract items
        sql_select_contract = """
        SELECT `ItemID`, `UnitsOrdered`, `PurchaseReqID`, `Rate`, `Name`, `BrandName`, `Code`, `UOM`, 
               `StockType`, `Department`, `GroupName`, `ExpDate`, `Status`, `Taxable`
        FROM `intbl_purchaserequisition_contract`
        WHERE `PurchaseReqID` = %s
        """
        cursor.execute(sql_select_contract, (purchase_id,))
        contracts_to_delete = cursor.fetchall()

        sql_insert_contract = """
        INSERT INTO `deleted_purchaserequisition_contract`
        (`ItemID`, `UnitsOrdered`, `DeletedPurchaseReqID`, `Rate`, `Name`, `BrandName`, `Code`, `UOM`,
         `StockType`, `Department`, `GroupName`, `ExpDate`, `Status`, `Taxable`)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        contracts_to_insert = [
            (c[0], c[1], deleted_purchase_id, c[3], c[4], c[5], c[6], c[7], c[8], c[9], c[10], c[11], c[12], c[13])
            for c in contracts_to_delete
        ]
        cursor.executemany(sql_insert_contract, contracts_to_insert)

        # Delete from original tables
        cursor.execute("DELETE FROM `intbl_purchaserequisition_contract` WHERE `PurchaseReqID` = %s", (purchase_id,))
        cursor.execute("DELETE FROM `intbl_purchaserequisition` WHERE `IDIntbl_PurchaseRequisition` = %s", (purchase_id,))

        # Commit all changes
        mydb.commit()

        return {
            "success": "Deleted record successfully. Stock levels reversed completely.",
            "details": {
                "purchase_reversed": purchase_state == "Received",
                "store_requisitions_reversed": len(outletreq_ids) if outletreq_ids else 0
            }
        }, 200

    except mysql.connector.Error as db_error:
        if mydb:
            mydb.rollback()
        return {"error": f"Database error: {str(db_error)}"}, 500
    except Exception as e:
        if mydb:
            mydb.rollback()
        return {"error": f"An unexpected error occurred: {str(e)}"}, 500
    finally:
        if mydb:
            mydb.close()


@app_file44.route("/deleteinventory_web", methods=['PUT'])
@cross_origin()
def delete_inventory_web():
    mydb = None
    try:
        # Connect to the database
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password'),
            database=os.getenv('database')
        )
        cursor = mydb.cursor(buffered=True)

        # Parse request data
        data = request.get_json()
        outlet_purchase_id = data.get("PurchaseReqID")
        outlet_name = data.get("outletName")

        

        # outletreq_ids = data.get("storereqIds", [])

        if not outlet_purchase_id or not outlet_name:
            return {"error": "PurchaseReqID and outletName are required."}, 400

        # Check if the purchase exists
        sql_check = """
        SELECT `IDIntbl_PurchaseRequisition`
        FROM `intbl_purchaserequisition`
        WHERE `IDIntbl_PurchaseRequisition` = %s AND `Outlet_Name` = %s 
        """
        cursor.execute(sql_check, (outlet_purchase_id, outlet_name))
        result = cursor.fetchone()

        if not result:
            return {"error": "No purchase found for the given PurchaseReqID and outletName."}, 404

        purchase_id = result[0]
        
        # Check the State of the purchase
        cursor.execute("SELECT `State` FROM `intbl_purchaserequisition` WHERE `IDIntbl_PurchaseRequisition` = %s", (purchase_id,))
        purchase_state = cursor.fetchone()[0]


        # ============ FETCH STORE REQUISITION IDs FROM DATABASE ============
        # Get all store requisition IDs linked to this purchase_id
        sql_get_storereqs = """
        SELECT `idintblStoreRequisition`
        FROM `intblstorerequisition`
        WHERE `purchase_id` = %s AND `Outlet` = %s
        """
        cursor.execute(sql_get_storereqs, (purchase_id, outlet_name))
        store_results = cursor.fetchall()
        
        # Extract store requisition IDs into a list
        outletreq_ids = [row[0] for row in store_results]


        # When transfer exists: reverse transfer (stock+100, item-100) THEN reverse purchase (stock-100)
        # Net effect: stock 0, item 0 (complete reversal of receive+transfer)

        # ============ 1. REVERSE STORE REQUISITION OPERATIONS (if any) ============
        if outletreq_ids:
            for outletreq_id in outletreq_ids:
                # Get store requisition details
                sql_check_store = """
                SELECT `idintblStoreRequisition`, `CostCenter`
                FROM `intblstorerequisition`
                WHERE `idintblStoreRequisition` = %s AND `Outlet` = %s
                """
                cursor.execute(sql_check_store, (outletreq_id, outlet_name))
                store_result = cursor.fetchone()

                if not store_result:
                    continue

                storereq_id = store_result[0]
                costcenter = store_result[1]
                
                # Get store items
                sql_get_store_items = """
                SELECT `ItemName`, `Amount`, `Rate`
                FROM `intblstorereqdetails`
                WHERE `StoreReqID` = %s
                """
                cursor.execute(sql_get_store_items, (storereq_id,))
                store_items = cursor.fetchall()
                
                # Reverse store operations: Add back to stock, remove from item_current_level
                for item in store_items:
                    item_name = item[0]
                    amount = float(item[1])
                    rate = float(item[2])
                    
                    # Add back to stock_current_level (reverse deduction)
                    cursor.execute("""
                        SELECT id, qty, total
                        FROM stock_current_level 
                        WHERE name = %s AND outlet = %s AND rate = %s
                        ORDER BY expiry_date ASC, id ASC
                        LIMIT 1
                    """, (item_name, outlet_name, rate))
                    
                    existing_batch = cursor.fetchone()
                    
                    if existing_batch:
                        batch_id = existing_batch[0]
                        new_qty = float(existing_batch[1]) + amount
                        new_total = new_qty * rate
                        cursor.execute("""
                            UPDATE stock_current_level 
                            SET qty = %s, total = %s 
                            WHERE id = %s
                        """, (new_qty, new_total, batch_id))
                    else:
                        cursor.execute("""
                            INSERT INTO stock_current_level (name, outlet, units, qty, expiry_date, rate, total)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, (item_name, outlet_name, "units", amount, None, rate, amount * rate))
                    
                    # Remove from item_current_level (reverse addition)
                    cursor.execute("""
                        SELECT quantity, id
                        FROM item_current_level
                        WHERE itemname = %s AND outlet = %s AND costcenter = %s
                    """, (item_name, outlet_name, costcenter))
                    
                    current_level = cursor.fetchone()
                    
                    if current_level:
                        current_qty = float(current_level[0])
                        level_id = current_level[1]
                        new_qty = current_qty - amount
                        
                        if new_qty <= 0:
                            cursor.execute("DELETE FROM item_current_level WHERE id = %s", (level_id,))
                        else:
                            cursor.execute("""
                                UPDATE item_current_level 
                                SET quantity = %s
                                WHERE id = %s
                            """, (new_qty, level_id))

                    # UPDATE stock_statement (ADD BACK stock)

                    cursor.execute("""
                        SELECT CurrentLevel, Total
                        FROM stock_statement
                        WHERE ItemName = %s AND OutletName = %s
                    """, (item_name, outlet_name))

                    stmt = cursor.fetchone()

                    if stmt:
                        current_level = float(stmt[0])
                        current_total = float(stmt[1]) if stmt[1] else 0

                        add_qty = amount
                        add_total = amount * rate

                        new_level = current_level + add_qty
                        new_total = current_total + add_total

                        cursor.execute("""
                            UPDATE stock_statement
                            SET CurrentLevel = %s,
                                Total = %s
                            WHERE ItemName = %s AND OutletName = %s
                        """, (
                            new_level,
                            new_total,
                            item_name,
                            outlet_name
                        ))
                    else:
                        # If missing, recreate row
                        cursor.execute("""
                            INSERT INTO stock_statement
                            (ItemName, OutletName, CurrentLevel, Total, Rate)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (
                            item_name,
                            outlet_name,
                            amount,
                            amount * rate,
                            rate
                        ))

                # Backup store requisition to deleted table
                sql_select_store = """
                SELECT `Date`, `CostCenter`, `Outlet`, `OutletREQID`
                FROM `intblstorerequisition`
                WHERE `idintblStoreRequisition` = %s
                """
                cursor.execute(sql_select_store, (storereq_id,))
                storereq_to_delete = cursor.fetchone()

                sql_insert_deleted_store = """
                INSERT INTO `deleted_storerequisition`
                (`Date`, `CostCenter`, `Outlet`, `OutletREQID`)
                VALUES (%s, %s, %s, %s)
                """
                cursor.execute(sql_insert_deleted_store, storereq_to_delete)
                deleted_storereq_id = cursor.lastrowid

                # Backup store details
                sql_select_details = """
                SELECT `ItemName`, `GroupName`, `BrandName`, `Amount`, `UOM`, `Rate`
                FROM `intblstorereqdetails`
                WHERE `StoreReqID` = %s
                """
                cursor.execute(sql_select_details, (storereq_id,))
                storereqdetails_to_delete = cursor.fetchall()

                sql_insert_deleted_details = """
                INSERT INTO `deletedstorereqdetails`
                (`ItemName`, `GroupName`, `BrandName`, `Amount`, `UOM`, `Rate`, `DeletedStoreReqID`)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                storereq_to_insert = [
                    (c[0], c[1], c[2], c[3], c[4], c[5], deleted_storereq_id)
                    for c in storereqdetails_to_delete
                ]
                cursor.executemany(sql_insert_deleted_details, storereq_to_insert)

                # Delete from original tables
                cursor.execute("DELETE FROM `intblstorereqdetails` WHERE `StoreReqID` = %s", (storereq_id,))
                cursor.execute("DELETE FROM `intblstorerequisition` WHERE `idintblStoreRequisition` = %s", (storereq_id,))

        # ============ 2. REVERSE PURCHASE REQUISITION OPERATIONS ============
        # Always reverse purchase if State was "Received"
        if purchase_state == "Received":
            # Get purchase items
            sql_get_purchase_items = """
            SELECT `Name`, `UnitsOrdered`, `Rate`
            FROM `intbl_purchaserequisition_contract`
            WHERE `PurchaseReqID` = %s
            """
            cursor.execute(sql_get_purchase_items, (purchase_id,))
            purchase_items = cursor.fetchall()

            # Remove from stock_current_level (reverse the original addition)
            for item in purchase_items:
                item_name = item[0]
                units_ordered = float(item[1])
                
                # Get stock batches ordered by expiry (FIFO)
                cursor.execute("""
                    SELECT id, qty, total, rate
                    FROM stock_current_level 
                    WHERE name = %s AND outlet = %s AND qty > 0
                    ORDER BY expiry_date ASC, id ASC
                """, (item_name, outlet_name))
                
                stock_batches = cursor.fetchall()
                remaining_to_remove = units_ordered
                
                for batch in stock_batches:
                    if remaining_to_remove <= 0:
                        break
                        
                    batch_id = batch[0]
                    current_qty = float(batch[1])
                    current_total = float(batch[2])
                    current_rate = float(batch[3])
                    
                    if current_qty <= remaining_to_remove:
                        # Remove entire batch
                        new_qty = 0
                        new_total = 0
                        remaining_to_remove -= current_qty
                    else:
                        # Partially remove from batch
                        new_qty = current_qty - remaining_to_remove
                        new_total = new_qty * current_rate
                        remaining_to_remove = 0
                    
                    if new_qty == 0:
                        cursor.execute("DELETE FROM stock_current_level WHERE id = %s", (batch_id,))

                            # new_level = 0
                            # new_total = 0
                    else:
                        cursor.execute("""
                            UPDATE stock_current_level 
                            SET qty = %s, total = %s 
                            WHERE id = %s
                        """, (new_qty, new_total, batch_id))


                # REVERSE stock_statement (summary table)

                cursor.execute("""
                        SELECT CurrentLevel, Total
                        FROM stock_statement
                        WHERE ItemName = %s AND OutletName = %s
                    """, (item_name, outlet_name))

                stock_stmt = cursor.fetchone()

                if stock_stmt:
                    current_level = float(stock_stmt[0])
                    current_total = float(stock_stmt[1]) if stock_stmt[1] else 0

                    qty = float(units_ordered)
                    rate = float(item[2])
                    deduction_total = qty * rate

                    new_level = current_level - qty
                    new_total = current_total - deduction_total

                    if new_level <= 0:

                        new_level = 0
                        new_total = 0
                    cursor.execute("""
                                UPDATE stock_statement
                                SET CurrentLevel = %s,
                                    Total = %s
                                WHERE ItemName = %s AND OutletName = %s
                            """, (
                                new_level,
                                new_total,
                                item_name,
                                outlet_name
                            ))

        # ============ 3. BACKUP AND DELETE PURCHASE REQUISITION ============
        # Backup purchase requisition
        sql_select_purchase = """
        SELECT `RequisitionType`, `Date`, `TotalAmount`, `TaxAmount`, `Company_Name`, `State`, 
               `ReceivedDate`, `purchaseBillNumber`, `DiscountAmount`, `Outlet_Name`, `GRN`, `Outlet_PurchaseReqID`
        FROM `intbl_purchaserequisition`
        WHERE `IDIntbl_PurchaseRequisition` = %s
        """
        cursor.execute(sql_select_purchase, (purchase_id,))
        purchase_to_delete = cursor.fetchone()

        sql_insert_purchase = """
        INSERT INTO `deleted_purchaserequisition`
        (`RequisitionType`, `Date`, `TotalAmount`, `TaxAmount`, `Company_Name`, `State`,
         `ReceivedDate`, `purchaseBillNumber`, `DiscountAmount`, `Outlet_Name`, `GRN`, `Outlet_PurchaseReqID`)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql_insert_purchase, purchase_to_delete)
        deleted_purchase_id = cursor.lastrowid

        # Backup purchase contract items
        sql_select_contract = """
        SELECT `ItemID`, `UnitsOrdered`, `PurchaseReqID`, `Rate`, `Name`, `BrandName`, `Code`, `UOM`, 
               `StockType`, `Department`, `GroupName`, `ExpDate`, `Status`, `Taxable`
        FROM `intbl_purchaserequisition_contract`
        WHERE `PurchaseReqID` = %s
        """
        cursor.execute(sql_select_contract, (purchase_id,))
        contracts_to_delete = cursor.fetchall()

        sql_insert_contract = """
        INSERT INTO `deleted_purchaserequisition_contract`
        (`ItemID`, `UnitsOrdered`, `DeletedPurchaseReqID`, `Rate`, `Name`, `BrandName`, `Code`, `UOM`,
         `StockType`, `Department`, `GroupName`, `ExpDate`, `Status`, `Taxable`)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        contracts_to_insert = [
            (c[0], c[1], deleted_purchase_id, c[3], c[4], c[5], c[6], c[7], c[8], c[9], c[10], c[11], c[12], c[13])
            for c in contracts_to_delete
        ]
        cursor.executemany(sql_insert_contract, contracts_to_insert)
        
        if purchase_state == "Received":
            # Get full purchase data to move to ordered_purchase table
            cursor.execute("""
                SELECT `RequisitionType`, `Date`, `TotalAmount`, `TaxAmount`, `Company_Name`, 
                    `ReceivedDate`, `purchaseBillNumber`, `DiscountAmount`, `Outlet_Name`, 
                    `GRN`, `Outlet_PurchaseReqID`, `purchase_id_ocular`, `company_pan`, 
                    `payment_mode`, `purchase_from`
                FROM `intbl_purchaserequisition`
                WHERE `IDIntbl_PurchaseRequisition` = %s
            """, (purchase_id,))
            purchase_data = cursor.fetchone()
            
            # Insert into ordered_purchase table using tuple indexes
            cursor.execute("""
                INSERT INTO `ordered_purchase`
                (`RequisitionType`, `Date`, `TotalAmount`, `TaxAmount`, `Company_Name`, 
                `State`, `ReceivedDate`, `ServerReceivedDate`, `purchaseBillNumber`, 
                `DiscountAmount`, `Outlet_Name`, `GRN`, `Outlet_PurchaseReqID`, 
                `purchase_id_ocular`, `company_pan`, `payment_mode`, `purchase_from`, 
                `original_purchase_id`, `created_at`)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """, (
                purchase_data[0],   # RequisitionType
                purchase_data[1],   # Date
                purchase_data[2],   # TotalAmount
                purchase_data[3],   # TaxAmount
                purchase_data[4],   # Company_Name
                'Ordered',          # State
                purchase_data[5],   # ReceivedDate
                None,               # ServerReceivedDate
                purchase_data[6],   # purchaseBillNumber
                purchase_data[7],   # DiscountAmount
                purchase_data[8],   # Outlet_Name
                purchase_data[9],   # GRN
                purchase_data[10],  # Outlet_PurchaseReqID
                purchase_data[11],  # purchase_id_ocular
                purchase_data[12],  # company_pan
                purchase_data[13],  # payment_mode
                purchase_data[14],  # purchase_from
                purchase_id         # original_purchase_id
            ))
            
            ordered_purchase_id = cursor.lastrowid
            
            # Move purchase contract items to ordered_purchaseitems
            cursor.execute("""
                SELECT `ItemID`, `UnitsOrdered`, `Rate`, `Name`, `BrandName`, `Code`, `UOM`, 
                    `StockType`, `Department`, `GroupName`, `ExpDate`, `Status`, `Taxable`
                FROM `intbl_purchaserequisition_contract`
                WHERE `PurchaseReqID` = %s
            """, (purchase_id,))
            contract_items = cursor.fetchall()
            
            # Insert items into ordered_purchaseitems using tuple indexes
            for item in contract_items:
                cursor.execute("""
                    INSERT INTO `ordered_purchaseitems`
                    (`ItemID`, `UnitsOrdered`, `OrderedPurchaseID`, `Rate`, `Name`, `BrandName`, 
                    `Code`, `UOM`, `StockType`, `Department`, `GroupName`, `ExpDate`, `Status`, 
                    `Taxable`, `created_at`)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                """, (
                    item[0],   # ItemID
                    item[1],   # UnitsOrdered
                    ordered_purchase_id,
                    item[2],   # Rate
                    item[3],   # Name
                    item[4],   # BrandName
                    item[5],   # Code
                    item[6],   # UOM
                    item[7],   # StockType
                    item[8],   # Department
                    item[9],   # GroupName
                    item[10],  # ExpDate
                    item[11],  # Status
                    item[12]   # Taxable
                ))

            # Delete from original tables
            cursor.execute("DELETE FROM `intbl_purchaserequisition_contract` WHERE `PurchaseReqID` = %s", (purchase_id,))
            cursor.execute("DELETE FROM `intbl_purchaserequisition` WHERE `IDIntbl_PurchaseRequisition` = %s", (purchase_id,))

        # else:


        # Commit all changes
        mydb.commit()

        return {
            "success": "Deleted record successfully. Stock levels reversed completely.",
            "details": {
                "purchase_reversed": purchase_state == "Received",
                "store_requisitions_reversed": len(outletreq_ids) if outletreq_ids else 0
            }
        }, 200

    except mysql.connector.Error as db_error:
        if mydb:
            mydb.rollback()
        return {"error": f"Database error: {str(db_error)}"}, 500
    except Exception as e:
        if mydb:
            mydb.rollback()
        return {"error": f"An unexpected error occurred: {str(e)}"}, 500
    finally:
        if mydb:
            mydb.close()


@app_file44.route("/deleteinventory/v4", methods=['PUT'])
@cross_origin()
def delete_inventory_v4():
    mydb = None
    try:
        # Connect to the database
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password'),
            database=os.getenv('database')
        )
        cursor = mydb.cursor(buffered=True)

        # Parse request data
        data = request.get_json()
        outlet_purchase_id = data.get("PurchaseReqID")
        outlet_name = data.get("outletName")
        outletreq_ids = data.get("storereqIds", [])

        if not outlet_purchase_id or not outlet_name:
            return {"error": "PurchaseReqID and outletName are required."}, 400

        # Check if the purchase exists
        sql_check = """
        SELECT `IDIntbl_PurchaseRequisition`
        FROM `intbl_purchaserequisition`
        WHERE `Outlet_PurchaseReqID` = %s AND `Outlet_Name` = %s
        """
        cursor.execute(sql_check, (outlet_purchase_id, outlet_name))
        result = cursor.fetchone()

        if not result:
            return {"error": "No purchase found for the given PurchaseReqID and outletName."}, 404

        purchase_id = result[0]
        
        # Check the State of the purchase
        cursor.execute("SELECT `State` FROM `intbl_purchaserequisition` WHERE `IDIntbl_PurchaseRequisition` = %s", (purchase_id,))
        purchase_state = cursor.fetchone()[0]

        # ============ 1. REVERSE STORE REQUISITION OPERATIONS (if any) ============
        if outletreq_ids:
            for outletreq_id in outletreq_ids:
                # Get store requisition details
                sql_check_store = """
                SELECT `idintblStoreRequisition`, `CostCenter`
                FROM `intblstorerequisition`
                WHERE `OutletREQID` = %s AND `Outlet` = %s
                """
                cursor.execute(sql_check_store, (outletreq_id, outlet_name))
                store_result = cursor.fetchone()

                if not store_result:
                    continue

                storereq_id = store_result[0]

                # Backup store requisition to deleted table
                sql_select_store = """
                SELECT `Date`, `CostCenter`, `Outlet`, `OutletREQID`
                FROM `intblstorerequisition`
                WHERE `idintblStoreRequisition` = %s
                """
                cursor.execute(sql_select_store, (storereq_id,))
                storereq_to_delete = cursor.fetchone()

                sql_insert_deleted_store = """
                INSERT INTO `deleted_storerequisition`
                (`Date`, `CostCenter`, `Outlet`, `OutletREQID`)
                VALUES (%s, %s, %s, %s)
                """
                cursor.execute(sql_insert_deleted_store, storereq_to_delete)
                deleted_storereq_id = cursor.lastrowid

                # Backup store details
                sql_select_details = """
                SELECT `ItemName`, `GroupName`, `BrandName`, `Amount`, `UOM`, `Rate`
                FROM `intblstorereqdetails`
                WHERE `StoreReqID` = %s
                """
                cursor.execute(sql_select_details, (storereq_id,))
                storereqdetails_to_delete = cursor.fetchall()

                sql_insert_deleted_details = """
                INSERT INTO `deletedstorereqdetails`
                (`ItemName`, `GroupName`, `BrandName`, `Amount`, `UOM`, `Rate`, `DeletedStoreReqID`)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                storereq_to_insert = [
                    (c[0], c[1], c[2], c[3], c[4], c[5], deleted_storereq_id)
                    for c in storereqdetails_to_delete
                ]
                cursor.executemany(sql_insert_deleted_details, storereq_to_insert)

                # Delete from original tables
                cursor.execute("DELETE FROM `intblstorereqdetails` WHERE `StoreReqID` = %s", (storereq_id,))
                cursor.execute("DELETE FROM `intblstorerequisition` WHERE `idintblStoreRequisition` = %s", (storereq_id,))

        # ============ 1. REVERSE PURCHASE REQUISITION OPERATIONS ============
        if purchase_state == "Received":
            # Get purchase items
            sql_get_purchase_items = """
            SELECT `Name`, `UnitsOrdered`, `Rate`, `UOM`, `GroupName`, `BrandName`
            FROM `intbl_purchaserequisition_contract`
            WHERE `PurchaseReqID` = %s
            """
            cursor.execute(sql_get_purchase_items, (purchase_id,))
            purchase_items = cursor.fetchall()
            
            for item in purchase_items:
                item_name = item[0]
                units_ordered = float(item[1])
                rate = float(item[2])
                uom = item[3]
                group_name = item[4]
                brand_name = item[5]
                
                # ============ DELETE all entries for this item from stock_current_level ============
                cursor.execute("""
                    DELETE FROM stock_current_level 
                    WHERE name = %s AND outlet = %s
                """, (item_name, outlet_name))
                
                deleted_count = cursor.rowcount
                print(f"Deleted {deleted_count} entries from stock_current_level for {item_name}")
                
                # ============ UPDATE stock_statement by subtracting (allow negative) ============
                cursor.execute("""
                    SELECT CurrentLevel, Total 
                    FROM stock_statement 
                    WHERE ItemName = %s AND UOM = %s AND OutletName = %s
                """, (item_name, uom, outlet_name))
                
                existing = cursor.fetchone()
                
                if existing:
                    current_level = float(existing[0])
                    current_total = float(existing[1]) if existing[1] else 0
                    
                    new_level = current_level - units_ordered
                    new_total = current_total - (units_ordered * rate)
                    
                    # Allow negative values - update even if negative
                    cursor.execute("""
                        UPDATE stock_statement
                        SET CurrentLevel = %s, Total = %s
                        WHERE ItemName = %s AND UOM = %s AND OutletName = %s
                    """, (new_level, new_total, item_name, uom, outlet_name))
                    
                    print(f"Updated stock_statement for {item_name}: {current_level} -> {new_level}")
                else:
                    # Create new record with negative values if doesn't exist
                    cursor.execute("""
                        INSERT INTO stock_statement 
                        (GroupName, ItemName, BrandName, UOM, CurrentLevel, Rate, OutletName, Total)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (group_name, item_name, brand_name, uom, -units_ordered, rate, outlet_name, -(units_ordered * rate)))
                    
                    print(f"Created new stock_statement record for {item_name} with negative value")

        # ============ 3. BACKUP AND DELETE PURCHASE REQUISITION ============
        # Backup purchase requisition
        sql_select_purchase = """
        SELECT `RequisitionType`, `Date`, `TotalAmount`, `TaxAmount`, `Company_Name`, `State`, 
               `ReceivedDate`, `purchaseBillNumber`, `DiscountAmount`, `Outlet_Name`, `GRN`, `Outlet_PurchaseReqID`
        FROM `intbl_purchaserequisition`
        WHERE `IDIntbl_PurchaseRequisition` = %s
        """
        cursor.execute(sql_select_purchase, (purchase_id,))
        purchase_to_delete = cursor.fetchone()

        sql_insert_purchase = """
        INSERT INTO `deleted_purchaserequisition`
        (`RequisitionType`, `Date`, `TotalAmount`, `TaxAmount`, `Company_Name`, `State`,
         `ReceivedDate`, `purchaseBillNumber`, `DiscountAmount`, `Outlet_Name`, `GRN`, `Outlet_PurchaseReqID`)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql_insert_purchase, purchase_to_delete)
        deleted_purchase_id = cursor.lastrowid

        # Backup purchase contract items
        sql_select_contract = """
        SELECT `ItemID`, `UnitsOrdered`, `PurchaseReqID`, `Rate`, `Name`, `BrandName`, `Code`, `UOM`, 
               `StockType`, `Department`, `GroupName`, `ExpDate`, `Status`, `Taxable`
        FROM `intbl_purchaserequisition_contract`
        WHERE `PurchaseReqID` = %s
        """
        cursor.execute(sql_select_contract, (purchase_id,))
        contracts_to_delete = cursor.fetchall()

        sql_insert_contract = """
        INSERT INTO `deleted_purchaserequisition_contract`
        (`ItemID`, `UnitsOrdered`, `DeletedPurchaseReqID`, `Rate`, `Name`, `BrandName`, `Code`, `UOM`,
         `StockType`, `Department`, `GroupName`, `ExpDate`, `Status`, `Taxable`)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        contracts_to_insert = [
            (c[0], c[1], deleted_purchase_id, c[3], c[4], c[5], c[6], c[7], c[8], c[9], c[10], c[11], c[12], c[13])
            for c in contracts_to_delete
        ]
        cursor.executemany(sql_insert_contract, contracts_to_insert)

        # Delete from original tables
        cursor.execute("DELETE FROM `intbl_purchaserequisition_contract` WHERE `PurchaseReqID` = %s", (purchase_id,))
        cursor.execute("DELETE FROM `intbl_purchaserequisition` WHERE `IDIntbl_PurchaseRequisition` = %s", (purchase_id,))

        # Commit all changes
        mydb.commit()

        return {
            "success": "Deleted record successfully. Stock levels reversed completely.",
            "details": {
                "purchase_reversed": purchase_state == "Received",
                "store_requisitions_reversed": len(outletreq_ids) if outletreq_ids else 0
            }
        }, 200

    except mysql.connector.Error as db_error:
        if mydb:
            mydb.rollback()
        return {"error": f"Database error: {str(db_error)}"}, 500
    except Exception as e:
        if mydb:
            mydb.rollback()
        return {"error": f"An unexpected error occurred: {str(e)}"}, 500
    finally:
        if mydb:
            mydb.close()