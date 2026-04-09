from flask import Blueprint, request
import mysql.connector
from flask_cors import CORS, cross_origin
import os
from dotenv import load_dotenv

load_dotenv()
app_file61 = Blueprint('app_file61', __name__)


@app_file61.route("/deleterequisition", methods=['PUT'])
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
        outletreq_id = data.get("ReqID")
        outlet_name = data.get("outletName")

        if not outletreq_id or not outlet_name:
            return {"error": "ReqID and outletName are required."}, 400

        # Check if the purchase exists
        sql_check = """
        SELECT `idintblStoreRequisition`
        FROM `intblstorerequisition`
        WHERE `OutletREQID` = %s AND `Outlet` = %s
        """
        cursor.execute(sql_check, (outletreq_id, outlet_name))
        result = cursor.fetchone()

        if not result:
            return {"error": "No stock found for the given OutletReqID and outletName."}, 404

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

