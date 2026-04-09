from flask import Blueprint, request
import mysql.connector
from flask_cors import CORS, cross_origin
import os
from dotenv import load_dotenv

load_dotenv()
app_file44 = Blueprint('app_file44', __name__)


# @app_file44.route("/deleteinventory", methods=['PUT'])
# @cross_origin()
# def stats():
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
#         if not outlet_purchase_id or not outlet_name:
#             return {"error": "PurchaseReqID and outletName are required."}, 400
        
#         # Check if purchases exist
#         sql_check = """
#         SELECT `IDIntbl_PurchaseRequisition` 
#         FROM `intbl_purchaserequisition` 
#         WHERE `Outlet_PurchaseReqID` = %s AND `Outlet_Name` = %s
#         """
#         cursor.execute(sql_check, (outlet_purchase_id, outlet_name))
#         result = cursor.fetchall()

#         if not result:
#             return {"error": "No purchases found for the given PurchaseReqID and outletName."}, 400
        
#         # Extract all matching IDs into a list
#         purchase_id_list = [row[0] for row in result]
        
#         # Delete from `intbl_purchaserequisition_contract` and `intbl_purchaserequisition`
#         placeholders = ', '.join(['%s'] * len(purchase_id_list))  # Create "%s, %s, %s"
#         sql_delete_contract = f"""
#         DELETE FROM `intbl_purchaserequisition_contract` 
#         WHERE `PurchaseReqID` IN ({placeholders})
#         """
#         sql_delete_purchase = f"""
#         DELETE FROM `intbl_purchaserequisition` 
#         WHERE `IDIntbl_PurchaseRequisition` IN ({placeholders})
#         """
        
#         # Use parameterized queries
#         cursor.execute(sql_delete_contract, purchase_id_list)
#         cursor.execute(sql_delete_purchase, purchase_id_list)

#         # Commit changes
#         mydb.commit()

#         return {"success": f"Deleted {len(purchase_id_list)} records successfully."}, 200
#     except mysql.connector.Error as db_error:
#         return {"error": f"Database error: {str(db_error)}"}, 500
#     except Exception as e:
#         return {"error": f"An unexpected error occurred: {str(e)}"}, 500
#     finally:
#         if mydb:
#             mydb.close()

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

        # Fetch and back up data to be deleted
        # Fetch from `intbl_purchaserequisition`
        sql_select_purchase = """
        SELECT `RequisitionType`, `Date`, `TotalAmount`, `TaxAmount`, `Company_Name`, `State`, 
               `ReceivedDate`, `purchaseBillNumber`, `DiscountAmount`, `Outlet_Name`, `GRN`, `Outlet_PurchaseReqID`
        FROM `intbl_purchaserequisition`
        WHERE `IDIntbl_PurchaseRequisition` = %s
        """
        cursor.execute(sql_select_purchase, (purchase_id,))
        purchase_to_delete = cursor.fetchone()

        # Insert into `deleted_purchaserequisition`
        sql_insert_purchase = """
        INSERT INTO `deleted_purchaserequisition`
        (`RequisitionType`, `Date`, `TotalAmount`, `TaxAmount`, `Company_Name`, `State`,
         `ReceivedDate`, `purchaseBillNumber`, `DiscountAmount`, `Outlet_Name`, `GRN`, `Outlet_PurchaseReqID`)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql_insert_purchase, purchase_to_delete)
        deleted_purchase_id = cursor.lastrowid  # Get the ID of the newly inserted record

        # Fetch from `intbl_purchaserequisition_contract`
        sql_select_contract = """
        SELECT `ItemID`, `UnitsOrdered`, `PurchaseReqID`, `Rate`, `Name`, `BrandName`, `Code`, `UOM`, 
               `StockType`, `Department`, `GroupName`, `ExpDate`, `Status`, `Taxable`
        FROM `intbl_purchaserequisition_contract`
        WHERE `PurchaseReqID` = %s
        """
        cursor.execute(sql_select_contract, (purchase_id,))
        contracts_to_delete = cursor.fetchall()

        # Insert into `deleted_purchaserequisition_contract`
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
        sql_delete_contract = "DELETE FROM `intbl_purchaserequisition_contract` WHERE `PurchaseReqID` = %s"
        sql_delete_purchase = "DELETE FROM `intbl_purchaserequisition` WHERE `IDIntbl_PurchaseRequisition` = %s"
        cursor.execute(sql_delete_contract, (purchase_id,))
        cursor.execute(sql_delete_purchase, (purchase_id,))

        # Commit transaction
        mydb.commit()

        return {"success": "Deleted record successfully."}, 200

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