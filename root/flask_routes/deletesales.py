# from flask import  Blueprint,request
# import mysql.connector
# from flask_cors import CORS, cross_origin
# import os
# from dotenv import load_dotenv
# load_dotenv()
# app_file9= Blueprint('app_file9',__name__)





# @app_file9.route("/deletedata", methods=['PUT'])
# @cross_origin()
# def stats():
#     try:
#         mydb = mysql.connector.connect(host=os.getenv('host'), user=os.getenv('user'), password=os.getenv('password'))
#         cursor = mydb.cursor(buffered=True)
#         database_sql = "USE {};".format(os.getenv('database'))
#         cursor.execute(database_sql)
#         data = request.get_json()
#         sql = f"""SELECT `idtblorderHistory`as order_id FROM `tblorderhistory` WHERE `Outlet_OrderID`=%s and `Date` =%s"""
#         cursor.execute(sql,(data["outlet_orderID"],data["date"],),)
#         result = cursor.fetchall()
#         if result == []:
#             data = {"error":"The data for this outlet orderID and date doesn't exist."}
#             return data,400
#         row_headers=[x[0] for x in cursor.description] 
#         outletIdDatajson=[]
#         for res in result:
#             outletIdDatajson.append(dict(zip(row_headers,res)))    
#         idList =outletIdDatajson
#         for i in idList:
#             pk =i["order_id"]
#             sql1 = f"delete from `tblorder_detailshistory` WHERE order_ID =%s;"
#             sql2 = f"delete from `tblorderhistory` WHERE `idtblorderHistory` =%s;"
#             cursor.execute(sql1,(pk,),)
#             cursor.execute(sql2,(pk,),)
#             mydb.commit()
#         creditDeleteSql=f"""DELETE FROM `CreditHistory` WHERE Outlet_OrderID=%s"""
#         cursor.execute(creditDeleteSql,(data["outlet_orderID"],),)
#         mydb.commit()
#         mydb.close()
#         data = {"success":"Data deleted successfully"}
#         return data,200
#     except Exception as error:
#         data ={'error':str(error)}
#         return data,400

from flask import  Blueprint,request
import mysql.connector
from flask_cors import CORS, cross_origin
import os
from dotenv import load_dotenv
load_dotenv()
app_file9= Blueprint('app_file9',__name__)

import datetime
from .ird.postvoidbillintoird import post_credit_note_to_ird

@app_file9.route("/deletedata", methods=['PUT'])
@cross_origin()
def delete_bill():
    try:
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password')
        )
        cursor = mydb.cursor(buffered=True)
        cursor.execute(f"USE {os.getenv('database')};")

        data = request.get_json()
        
        # 1️⃣ Fetch the bill details to be deleted
        cursor.execute(
            "SELECT * FROM tblorderhistory WHERE Outlet_OrderID=%s AND Date=%s AND Outlet_Name= %s",
            (data["outlet_orderID"], data["date"], data["Outlet_Name"])
        )
        bill = cursor.fetchone()
        if not bill:
            return {"error": "Bill not found"}, 400

        # 2️⃣ Prepare Credit Note payload
        # Convert AD to BS for IRD
        ad_date = bill[10]  # assuming Date is 11th column, adjust index if needed
        if isinstance(ad_date, str):
            ad_date = datetime.datetime.strptime(ad_date, "%Y-%m-%d").date()
        from nepali_datetime import date as nepali_date
        bs_date = nepali_date.from_datetime_date(ad_date)
        bs_date_str = f"{bs_date.year}.{bs_date.month:02d}.{bs_date.day:02d}"

        # Fetch IRD credentials
        cursor.execute("SELECT username, password, seller_pan FROM ird_credentials LIMIT 1")
        ird_creds = cursor.fetchone()
        if not ird_creds:
            return {"error": "IRD credentials not found"}, 400
        ird_username, ird_password, ird_seller_pan = ird_creds

        # Fetch outlet prefix
        cursor.execute(
            "SELECT bill_prefix, postingToIRD FROM outetNames WHERE Outlet=%s LIMIT 1",
            (data["Outlet_Name"],)
        )
        prefix_row = cursor.fetchone()
        bill_prefix = prefix_row[0] if prefix_row else ""
        postingToIRD = prefix_row[1] 

        credit_note_payload = {
            "username": ird_username,
            "password": ird_password,
            "seller_pan": ird_seller_pan,
            "buyer_pan": "0",  # adjust index for guest PAN
            "fiscal_year": bill[17],
            "buyer_name": bill[18],
            "ref_invoice_number": f"{bill_prefix}-{bill[11]}",  # original bill_no
            "credit_note_number": f"{bill_prefix}-VOID-{bill[11]}",  # generate unique credit note number
            "credit_note_date": bs_date_str,
            "reason_for_return": data.get("reason", "Voided bill"),
            "total_sales": float(bill[12]),
            "taxable_sales_vat": float(bill[12]) - float(bill[14]),
            "vat": float(bill[14]),
            "excisable_amount": 0,
            "excise": 0,
            "taxable_sales_hst": 0,
            "hst": 0,
            "amount_for_esf": 0,
            "esf": 0,
            "export_sales": 0,
            "tax_exempted_sales": 0,
            "isrealtime": True,
            "datetimeClient": datetime.datetime.now().isoformat()
        }

        if postingToIRD:
            success, response_text = post_credit_note_to_ird(credit_note_payload)
            if not success:
                return {"error": "Failed to post credit note to IRD", "details": response_text}, 400

        cursor.execute("DELETE FROM tblorder_detailshistory WHERE order_ID=%s", (bill[0],))
        cursor.execute("delete from `payment_history` WHERE orderHistoryid =%s;", (bill[0],))
        cursor.execute("DELETE FROM tblorderhistory WHERE idtblorderhistory=%s", (bill[0],))

        cursor.execute("DELETE FROM CreditHistory WHERE Outlet_OrderID=%s and outetName=%s and Date=%s", (data["outlet_orderID"], data["Outlet_Name"], data["date"],))
        mydb.commit()
        mydb.close()

        return {"success": "Bill voided and credit note posted to IRD"}, 200

    except Exception as e:
        return {"error": str(e)}, 400
