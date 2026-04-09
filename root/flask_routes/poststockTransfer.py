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

        insert_storerequisitionSql = """ Insert into intblstorerequisition (`Date`, `CostCenter`, `Outlet`, `OutletREQID`) values (%s,%s,%s,%s)"""

        cursor.execute(insert_storerequisitionSql, (formatted_date,store_requisition["CostCenter"], store_requisition["OutletName"],store_requisition["Outlet_Req_ID"],))

        # Get the id of the last inserted record in intblstorerequisition
        store_req_id = cursor.lastrowid

        for item in store_itemdetails:

            insert_storerequisitiondetailsSql = """ Insert into intblstorereqdetails (`ItemName`, `GroupName`, `BrandName`, `Amount`, `UOM`, `Rate`, `StoreReqID`) values (%s,%s,%s,%s,%s,%s,%s)"""


            cursor.execute(insert_storerequisitiondetailsSql, (item["ItemName"], item["GroupName"], item["BrandName"], item["Amount"], item["UOM"], item["Rate"], store_req_id,))


        # Commit the transaction to save changes
        mydb.commit()

        # Return a success response
        return jsonify({"status": "success", "message": "Stock transfer request added successfully!"})
    
    except Exception as e:

        data = {"error": str(e)}
        return data, 400
    
    finally:
        mydb.close()