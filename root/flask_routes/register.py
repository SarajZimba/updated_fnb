from flask import  Blueprint,request
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv
load_dotenv()
app_file38 = Blueprint('app_file38',__name__)
import secrets
from .postintosalesproportal import registeruserinsalesproportal

@app_file38.route("/register", methods=["POST"])
@cross_origin()
def login():
    try:
        mydb = mysql.connector.connect(host=os.getenv('host'), user=os.getenv('user'), password=os.getenv('password'))
        cursor = mydb.cursor(buffered=True)
        database_sql = "USE {};".format(os.getenv('database'))
        cursor.execute(database_sql)
        json = request.get_json()
        if "baseURL" not in json  or "restaurantURL" not in json or not json["restaurantURL"] or "username" not in json or "password" not in json or not any([json["username"],json["password"], json["type"]]) or json["username"] =="" or json["password"]=="" or json["type"] == "" or "type" not in json or json["type"] == "":
            data = {"error":"Some fields missing."}
            return data,400
        uname = json["username"]
        upass = json["password"]
        type = json["type"]
        # token = secrets.token_hex(16)
        token = "test"

        restaurantURL = json["restaurantURL"]

        baseURL = json["baseURL"]

        # Check if the username already exists
        check_user_sql = """SELECT COUNT(*) FROM EmployeeLogin WHERE userName = %s"""
        cursor.execute(check_user_sql, (uname,))
        user_exists = cursor.fetchone()[0]
        
        if user_exists > 0:
            return {"error": "Username already exists."}, 400

        get_outlet_sql =f"""insert into EmployeeLogin (userName, Password, type, token) Values (%s, %s, %s, %s)"""
        cursor.execute(get_outlet_sql,(uname,upass, type, token),)

        # 1️⃣ Get new employee ID
        employee_id = cursor.lastrowid

        # 2️⃣ Get all outlet IDs
        cursor.execute("SELECT id FROM outetNames")
        outlet_ids = [row[0] for row in cursor.fetchall()]

        # 3️⃣ Assign employee to all outlets
        for outlet_id in outlet_ids:
            cursor.execute(
                "INSERT IGNORE INTO employeeoutlets (employee_id, outlet_id) VALUES (%s, %s)",
                (employee_id, outlet_id)
            )
        mydb.commit()
        mydb.close()

        if type == "admin":
            insertaccountingdata = {
                "username": uname,
                "password": upass,
                "restaurantURL": restaurantURL,
                "baseURL": baseURL
            }


            register_url = registeruserinsalesproportal(insertaccountingdata)
            return {"data":"user registered successfully"},200
        
        salespropotal_url = os.getenv('salesproportal_url')
        register_url = salespropotal_url + "/registerAccountingInfopwordersystem"
        return {"data":"user registered successfully"},200
    except Exception as error:
        data ={'error':str(error)}
        return data,400

# from flask import  Blueprint,request
# import mysql.connector
# from flask_cors import cross_origin
# import os
# from dotenv import load_dotenv
# load_dotenv()
# app_file38 = Blueprint('app_file38',__name__)
# import secrets
# from .postintosalesproportal import registeruserinsalesproportal

# @app_file38.route("/register", methods=["POST"])
# @cross_origin()
# def login():
#     try:
#         mydb = mysql.connector.connect(host=os.getenv('host'), user=os.getenv('user'), password=os.getenv('password'))
#         cursor = mydb.cursor(buffered=True)
#         database_sql = "USE {};".format(os.getenv('database'))
#         cursor.execute(database_sql)
#         json = request.get_json()
#         if "baseURL" not in json  or "restaurantURL" not in json or not json["restaurantURL"] or "username" not in json or "password" not in json or not any([json["username"],json["password"], json["type"]]) or json["username"] =="" or json["password"]=="" or json["type"] == "" or "type" not in json or json["type"] == "":
#             data = {"error":"Some fields missing."}
#             return data,400
#         uname = json["username"]
#         upass = json["password"]
#         type = json["type"]
#         # token = secrets.token_hex(16)
#         token = "test"

#         restaurantURL = json["restaurantURL"]

#         baseURL = json["baseURL"]

#         # Check if the username already exists
#         check_user_sql = """SELECT COUNT(*) FROM EmployeeLogin WHERE userName = %s"""
#         cursor.execute(check_user_sql, (uname,))
#         user_exists = cursor.fetchone()[0]
        
#         if user_exists > 0:
#             return {"error": "Username already exists."}, 400

#         get_outlet_sql =f"""insert into EmployeeLogin (userName, Password, type, token) Values (%s, %s, %s, %s)"""
#         cursor.execute(get_outlet_sql,(uname,upass, type, token),)

#         if type == "admin":
#             insertaccountingdata = {
#                 "username": uname,
#                 "password": upass,
#                 "restaurantURL": restaurantURL,
#                 "baseURL": baseURL
#             }


#             register_url = registeruserinsalesproportal(insertaccountingdata)
#             return {"data":"user registered successfully"},200
        
#         outlet = None
#         if type == "counteruser":
#             outlet = json.get("outlet", None)
#             insert_query = """
#                 INSERT INTO tblcounteruser (userName, Password, token, type, outlet)
#                 VALUES (%s, %s, %s, %s, %s)
#             """
#             cursor.execute(insert_query, (uname, upass, token, type, outlet))

#         mydb.commit()
#         mydb.close()
#         salespropotal_url = os.getenv('salesproportal_url')
#         register_url = salespropotal_url + "/registerAccountingInfopwordersystem"
#         return {"data":"user registered successfully"},200
#     except Exception as error:
#         data ={'error':str(error)}
#         return data,400