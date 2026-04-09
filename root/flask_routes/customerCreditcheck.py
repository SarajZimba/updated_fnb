# from flask import Flask, Blueprint,request
# import mysql.connector
# from flask_cors import cross_origin
# import os
# from dotenv import load_dotenv
# load_dotenv()
# app_file27 = Blueprint('app_file27',__name__)
# from root.auth.check import token_auth



# @app_file27.route("/customerCreditData", methods=["POST"])
# @cross_origin()
# def customerCreditCheck():
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
#         if not "outlet" in json or "customerName" not in json:
#             data= {"error":"Missing parameters."}
#             return data,400
#         get_customer_creditSql =f"""SELECT 	guestID,GuestName, guestEmail, guestPhone,guestAddress FROM tblorderhistory where GuestName=%s  and Outlet_Name=%s and guestID!='' GROUP BY guestID"""
#         cursor.execute(get_customer_creditSql,(json["customerName"],json["outlet"],),)
#         result = cursor.fetchall()
#         if result == []:
#             data = {"error":"Temporarily unavailable."}
#             return data,400
#         row_headers=[x[0] for x in cursor.description] 
#         json_data=[]
#         for res in result:
#             guestID=dict(zip(row_headers,res))["guestID"]
#             GuestName=dict(zip(row_headers,res))["GuestName"]
#             guestEmail=dict(zip(row_headers,res))["guestEmail"]
#             guestPhone=dict(zip(row_headers,res))["guestPhone"]
#             guestAddress=dict(zip(row_headers,res))["guestAddress"]
#             getAmountdueSql=f"""Select (SELECT sum(Amount)  FROM CreditHistory where 	creditState='Payment' and   guestID=%s  and outetName=%s) as AmountPaid,(SELECT sum(Total)   FROM tblorderhistory where PaymentMode='Credit'  and guestID=%s and Outlet_Name=%s) as  TotalCredit, (Select TotalCredit- AmountPaid  ) as amountDue"""
#             cursor.execute(getAmountdueSql,(guestID,json["outlet"],guestID,json["outlet"],),)
#             amountDueresult = cursor.fetchall()
#             duerow_headers=[x[0] for x in cursor.description] 
#             amountdueDatajson=[]
#             for dueres in amountDueresult:
#                 amountdueDatajson.append(dict(zip(duerow_headers,dueres)))    
#             customercreditCheckJson={"creditDetails":amountdueDatajson,"guestAddress":guestAddress,"guestPhone":guestPhone,"guestEmail":guestEmail,"guestID":guestID,"GuestName":GuestName}
#             json_data.append(customercreditCheckJson)
#         mydb.close()
#         return json_data,200
#     except Exception as error:
#         data ={'error':str(error)}
#         return data,400

from flask import Flask, Blueprint, request, jsonify
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv
from root.auth.check import token_auth

load_dotenv()
app_file27 = Blueprint('app_file27', __name__)

@app_file27.route("/customerCreditData", methods=["POST"])
@cross_origin()
def customerCreditCheck():
    try:
        # Connect to MySQL
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password')
        )
        cursor = mydb.cursor(buffered=True)

        # Use correct database
        cursor.execute(f"USE {os.getenv('database')}")

        # Load JSON request
        json_data = request.get_json()

        # Validate token
        if "token" not in json_data or not json_data["token"]:
            return {"error": "No token provided."}, 400

        token = json_data["token"]
        if not token_auth(token):
            return {"error": "Invalid token."}, 400

        # Validate required fields
        if "outlet" not in json_data or "customerName" not in json_data:
            return {"error": "Missing parameters."}, 400

        outlet = json_data["outlet"]
        customerName = json_data["customerName"]

        get_customer_credit_sql = """
            SELECT 
                guestID,
                MIN(GuestName) AS GuestName,
                MIN(guestEmail) AS guestEmail,
                MIN(guestPhone) AS guestPhone,
                MIN(guestAddress) AS guestAddress
            FROM tblorderhistory 
            WHERE GuestName = %s AND Outlet_Name = %s AND guestID != ''
            GROUP BY guestID
        """
        cursor.execute(get_customer_credit_sql, (customerName, outlet))
        result = cursor.fetchall()

        if not result:
            return {"error": "Temporarily unavailable."}, 400

        row_headers = [x[0] for x in cursor.description]
        json_data_out = []

        for res in result:
            row = dict(zip(row_headers, res))
            guestID = row["guestID"]

            get_amount_due_sql = """
                SELECT 
                    IFNULL((
                        SELECT SUM(Amount) 
                        FROM CreditHistory 
                        WHERE creditState = 'Payment' AND guestID = %s AND outetName = %s
                    ), 0) AS AmountPaid,
                    IFNULL((
                        SELECT SUM(Total) 
                        FROM tblorderhistory 
                        WHERE PaymentMode = 'Credit' AND guestID = %s AND Outlet_Name = %s
                    ), 0) AS TotalCredit,
                    (
                        IFNULL((
                            SELECT SUM(Total) 
                            FROM tblorderhistory 
                            WHERE PaymentMode = 'Credit' AND guestID = %s AND Outlet_Name = %s
                        ), 0) - 
                        IFNULL((
                            SELECT SUM(Amount) 
                            FROM CreditHistory 
                            WHERE creditState = 'Payment' AND guestID = %s AND outetName = %s
                        ), 0)
                    ) AS amountDue
            """
            cursor.execute(get_amount_due_sql, (
                guestID, outlet,
                guestID, outlet,
                guestID, outlet,
                guestID, outlet
            ))

            amount_due_result = cursor.fetchall()
            amount_due_headers = [x[0] for x in cursor.description]
            amount_due_data_json = [dict(zip(amount_due_headers, r)) for r in amount_due_result]

            customer_credit_data = {
                "guestID": row["guestID"],
                "GuestName": row["GuestName"],
                "guestEmail": row["guestEmail"],
                "guestPhone": row["guestPhone"],
                "guestAddress": row["guestAddress"],
                "creditDetails": amount_due_data_json
            }

            json_data_out.append(customer_credit_data)

        mydb.close()
        return jsonify(json_data_out), 200

    except Exception as error:
        return {"error": str(error)}, 400

