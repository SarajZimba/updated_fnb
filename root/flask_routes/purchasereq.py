from flask import  Blueprint,request
import mysql.connector
from flask_cors import  cross_origin
import os
from dotenv import load_dotenv
load_dotenv()
app_file12= Blueprint('app_file12',__name__)

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
        # sql = f"""INSERT INTO `intbl_purchaserequisition` (Outlet_PurchaseReqID,RequisitionType,Date,TotalAmount,TaxAmount,Company_Name,State,ReceivedDate,purchaseBillNumber,DiscountAmount,Outlet_Name,GRN)
        # VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        # """
        sql = f"""INSERT INTO `intbl_purchaserequisition` (Outlet_PurchaseReqID,RequisitionType,Date,TotalAmount,TaxAmount,Company_Name,State,ReceivedDate,ServerReceivedDate,purchaseBillNumber,DiscountAmount,Outlet_Name,GRN, purchase_id_ocular)
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s)
        """
        sql2 = f"""
        INSERT INTO `intbl_purchaserequisition_contract`    (ItemID,UnitsOrdered,PurchaseReqID,Rate,Name,BrandName,Code,UOM,StockType,Department,GroupName,ExpDate,Status,Taxable) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)   """
        cursor.execute(
            sql,
            (
                data["PurchaseRequistionID"],
                data["RequisitionType"],
                data["Date"],
                data["TotalAmount"],
                data["TaxAmount"],
                data["Company_Name"],
                data["State"],
                data["ReceivedDate"],
                today_str,
                data["purchaseBillNumber"],
                data["DiscountAmount"],
                data["Outlet_Name"],
                data["GRN"],
                data.get("purchase_id_ocular", None)

            ),
        )
        mydb.commit()
        purchase_req_id = cursor.lastrowid
        for data in data["RequisitionDetailsList"]:
            listdata = (
                data["ItemID"],
                data["UnitsOrdered"],
                purchase_req_id,
                data["Rate"],
                data["Name"],
                data["BrandName"],
                data["Code"],
                data["UOM"],
                data["StockType"],
                data["Department"],
                data["GroupName"],
                data["ExpDate"],
                data["Status"],
                data["Taxable"],
            )
            try:
                cursor.execute(sql2, listdata)
                mydb.commit()
            except Exception as e:
                data={"error":str(e)}
                return data,400
        mydb.close()
        data ={"success":"Data posted successfully."}
        return data,200
    except Exception as error:
        data ={'error':str(error)}
        return data,400



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