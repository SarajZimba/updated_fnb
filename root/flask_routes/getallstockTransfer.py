from flask import Flask, Blueprint, request, jsonify
import mysql.connector
from flask_cors import cross_origin

import os

from dotenv import load_dotenv

load_dotenv()


app_file59 = Blueprint('appfile_59', __name__)


@app_file59.route('/getAllStockTransfers', methods=["GET"])
@cross_origin()
def getAllStockTransfers():
    try:
        mydb = mysql.connector.connect(user=os.getenv('user'), password=os.getenv('password'), host=os.getenv('host'))

        cursor = mydb.cursor(buffered=True)

        # Use the correct database
        database_sql = "USE {};".format(os.getenv('database'))
        cursor.execute(database_sql)

        # Query to get all stock requisition data
        query_storerequisition = """
            SELECT `idintblStoreRequisition`, `Date`, `CostCenter`, `Outlet`, `OutletREQID`
            FROM `intblstorerequisition`
        """
        cursor.execute(query_storerequisition)
        store_requisitions = cursor.fetchall()

        if not store_requisitions:
            return jsonify({"error": "No stock requisitions found!"}), 404

        all_requisitions = []

        for store_requisition in store_requisitions:
            store_req_id = store_requisition[0]
            store_requisition_data = {
                "ItemDetailsList": [],
                "OutletName": store_requisition[3],
                "CostCenter": store_requisition[2],
                "Date": store_requisition[1].strftime('%Y-%m-%dT%H:%M:%S'),
                "Outlet_Req_ID": store_requisition[4]
            }

            # Query to get the item details for the specific store requisition
            query_storereqdetails = """
                SELECT `ItemName`, `GroupName`, `BrandName`, `Amount`, `UOM`, `Rate`
                FROM `intblstorereqdetails`
                WHERE `StoreReqID` = %s
            """
            cursor.execute(query_storereqdetails, (store_req_id,))
            store_itemdetails = cursor.fetchall()

            for item in store_itemdetails:
                store_requisition_data["ItemDetailsList"].append({
                    "ItemName": item[0],
                    "GroupName": item[1],
                    "BrandName": item[2],
                    "Amount": float(item[3]),
                    "UOM": item[4],
                    "Rate": float(item[5])
                })

            # Add this requisition's data to the overall list
            all_requisitions.append(store_requisition_data)

        return jsonify(all_requisitions)

    except Exception as e:
        data = {"error": str(e)}
        return data, 400

    finally:
        mydb.close()
