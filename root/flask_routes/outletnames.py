# from flask import  Blueprint,request
# import mysql.connector
# from flask_cors import  cross_origin
# import os
# from dotenv import load_dotenv
# load_dotenv()
# app_file2 = Blueprint('app_file2',__name__)
# from root.auth.check import token_auth



# @app_file2.route("/outlets", methods=["POST"])
# @cross_origin()
# def outlets():
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
#         get_outlet_sql =f"""select distinct Outlet, Company_name, address, loyalty_percent, sms_text, logo, bill_prefix from outetNames"""
#         cursor.execute(get_outlet_sql)
#         result = cursor.fetchall()
#         if result == []:
#             data = {"error":"Temporarily unavailable."}
#             return data,400
#         row_headers=[x[0] for x in cursor.description] 
#         json_data=[]
#         for res in result:
#             json_data.append(dict(zip(row_headers,res)))
#         response_json = []
#         for i in json_data:
#             outlet_json ={"name":i["Outlet"],"value":i["Outlet"], "company": i["Company_name"], "address": i["address"], "loyalty_percent": float(i["loyalty_percent"]), "sms_text": i["sms_text"], "logo": i["logo"], "bill_prefix": i["bill_prefix"]}
#             response_json.append(outlet_json)
#         mydb.close()
#         return response_json,200
#     except Exception as error:
#         data ={'error':str(error)}
#         return data,400

from flask import  Blueprint,request
import mysql.connector
from flask_cors import  cross_origin
import os
from dotenv import load_dotenv
load_dotenv()
app_file2 = Blueprint('app_file2',__name__)
from root.auth.check import token_auth



@app_file2.route("/outlets", methods=["POST"])
@cross_origin()
def outlets():
    try:
        mydb = mysql.connector.connect(host=os.getenv('host'), user=os.getenv('user'), password=os.getenv('password'))
        cursor = mydb.cursor(buffered=True)
        database_sql = "USE {};".format(os.getenv('database'))
        cursor.execute(database_sql)
        json = request.get_json()
        if "token" not in json  or not any([json["token"]])  or json["token"]=="":
            data = {"error":"No token provided."}
            return data,400
        token = json["token"]
        if not token_auth(token):
            data = {"error":"Invalid token."}
            return data,400
        # Validate employee_id
        # if "employee_id" not in json or not json["employee_id"]:
        #     return {"error": "No employee_id provided."}, 400
        # employee_id = json["employee_id"]

        employee_id = json.get("employee_id", None)

        if employee_id:


            # Get only outlets the employee has access to (status = TRUE)
            cursor.execute("""
                SELECT o.id, o.Outlet, o.Company_name, o.address, o.logo, o.sms_text, o.bill_prefix, o.loyalty_percent, o.id
                FROM outetNames o
                JOIN employeeoutlets eo ON eo.outlet_id = o.id
                WHERE eo.employee_id = %s AND eo.status = TRUE
            """, (employee_id,))

        else:
            get_outlet_sql =f"""select distinct Outlet, Company_name, address, loyalty_percent, sms_text, logo, bill_prefix, id from outetNames"""
            cursor.execute(get_outlet_sql)
            # result = cursor.fetchall()
            # if result == []:
            #     data = {"error":"Temporarily unavailable."}
            #     return data,400
        result = cursor.fetchall()

        if not result:
            return {"error": "No outlets available for this employee."}, 400
        row_headers=[x[0] for x in cursor.description] 
        json_data=[]
        for res in result:
            json_data.append(dict(zip(row_headers,res)))
        response_json = []
        for i in json_data:
            outlet_json ={"name":i["Outlet"],"value":i["Outlet"], "company": i["Company_name"], "address": i["address"], "loyalty_percent": float(i["loyalty_percent"]), "sms_text": i["sms_text"], "logo": i["logo"], "bill_prefix": i["bill_prefix"]}
            response_json.append(outlet_json)
        mydb.close()
        return response_json,200
    except Exception as error:
        data ={'error':str(error)}
        return data,400