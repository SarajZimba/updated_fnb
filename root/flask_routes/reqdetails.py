from flask import  Blueprint, request
import mysql.connector
from flask_cors import  cross_origin
import os
from dotenv import load_dotenv
load_dotenv()
app_file14= Blueprint('app_file14',__name__)


def addDatatoDict(dicdata=0, data=0):
    _data = []
    for i in range(len(data)):
        if len(dicdata[i]) != 0:
            temp = data[i]
            temp1 = dicdata[i]
            key = temp1.keys()
            value = temp1.values()
            a = list(key)
            b = list(value)
            temp[a[0]] = float(b[0])
            _data.append(temp)
        else:
            _data.append(data[i])
    return _data


# @app_file14.route("/reqdetails/<int:id>", methods=["GET"])
# @cross_origin()
# def reqdetails(id):
#     try:
#         mydb = mysql.connector.connect(
#             host=os.getenv('host'), 
#             user=os.getenv('user'), 
#             password=os.getenv('password')
#         )
#         cursor = mydb.cursor(buffered=True, dictionary=True)
#         database_sql = "USE {};".format(os.getenv('database'))
#         cursor.execute(database_sql)
        
#         # -------- FETCH PURCHASE REQUISITION CONTRACT ITEMS --------
#         sql = """
#         SELECT * FROM intbl_purchaserequisition_contract 
#         WHERE PurchaseReqID = %s 
#         ORDER BY ItemID DESC;
#         """
#         cursor.execute(sql, (id,))
#         contract_items = cursor.fetchall()
        
#         # -------- FETCH PURCHASE REQUISITION DETAILS TO GET GRN, OUTLET_PURCHASEREQID, OUTLET_NAME --------
#         pr_sql = """
#         SELECT GRN, Outlet_PurchaseReqID, Outlet_Name, Company_Name, TotalAmount, ReceivedDate 
#         FROM intbl_purchaserequisition 
#         WHERE IDIntbl_PurchaseRequisition = %s
#         """
#         cursor.execute(pr_sql, (id,))
#         purchase_requisition = cursor.fetchone()
        
#         if not purchase_requisition:
#             return {"error": "Purchase requisition not found"}, 404
        
#         # -------- FETCH LAST PURCHASE RATE FOR EACH ITEM --------
#         query_list = []
#         for item in contract_items:
#             sql = """SELECT Rate as last_purchase 
#                      FROM `intbl_purchaserequisition_contract` 
#                      WHERE ItemID = %s 
#                      AND PurchaseReqID != %s 
#                      ORDER BY PurchaseReqID DESC 
#                      LIMIT 1;"""
#             query_list.append((sql, item['ItemID'], id))
        
#         last_purchase_data = []
#         for sql_query, item_id, req_id in query_list:
#             cursor.execute(sql_query, (item_id, req_id))
#             result = cursor.fetchone()
#             if result:
#                 last_purchase_data.append({"last_purchase": result['last_purchase']})
#             else:
#                 last_purchase_data.append({"last_purchase": 0})
        
#         # -------- FETCH DEBITNOTES FOR THIS PURCHASE REQUISITION --------
#         debitnotes_data = []
        
#         # Get GRN and Outlet_PurchaseReqID from purchase requisition
#         grn = purchase_requisition.get('GRN')
#         outlet_purchase_req_id = purchase_requisition.get('Outlet_PurchaseReqID')
        
#         # Build query to fetch debitnotes
#         debitnote_conditions = []
#         params = []
        
#         if grn:
#             debitnote_conditions.append("GRN = %s")
#             params.append(grn)
        
#         if outlet_purchase_req_id:
#             debitnote_conditions.append("Outlet_PurchaseReqID = %s")
#             params.append(outlet_purchase_req_id)
        
#         if debitnote_conditions:
#             debitnote_query = f"""
#             SELECT * FROM debitnote 
#             WHERE {' OR '.join(debitnote_conditions)}
#             ORDER BY created_at DESC
#             """
#             cursor.execute(debitnote_query, tuple(params))
#             debitnotes_data = cursor.fetchall()
        
#         # -------- ATTACH LAST PURCHASE RATE TO CONTRACT ITEMS --------
#         for i in range(len(contract_items)):
#             contract_items[i]['last_purchase'] = last_purchase_data[i]['last_purchase']
        
#         # -------- ADD DEBITNOTES SUMMARY TO PURCHASE REQUISITION --------
#         purchase_requisition['debitnotes'] = debitnotes_data
        
#         # FIXED: Handle NULL values in Quantity
#         total_debit_quantity = 0
#         for dn in debitnotes_data:
#             quantity = dn.get('Quantity')
#             if quantity is not None:
#                 total_debit_quantity += quantity
        
#         purchase_requisition['total_debit_quantity'] = total_debit_quantity
        
#         purchase_requisition['has_debitnote'] = len(debitnotes_data) > 0
        
#         # -------- PREPARE FINAL RESPONSE --------
#         data = {
#             "intbl_purchaserequisition_contract": contract_items,
#             "purchase_requisition_details": purchase_requisition,
#             "debitnotes": debitnotes_data  # Also at same level for easy access
#         }
        
#         mydb.close()
#         return data, 200
        
#     except Exception as error:
#         data = {'error': str(error)}
#         return data, 400


@app_file14.route("/reqdetails/<int:id>", methods=["GET"])
@cross_origin()
def reqdetails(id):
    try:
        mydb = mysql.connector.connect(
            host=os.getenv('host'), 
            user=os.getenv('user'), 
            password=os.getenv('password'),
            database=os.getenv('database')
        )
        cursor = mydb.cursor(buffered=True, dictionary=True)

        # -------- FETCH PURCHASE REQUISITION CONTRACT ITEMS --------
        sql = """
        SELECT * FROM intbl_purchaserequisition_contract 
        WHERE PurchaseReqID = %s 
        ORDER BY ItemID DESC;
        """
        cursor.execute(sql, (id,))
        contract_items = cursor.fetchall()
        
        # -------- FETCH PURCHASE REQUISITION DETAILS --------
        pr_sql = """
        SELECT GRN, Outlet_PurchaseReqID, Outlet_Name, Company_Name, TotalAmount, ReceivedDate 
        FROM intbl_purchaserequisition 
        WHERE IDIntbl_PurchaseRequisition = %s
        """
        cursor.execute(pr_sql, (id,))
        purchase_requisition = cursor.fetchone()
        
        if not purchase_requisition:
            return {"error": "Purchase requisition not found"}, 404

        # -------- FETCH LAST PURCHASE RATE FOR EACH ITEM --------
        last_purchase_data = []
        for item in contract_items:
            sql = """SELECT Rate as last_purchase 
                     FROM `intbl_purchaserequisition_contract` 
                     WHERE ItemID = %s AND PurchaseReqID != %s 
                     ORDER BY PurchaseReqID DESC 
                     LIMIT 1;"""
            cursor.execute(sql, (item['ItemID'], id))
            result = cursor.fetchone()
            last_purchase_data.append({"last_purchase": result['last_purchase'] if result else 0})

        # Attach last purchase rate
        for i in range(len(contract_items)):
            contract_items[i]['last_purchase'] = last_purchase_data[i]['last_purchase']

        # -------- FETCH DEBITNOTES FROM NEW MASTER/DETAIL TABLE --------
        debitnotes_data = []
        grn = purchase_requisition.get('GRN')
        outlet_purchase_req_id = purchase_requisition.get('Outlet_PurchaseReqID')

        conditions = []
        params = []

        if grn:
            conditions.append("GRN = %s")
            params.append(grn)
        if outlet_purchase_req_id:
            conditions.append("Outlet_PurchaseReqID = %s")
            params.append(outlet_purchase_req_id)

        if conditions:
            master_query = f"""
            SELECT * FROM debitnote_master
            WHERE {' OR '.join(conditions)}
            ORDER BY created_at DESC
            """
            cursor.execute(master_query, tuple(params))
            masters = cursor.fetchall()

            # Fetch corresponding details for each master
            for master in masters:
                cursor.execute(
                    "SELECT * FROM debitnote_details WHERE debitnote_id = %s",
                    (master['id'],)
                )
                details = cursor.fetchall()
                master['details'] = details
                master['total_debit_quantity'] = sum(d['Quantity'] for d in details) if details else 0
                master['total_debit_amount'] = sum(d.get('total_amount', 0) for d in details) if details else 0
                master['has_details'] = len(details) > 0

            debitnotes_data = masters

        # -------- ADD DEBITNOTES SUMMARY TO PURCHASE REQUISITION --------
        purchase_requisition['debitnotes'] = debitnotes_data
        purchase_requisition['total_debit_quantity'] = sum(
            md['total_debit_quantity'] for md in debitnotes_data
        ) if debitnotes_data else 0
        purchase_requisition['total_debit_amount'] = sum(
            md['total_debit_amount'] for md in debitnotes_data
        ) if debitnotes_data else 0
        purchase_requisition['has_debitnote'] = len(debitnotes_data) > 0

        # -------- FINAL RESPONSE --------
        data = {
            "intbl_purchaserequisition_contract": contract_items,
            "purchase_requisition_details": purchase_requisition,
            "debitnotes": debitnotes_data
        }

        mydb.close()
        return data, 200

    except Exception as error:
        return {'error': str(error)}, 400