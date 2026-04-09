from flask import Flask, Blueprint,request
import mysql.connector
from flask_cors import  cross_origin
import os
from dotenv import load_dotenv
load_dotenv()
app_file72= Blueprint('app_file72',__name__)
from root.auth.check import token_auth





@app_file72.route("/billinfo_byid", methods=["POST"])
@cross_origin()
def billinfo():
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
        if  "bill_id" not in json:
            data = {"error":"Some fields are missing"}
            return data,400
        BillId = json["bill_id"]
        billdetailsSql =f"""SELECT bill_no, employee, Table_No,Start_Time,End_Time,Type,Date,serviceCharge,vat,total,PaymentMode FROM `tblorderhistory` WHERE idtblorderHistory=%s """
        cursor.execute(billdetailsSql,(BillId,),)
        result = cursor.fetchall()
        if result == []:
            data = {"error":"No data available."}
            return data,400
        row_headers=[x[0] for x in cursor.description] 
        json_data=[]
        for res in result:
            json_data.append(dict(zip(row_headers,res)))
        billitemDetailsSql = f"""SELECT a.itemName, sum(a.count) as Quantity, a.itemrate, a.total,a.ItemType FROM tblorder_detailshistory a, tblorderhistory b  WHERE a.order_ID = b.idtblorderHistory and b.idtblorderHistory =%s group by a.itemName"""
        cursor.execute(billitemDetailsSql,(BillId,),)
        billitemresult = cursor.fetchall()
        if billitemresult == []:
            data = {"error":"No data available."}
            return data,400
        row_headers=[x[0] for x in cursor.description] 
        billItemdata ={}
        for res in billitemresult:
            billItemdata.setdefault("Details",[]).append(dict(zip(row_headers,res)))
        json_data[0]["details"]=billItemdata["Details"]   
        
        billTotalQuantitySql =f"""SELECT a.itemName, sum(a.count) as Quantity FROM tblorder_detailshistory a, tblorderhistory b  WHERE a.order_ID = b.idtblorderHistory and  b.idtblorderHistory =%s"""
        cursor.execute(billTotalQuantitySql,(BillId,),)
        billTotalQuantityresult = cursor.fetchall()
        billTotalQuantitdata =[]
        for res in billTotalQuantityresult:
            billTotalQuantitdata.append(dict(zip(row_headers,res)))
        json_data[0]["TotalCount"]=billTotalQuantitdata[0]["Quantity"]
        mydb.close()
        return json_data[0],200
    except Exception as error:
        data ={'error':str(error)}
        return data,400
    