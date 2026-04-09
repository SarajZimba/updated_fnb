# from flask import  Blueprint,request
# import mysql.connector
# from flask_cors import cross_origin
# import os
# from dotenv import load_dotenv
# load_dotenv()
# app_file10= Blueprint('app_file10',__name__)
# from root.auth.check import token_auth
# import re

# def valid_date(datestring):
#         try:
#                 regex = re.compile("^(\d{4})-(0[1-9]|1[0-2]|[1-9])-([1-9]|0[1-9]|[1-2]\d|3[0-1])$")
#                 match = re.match(regex, datestring)
#                 if match is not None:
#                     return True
#         except ValueError:
#             return False
#         return False
# @app_file10.route("/summaryreport", methods=["POST"])
# @cross_origin()
# def statsummary():
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
#         if "outlet" not in json or "dateStart" not in json or "dateEnd" not in json:
#             data = {"error":"Some fields are missing"}
#             return data,400
#         outletName = json["outlet"]
#         start_Date = json["dateStart"]
#         end_Date = json["dateEnd"]
#         if not valid_date(start_Date) or not valid_date(end_Date):
#             data={"error":"Invalid date supplied."}
#             return data,400
#         statsSql =f"""SELECT (SELECT sum(b.total) FROM  tblorderhistory b WHERE not b.bill_no='' and  b.Date BETWEEN '{start_Date}' and '{end_Date}' and b.Outlet_Name = %s) AS TOTALSALES,(SELECT sum(b.total) FROM  tblorderhistory b WHERE not b.bill_no='' and  b.Date BETWEEN '{start_Date}' and '{end_Date}' and b.Outlet_Name = %s and b.Type='Dine-In' ) AS DineInSALES,(SELECT sum(b.total) FROM  tblorderhistory b WHERE not b.bill_no='' and  b.Date BETWEEN '{start_Date}' and '{end_Date}' and b.Outlet_Name = %s and b.Type='Order') AS TabSALES,
# (SELECT SUM(b.Total-b.serviceCharge-b.VAT) FROM  tblorderhistory b WHERE not b.bill_no='' and  b.Date BETWEEN '{start_Date}' and '{end_Date}' and b.Outlet_Name = %s) AS netTOTALSALES,
# (SELECT SUM(b.Total-b.serviceCharge-b.VAT) FROM  tblorderhistory b WHERE not b.bill_no='' and  b.Date BETWEEN '{start_Date}' and '{end_Date}' and b.Outlet_Name = %s and b.Type='Dine-In') AS netDineInSALES,
# (SELECT SUM(b.Total-b.serviceCharge-b.VAT) FROM  tblorderhistory b WHERE not b.bill_no='' and  b.Date BETWEEN '{start_Date}' and '{end_Date}' and b.Outlet_Name = %s and b.Type='Order') AS netTabSALES,
# (SELECT SUM(b.VAT) FROM  tblorderhistory b WHERE not b.bill_no='' and  b.Date BETWEEN '{start_Date}' and '{end_Date}' and b.Outlet_Name = %s) AS TotalVat,(SELECT SUM(b.VAT) FROM  tblorderhistory b WHERE not b.bill_no='' and  b.Date BETWEEN '{start_Date}' and '{end_Date}' and b.Outlet_Name = %s and b.Type='Dine-In') AS DineInVAT,
# (SELECT SUM(b.VAT) FROM  tblorderhistory b WHERE not b.bill_no='' and  b.Date BETWEEN '{start_Date}' and '{end_Date}' and b.Outlet_Name = %s and b.Type='Order') AS TabVAT,(SELECT SUM(b.serviceCharge) FROM  tblorderhistory b WHERE not b.bill_no='' and  b.Date BETWEEN '{start_Date}' and '{end_Date}' and b.Outlet_Name = %s) AS TotalServiceCharge,(SELECT SUM(b.serviceCharge) FROM  tblorderhistory b WHERE not b.bill_no='' and  b.Date BETWEEN '{start_Date}' and '{end_Date}' and b.Outlet_Name = %s and b.Type='Dine-In') AS DineInServiceCharge,(SELECT SUM(b.serviceCharge) FROM  tblorderhistory b WHERE not b.bill_no='' and  b.Date BETWEEN '{start_Date}' and '{end_Date}' and b.Outlet_Name = %s and b.Type='Order') AS TabServiceCharge,(SELECT SUM(b.NoOfGuests) FROM  tblorderhistory b WHERE not b.bill_no='' and  b.Date BETWEEN '{start_Date}' and '{end_Date}' and b.Outlet_Name = %s ) AS TotalGuests,(SELECT SUM(b.DiscountAmt) FROM  tblorderhistory b WHERE not b.bill_no='' and  b.Date BETWEEN '{start_Date}' and '{end_Date}' and b.Outlet_Name = %s ) AS DiscountAmountSum,
# (SELECT SUM(a.total) FROM tblorder_detailshistory a, tblorderhistory b WHERE not b.bill_no='' and a.order_ID = b.idtblorderHistory and b.Date BETWEEN '{start_Date}' and '{end_Date}' and b.Outlet_Name = %s and a.itemType='Food' ) AS FoodSale,(SELECT SUM(a.total) FROM tblorder_detailshistory a, tblorderhistory b WHERE not b.bill_no='' and a.order_ID = b.idtblorderHistory and b.Date BETWEEN '{start_Date}' and '{end_Date}' and b.Outlet_Name = %s and a.itemType='Beverage' ) AS BeverageSale,(SELECT SUM(a.total) FROM tblorder_detailshistory a, tblorderhistory b WHERE not b.bill_no='' and a.order_ID = b.idtblorderHistory and b.Date BETWEEN '{start_Date}' and '{end_Date}' and b.Outlet_Name = %s and a.itemType='Other' ) AS OtherSale"""
#         cursor.execute(statsSql,(outletName,outletName,outletName,outletName,outletName,outletName,outletName,outletName,outletName,outletName,outletName,outletName,outletName,outletName,outletName,outletName,outletName,),)
#         statsResult = cursor.fetchall()
#         Stats_json_data=[]
#         if statsResult == []:
#             Stats_json_data["Data"] = {"error":"No data available."}
#         else:    
#             row_headers=[x[0] for x in cursor.description] 
#             for res in statsResult:
#                 Stats_json_data.append(dict(zip(row_headers,res)))
#         paymentStats_Sql =f"""SELECT  CONVERT(sum(Total),CHAR) as Total, PaymentMode FROM tblorderhistory where Date BETWEEN %s and %s and Outlet_Name =%s group by PaymentMode """
#         cursor.execute(paymentStats_Sql,(start_Date,end_Date,outletName,),)
#         paymentStatsResult = cursor.fetchall()
#         paymentStats_json_data={}
#         if paymentStatsResult == []:
#             paymentStats_json_data["Data"] = {"error":"No data available."}
#         else:
#             row_headers=[x[0] for x in cursor.description] 
#             for res in paymentStatsResult:
#                 paymentkey= dict(zip(row_headers,res))["PaymentMode"]
#                 paymentkey=paymentkey.replace(" ", "")
#                 paymentStats_json_data[paymentkey]=dict(zip(row_headers,res))["Total"]
#             if "Cash" not in paymentStats_json_data:
#                 paymentStats_json_data["Cash"]="0"
        
#             if "Complimentary" not in paymentStats_json_data and "NonChargeable" not in paymentStats_json_data:
#                 paymentStats_json_data["Complimentary"]="0"
#             if "CreditCard" not in paymentStats_json_data:
#                 paymentStats_json_data["CreditCard"]="0"    
#             if "MobilePayment" not in paymentStats_json_data:
#                 paymentStats_json_data["MobilePayment"]="0"    
#             if "NonChargeable" not in paymentStats_json_data:
#                 paymentStats_json_data["NonChargeable"]="0"
#             if "Split" not in paymentStats_json_data:
#                 paymentStats_json_data["Split"]="0"    
#             if "Credit" not in paymentStats_json_data:
#                 paymentStats_json_data["Credit"]="0"  
#             if "NonChargeable" in paymentStats_json_data and "Complimentary" in paymentStats_json_data:
#                 paymentStats_json_data["Complimentary"]=str(float(paymentStats_json_data["NonChargeable"]) +   float(paymentStats_json_data["Complimentary"]) or 0 )        
#             if "NonChargeable" in paymentStats_json_data and "Complimentary" not in paymentStats_json_data:
#                 paymentStats_json_data["Complimentary"]= paymentStats_json_data["NonChargeable"]
#         # Stats_json_data[0]["paymentStats"]=paymentStats_json_data

#         # =========================
#         # GET TOTAL VALUE OF SPLIT BILLS
#         # =========================
#         split_total_sql = """
#         SELECT SUM(Total)
#         FROM tblorderhistory
#         WHERE Date BETWEEN %s AND %s
#         AND Outlet_Name=%s
#         AND PaymentMode='Split'
#         """
#         cursor.execute(split_total_sql,(start_Date,end_Date,outletName))
#         split_total = cursor.fetchone()[0] or 0

#         # create split object
#         split_object = {
#             "total": str(float(split_total))
#         }


#         # =========================
#         # GET PAYMENT BREAKDOWN INSIDE SPLIT
#         # =========================
#         split_sql = """
#         SELECT ph.paymentMode, SUM(ph.paymentAmount) as Total
#         FROM payment_history ph
#         JOIN tblorderhistory th
#         ON ph.orderHistoryid = th.idtblorderhistory
#         WHERE th.Date BETWEEN %s AND %s
#         AND th.Outlet_Name = %s
#         GROUP BY ph.paymentMode
#         """
#         cursor.execute(split_sql,(start_Date,end_Date,outletName))
#         split_rows = cursor.fetchall()

#         for mode,total in split_rows:

#             mode = mode.replace(" ","")

#             # ADD TO MAIN PAYMENT TOTALS
#             if mode in paymentStats_json_data:
#                 paymentStats_json_data[mode] = str(
#                     float(paymentStats_json_data[mode]) + float(total or 0)
#                 )
#             else:
#                 paymentStats_json_data[mode] = str(float(total or 0))

#             # ADD INSIDE SPLIT OBJECT
#             split_object[mode] = str(float(total or 0))


#         # =========================
#         # REPLACE SPLIT VALUE WITH OBJECT
#         # =========================
#         # paymentStats_json_data["Split"] = split_object
#         paymentStats_json_data["Split"] = split_object["total"]


#         # update again in main json
#         Stats_json_data[0]["paymentStats"]=paymentStats_json_data



#         query = """
#         SELECT 
#             oh.Outlet_Name AS Outlet,
#             -- Calculate Complimentary Sales
#             COALESCE(SUM(CASE WHEN oh.PaymentMode IN ('Complimentary', 'Non Chargeable') THEN oh.Total END), 0) AS Complimentary_Sales,
#             -- Calculate Banquet Sales
#             COALESCE(SUM(CASE WHEN oh.Type = 'Banquet' THEN oh.Total END), 0) AS Banquet_Sales,
#             -- Calculate Discount Sales
#             COALESCE(SUM(oh.DiscountAmt), 0) AS Discounts_Sales,
#             -- Calculate Food Sales from tblorder_detailshistory
#             COALESCE((
#                 SELECT SUM(od.Total)
#                 FROM tblorder_detailshistory od
#                 WHERE od.ItemType = 'Food'
#                 AND od.order_ID IN (
#                     SELECT idtblorderHistory 
#                     FROM tblorderhistory 
#                     WHERE oh.Outlet_Name = Outlet_Name AND Date BETWEEN %s AND %s AND bill_no != ''
#                 )
#             ), 0) AS Food_Sales,
#             -- Calculate Beverage Sales from tblorder_detailshistory
#             COALESCE((
#                 SELECT SUM(od.Total)
#                 FROM tblorder_detailshistory od
#                 WHERE od.ItemType = 'Beverage'
#                 AND od.order_ID IN (
#                     SELECT idtblorderHistory 
#                     FROM tblorderhistory 
#                     WHERE oh.Outlet_Name = Outlet_Name AND Date BETWEEN %s AND %s AND bill_no != ''
#                 )
#             ), 0) AS Beverage_Sales,
#             COALESCE((
#                 SELECT SUM(od.Total)
#                 FROM tblorder_detailshistory od
#                 WHERE od.ItemType = 'Other'
#                 AND od.order_ID IN (
#                     SELECT idtblorderHistory 
#                     FROM tblorderhistory 
#                     WHERE oh.Outlet_Name = Outlet_Name AND Date BETWEEN %s AND %s AND bill_no != ''
#                 )
#             ), 0) AS Other_Sales,
#             -- Calculate Total Sales from tblorderhistory for each outlet (bill_no != '' and date between given dates)
#             COALESCE(SUM(CASE 
#                 WHEN oh.bill_no != '' 
#                 AND oh.Date BETWEEN %s AND %s AND oh.Outlet_Name = Outlet_Name 
#                 THEN oh.Total 
#                 ELSE 0 
#                 END), 0) AS Total_Sales
#         FROM 
#             tblorderhistory oh
#         WHERE 
#             oh.Date BETWEEN %s AND %s
#         GROUP BY 
#             oh.Outlet_Name;
#         """

#         cursor.execute(query, (start_Date, end_Date, start_Date, end_Date, start_Date, end_Date, start_Date, end_Date, start_Date, end_Date))
#         result = cursor.fetchall()


#         sales_data = []
#         outlet_sales_set = set()  # To track outlets with data
#         for row in result:
#             outlet = row[0]
#             complimentary_sales = row[1]
#             banquet_sales = row[2]
#             discounts_sales = row[3]
#             food_sales = row[4]
#             beverage_sales = row[5]
#             other_sales = row[6]
#             total_sales = row[7]


#             net_total_sales = food_sales + beverage_sales + banquet_sales - discounts_sales + other_sales

#             without_complimentary_total_sales = food_sales + beverage_sales + banquet_sales - discounts_sales - complimentary_sales 

#             sales_data.append({
#                 "Outlet": outlet,
#                 "TotalSales": float(total_sales),
#                 "ComplimentarySales": float(complimentary_sales),
#                 "BanquetSales": float(banquet_sales),
#                 "discount": float(discounts_sales),
#                 "foodSale": float(food_sales),
#                 "beverageSale": float(beverage_sales),
#                 "otherSale": float(other_sales),
#                 "NetTotalSales": float(net_total_sales)


#             })
#             outlet_sales_set.add(row[0])
#         Stats_json_data[0]["outletwise_sales"] =sales_data

#         all_outlet_query = '''SELECT Outlet FROM outetNames'''  # Correct table name assumed to be 'outetNames'
#         cursor.execute(all_outlet_query)
#         all_outlet_result = cursor.fetchall()
#         # Extract outlet names into a set for easier comparison
#         all_outlets = {row[0] for row in all_outlet_result}
#         # Find outlets without sales and append null data for them
#         for outlet in all_outlets - outlet_sales_set:
#             sales_data.append({
#                 "outlet_name": outlet,
#                 "Outlet": outlet,
#                 "TotalSales": float(0.0),
#                 "ComplimentarySales": float(0.0),
#                 "BanquetSales": float(0.0),
#                 "discount": float(0.0),
#                 "foodSale": float(0.0),  
#                 "beverageSale": float(0.0),
#                 "otherSale": float(0.0),
#                 "NetTotalSales": float(0.0)


#             })
#         mydb.close()
#         return Stats_json_data[0]
#     except Exception as error:
#         data ={'error':str(error)}
#         return data,400


from flask import  Blueprint,request
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv
load_dotenv()
app_file10= Blueprint('app_file10',__name__)
from root.auth.check import token_auth
import re

def valid_date(datestring):
        try:
                regex = re.compile("^(\d{4})-(0[1-9]|1[0-2]|[1-9])-([1-9]|0[1-9]|[1-2]\d|3[0-1])$")
                match = re.match(regex, datestring)
                if match is not None:
                    return True
        except ValueError:
            return False
        return False
@app_file10.route("/summaryreport", methods=["POST"])
@cross_origin()
def statsummary():
    try:
        mydb = mysql.connector.connect(host=os.getenv('host'), user=os.getenv('user'), password=os.getenv('password'),charset='utf8mb4',collation='utf8mb4_unicode_ci')
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
        if "outlet" not in json or "dateStart" not in json or "dateEnd" not in json:
            data = {"error":"Some fields are missing"}
            return data,400
        # # Validate employee_id
        # if "employee_id" not in json or not json["employee_id"]:
        #     return {"error": "No employee_id provided."}, 400
        # employee_id = json["employee_id"]
        employee_id = json.get("employee_id", None)
        outletName = json["outlet"]
        start_Date = json["dateStart"]
        end_Date = json["dateEnd"]
        if not valid_date(start_Date) or not valid_date(end_Date):
            data={"error":"Invalid date supplied."}
            return data,400
        statsSql =f"""SELECT (SELECT sum(b.total) FROM  tblorderhistory b WHERE not b.bill_no='' and  b.Date BETWEEN '{start_Date}' and '{end_Date}' and b.Outlet_Name = %s) AS TOTALSALES,(SELECT sum(b.total) FROM  tblorderhistory b WHERE not b.bill_no='' and  b.Date BETWEEN '{start_Date}' and '{end_Date}' and b.Outlet_Name = %s and b.Type='Dine-In' ) AS DineInSALES,(SELECT sum(b.total) FROM  tblorderhistory b WHERE not b.bill_no='' and  b.Date BETWEEN '{start_Date}' and '{end_Date}' and b.Outlet_Name = %s and b.Type='Order') AS TabSALES,
(SELECT SUM(b.Total-b.serviceCharge-b.VAT) FROM  tblorderhistory b WHERE not b.bill_no='' and  b.Date BETWEEN '{start_Date}' and '{end_Date}' and b.Outlet_Name = %s) AS netTOTALSALES,
(SELECT SUM(b.Total-b.serviceCharge-b.VAT) FROM  tblorderhistory b WHERE not b.bill_no='' and  b.Date BETWEEN '{start_Date}' and '{end_Date}' and b.Outlet_Name = %s and b.Type='Dine-In') AS netDineInSALES,
(SELECT SUM(b.Total-b.serviceCharge-b.VAT) FROM  tblorderhistory b WHERE not b.bill_no='' and  b.Date BETWEEN '{start_Date}' and '{end_Date}' and b.Outlet_Name = %s and b.Type='Order') AS netTabSALES,
(SELECT SUM(b.VAT) FROM  tblorderhistory b WHERE not b.bill_no='' and  b.Date BETWEEN '{start_Date}' and '{end_Date}' and b.Outlet_Name = %s) AS TotalVat,(SELECT SUM(b.VAT) FROM  tblorderhistory b WHERE not b.bill_no='' and  b.Date BETWEEN '{start_Date}' and '{end_Date}' and b.Outlet_Name = %s and b.Type='Dine-In') AS DineInVAT,
(SELECT SUM(b.VAT) FROM  tblorderhistory b WHERE not b.bill_no='' and  b.Date BETWEEN '{start_Date}' and '{end_Date}' and b.Outlet_Name = %s and b.Type='Order') AS TabVAT,(SELECT SUM(b.serviceCharge) FROM  tblorderhistory b WHERE not b.bill_no='' and  b.Date BETWEEN '{start_Date}' and '{end_Date}' and b.Outlet_Name = %s) AS TotalServiceCharge,(SELECT SUM(b.serviceCharge) FROM  tblorderhistory b WHERE not b.bill_no='' and  b.Date BETWEEN '{start_Date}' and '{end_Date}' and b.Outlet_Name = %s and b.Type='Dine-In') AS DineInServiceCharge,(SELECT SUM(b.serviceCharge) FROM  tblorderhistory b WHERE not b.bill_no='' and  b.Date BETWEEN '{start_Date}' and '{end_Date}' and b.Outlet_Name = %s and b.Type='Order') AS TabServiceCharge,(SELECT SUM(b.NoOfGuests) FROM  tblorderhistory b WHERE not b.bill_no='' and  b.Date BETWEEN '{start_Date}' and '{end_Date}' and b.Outlet_Name = %s ) AS TotalGuests,(SELECT SUM(b.DiscountAmt) FROM  tblorderhistory b WHERE not b.bill_no='' and  b.Date BETWEEN '{start_Date}' and '{end_Date}' and b.Outlet_Name = %s ) AS DiscountAmountSum,
(SELECT SUM(a.total) FROM tblorder_detailshistory a, tblorderhistory b WHERE not b.bill_no='' and a.order_ID = b.idtblorderHistory and b.Date BETWEEN '{start_Date}' and '{end_Date}' and b.Outlet_Name = %s and a.itemType='Food' ) AS FoodSale,(SELECT SUM(a.total) FROM tblorder_detailshistory a, tblorderhistory b WHERE not b.bill_no='' and a.order_ID = b.idtblorderHistory and b.Date BETWEEN '{start_Date}' and '{end_Date}' and b.Outlet_Name = %s and a.itemType='Beverage' ) AS BeverageSale,(SELECT SUM(a.total) FROM tblorder_detailshistory a, tblorderhistory b WHERE not b.bill_no='' and a.order_ID = b.idtblorderHistory and b.Date BETWEEN '{start_Date}' and '{end_Date}' and b.Outlet_Name = %s and a.itemType='Other' ) AS OtherSale"""
        cursor.execute(statsSql,(outletName,outletName,outletName,outletName,outletName,outletName,outletName,outletName,outletName,outletName,outletName,outletName,outletName,outletName,outletName,outletName,outletName,),)
        statsResult = cursor.fetchall()
        Stats_json_data=[]
        if statsResult == []:
            # Stats_json_data["Data"] = {"error":"No data available."}
            Stats_json_data = []
        else:    
            row_headers=[x[0] for x in cursor.description] 
            for res in statsResult:
                Stats_json_data.append(dict(zip(row_headers,res)))
        paymentStats_Sql =f"""SELECT  CONVERT(sum(Total),CHAR) as Total, PaymentMode FROM tblorderhistory where Date BETWEEN %s and %s and Outlet_Name =%s group by PaymentMode """
        cursor.execute(paymentStats_Sql,(start_Date,end_Date,outletName,),)
        paymentStatsResult = cursor.fetchall()
        paymentStats_json_data={}
        if paymentStatsResult == []:
            # paymentStats_json_data["Data"] = {"error":"No data available."}
            paymentStats_json_data = {}
        else:
            row_headers=[x[0] for x in cursor.description] 
            for res in paymentStatsResult:
                paymentkey= dict(zip(row_headers,res))["PaymentMode"]
                paymentkey=paymentkey.replace(" ", "")
                paymentStats_json_data[paymentkey]=dict(zip(row_headers,res))["Total"]
            if "Cash" not in paymentStats_json_data:
                paymentStats_json_data["Cash"]="0"
        
            if "Complimentary" not in paymentStats_json_data and "NonChargeable" not in paymentStats_json_data:
                paymentStats_json_data["Complimentary"]="0"
            if "CreditCard" not in paymentStats_json_data:
                paymentStats_json_data["CreditCard"]="0"    
            if "MobilePayment" not in paymentStats_json_data:
                paymentStats_json_data["MobilePayment"]="0"    
            if "NonChargeable" not in paymentStats_json_data:
                paymentStats_json_data["NonChargeable"]="0"
            if "Split" not in paymentStats_json_data:
                paymentStats_json_data["Split"]="0"    
            if "Credit" not in paymentStats_json_data:
                paymentStats_json_data["Credit"]="0"  
            if "NonChargeable" in paymentStats_json_data and "Complimentary" in paymentStats_json_data:
                paymentStats_json_data["Complimentary"]=str(float(paymentStats_json_data["NonChargeable"]) +   float(paymentStats_json_data["Complimentary"]) or 0 )        
            if "NonChargeable" in paymentStats_json_data and "Complimentary" not in paymentStats_json_data:
                paymentStats_json_data["Complimentary"]= paymentStats_json_data["NonChargeable"]
        # Stats_json_data[0]["paymentStats"]=paymentStats_json_data

        # =========================
        # GET TOTAL VALUE OF SPLIT BILLS
        # =========================
        split_total_sql = """
        SELECT SUM(Total)
        FROM tblorderhistory
        WHERE Date BETWEEN %s AND %s
        AND Outlet_Name=%s
        AND PaymentMode='Split'
        """
        cursor.execute(split_total_sql,(start_Date,end_Date,outletName))
        split_total = cursor.fetchone()[0] or 0

        # create split object
        split_object = {
            "total": str(float(split_total))
        }


        # =========================
        # GET PAYMENT BREAKDOWN INSIDE SPLIT
        # =========================
        split_sql = """
        SELECT ph.paymentMode, SUM(ph.paymentAmount) as Total
        FROM payment_history ph
        JOIN tblorderhistory th
        ON ph.orderHistoryid = th.idtblorderhistory
        WHERE th.Date BETWEEN %s AND %s
        AND th.Outlet_Name = %s
        GROUP BY ph.paymentMode
        """
        cursor.execute(split_sql,(start_Date,end_Date,outletName))
        split_rows = cursor.fetchall()

        for mode,total in split_rows:

            mode = mode.replace(" ","")

            # ADD TO MAIN PAYMENT TOTALS
            if mode in paymentStats_json_data:
                paymentStats_json_data[mode] = str(
                    float(paymentStats_json_data[mode]) + float(total or 0)
                )
            else:
                paymentStats_json_data[mode] = str(float(total or 0))

            # ADD INSIDE SPLIT OBJECT
            split_object[mode] = str(float(total or 0))


        # =========================
        # REPLACE SPLIT VALUE WITH OBJECT
        # =========================
        # paymentStats_json_data["Split"] = split_object
        paymentStats_json_data["Split"] = split_object["total"]


        # update again in main json
        Stats_json_data[0]["paymentStats"]=paymentStats_json_data

        if employee_id:
            # Step 1: Get accessible outlets for this employee
            cursor.execute("""
                SELECT o.Outlet
                FROM outetNames o
                JOIN employeeoutlets eo ON eo.outlet_id = o.id
                WHERE eo.employee_id = %s AND eo.status = TRUE
            """, (employee_id,))
            accessible_outlet_result = cursor.fetchall()
            accessible_outlets = {row[0] for row in accessible_outlet_result if row[0]}  # set for faster lookup

            print("Accessible outlets:", accessible_outlets)

            if not accessible_outlets:
                Stats_json_data[0]["outletwise_sales"] = []
                return Stats_json_data[0]

            # Step 2: Query ALL outlet sales (like else block)
            query = """
            SELECT 
                oh.Outlet_Name AS Outlet,
                COALESCE(SUM(CASE WHEN oh.PaymentMode IN ('Complimentary','Non Chargeable') THEN oh.Total END),0) AS ComplimentarySales,
                COALESCE(SUM(CASE WHEN oh.Type='Banquet' THEN oh.Total END),0) AS BanquetSales,
                COALESCE(SUM(oh.DiscountAmt),0) AS Discounts,
                COALESCE((SELECT SUM(od.Total) FROM tblorder_detailshistory od 
                        WHERE od.ItemType='Food' AND od.order_ID IN (
                                SELECT idtblorderHistory FROM tblorderhistory 
                                WHERE Outlet_Name = oh.Outlet_Name AND Date BETWEEN %s AND %s AND bill_no!=''
                        )),0) AS FoodSales,
                COALESCE((SELECT SUM(od.Total) FROM tblorder_detailshistory od 
                        WHERE od.ItemType='Beverage' AND od.order_ID IN (
                                SELECT idtblorderHistory FROM tblorderhistory 
                                WHERE Outlet_Name = oh.Outlet_Name AND Date BETWEEN %s AND %s AND bill_no!=''
                        )),0) AS BeverageSales,
                COALESCE((SELECT SUM(od.Total) FROM tblorder_detailshistory od 
                        WHERE od.ItemType='Other' AND od.order_ID IN (
                                SELECT idtblorderHistory FROM tblorderhistory 
                                WHERE Outlet_Name = oh.Outlet_Name AND Date BETWEEN %s AND %s AND bill_no!=''
                        )),0) AS OtherSales,
                COALESCE(SUM(CASE WHEN oh.bill_no!='' THEN oh.Total ELSE 0 END),0) AS TotalSales
            FROM tblorderhistory oh
            WHERE oh.Date BETWEEN %s AND %s
            GROUP BY oh.Outlet_Name
            """
            params = (start_Date, end_Date, start_Date, end_Date, start_Date, end_Date, start_Date, end_Date)
            cursor.execute(query, params)
            all_results = cursor.fetchall()

            # Step 3: Keep only accessible outlets
            sales_data = []
            outlet_sales_set = set()
            for row in all_results:
                outlet = row[0]
                if outlet not in accessible_outlets:
                    continue  # skip outlets this employee cannot access

                complimentary_sales = row[1]
                banquet_sales = row[2]
                discounts_sales = row[3]
                food_sales = row[4]
                beverage_sales = row[5]
                other_sales = row[6]
                total_sales = row[7]

                net_total_sales = food_sales + beverage_sales + banquet_sales - discounts_sales + other_sales

                sales_data.append({
                    "Outlet": outlet,
                    "TotalSales": float(total_sales),
                    "ComplimentarySales": float(complimentary_sales),
                    "BanquetSales": float(banquet_sales),
                    "discount": float(discounts_sales),
                    "foodSale": float(food_sales),
                    "beverageSale": float(beverage_sales),
                    "otherSale": float(other_sales),
                    "NetTotalSales": float(net_total_sales)
                })
                outlet_sales_set.add(outlet)

            # Step 4: Add zero-data entries for accessible outlets with no sales
            for outlet in accessible_outlets - outlet_sales_set:
                sales_data.append({
                    "Outlet": outlet,
                    "TotalSales": 0.0,
                    "ComplimentarySales": 0.0,
                    "BanquetSales": 0.0,
                    "discount": 0.0,
                    "foodSale": 0.0,
                    "beverageSale": 0.0,
                    "otherSale": 0.0,
                    "NetTotalSales": 0.0
                })

            Stats_json_data[0]["outletwise_sales"] = sales_data
            mydb.close()
            return Stats_json_data[0]

        else:

            query = """
            SELECT 
                oh.Outlet_Name AS Outlet,
                -- Calculate Complimentary Sales
                COALESCE(SUM(CASE WHEN oh.PaymentMode IN ('Complimentary', 'Non Chargeable') THEN oh.Total END), 0) AS Complimentary_Sales,
                -- Calculate Banquet Sales
                COALESCE(SUM(CASE WHEN oh.Type = 'Banquet' THEN oh.Total END), 0) AS Banquet_Sales,
                -- Calculate Discount Sales
                COALESCE(SUM(oh.DiscountAmt), 0) AS Discounts_Sales,
                -- Calculate Food Sales from tblorder_detailshistory
                COALESCE((
                    SELECT SUM(od.Total)
                    FROM tblorder_detailshistory od
                    WHERE od.ItemType = 'Food'
                    AND od.order_ID IN (
                        SELECT idtblorderHistory 
                        FROM tblorderhistory 
                        WHERE oh.Outlet_Name = Outlet_Name AND Date BETWEEN %s AND %s AND bill_no != ''
                    )
                ), 0) AS Food_Sales,
                -- Calculate Beverage Sales from tblorder_detailshistory
                COALESCE((
                    SELECT SUM(od.Total)
                    FROM tblorder_detailshistory od
                    WHERE od.ItemType = 'Beverage'
                    AND od.order_ID IN (
                        SELECT idtblorderHistory 
                        FROM tblorderhistory 
                        WHERE oh.Outlet_Name = Outlet_Name AND Date BETWEEN %s AND %s AND bill_no != ''
                    )
                ), 0) AS Beverage_Sales,
                COALESCE((
                    SELECT SUM(od.Total)
                    FROM tblorder_detailshistory od
                    WHERE od.ItemType = 'Other'
                    AND od.order_ID IN (
                        SELECT idtblorderHistory 
                        FROM tblorderhistory 
                        WHERE oh.Outlet_Name = Outlet_Name AND Date BETWEEN %s AND %s AND bill_no != ''
                    )
                ), 0) AS Other_Sales,
                -- Calculate Total Sales from tblorderhistory for each outlet (bill_no != '' and date between given dates)
                COALESCE(SUM(CASE 
                    WHEN oh.bill_no != '' 
                    AND oh.Date BETWEEN %s AND %s AND oh.Outlet_Name = Outlet_Name 
                    THEN oh.Total 
                    ELSE 0 
                    END), 0) AS Total_Sales
            FROM 
                tblorderhistory oh
            WHERE 
                oh.Date BETWEEN %s AND %s
            GROUP BY 
                oh.Outlet_Name;
            """

            cursor.execute(query, (start_Date, end_Date, start_Date, end_Date, start_Date, end_Date, start_Date, end_Date, start_Date, end_Date))
            result = cursor.fetchall()


            sales_data = []
            outlet_sales_set = set()  # To track outlets with data
            for row in result:
                outlet = row[0]
                complimentary_sales = row[1]
                banquet_sales = row[2]
                discounts_sales = row[3]
                food_sales = row[4]
                beverage_sales = row[5]
                other_sales = row[6]
                total_sales = row[7]


                net_total_sales = food_sales + beverage_sales + banquet_sales - discounts_sales + other_sales

                without_complimentary_total_sales = food_sales + beverage_sales + banquet_sales - discounts_sales - complimentary_sales 

                sales_data.append({
                    "Outlet": outlet,
                    "TotalSales": float(total_sales),
                    "ComplimentarySales": float(complimentary_sales),
                    "BanquetSales": float(banquet_sales),
                    "discount": float(discounts_sales),
                    "foodSale": float(food_sales),
                    "beverageSale": float(beverage_sales),
                    "otherSale": float(other_sales),
                    "NetTotalSales": float(net_total_sales)


                })
                outlet_sales_set.add(row[0])
            Stats_json_data[0]["outletwise_sales"] =sales_data

            all_outlet_query = '''SELECT Outlet FROM outetNames'''  # Correct table name assumed to be 'outetNames'
            cursor.execute(all_outlet_query)
            all_outlet_result = cursor.fetchall()
            # Extract outlet names into a set for easier comparison
            all_outlets = {row[0] for row in all_outlet_result}
            # Find outlets without sales and append null data for them
            for outlet in all_outlets - outlet_sales_set:
                sales_data.append({
                    "outlet_name": outlet,
                    "Outlet": outlet,
                    "TotalSales": float(0.0),
                    "ComplimentarySales": float(0.0),
                    "BanquetSales": float(0.0),
                    "discount": float(0.0),
                    "foodSale": float(0.0),  
                    "beverageSale": float(0.0),
                    "otherSale": float(0.0),
                    "NetTotalSales": float(0.0)


                })
            mydb.close()
            return Stats_json_data[0]


    except Exception as error:
        data ={'error':str(error)}
        return data,400