from flask import  Blueprint,request
import mysql.connector
from flask_cors import  cross_origin
import os
from dotenv import load_dotenv
load_dotenv()
app_file12= Blueprint('app_file12',__name__)

from datetime import datetime


# @app_file12.route("/req", methods=["POST"])
# @cross_origin()
# def purchasereqPost():
#     try:
#         # Get today's date as a string in 'YYYY-MM-DD' format
#         today_str = datetime.today().strftime('%Y-%m-%d')
#         mydb = mysql.connector.connect(host=os.getenv('host'), user=os.getenv('user'), password=os.getenv('password'))
#         cursor = mydb.cursor(buffered=True)
#         database_sql = "USE {};".format(os.getenv('database'))
#         cursor.execute(database_sql)
#         data = request.get_json()
#         # sql = f"""INSERT INTO `intbl_purchaserequisition` (Outlet_PurchaseReqID,RequisitionType,Date,TotalAmount,TaxAmount,Company_Name,State,ReceivedDate,purchaseBillNumber,DiscountAmount,Outlet_Name,GRN)
#         # VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
#         # """
#         sql = f"""INSERT INTO `intbl_purchaserequisition` (Outlet_PurchaseReqID,RequisitionType,Date,TotalAmount,TaxAmount,Company_Name,State,ReceivedDate,ServerReceivedDate,purchaseBillNumber,DiscountAmount,Outlet_Name,GRN, purchase_id_ocular)
#         VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s)
#         """
#         sql2 = f"""
#         INSERT INTO `intbl_purchaserequisition_contract`    (ItemID,UnitsOrdered,PurchaseReqID,Rate,Name,BrandName,Code,UOM,StockType,Department,GroupName,ExpDate,Status,Taxable) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)   """
#         cursor.execute(
#             sql,
#             (
#                 data["PurchaseRequistionID"],
#                 data["RequisitionType"],
#                 data["Date"],
#                 data["TotalAmount"],
#                 data["TaxAmount"],
#                 data["Company_Name"],
#                 data["State"],
#                 data["ReceivedDate"],
#                 today_str,
#                 data["purchaseBillNumber"],
#                 data["DiscountAmount"],
#                 data["Outlet_Name"],
#                 data["GRN"],
#                 data.get("purchase_id_ocular", None)

#             ),
#         )
#         mydb.commit()

#         # Prepare list for stock_current_level entries
#         current_level_entries = []
#         purchase_req_id = cursor.lastrowid

#         state = data.get("State", "")

#         for item in data["RequisitionDetailsList"]:
#             listitem = (
#                 item["ItemID"],
#                 item["UnitsOrdered"],
#                 purchase_req_id,
#                 item["Rate"],
#                 item["Name"],
#                 item["BrandName"],
#                 item["Code"],
#                 item["UOM"],
#                 item["StockType"],
#                 item["Department"],
#                 item["GroupName"],
#                 item["ExpDate"],
#                 item["Status"],
#                 item["Taxable"],
#             )
#             try:
#                 cursor.execute(sql2, listitem)

#                 # Only add to stock_current_level if State is "Received"
#                 if state == "Received":
#                     # Calculate total for this item
#                     item_total = float(item["UnitsOrdered"]) * float(item["Rate"])
                    
#                     current_level_entries.append((
#                         item["Name"],           # name
#                         data["Outlet_Name"],
#                         item["UOM"],            # units (using UOM from purchase)
#                         item["UnitsOrdered"],   # qty (units ordered/purchased)
#                         item.get("ExpDate"),    # expiry_date
#                         item["Rate"],           # rate
#                         item_total              # total
#                     ))
#                 mydb.commit()
#             except Exception as e:
#                 data={"error":str(e)}
#                 return data,400
            
#         # Only insert into stock_current_level if there are entries (meaning State is "Received")
#         if current_level_entries:
#             sql3 = """
#             INSERT INTO stock_current_level (name, outlet, units, qty, expiry_date, rate, total)
#             VALUES (%s, %s, %s, %s, %s, %s, %s)
#             """
#             cursor.executemany(sql3, current_level_entries)
#             mydb.commit()
#         mydb.close()
#         data ={"success":"Data posted successfully."}
#         return data,200
#     except Exception as error:
#         data ={'error':str(error)}
#         return data,400



from flask import Blueprint, request, jsonify
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv
load_dotenv()
app_file12 = Blueprint('app_file12', __name__)

from datetime import datetime


@app_file12.route("/req", methods=["POST"])
@cross_origin()
def purchasereqPost():
    try:
        # Get today's date as a string in 'YYYY-MM-DD' format
        today_str = datetime.today().strftime('%Y-%m-%d')
        mydb = mysql.connector.connect(host=os.getenv('host'), user=os.getenv('user'), password=os.getenv('password'))
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
            cursor.execute("SELECT MAX(Outlet_PurchaseReqID) FROM intbl_purchaserequisition where Outlet_Name = %s and purchase_from = 'web' ", (outlet_name,))
            max_purchase_id = cursor.fetchone()[0]
            if max_purchase_id is None:
                purchase_requisition_id = 1
            else:
                purchase_requisition_id = max_purchase_id + 1
            
            # Get the maximum GRN and increment
            cursor.execute("SELECT MAX(GRN) FROM intbl_purchaserequisition where Outlet_Name = %s and purchase_from = 'web' ", (outlet_name,))
            max_grn = cursor.fetchone()[0]
            if max_grn is None:
                grn = 1
            else:
                grn = max_grn + 1
        else:
            # For c_app, use values from request
            purchase_requisition_id = data["PurchaseRequistionID"]
            grn = data["GRN"]
        
        # Updated SQL with purchase_from field
        sql = f"""INSERT INTO `intbl_purchaserequisition` 
        (Outlet_PurchaseReqID, RequisitionType, Date, TotalAmount, TaxAmount, Company_Name, 
         State, ReceivedDate, ServerReceivedDate, purchaseBillNumber, DiscountAmount, 
         Outlet_Name, GRN, purchase_id_ocular, purchase_from, company_pan, payment_mode)
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        sql2 = f"""
        INSERT INTO `intbl_purchaserequisition_contract`    
        (ItemID, UnitsOrdered, PurchaseReqID, Rate, Name, BrandName, Code, UOM, 
         StockType, Department, GroupName, ExpDate, Status, Taxable) 
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(
            sql,
            (
                purchase_requisition_id,  # Use auto-incremented or provided value
                data["RequisitionType"],
                data["Date"],
                data["TotalAmount"],
                data["TaxAmount"],
                data.get("Company_Name", None),
                data["State"],
                data["ReceivedDate"],
                today_str,
                data["purchaseBillNumber"],
                data["DiscountAmount"],
                data["Outlet_Name"],
                grn,  # Use auto-incremented or provided value
                data.get("purchase_id_ocular", None),
                purchase_from,
                data.get("company_pan", None),
                data.get("payment_mode", None)
            ),
        )
        mydb.commit()

        # Prepare list for stock_current_level entries
        current_level_entries = []
        purchase_req_id = cursor.lastrowid
        state = data.get("State", "")

        for item in data["RequisitionDetailsList"]:
            listitem = (
                item["ItemID"],
                item["UnitsOrdered"],
                purchase_req_id,
                item["Rate"],
                item["Name"],
                item["BrandName"],
                item["Code"],
                item["UOM"],
                item["StockType"],
                item["Department"],
                item["GroupName"],
                item["ExpDate"],
                item["Status"],
                item["Taxable"],
            )
            try:
                cursor.execute(sql2, listitem)

                # Only add to stock_current_level if State is "Received"
                if state == "Received":
                    # Calculate total for this item
                    item_total = float(item["UnitsOrdered"]) * float(item["Rate"])
                    
                    # if item["StockType"] == "Stockable" :

                    # Update stock_statement
                    cursor.execute("""
                        SELECT CurrentLevel 
                        FROM stock_statement 
                        WHERE ItemName = %s AND UOM = %s AND OutletName = %s
                    """, (item["Name"], item["UOM"], data["Outlet_Name"]))

                    existing = cursor.fetchone()

                    if existing:
                        # Update existing stock
                        cursor.execute("""
                            UPDATE stock_statement
                            SET CurrentLevel = CurrentLevel + %s, Rate=%s
                            WHERE ItemName = %s AND UOM = %s AND OutletName = %s
                        """, (item["UnitsOrdered"], item["Rate"], item["Name"], item["UOM"], data["Outlet_Name"]))
                    else:
                        # Insert new stock entry
                        cursor.execute("""
                            INSERT INTO stock_statement 
                            (GroupName, ItemName, BrandName, UOM, CurrentLevel, Rate, OutletName)
                            VALUES (%s, %s, %s, %s, %s, %s ,%s)
                        """, (
                            item["GroupName"],
                            item["Name"],
                            item["BrandName"],
                            item["UOM"],
                            item["UnitsOrdered"],
                            item["Rate"],
                            data["Outlet_Name"]
                        ))


                    # if item.get("ExpDate", None):
                    current_level_entries.append((
                                item["Name"],           # name
                                data["Outlet_Name"],
                                item["UOM"],            # units
                                item["UnitsOrdered"],   # qty
                                item.get("ExpDate") if item.get("ExpDate") else None,    # expiry_date
                                item["Rate"],           # rate
                                item_total,             # total
                                purchase_req_id
                            ))


                mydb.commit()
            except Exception as e:
                data = {"error": str(e)}
                return data, 400
            
        # Only insert into stock_current_level if there are entries
        if current_level_entries:
            sql3 = """
            INSERT INTO stock_current_level (name, outlet, units, qty, expiry_date, rate, total, purchase_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.executemany(sql3, current_level_entries)
            mydb.commit()
            
        mydb.close()
        
        # Return success with generated IDs for web
        if purchase_from == "web":
            data = {
                "success": "Data posted successfully.",
                "purchase_requisition_id": purchase_req_id,
                "grn": grn
            }
        else:
            data = {"success": "Data posted successfully."}
            
        return data, 200
    except Exception as error:
        data = {'error': str(error)}
        return data, 400




# @app_file12.route("/getOrderedPurchases", methods=["POST"])
# @cross_origin()
# def get_ordered_purchases():
#     try:
#         mydb = mysql.connector.connect(
#             host=os.getenv('host'),
#             user=os.getenv('user'),
#             password=os.getenv('password')
#         )
#         cursor = mydb.cursor(dictionary=True)
        
#         database_sql = "USE {};".format(os.getenv('database'))
#         cursor.execute(database_sql)
        
#         # Get data from request body
#         data = request.get_json()
        
#         if not data:
#             return jsonify({"error": "Request body is required"}), 400
        
#         # Get filter parameters from body
#         outlet_name = data.get('outlet_name')
#         company_name = data.get('company_name')
#         from_date = data.get('from_date')
#         to_date = data.get('to_date')
#         page = data.get('page', 1)
#         limit = data.get('limit', 10)
        
#         if not outlet_name:
#             return jsonify({"error": "outlet_name is required"}), 400
        
#         # Calculate offset for pagination
#         offset = (int(page) - 1) * int(limit)
        
#         # Build query for total count
#         count_sql = """
#         SELECT COUNT(*) as total 
#         FROM intbl_purchaserequisition 
#         WHERE State IN ('Ordered','Received') AND Outlet_Name = %s
#         """
        
#         count_params = [outlet_name]
        
#         if company_name:
#             count_sql += " AND Company_Name = %s"
#             count_params.append(company_name)
        
#         if from_date:
#             count_sql += " AND Date >= %s"
#             count_params.append(from_date)
        
#         if to_date:
#             count_sql += " AND Date <= %s"
#             count_params.append(to_date)
        
#         cursor.execute(count_sql, count_params)
#         total_count = cursor.fetchone()['total']
        
#         # Build main query
#         sql = """
#         SELECT *
#         FROM intbl_purchaserequisition 
#         WHERE State IN ('Ordered','Received') AND Outlet_Name = %s AND purchase_from = 'web'
#         """
        
#         params = [outlet_name]
        
#         if company_name:
#             sql += " AND Company_Name = %s"
#             params.append(company_name)
        
#         if from_date:
#             sql += " AND Date >= %s"
#             params.append(from_date)
        
#         if to_date:
#             sql += " AND Date <= %s"
#             params.append(to_date)
        
#         sql += " ORDER BY Date DESC LIMIT %s OFFSET %s"
#         params.append(int(limit))
#         params.append(offset)
        
#         cursor.execute(sql, params)
#         purchases = cursor.fetchall()
        
#         # Get purchase details (items) for each purchase
#         for purchase in purchases:
#             items_sql = """
#             SELECT 
#                 *
#             FROM intbl_purchaserequisition_contract
#             WHERE PurchaseReqID = %s
#             """
#             cursor.execute(items_sql, (purchase['IDIntbl_PurchaseRequisition'],))
#             items = cursor.fetchall()
#             purchase['items'] = items
            
#             # # Calculate summary
#             # purchase['total_items_count'] = len(items)
#             # purchase['total_units_ordered'] = sum(float(item['UnitsOrdered']) for item in items)
#             # purchase['subtotal'] = sum(float(item['total_amount']) for item in items)
        
#         mydb.close()
        
#         return jsonify({
#             "success": True,
#             "outlet_name": outlet_name,
#             "filters_applied": {
#                 "company_name": company_name,
#                 "from_date": from_date,
#                 "to_date": to_date
#             },
#             "pagination": {
#                 "current_page": int(page),
#                 "limit": int(limit),
#                 "total_count": total_count,
#                 "total_pages": (total_count + int(limit) - 1) // int(limit)
#             },
#             "count": len(purchases),
#             "purchases": purchases
#         }), 200
        
#     except Exception as e:
#         return jsonify({"error": str(e)}), 400

@app_file12.route("/getOrderedPurchases", methods=["POST"])
@cross_origin()
def get_ordered_purchases():
    try:
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password')
        )
        cursor = mydb.cursor(dictionary=True)
        
        database_sql = "USE {};".format(os.getenv('database'))
        cursor.execute(database_sql)
        
        # Get data from request body
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        # Get filter parameters from body
        outlet_name = data.get('outlet_name')
        company_name = data.get('company_name')
        from_date = data.get('from_date')
        to_date = data.get('to_date')
        grn = data.get('grn')
        bill_number = data.get('bill_number')
        purchase_id = data.get('purchase_id')
        state = data.get('state')  # Allow filtering by specific state (Ordered/Received)
        page = data.get('page', 1)
        limit = data.get('limit', 10)
        
        if not outlet_name:
            return jsonify({"error": "outlet_name is required"}), 400
        
        # Calculate offset for pagination
        offset = (int(page) - 1) * int(limit)
        
        # Base conditions
        conditions = ["State IN ('Ordered','Received')", "Outlet_Name = %s"]
        params = [outlet_name]
        
        # Override state filter if specific state is provided
        if state:
            conditions = [f"State = %s", "Outlet_Name = %s"]
            params = [state, outlet_name]
        
        # Add optional filters
        if company_name:
            conditions.append("Company_Name = %s")
            params.append(company_name)
        
        if from_date:
            conditions.append("Date >= %s")
            params.append(from_date)
        
        if to_date:
            conditions.append("Date <= %s")
            params.append(to_date)
        
        if grn:
            conditions.append("GRN = %s")
            params.append(grn)
        
        if bill_number:
            conditions.append("purchaseBillNumber = %s")
            params.append(bill_number)
        
        if purchase_id:
            conditions.append("id = %s")
            params.append(purchase_id)
        
        # Build WHERE clause
        where_clause = " AND ".join(conditions)
        
        # Query for total count
        count_sql = f"""
        SELECT COUNT(*) as total 
        FROM intbl_purchaserequisition 
        WHERE {where_clause}
        """
        
        cursor.execute(count_sql, params)
        total_count = cursor.fetchone()['total']
        
        # Build main query with same conditions
        sql = f"""
        SELECT *
        FROM intbl_purchaserequisition 
        WHERE {where_clause}
        ORDER BY Date DESC 
        LIMIT %s OFFSET %s
        """
        
        query_params = params + [int(limit), offset]
        
        cursor.execute(sql, query_params)
        purchases = cursor.fetchall()
        
        # Get purchase details (items) for each purchase
        for purchase in purchases:
            items_sql = """
            SELECT 
                *
            FROM intbl_purchaserequisition_contract
            WHERE PurchaseReqID = %s and purchase_from = 'web'
            """
            cursor.execute(items_sql, (purchase['IDIntbl_PurchaseRequisition'],))
            items = cursor.fetchall()
            purchase['items'] = items
            
            # Add summary calculations
            purchase['total_items_count'] = len(items)
            purchase['total_units_ordered'] = sum(float(item['UnitsOrdered']) for item in items) if items else 0
        
        mydb.close()
        
        # Prepare response with applied filters
        applied_filters = {
            "state": state if state else "Ordered/Received",
            "company_name": company_name,
            "from_date": from_date,
            "to_date": to_date,
            "grn": grn,
            "bill_number": bill_number,
            "purchase_id": purchase_id
        }
        
        # Remove None values from applied_filters
        applied_filters = {k: v for k, v in applied_filters.items() if v is not None}
        
        return jsonify({
            "success": True,
            "outlet_name": outlet_name,
            "filters_applied": applied_filters,
            "pagination": {
                "current_page": int(page),
                "limit": int(limit),
                "total_count": total_count,
                "total_pages": (total_count + int(limit) - 1) // int(limit) if total_count > 0 else 0
            },
            "count": len(purchases),
            "purchases": purchases
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# from flask import  Blueprint,request
# import mysql.connector
# from flask_cors import  cross_origin
# import os
# from dotenv import load_dotenv
# load_dotenv()
# app_file12= Blueprint('app_file12',__name__)

# from datetime import datetime



# @app_file12.route("/req", methods=["POST"])
# @cross_origin()
# def purchasereqPost():
#     try:
#         # Get today's date as a string in 'YYYY-MM-DD' format
#         today_str = datetime.today().strftime('%Y-%m-%d')
#         mydb = mysql.connector.connect(host=os.getenv('host'), user=os.getenv('user'), password=os.getenv('password'))
#         cursor = mydb.cursor(buffered=True)
#         database_sql = "USE {};".format(os.getenv('database'))
#         cursor.execute(database_sql)
#         data = request.get_json()
        
#         sql = f"""INSERT INTO `intbl_purchaserequisition` (Outlet_PurchaseReqID,RequisitionType,Date,TotalAmount,TaxAmount,Company_Name,State,ReceivedDate,ServerReceivedDate,purchaseBillNumber,DiscountAmount,Outlet_Name,GRN, purchase_id_ocular)
#         VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s)
#         """
#         sql2 = f"""
#         INSERT INTO `intbl_purchaserequisition_contract` (ItemID,UnitsOrdered,PurchaseReqID,Rate,Name,BrandName,Code,UOM,StockType,Department,GroupName,ExpDate,Status,Taxable) 
#         VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
#         """
        
#         # SQL for received_items
#         sql3 = f"""
#         INSERT INTO `received_items` (item_name, outlet_name, quantity, price, uom, received_date, department)
#         VALUES(%s, %s, %s, %s, %s, %s, %s)
#         """
        
#         cursor.execute(
#             sql,
#             (
#                 data["PurchaseRequistionID"],
#                 data["RequisitionType"],
#                 data["Date"],
#                 data["TotalAmount"],
#                 data["TaxAmount"],
#                 data["Company_Name"],
#                 data["State"],
#                 data["ReceivedDate"],
#                 today_str,
#                 data["purchaseBillNumber"],
#                 data["DiscountAmount"],
#                 data["Outlet_Name"],
#                 data["GRN"],
#                 data.get("purchase_id_ocular", None)
#             ),
#         )
#         mydb.commit()
#         purchase_req_id = cursor.lastrowid
        
#         for item in data["RequisitionDetailsList"]:
#             listdata = (
#                 item["ItemID"],
#                 item["UnitsOrdered"],
#                 purchase_req_id,
#                 item["Rate"],
#                 item["Name"],
#                 item["BrandName"],
#                 item["Code"],
#                 item["UOM"],
#                 item["StockType"],
#                 item["Department"],
#                 item["GroupName"],
#                 item["ExpDate"],
#                 item["Status"],
#                 item["Taxable"],
#             )
#             try:
#                 cursor.execute(sql2, listdata)
#                 mydb.commit()
                
#                 # Insert into received_items for each purchased item
#                 received_item_data = (
#                     item["Name"],  # item_name
#                     data["Outlet_Name"],  # outlet_name
#                     item["UnitsOrdered"],  # quantity
#                     item["Rate"],  # price
#                     item["UOM"],  # uom
#                     data["ReceivedDate"],  # received_date
#                     item.get("Department", None)  # department (using get to handle if missing)
#                 )
#                 cursor.execute(sql3, received_item_data)
#                 mydb.commit()
                
#             except Exception as e:
#                 data = {"error": str(e)}
#                 return data, 400
        
#         mydb.close()
#         data = {"success": "Data posted successfully."}
#         return data, 200
#     except Exception as error:
#         data = {'error': str(error)}
#         return data, 400
