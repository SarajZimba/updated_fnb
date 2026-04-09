from flask import Flask, Blueprint,request
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv
load_dotenv()
app_file48= Blueprint('app_file48',__name__)
from root.auth.check import token_auth
from datetime import datetime, timedelta



@app_file48.route("/compareyearchart", methods=["POST"])
@cross_origin()
def comparetwoyearchartsummary():
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
        if "outlet" not in json :
            data = {"error":"Some fields are missing"}
            return data,400
        outletName = json["outlet"]


        cursor.execute("SELECT MIN(YEAR(DATE)) AS minYear, MAX(YEAR(DATE)) AS maxYear FROM tblorderhistory")

        year_range = cursor.fetchone()

        if not year_range or year_range[0] is None or year_range[1] is None:
            return {"error" : "No data available in the database"}, 400
        
        min_year, max_year = year_range

        responseJsonList = []

        for year in range(min_year, max_year + 1):
            yearly_data = get_yearlyjson(outletName, year, cursor)
            responseJsonList.append({"year":year, "yearly_data":yearly_data})

        mydb.close()
        return responseJsonList, 200

    except Exception as e :
        return {"error": str(e)}, 400
    

# def get_yearlyjson(outletName, year, cursor):
#         dailySql = f"""SELECT SUM(Total) as Total,DAYNAME(Date) as dayName from tblorderhistory where Outlet_Name=%s and YEAR(Date)=%s GROUP BY WEEKDAY(Date)"""
#         cursor.execute(dailySql,(outletName,year,),)
#         dailystatsResult = cursor.fetchall()
#         dailyStats_json_data=[]
#         monthTotal=[]
#         dailyTotal=[]
#         dailylabel=[]    
#         monthlylabel=[]
#         if dailystatsResult == []:
#             daily={"error":"No data available."}
#             return daily,400
#         else:
#             row_headers=[x[0] for x in cursor.description] 
#             for res in dailystatsResult:
#                 dailyStats_json_data.append(dict(zip(row_headers,res)))
#                 dailyTotal.append(str(dict(zip(row_headers,res))["Total"]))
#                 dailylabel.append(str(dict(zip(row_headers,res))["dayName"]))
#             daily=dailyStats_json_data
#             dailytotal=dailyTotal
#         monthlysql=f"""SELECT SUM(Total) as Total,MONTHNAME(Date) as monthName from tblorderhistory where Outlet_Name=%s and YEAR(Date)=%s GROUP BY MONTH(Date)"""
#         cursor.execute(monthlysql,(outletName,year,),)
#         monthlystatsResult = cursor.fetchall()
#         monthlyStats_json_data=[]
#         if monthlystatsResult == []:
#             monthly={"error":"No data available."}
#             return monthly,400
#         else:
#             row_headers=[x[0] for x in cursor.description] 
#             for res in monthlystatsResult:
#                 monthlyStats_json_data.append(dict(zip(row_headers,res)))
#                 monthTotal.append(str(dict(zip(row_headers,res))["Total"]))
#                 monthlylabel.append(str(dict(zip(row_headers,res))["monthName"]))
#             monthly=monthlyStats_json_data 
#             monthlytotal=monthTotal
#         responseJson={"daily":daily,"dailytotal":dailytotal,"dailylabel":dailylabel,"monthly":monthly,"monthlytotal":monthlytotal,"monthlylabel":monthlylabel}

#         return responseJson


def get_yearlyjson(outletName, year, cursor):
    # Define all months
    all_months = [
        "January", "February", "March", "April", "May", "June", 
        "July", "August", "September", "October", "November", "December"
    ]
    
    dailySql = f"""SELECT SUM(Total) as Total,DAYNAME(Date) as dayName 
                   from tblorderhistory 
                   where Outlet_Name=%s and YEAR(Date)=%s and not bill_no = ''
                   GROUP BY WEEKDAY(Date)"""
    cursor.execute(dailySql, (outletName, year,))
    dailystatsResult = cursor.fetchall()
    dailyStats_json_data = []
    dailyTotal = []
    dailylabel = []
    
    if dailystatsResult == []:
        daily = {"error": "No data available."}
        return daily, 400
    else:
        row_headers = [x[0] for x in cursor.description]
        for res in dailystatsResult:
            dailyStats_json_data.append(dict(zip(row_headers, res)))
            dailyTotal.append(str(dict(zip(row_headers, res))["Total"]))
            dailylabel.append(str(dict(zip(row_headers, res))["dayName"]))
        daily = dailyStats_json_data
        dailytotal = dailyTotal
    
    monthlysql = f"""SELECT SUM(Total) as Total, MONTH(Date) as month, MONTHNAME(Date) as monthName 
                     from tblorderhistory 
                     where Outlet_Name=%s and YEAR(Date)=%s and not bill_no = ''
                     GROUP BY MONTH(Date)"""
    cursor.execute(monthlysql, (outletName, year,))
    monthlystatsResult = cursor.fetchall()
    monthlyStats_json_data = []
    monthTotal = []
    monthlylabel = []
    
    # Set default Total for all months to 0.0
    monthly_data_dict = {month: {"Total": 0.0, "monthName": month} for month in all_months}
    
    # Populate months with data from the query
    for res in monthlystatsResult:
        month_number = res[1]
        month_name = res[2]
        total = res[0]
        
        # Update the data for the month
        if month_name in monthly_data_dict:
            monthly_data_dict[month_name]["Total"] = total
    
    # Extract the data for the response
    for month in all_months:
        month_data = monthly_data_dict[month]
        monthlyStats_json_data.append({"Total": str(month_data["Total"]), "monthName": month_data["monthName"]})
        monthTotal.append(str(month_data["Total"]))
        monthlylabel.append(month_data["monthName"])
    
    responseJson = {
        "daily": daily,
        "dailytotal": dailytotal,
        "dailylabel": dailylabel,
        "monthly": monthlyStats_json_data,
        "monthlytotal": monthTotal,
        "monthlylabel": monthlylabel
    }

    return responseJson