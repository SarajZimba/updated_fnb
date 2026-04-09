# from flask import  Blueprint,request
# import mysql.connector
# from flask_cors import  cross_origin
# import os
# from dotenv import load_dotenv
# load_dotenv()
# app_file16= Blueprint('app_file16',__name__)


# @app_file16.route("/reqfilterfirst/", methods=["GET"])
# @cross_origin()
# def reqfilterfirst():
#     try:
#         mydb = mysql.connector.connect(host=os.getenv('host'), user=os.getenv('user'), password=os.getenv('password'))
#         cursor = mydb.cursor(buffered=True)
#         database_sql = "USE {};".format(os.getenv('database'))
#         cursor.execute(database_sql)
#         time = request.args.get("firsttime", "")
#         time2 = request.args.get("secondtime", "")
#         outletname = request.args.get("outlet_name", "")
#         #outletname.replace('%20',' ')
#         if time=="" or time2=="" or outletname =="":
#             data={"eror":"Some fields are missing."}
#             return data,400
#         sql = f"""SELECT * FROM intbl_purchaserequisition WHERE ReceivedDate BETWEEN %s AND %s and Outlet_Name=%s ORDER BY IDIntbl_PurchaseRequisition DESC ;"""
#         purchase_items_sql = f"""select a.GroupName, a.Name, sum(a.UnitsOrdered) as Count, a.Rate,(sum(a.UnitsOrdered)* a.Rate) as Total, a.Taxable, a.UOM, b.Company_Name,
#         (
#             SELECT 
#                 Rate 
#                     FROM 
#                         intbl_purchaserequisition_contract 
#                     WHERE 
#                         ItemID = a.ItemID 
#                         AND PurchaseReqID != a.PurchaseReqID 
#                     ORDER BY 
#                         PurchaseReqID DESC 
#                     LIMIT 1
#         ) AS LastPurchaseRate
#             from intbl_purchaserequisition_contract a, intbl_purchaserequisition b where a.PurchaseReqID = b.IDIntbl_PurchaseRequisition and b.ReceivedDate BETWEEN %s AND %s and b.Outlet_Name=%s GROUP BY a.GroupName ,a.Name, a.Rate ORDER BY  a.GroupName , a.Name"""
#         cursor.execute(sql,(time,time2,outletname),)
#         desc = cursor.description
#         data = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]

#         cursor.execute(purchase_items_sql,(time,time2,outletname),)
#         purchase_items_desc = cursor.description
#         purchase_items_data = [dict(zip([col[0] for col in purchase_items_desc], row)) for row in cursor.fetchall()]

#         vendorwise_totals = {}

#         for vendor_data in data:
#             company_name = vendor_data["Company_Name"]
#             total_amount = float(vendor_data["TotalAmount"])  # Convert to float for summation
            
#             # Accumulate totals for the same vendor
#             if company_name not in vendorwise_totals:
#                 vendorwise_totals[company_name] = total_amount
#             else:
#                 vendorwise_totals[company_name] += total_amount

#         vendorwise_totals_list = []
#         for key, item in vendorwise_totals.items():
#             vendor_data = {
#                 "vendor" : key,
#                 "total": item
#             }

#             vendorwise_totals_list.append(vendor_data)
#         data = {"purchaserequisition":data,"outletname":outletname, "purchase_items_data": purchase_items_data, "vendorwise_totals": vendorwise_totals_list}


#         mydb.close()
#         return data,200
#     except Exception as error:
#         data ={'error':str(error)}
#         return data,400

# from flask import Blueprint, request
# import mysql.connector
# from flask_cors import cross_origin
# import os
# from dotenv import load_dotenv

# load_dotenv()
# app_file16 = Blueprint('app_file16', __name__)

# @app_file16.route("/reqfilterfirst/", methods=["GET"])
# @cross_origin()
# def reqfilterfirst():
#     try:
#         mydb = mysql.connector.connect(
#             host=os.getenv('host'), 
#             user=os.getenv('user'), 
#             password=os.getenv('password')
#         )
#         cursor = mydb.cursor(buffered=True)
#         database_sql = "USE {};".format(os.getenv('database'))
#         cursor.execute(database_sql)
        
#         time = request.args.get("firsttime", "")
#         time2 = request.args.get("secondtime", "")
#         outletname = request.args.get("outlet_name", "")
        
#         if time == "" or time2 == "" or outletname == "":
#             data = {"error": "Some fields are missing."}
#             return data, 400
            
#         sql = """SELECT * FROM intbl_purchaserequisition 
#                  WHERE ReceivedDate BETWEEN %s AND %s AND Outlet_Name=%s 
#                  ORDER BY IDIntbl_PurchaseRequisition DESC;"""
        
#         purchase_items_sql = """SELECT 
#             a.GroupName, 
#             a.Name, 
#             SUM(a.UnitsOrdered) as Count, 
#             a.Rate,
#             (SUM(a.UnitsOrdered) * a.Rate) as Total, 
#             a.Taxable, 
#             a.UOM, 
#             b.Company_Name,
#             (
#                 SELECT Rate 
#                 FROM intbl_purchaserequisition_contract 
#                 WHERE ItemID = a.ItemID 
#                 AND PurchaseReqID != a.PurchaseReqID 
#                 ORDER BY PurchaseReqID DESC 
#                 LIMIT 1
#             ) AS LastPurchaseRate
#         FROM intbl_purchaserequisition_contract a, intbl_purchaserequisition b 
#         WHERE a.PurchaseReqID = b.IDIntbl_PurchaseRequisition 
#         AND b.ReceivedDate BETWEEN %s AND %s 
#         AND b.Outlet_Name = %s 
#         GROUP BY a.GroupName, a.Name, a.Rate, a.Taxable, a.UOM, b.Company_Name, a.ItemID 
#         ORDER BY a.GroupName, a.Name;"""
        
#         cursor.execute(sql, (time, time2, outletname))
#         desc = cursor.description
#         data = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]

#         cursor.execute(purchase_items_sql, (time, time2, outletname))
#         purchase_items_desc = cursor.description
#         purchase_items_data = [dict(zip([col[0] for col in purchase_items_desc], row)) for row in cursor.fetchall()]

#         vendorwise_totals = {}

#         for vendor_data in data:
#             company_name = vendor_data["Company_Name"]
#             total_amount = float(vendor_data["TotalAmount"])
            
#             if company_name not in vendorwise_totals:
#                 vendorwise_totals[company_name] = total_amount
#             else:
#                 vendorwise_totals[company_name] += total_amount

#         vendorwise_totals_list = []
#         for key, item in vendorwise_totals.items():
#             vendor_data = {
#                 "vendor": key,
#                 "total": item
#             }
#             vendorwise_totals_list.append(vendor_data)
            
#         data = {
#             "purchaserequisition": data,
#             "outletname": outletname, 
#             "purchase_items_data": purchase_items_data, 
#             "vendorwise_totals": vendorwise_totals_list
#         }

#         mydb.close()
#         return data, 200
        
#     except Exception as error:
#         data = {'error': str(error)}
#         return data, 400

from flask import Blueprint, request
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv

load_dotenv()
app_file16 = Blueprint('app_file16', __name__)

@app_file16.route("/reqfilterfirst/", methods=["GET"])
@cross_origin()
def reqfilterfirst():
    try:
        mydb = mysql.connector.connect(
            host=os.getenv('host'), 
            user=os.getenv('user'), 
            password=os.getenv('password')
        )
        cursor = mydb.cursor(buffered=True)
        database_sql = "USE {};".format(os.getenv('database'))
        cursor.execute(database_sql)
        
        time = request.args.get("firsttime", "")
        time2 = request.args.get("secondtime", "")
        outletname = request.args.get("outlet_name", "")
        
        if time == "" or time2 == "" or outletname == "":
            data = {"error": "Some fields are missing."}
            return data, 400
            
        sql = """SELECT * FROM intbl_purchaserequisition 
                 WHERE ReceivedDate BETWEEN %s AND %s AND Outlet_Name=%s 
                 ORDER BY IDIntbl_PurchaseRequisition DESC;"""
        
        purchase_items_sql = """SELECT 
            a.GroupName, 
            a.Name, 
            SUM(a.UnitsOrdered) as Count, 
            a.Rate,
            (SUM(a.UnitsOrdered) * a.Rate) as Total, 
            a.Taxable, 
            a.UOM, 
            b.Company_Name,
            (
                SELECT Rate 
                FROM intbl_purchaserequisition_contract 
                WHERE ItemID = a.ItemID 
                AND PurchaseReqID != a.PurchaseReqID 
                ORDER BY PurchaseReqID DESC 
                LIMIT 1
            ) AS LastPurchaseRate
        FROM intbl_purchaserequisition_contract a, intbl_purchaserequisition b 
        WHERE a.PurchaseReqID = b.IDIntbl_PurchaseRequisition 
        AND b.ReceivedDate BETWEEN %s AND %s 
        AND b.Outlet_Name = %s 
        GROUP BY a.GroupName, a.Name, a.Rate, a.Taxable, a.UOM, b.Company_Name, a.ItemID, a.PurchaseReqID 
        ORDER BY a.GroupName, a.Name;"""
        
        cursor.execute(sql, (time, time2, outletname))
        desc = cursor.description
        data = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]

        cursor.execute(purchase_items_sql, (time, time2, outletname))
        purchase_items_desc = cursor.description
        purchase_items_data = [dict(zip([col[0] for col in purchase_items_desc], row)) for row in cursor.fetchall()]

        vendorwise_totals = {}

        for vendor_data in data:
            company_name = vendor_data["Company_Name"]
            total_amount = float(vendor_data["TotalAmount"])
            
            if company_name not in vendorwise_totals:
                vendorwise_totals[company_name] = total_amount
            else:
                vendorwise_totals[company_name] += total_amount

        vendorwise_totals_list = []
        for key, item in vendorwise_totals.items():
            vendor_data = {
                "vendor": key,
                "total": item
            }
            vendorwise_totals_list.append(vendor_data)
            
        data = {
            "purchaserequisition": data,
            "outletname": outletname, 
            "purchase_items_data": purchase_items_data, 
            "vendorwise_totals": vendorwise_totals_list
        }

        mydb.close()
        return data, 200
        
    except Exception as error:
        data = {'error': str(error)}
        return data, 400