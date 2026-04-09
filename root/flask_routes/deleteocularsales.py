from flask import  Blueprint,request
import mysql.connector
from flask_cors import CORS, cross_origin
import os
from dotenv import load_dotenv
load_dotenv()
app_file64= Blueprint('app_file64',__name__)





@app_file64.route("/deleteoculardata", methods=['PUT'])
@cross_origin()
def stats():
    try:
        mydb = mysql.connector.connect(host=os.getenv('host'), user=os.getenv('user'), password=os.getenv('password'))
        cursor = mydb.cursor(buffered=True)
        database_sql = "USE {};".format(os.getenv('database'))
        cursor.execute(database_sql)
        data = request.get_json()
        sql = f"""SELECT `idtblorderHistory`as order_id FROM `tblorderhistory` WHERE `order_id_ocular`=%s"""
        cursor.execute(sql,(data["order_id_ocular"],),)
        result = cursor.fetchall()
        if result == []:
            data = {"error":"The data for this outlet orderID and date doesn't exist."}
            return data,400
        row_headers=[x[0] for x in cursor.description] 
        outletIdDatajson=[]
        for res in result:
            outletIdDatajson.append(dict(zip(row_headers,res)))    
        idList =outletIdDatajson
        for i in idList:
            pk =i["order_id"]
            sql1 = f"delete from `tblorder_detailshistory` WHERE order_ID =%s;"
            sql2 = f"delete from `tblorderhistory` WHERE `idtblorderHistory` =%s;"
            cursor.execute(sql1,(pk,),)
            cursor.execute(sql2,(pk,),)
            mydb.commit()
        creditDeleteSql=f"""DELETE FROM `CreditHistory` WHERE Outlet_OrderID=%s and Date(`Date`) = %s"""
        cursor.execute(creditDeleteSql,(data["outlet_orderID"], data["date"],),)
        mydb.commit()
        mydb.close()
        data = {"success":"Data deleted successfully"}
        return data,200
    except Exception as error:
        data ={'error':str(error)}
        return data,400