# from flask import Flask, Blueprint, request, jsonify
# import os
# import mysql.connector
# from flask_cors import cross_origin
# from dotenv import load_dotenv
# load_dotenv()
# from root.auth.check import token_auth
# app_file49 = Blueprint('app_file49', __name__)



# @app_file49.route("/purchasefiltervendorwisefrompurchaseitem", methods=["POST"])
# @cross_origin()
# def purchasefilter():
#     try:
#         mydb = mysql.connector.connect(host=os.getenv('host'), user=os.getenv('user'), password=os.getenv('password'))

#         cursor = mydb.cursor(buffered=True)

#         database_sql = "USE {};".format(os.getenv('database'))

#         cursor.execute(database_sql)
#         json =request.get_json()

#         if "token" not in json or json["token"] == "":
#             return {"error": "Token is not provided"}, 400

#         token = json["token"]

#         if not token_auth(token):
#             return {"error": "Invalid Token provided"}, 400

#         if "item" not in json or json["item"] == "" or "dateStart" not in json or json["dateStart"] == "" or "dateEnd" not in json or json["dateEnd"] == "":
#             return {"error": "Some fields are missing"}, 400

#         item = json["item"]
#         dateStart = json["dateStart"]
#         dateEnd = json["dateEnd"]

#         sql = """SELECT a.ReceivedDate, a.Company_Name, b.UnitsOrdered, b.UOM , b.Rate, (b.UnitsOrdered* b.Rate) as Total,a.GRN, b.Taxable , b.StockType , b.GroupName, b.Department  from intbl_purchaserequisition a , intbl_purchaserequisition_contract b where a.IDIntbl_PurchaseRequisition = b.PurchaseReqID and b.Name = %s and a.ReceivedDate between %s and %s order by a.ReceivedDate DESC """


#         cursor.execute(sql, (item, dateStart, dateEnd,))

#         # cursor.description has the metadata about the elements in the first index or 0 
#         columns = [col[0] for col in cursor.description]

#         # cursor.fetchall() give the rows and zip combines the column names with the rows and dict then converts it into dictinaries
#         data = [dict(zip(columns, row)) for row in cursor.fetchall()]


#         responseJson = {"data":data}
#         return responseJson, 200 


#     except mysql.connector.Error as db_error:
#         return jsonify({"error": f"Database error: {str(db_error)}"}), 500
#     except Exception as e:
#         return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
#     finally:
#         if mydb:
#             mydb.close()

from flask import Flask, Blueprint, request, jsonify
import os
import mysql.connector
from flask_cors import cross_origin
from dotenv import load_dotenv
load_dotenv()
from root.auth.check import token_auth
app_file49 = Blueprint('app_file49', __name__)


from .utils import get_costcenterwisestockissue


@app_file49.route("/purchasefiltervendorwisefrompurchaseitem", methods=["POST"])
@cross_origin()
def purchasefilter():
    try:
        mydb = mysql.connector.connect(host=os.getenv('host'), user=os.getenv('user'), password=os.getenv('password'))

        cursor = mydb.cursor(buffered=True)

        database_sql = "USE {};".format(os.getenv('database'))

        cursor.execute(database_sql)
        json =request.get_json()

        if "token" not in json or json["token"] == "":
            return {"error": "Token is not provided"}, 400

        token = json["token"]

        if not token_auth(token):
            return {"error": "Invalid Token provided"}, 400

        # if "item" not in json or json["item"] == "" or "outlet" not in json or json["outlet"] == "" or "dateStart" not in json or json["dateStart"] == "" or "dateEnd" not in json or json["dateEnd"] == "":
        if "item" not in json or json["item"] == "" or "dateStart" not in json or json["dateStart"] == "" or "dateEnd" not in json or json["dateEnd"] == "":
            return {"error": "Some fields are missing"}, 400

        item = json["item"]
        dateStart = json["dateStart"]
        dateEnd = json["dateEnd"]
        outlet = json.get("outlet", None)

        sql = """SELECT a.ReceivedDate, a.Company_Name, b.UnitsOrdered, b.UOM , b.Rate, (b.UnitsOrdered* b.Rate) as Total,a.GRN, b.Taxable , b.StockType , b.GroupName, b.Department  from intbl_purchaserequisition a , intbl_purchaserequisition_contract b where a.IDIntbl_PurchaseRequisition = b.PurchaseReqID and b.Name = %s and a.ReceivedDate between %s and %s and a.Outlet_Name = %s order by a.ReceivedDate DESC """


        cursor.execute(sql, (item, dateStart, dateEnd,outlet, ))

        # cursor.description has the metadata about the elements in the first index or 0 
        columns = [col[0] for col in cursor.description]

        # cursor.fetchall() give the rows and zip combines the column names with the rows and dict then converts it into dictinaries
        data = [dict(zip(columns, row)) for row in cursor.fetchall()]

        itemsCostCenterWisedata  = get_costcenterwisestockissue(item,dateStart, dateEnd, cursor, outlet)

        responseJson = {"data":data, "CostCenterIssuedData": itemsCostCenterWisedata}
        return responseJson, 200 


    except mysql.connector.Error as db_error:
        return jsonify({"error": f"Database error: {str(db_error)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
    finally:
        if mydb:
            mydb.close()


