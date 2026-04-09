from flask import Flask, Blueprint,request
import mysql.connector
from flask_cors import  cross_origin
import os
from dotenv import load_dotenv
load_dotenv()
app_file23= Blueprint('app_file23',__name__)
from root.auth.check import token_auth



# @app_file23.route("/billsearch", methods=["POST"])
# @cross_origin()
# def billsearch():
#     try:
#         mydb = mysql.connector.connect(host=os.getenv('host'), user=os.getenv('user'), password=os.getenv('password'))
#         cursor = mydb.cursor(buffered=True)
#         database_sql = "USE {};".format(os.getenv('database'))
#         cursor.execute(database_sql)
#         json = request.get_json()
#         if "token" not in json  or not any([json["token"]])  or json["token"]=="":
#             data = {"error":"No token provided."}
#             return data,400
#         token = json["token"]
#         if not token_auth(token):
#             data = {"error":"Invalid token."}
#             return data,400
#         if "outlet" not in json or "billno" not in json:
#             data = {"error":"Some fields are missing"}
#             return data,400
#         outlet = json["outlet"]
#         billno = json["billno"]
        
#         orderHistory =f"""SELECT Date,bill_no,(Total-serviceCharge-VAT) as 'Subtotal', Outlet_OrderID as id,serviceCharge, VAT,  Total, DiscountAmt, PaymentMode, GuestName FROM `tblorderhistory` where Outlet_Name =%s and  bill_no=%s """
#         cursor.execute(orderHistory,(
#             outlet,billno,
#         ),)
#         result = cursor.fetchall()
#         if result == []:
#             data = {"error":"No data available."}
#             return data,400
#         row_headers=[x[0] for x in cursor.description] 
#         json_data=[]
#         for res in result:
#             json_data.append(dict(zip(row_headers,res)))
        
        
        
        
        
    #     mydb.close()
    #     return json_data
    # except Exception as error:
    #     data ={'error':str(error)}
    #     return data,400


@app_file23.route("/billsearch", methods=["POST"])
@cross_origin()
def billsearch():
    try:
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password'),
            database=os.getenv('database')
        )
        cursor = mydb.cursor(buffered=True)

        json = request.get_json()

        # ---------- Token check ----------
        if not json or "token" not in json or json["token"] == "":
            return {"error": "No token provided."}, 400

        if not token_auth(json["token"]):
            return {"error": "Invalid token."}, 400

        # ---------- Required fields ----------
        if "outlet" not in json or "billno" not in json:
            return {"error": "Some fields are missing"}, 400

        outlet = json["outlet"]
        billno = json["billno"]

        # ---------- Get bill prefix ----------
        cursor.execute(
            "SELECT bill_prefix FROM outetNames WHERE Outlet=%s LIMIT 1",
            (outlet,)
        )
        row = cursor.fetchone()
        bill_prefix = row[0] if row else "GEN"

        # ---------- Get bill data ----------
        query = """
        SELECT Date, bill_no,
        (Total-serviceCharge-VAT) AS Subtotal,
        Outlet_OrderID AS id,
        serviceCharge, VAT, Total,
        DiscountAmt, PaymentMode, GuestName,
        fiscal_year, idtblorderHistory
        FROM tblorderhistory
        WHERE Outlet_Name=%s AND bill_no=%s
        """
        cursor.execute(query, (outlet, billno))
        result = cursor.fetchall()

        if not result:
            return {"error": "No data available."}, 400

        headers = [x[0] for x in cursor.description]

        json_data = []
        for r in result:
            row_dict = dict(zip(headers, r))

            # ---------- Add formatted bill ----------
            bill_no = str(row_dict.get("bill_no", ""))
            fiscal_year = str(row_dict.get("fiscal_year", ""))
            row_dict["formatted_bill_no"] = f"{bill_prefix}/{bill_no}/{fiscal_year}"

            json_data.append(row_dict)

        mydb.close()
        return json_data

    except Exception as error:
        return {'error': str(error)}, 400
