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

        outletreq_ids = data.get("storereqIds")

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


        if outletreq_ids:

            for outletreq_id in outletreq_ids:
                # Check if the purchase exists
                sql_check = """
                SELECT `idintblStoreRequisition`
                FROM `intblstorerequisition`
                WHERE `OutletREQID` = %s AND `Outlet` = %s
                """
                cursor.execute(sql_check, (outletreq_id, outlet_name))
                result = cursor.fetchone()

                if not result:
                    continue  # skip this outletreq_id if not found

                storereq_id = result[0]

                # Fetch from `intblstorerequisition`
                sql_select_purchase = """
                SELECT `Date`, `CostCenter`, `Outlet`, `OutletREQID`
                FROM `intblstorerequisition`
                WHERE `idintblStoreRequisition` = %s
                """
                cursor.execute(sql_select_purchase, (storereq_id,))
                storereq_to_delete = cursor.fetchone()

                # Insert into `deleted_storerequisition`
                sql_insert_purchase = """
                INSERT INTO `deleted_storerequisition`
                (`Date`, `CostCenter`, `Outlet`, `OutletREQID`)
                VALUES (%s, %s, %s, %s)
                """
                cursor.execute(sql_insert_purchase, storereq_to_delete)
                deleted_storereq_id = cursor.lastrowid  # Get the ID of the newly inserted record

                # Fetch from `intblstorereqdetails`
                sql_select_contract = """
                SELECT `ItemName`, `GroupName`, `BrandName`, `Amount`, `UOM`, `Rate`
                FROM `intblstorereqdetails`
                WHERE `StoreReqID` = %s
                """
                cursor.execute(sql_select_contract, (storereq_id,))
                storereqdetails_to_delete = cursor.fetchall()

                # Insert into `deleted_purchaserequisition_contract`
                sql_insert_contract = """
                INSERT INTO `deletedstorereqdetails`
                (`ItemName`, `GroupName`, `BrandName`, `Amount`, `UOM`, `Rate`, `DeletedStoreReqID`)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                storereq_to_insert = [
                    (c[0], c[1], c[2], c[3], c[4], c[5], deleted_storereq_id)
                    for c in storereqdetails_to_delete
                ]
                cursor.executemany(sql_insert_contract, storereq_to_insert)

                # Delete from original tables
                sql_delete_contract = "DELETE FROM `intblstorereqdetails` WHERE `StoreReqID` = %s"
                sql_delete_purchase = "DELETE FROM `intblstorerequisition` WHERE `idintblStoreRequisition` = %s"
                cursor.execute(sql_delete_contract, (storereq_id,))
                cursor.execute(sql_delete_purchase, (storereq_id,)) 

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