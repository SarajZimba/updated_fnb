from flask import  Blueprint,request, jsonify
import mysql.connector
from flask_cors import  cross_origin
import os
from dotenv import load_dotenv
load_dotenv()
app_file229= Blueprint('app_file229',__name__)

from datetime import datetime

@app_file229.route("/ordered_purchase", methods=["POST"])
@cross_origin()
def ordered_purchase_post():
    try:
        # Get today's date as a string in 'YYYY-MM-DD' format
        today_str = datetime.today().strftime('%Y-%m-%d')
        mydb = mysql.connector.connect(
            host=os.getenv('host'), 
            user=os.getenv('user'), 
            password=os.getenv('password')
        )
        cursor = mydb.cursor(buffered=True)
        database_sql = "USE {};".format(os.getenv('database'))
        cursor.execute(database_sql)
        data = request.get_json()
        
        # Get purchase_from from request data
        purchase_from = data.get("purchase_from", "c_app")
        outlet_name = data.get("Outlet_Name")
        
        # Handle automatic increment for web
        if purchase_from == "web":
            # Get the maximum Outlet_PurchaseReqID and increment
            cursor.execute("""
                SELECT MAX(Outlet_PurchaseReqID) 
                FROM ordered_purchase 
                WHERE Outlet_Name = %s AND purchase_from = 'web'
            """, (outlet_name,))
            max_purchase_id = cursor.fetchone()[0]
            if max_purchase_id is None:
                purchase_requisition_id = 1
            else:
                purchase_requisition_id = max_purchase_id + 1
            
            # Get the maximum GRN and increment
            cursor.execute("""
                SELECT MAX(GRN) 
                FROM ordered_purchase 
                WHERE Outlet_Name = %s AND purchase_from = 'web'
            """, (outlet_name,))
            max_grn = cursor.fetchone()[0]
            if max_grn is None:
                grn = 1
            else:
                grn = max_grn + 1
        else:
            # For c_app, use values from request
            purchase_requisition_id = data["PurchaseRequistionID"]
            grn = data["GRN"]
        
        # Insert into ordered_purchase table (master)
        sql_master = """
        INSERT INTO `ordered_purchase` 
        (Outlet_PurchaseReqID, RequisitionType, Date, TotalAmount, TaxAmount, Company_Name, 
         State, ReceivedDate, ServerReceivedDate, purchaseBillNumber, DiscountAmount, 
         Outlet_Name, GRN, purchase_id_ocular, purchase_from, company_pan, payment_mode, 
         original_purchase_id, created_at)
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # Insert into ordered_purchaseitems table (details)
        sql_details = """
        INSERT INTO `ordered_purchaseitems`    
        (ItemID, UnitsOrdered, OrderedPurchaseID, Rate, Name, BrandName, Code, UOM, 
         StockType, Department, GroupName, ExpDate, Status, Taxable, created_at) 
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # Execute master insert
        cursor.execute(
            sql_master,
            (
                purchase_requisition_id,
                data["RequisitionType"],
                data["Date"],
                data["TotalAmount"],
                data["TaxAmount"],
                data.get("Company_Name", None),
                "Ordered",  # Force state to "Ordered"
                data.get("ReceivedDate", None),  # May be NULL for ordered purchases
                today_str,  # ServerReceivedDate
                data.get("purchaseBillNumber", None),
                data.get("DiscountAmount", None),
                data["Outlet_Name"],
                grn,
                data.get("purchase_id_ocular", None),
                purchase_from,
                data.get("company_pan", None),
                data.get("payment_mode", None),
                data.get("original_purchase_id", None),  # Track original ID if moving from main table
                today_str  # created_at
            ),
        )
        
        # Get the auto-generated ID from ordered_purchase
        ordered_purchase_id = cursor.lastrowid
        
        # Insert all items into ordered_purchaseitems
        for item in data["RequisitionDetailsList"]:
            listitem = (
                item.get("ItemID", None),
                item["UnitsOrdered"],
                ordered_purchase_id,  # Use the ordered_purchase ID as foreign key
                item["Rate"],
                item["Name"],
                item.get("BrandName", ""),
                item.get("Code", ""),
                item.get("UOM", ""),
                item.get("StockType", ""),
                item.get("Department", ""),
                item.get("GroupName", ""),
                item.get("ExpDate", None),
                item.get("Status", ""),
                item.get("Taxable", "No"),
                today_str  # created_at
            )
            cursor.execute(sql_details, listitem)
        
        # Commit all changes
        mydb.commit()
        
        # Return success with generated IDs for web
        if purchase_from == "web":
            response = {
                "success": "Ordered purchase created successfully.",
                "ordered_purchase_id": ordered_purchase_id,
                "outlet_purchase_req_id": purchase_requisition_id,
                "grn": grn,
                "state": "Ordered"
            }
        else:
            response = {
                "success": "Ordered purchase created successfully.",
                "ordered_purchase_id": ordered_purchase_id,
                "state": "Ordered"
            }
            
        return jsonify(response), 200
        
    except Exception as error:
        if mydb:
            mydb.rollback()
        return jsonify({'error': str(error)}), 400
        
    finally:
        if mydb:
            mydb.close()


@app_file229.route("/ordered_purchase/get_by_outlet", methods=["POST"])
@cross_origin()
def get_ordered_purchases_by_outlet():
    """Get all ordered purchases for an outlet (outlet_name in request body)"""
    try:
        mydb = mysql.connector.connect(
            host=os.getenv('host'), 
            user=os.getenv('user'), 
            password=os.getenv('password')
        )
        cursor = mydb.cursor(dictionary=True, buffered=True)
        cursor.execute(f"USE {os.getenv('database')}")
        
        # Get outlet_name from request body
        data = request.get_json()
        outlet_name = data.get("outlet_name")
        
        if not outlet_name:
            return jsonify({"error": "outlet_name is required"}), 400
        
        cursor.execute("""
            SELECT * FROM ordered_purchase 
            WHERE Outlet_Name = %s 
            ORDER BY created_at DESC
        """, (outlet_name,))
        
        purchases = cursor.fetchall()
        
        # Get items for each purchase
        for purchase in purchases:
            cursor.execute("""
                SELECT * FROM ordered_purchaseitems 
                WHERE OrderedPurchaseID = %s
            """, (purchase['IDOrdered_Purchase'],))
            purchase['items'] = cursor.fetchall()
        
        return jsonify(purchases), 200
        
    except Exception as error:
        return jsonify({'error': str(error)}), 400
    finally:
        if mydb:
            mydb.close()