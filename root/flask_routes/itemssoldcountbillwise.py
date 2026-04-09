from flask import  Blueprint,request
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv
load_dotenv()
from root.auth.check import token_auth
app_file71= Blueprint('app_file71',__name__)


@app_file71.route("/itemssoldcountbillwise/", methods=["POST"])
@cross_origin()
def reqfilterfirst():
    try:
        mydb = mysql.connector.connect(host=os.getenv('host'), user=os.getenv('user'), password=os.getenv('password'))
        cursor = mydb.cursor(buffered=True)
        database_sql = "USE {};".format(os.getenv('database'))
        cursor.execute(database_sql)

        data = request.get_json()


        json = request.get_json()
        if "token" not in json  or not any([json["token"]])  or json["token"]=="":
            data = {"error":"No token provided."}
            return data,400
        token = json["token"]
        if not token_auth(token):
            data = {"error":"Invalid token."}
            return data,400
        if "outlet" not in json or "dateStart" not in json or "dateEnd" not in json and "itemName" not in json:
            data = {"error":"Some fields are missing"}
            return data,400
        outlet = json["outlet"]
        startDate = json["dateStart"]
        endDate = json["dateEnd"]
        itemName = json["itemName"]


        query = """SELECT b.`Date`,b.`bill_no`,b.`Type`,b.`Start_Time`,b.`End_Time`,b.`Employee`,b.`NoOfGuests`,b.`GuestName`,a.`count`,a.`ItemName`, a.`Description`, a.`itemRate`, (a.`count`*a.`itemRate`) as Total FROM tblorderhistory b JOIN tblorder_detailshistory a ON b.idtblorderHistory = a.order_ID WHERE b.`Date` BETWEEN %s AND %s AND b.`Outlet_Name` = %s AND a.`ItemName` = %s ORDER BY b.`Date`, CAST(b.`bill_no` as unsigned)"""
        
        cursor.execute(query, (startDate, endDate, outlet, itemName,))

        results = cursor.fetchall()

        # Process results
        processed_results = []
        for row in results:
            row_dict = {
                "Date": row[0],
                "Bill_No": row[1],
                "Type": row[2],
                "Start_Time": row[3],
                "End_Time": row[4],
                "Employee": row[5],
                "NoOfGuests": row[6],
                "GuestName": row[7],
                "Count": row[8],
                "ItemName": row[9],
                "Description": row[10],
                "ItemRate": float(row[11]),  # Convert ItemRate to float
                "Total": float(row[12])  # Convert calculated Total to float
            }
            processed_results.append(row_dict)

        # responseJson = [dict(zip(columns, rows)) for rows in cursor.fetchall()]
        return processed_results,200
    except Exception as error:
        data ={'error':str(error)}                                 
        return data,400



