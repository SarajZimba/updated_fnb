from flask import Flask, request, Blueprint
app = Flask(__name__)
import mysql.connector
from datetime import datetime
from flask_cors import CORS, cross_origin
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SECRET_KEY'] = 'secret!'
import os
from dotenv import load_dotenv
load_dotenv()
# from flask_socketio import SocketIO, emit,join_room,leave_room
# socketio = SocketIO(app, cors_allowed_origins="*",monitor_clients=True,allow_upgrades=False)
import jwt
import pytz
from tasks import send_bulk_emails

from root.flask_routes.report import app_file1
from root.flask_routes.outletnames import app_file2
from root.flask_routes.itemStats import app_file3
from root.flask_routes.login import app_file4
from root.flask_routes.stats import app_file5
from root.flask_routes.orderhistory import app_file6
from root.flask_routes.salesreport import app_file7
from root.flask_routes.postsales import app_file8
from root.flask_routes.deletesales import app_file9
from root.flask_routes.statsummary import app_file10
from root.flask_routes.chartsummary import app_file11
from root.flask_routes.purchasereq import app_file12
from root.flask_routes.reqget import app_file13
from root.flask_routes.reqdetails import app_file14
from root.flask_routes.reqfilter import app_file15
from root.flask_routes.reqfilterfirst import app_file16
from root.flask_routes.reqitemhistory import app_file17
from root.flask_routes.customersaleshistory import app_file18
from root.flask_routes.billinfo import app_file19
from root.flask_routes.customerComplimentary import app_file20
from root.flask_routes.graphstats import app_file21
from root.flask_routes.years import app_file22
from root.flask_routes.billsearch import app_file23
from root.flask_routes.customercredit import app_file24
from root.flask_routes.CustomerCreditInsert import app_file25
from root.flask_routes.customerCreditdetails import app_file26
from root.flask_routes.customerCreditcheck import app_file27
from root.flask_routes.customerCreditleft import app_file28
from root.flask_routes.give_itemdetails import app_file29
from root.flask_routes.item_lists import app_file30



from root.flask_routes.register import app_file38 
from root.flask_routes.agentlogin import app_file39 
from root.flask_routes.userlists import app_file40
from root.flask_routes.deleteuser import app_file41
from root.flask_routes.postmenu import app_file42
from root.flask_routes.updateuser import app_file43
from root.flask_routes.deletepurchase import app_file44
from root.flask_routes.poststockstatement import app_file45
from root.flask_routes.getstocks import app_file46
from root.flask_routes.getlatestsyncdate import app_file47
from root.flask_routes.compareyearschart import app_file48
from root.flask_routes.purchasefiltervendorwisefrompurchaseItem import app_file49
from root.flask_routes.purchaseitemslist import app_file50
from root.flask_routes.topvendors import app_file51
from root.flask_routes.toppurchasingvendorsfromcount import app_file53
from root.flask_routes.salesvspurchase import app_file54
from root.flask_routes.reqdetails_portal import app_file56


from root.flask_routes.poststockTransfer import app_file57

from root.flask_routes.getallstockTransfer import app_file59
from root.flask_routes.costcenterwisestockTransfer import app_file60
from root.flask_routes.deleterequisition import app_file61
from root.flask_routes.deleteocularsales import app_file64
from root.flask_routes.daily_report import app_file65

from root.flask_routes.vendorwisepurchaseitems import app_file70
from root.flask_routes.itemssoldcountbillwise import app_file71
from root.flask_routes.billinfo_byid import app_file72
# from root.flask_routes.getsaleforecast import app_file73
# from root.flask_routes.getmonthlysaleforecast import app_file74


from root.flask_routes.posteventdate import app_file75

# from root.flask_routes.getyearlysalesforecast import app_file76
from root.flask_routes.getactualmonthsales import app_file77

from root.flask_routes.getbillno import app_file78
from root.flask_routes.getspecialevents import app_file79
# from root.flask_routes.getsaleforecastbydaterange import app_file80
from root.flask_routes.lastyear_salescheck import app_file81
from root.flask_routes.post_lastyearsales import app_file82
from root.flask_routes.deletespecialevents import app_file83
from root.flask_routes.void.gettodaysvoid_items import app_file84
from root.flask_routes.void.getvoiditemsdateandkotwise import app_file85
# from root.flask_routes.getmonthlytrackforecast import app_file86

from root.flask_routes.void.getreportitemlistsofordertracker import app_file87

from root.flask_routes.trackerreport.todaystrackerreport import app_file88

from root.flask_routes.credit.debtorssummary import app_file90
from root.flask_routes.loyalty.loyalty_customers import app_file91
from root.flask_routes.loyalty.check_guestphoneno import app_file92

from root.flask_routes.loyalty.provide_url import app_file93

from root.flask_routes.loyalty.add_loyalty_points import app_file94

# from root.flask_routes.loyalty.create_guests import app_file96
from root.flask_routes.loyalty.redeem.add_redeemableprod import app_file97
from root.flask_routes.loyalty.redeem.get_redeemableprod import app_file98
from root.flask_routes.loyalty.redeem.get_customer_redeemableprod import app_file99
from root.flask_routes.loyalty.counter.productredeemed import app_file100
from root.flask_routes.loyalty.counter.counter_login import app_file101
from root.flask_routes.employee.item_analytics import app_file102

from root.flask_routes.loyalty.get_customer_loyalty import app_file103

from root.flask_routes.employee.employee_analytics import app_file104
from root.flask_routes.employee.employee_orders import app_file105
from root.flask_routes.customerreview.customerreview import app_file106
from root.flask_routes.recipe.subrecipe import app_file107
from root.flask_routes.recipe.recipe import app_file108
from root.flask_routes.menuengineering.menuanalytics import app_file109
from root.flask_routes.menuengineering.menuconsumption import app_file110
from root.flask_routes.unitdefinition.create_stock_statement_item import app_file111
from root.flask_routes.syncmenu.syncmenu import app_file112
from root.flask_routes.menuengineering.givemenudetails import app_file113
from root.flask_routes.menuengineering.received.received_report import app_file114
from root.flask_routes.menuengineering.received.consumptionreportitemwise import app_file115
from root.flask_routes.menuengineering.received.save_summary_report import app_file116
from root.flask_routes.menuengineering.received.wastage_report import app_file117
from root.flask_routes.menuengineering.received.itemdetailconsumptionreportforsale import app_file118
from root.flask_routes.menuengineering.received.inventorysnapshotsreport import app_file119
from root.flask_routes.menuengineering.received.inventorysnapshotsreportdetails import app_file120
from root.flask_routes.menuengineering.received.physical_report import app_file121
from root.flask_routes.stocks.updatestocks import app_file122
from root.flask_routes.stocks.deletestocks import app_file123
from root.flask_routes.menuengineering.received.giveopeningclosingdate import app_file124
from root.flask_routes.menuengineering.foodandcostinganalysis import app_file125
from root.flask_routes.menuengineering.received.editinventorysnapshotdetails import app_file126
from root.flask_routes.postcustomer import customer_bp
from root.flask_routes.email_history import email_history_bp

from root.flask_routes.unitdefinition.unitdefinition import app_file200
from root.flask_routes.sms_outlet.smsforoutlet import app_file201
from root.flask_routes.sms_outlet.sparrowsms import app_file202
from root.flask_routes.sms_outlet.bulksparrowsms import app_file204
from root.flask_routes.sms_outlet.sms_history import app_file205

from root.flask_routes.getweeklysales  import app_file207
from root.flask_routes.outletlogo import app_file208
from root.flask_routes.postaddcustomerinbill import app_file209
from root.flask_routes.gettableno import app_file210
from root.flask_routes.table.save_table_coordinates import app_file211
from root.flask_routes.table.get_table_coordinates import app_file212
from root.flask_routes.heatmap.heatmap_by_sales import app_file213
from root.flask_routes.heatmap.heatmap_by_ordercount import app_file214
from root.flask_routes.salesitems_itemwise_alloutlets import app_file215
from root.flask_routes.item_lists_from_order import app_file216
from root.flask_routes.purchasebyoutlet import app_file217

from root.flask_routes.employee_outlets.give_employee_outlets import app_file220
from root.flask_routes.employee_outlets.remove_employeeaccess_to_outlet import app_file221

from root.flask_routes.postdebitnote import app_file224


app.register_blueprint(app_file1)
app.register_blueprint(app_file2)
app.register_blueprint(app_file3)
app.register_blueprint(app_file4)
app.register_blueprint(app_file5)
app.register_blueprint(app_file6)
app.register_blueprint(app_file7)
app.register_blueprint(app_file8)
app.register_blueprint(app_file9)
app.register_blueprint(app_file10)
app.register_blueprint(app_file11)
app.register_blueprint(app_file12)
app.register_blueprint(app_file13)
app.register_blueprint(app_file14)
app.register_blueprint(app_file15)
app.register_blueprint(app_file16)
app.register_blueprint(app_file17)
app.register_blueprint(app_file18)
app.register_blueprint(app_file19)
app.register_blueprint(app_file20)
app.register_blueprint(app_file21)
app.register_blueprint(app_file22)
app.register_blueprint(app_file23)
app.register_blueprint(app_file24)
app.register_blueprint(app_file25)
app.register_blueprint(app_file26)
app.register_blueprint(app_file27)
app.register_blueprint(app_file28)
app.register_blueprint(app_file29)
app.register_blueprint(app_file30)


app.register_blueprint(app_file38)
app.register_blueprint(app_file39)
app.register_blueprint(app_file40)
app.register_blueprint(app_file41)
app.register_blueprint(app_file42)
app.register_blueprint(app_file43)
app.register_blueprint(app_file44)
app.register_blueprint(app_file45)
app.register_blueprint(app_file46)
app.register_blueprint(app_file47)
app.register_blueprint(app_file48)
app.register_blueprint(app_file49)
app.register_blueprint(app_file50)
app.register_blueprint(app_file51)
app.register_blueprint(app_file53)
app.register_blueprint(app_file54)


app.register_blueprint(app_file56)
app.register_blueprint(app_file57)

app.register_blueprint(app_file59)
app.register_blueprint(app_file60)
app.register_blueprint(app_file61)
app.register_blueprint(app_file64)
app.register_blueprint(app_file65)
app.register_blueprint(app_file70)
app.register_blueprint(app_file71) 
app.register_blueprint(app_file72) 
# app.register_blueprint(app_file73)
# app.register_blueprint(app_file74)
app.register_blueprint(app_file75)
# app.register_blueprint(app_file76)
app.register_blueprint(app_file77)
app.register_blueprint(app_file78)
app.register_blueprint(app_file79)
# app.register_blueprint(app_file80)
app.register_blueprint(app_file81)
app.register_blueprint(app_file82)
app.register_blueprint(app_file83)
app.register_blueprint(app_file84)
app.register_blueprint(app_file85)
# app.register_blueprint(app_file86)

app.register_blueprint(app_file87)
app.register_blueprint(app_file88)

app.register_blueprint(app_file90)
app.register_blueprint(app_file91)
app.register_blueprint(app_file92)

app.register_blueprint(app_file93)
app.register_blueprint(app_file94)

# app.register_blueprint(app_file96)
app.register_blueprint(app_file97)
app.register_blueprint(app_file98)
app.register_blueprint(app_file99)
app.register_blueprint(app_file100)


app.register_blueprint(app_file101)
app.register_blueprint(app_file102)

app.register_blueprint(app_file103)
app.register_blueprint(app_file104)
app.register_blueprint(app_file105)
app.register_blueprint(app_file106) 

app.register_blueprint(app_file107)
app.register_blueprint(app_file108)
app.register_blueprint(app_file109)
app.register_blueprint(app_file110)
app.register_blueprint(app_file111)
app.register_blueprint(app_file112)
app.register_blueprint(app_file113)
app.register_blueprint(app_file114)
app.register_blueprint(app_file115)
app.register_blueprint(app_file116)
app.register_blueprint(app_file117)
app.register_blueprint(app_file118)
app.register_blueprint(app_file119)
app.register_blueprint(app_file120)
app.register_blueprint(app_file121)
app.register_blueprint(app_file122)
app.register_blueprint(app_file123)
app.register_blueprint(app_file124)
app.register_blueprint(app_file125)
app.register_blueprint(app_file126)
app.register_blueprint(customer_bp)
app.register_blueprint(email_history_bp)


app.register_blueprint(app_file200)
app.register_blueprint(app_file201)
app.register_blueprint(app_file202)
app.register_blueprint(app_file204)
app.register_blueprint(app_file205)
app.register_blueprint(app_file207)
app.register_blueprint(app_file208)
app.register_blueprint(app_file209)
app.register_blueprint(app_file210)
app.register_blueprint(app_file211)
app.register_blueprint(app_file212)
app.register_blueprint(app_file213)
app.register_blueprint(app_file214)
app.register_blueprint(app_file215)
app.register_blueprint(app_file216)
app.register_blueprint(app_file217)
# app.register_blueprint(app_file218)
# app.register_blueprint(app_file219)
app.register_blueprint(app_file220)
app.register_blueprint(app_file221)
app.register_blueprint(app_file224)


@app.route("/entry1", methods=["POST"])
@cross_origin()
def entry1():
    mydb = mysql.connector.connect(host=os.getenv('host'), user=os.getenv('user'), password=os.getenv('password'))
    cursor = mydb.cursor(buffered=True)
    database_sql = "USE {};".format(os.getenv('database'))
    cursor.execute(database_sql)
    json_data = request.get_json()
    
    perm_outlet_orderID = json_data["outlet_orderID"]
    perm_orderTime = json_data["orderTime"]
    perm_completedAt = json_data["completedAt"]
    perm_totalTime = json_data["TotalTime"]
    perm_tableNum = json_data["tableNum"]
    perm_employee = json_data["employee"]
    perm_orderType = json_data["orderType"]
    perm_currentState = json_data["currentState"]
    perm_outlet_Name = json_data["outlet_Name"]
    perm_guests = json_data["Guest_count"]
    perm_OrderItemDetailsList = json_data["OrderItemDetailsList"]
    perm_kotid = json_data["KOTID"]
    import datetime
    date = datetime.date.today().strftime('%Y-%m-%d')

    try:
        # Insert main order details into tblorderTracker
        sql_order_tracker = """INSERT INTO tblorderTracker (outlet_orderID, Date, tableNum, orderedAt, completedAt, TotalTime, orderType, currentState, Quantity, outlet_Name, Employee, Guest_count, KOTID)
                              VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(sql_order_tracker, (perm_outlet_orderID, date, perm_tableNum, perm_orderTime, perm_completedAt, perm_totalTime, perm_orderType, perm_currentState, perm_guests, perm_outlet_Name, perm_employee, perm_guests, perm_kotid))
        mydb.commit()

        # Get the ID of the inserted order
        order_id = cursor.lastrowid

        # Insert each item detail into tblorderTracker_Details
        for item_details in perm_OrderItemDetailsList:
            item_name = item_details["ItemName"]
            item_quantity = item_details["Quantity"]
            item_modifications = item_details.get("Modifications", "")
            item_prep_time = item_details.get("AveragePrepTime", "")
            item_price = item_details["item_price"]
            item_category = item_details["category"]
            item_completedAt = item_details["completedAt"]
            item_totalTime = item_details["TotalTime"]
            item_prepTime = item_details["prepTimeDifference"]
            # item_voidAt = item_details["voidAt"]
            # item_voidTotalTime = item_details["voidTotalTime"]

            if "voidAt" in item_details and "voidTotalTime" in item_details:
                item_voidAt = item_details["voidAt"]
                item_voidTotalTime = item_details["voidTotalTime"]
            else:
                item_voidAt = None  # If not present, set to None
                item_voidTotalTime = None

            sql_item_details = """INSERT INTO tblorderTracker_Details (orderedAt, completedAt, TotalTime, ItemName, Quantity, Modification, AvgPrepTime, item_price, category, orderTrackerID, prepTimeDifference, voidAt, voidTotalTime)
                                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql_item_details, (perm_orderTime, item_completedAt, item_totalTime, item_name, item_quantity, item_modifications, item_prep_time, item_price, item_category, order_id, item_prepTime, item_voidAt, item_voidTotalTime))
            mydb.commit()

        cursor.close()
        mydb.close()

        return json_data, 200  # Return a success response

    except Exception as error:
        data = {'error': str(error)}
        return data, 400  # Return an error response


@app.route("/entry", methods=["POST"])
@cross_origin()
def entry():
    mydb = mysql.connector.connect(host=os.getenv('host'), user=os.getenv('user'), password=os.getenv('password'))
    cursor = mydb.cursor(buffered=True)
    database_sql = "USE {};".format(os.getenv('database'))
    cursor.execute(database_sql)
    json = request.get_json()
    TotalTime= ""
    completedAt= ""
    perm_Quantity=0
    now = datetime.now(tz=pytz.timezone("Asia/Kathmandu"))
    formatted_date = now.strftime('%Y-%m-%d')
    perm_outlet_orderID = json["outlet_orderID"]
    perm_orderTime = json["orderTime"]
    perm_tableNum = json["tableNum"]
    perm_employee = json["employee"]
    perm_orderType = json["orderType"]
    perm_currentState = json["currentState"]
    perm_outlet_Name = json["outlet_Name"]
    perm_guests = json["Guest_count"]
    perm_OrderItemDetailsList = json["OrderItemDetailsList"] 
    OrderItemDetailsList_details=  perm_OrderItemDetailsList[0]
    perm_kotid = json["KOTID"]
    if perm_orderType =="Take-Away":
        json["Guest_count"]=0
        json["tableNum"]="Take-Away"
        perm_guests = 0
        perm_tableNum="Take-Away"
    if  perm_kotid=="" or OrderItemDetailsList_details=="" or OrderItemDetailsList_details==[]  or  perm_OrderItemDetailsList=="" or  perm_guests=="" or perm_outlet_Name=="" or perm_currentState=="" or perm_orderType=="" or perm_employee=="" or perm_tableNum=="" or perm_orderTime=="" or not any([perm_guests,perm_outlet_orderID,perm_orderTime,perm_tableNum,perm_employee,perm_orderType,perm_currentState,perm_outlet_Name]) or perm_outlet_orderID=="":
        data = {"error":"Some fields are missing."}
        return data,400
    check = True
    orderDetails_length = len(perm_OrderItemDetailsList)
    if orderDetails_length==0:
        data ={'error':"Some fields under 'OrderItemDetailsList' missing."}
        return data,400
    for y in range(orderDetails_length):
        for x in perm_OrderItemDetailsList:
            try:
                if x["orderTime"]==""or x["ItemName"]=="" or x["Quantity"]=="" or x["item_price"]=="" or x["category"]==""  or x["item_price"] is None or x["category"] is None or x["orderTime"]is None  or x["ItemName"]is None or x["Quantity"]is None  or x["item_price"] is None :
                    check =False 
                orderDetails_length = orderDetails_length - 1
            except Exception as error:
                check =False
    if not check:
        data ={'error':"Some fields under 'OrderItemDetailsList' missing."}
        return data,400
    else:
        try:
            sql =f"""INSERT INTO tblorderTracker (outlet_orderID,Date,tableNum,orderedAt,completedAt,TotalTime,orderType,currentState,Quantity,outlet_Name,Employee,Guest_count,KOTID) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            cursor.execute(sql,(perm_outlet_orderID,formatted_date,perm_tableNum,perm_orderTime,completedAt,TotalTime,perm_orderType,perm_currentState,perm_Quantity,perm_outlet_Name,perm_employee,perm_guests,perm_kotid,),)
            mydb.commit()
            global ordertracker_id
            ordertracker_sql =f"""select idtblorderTracker from tblorderTracker order by idtblorderTracker desc limit 1"""
            cursor.execute(ordertracker_sql)
            mydb.commit()
            result = cursor.fetchall()
            row_headers=[x[0] for x in cursor.description] 
            json_data=[]
            for res in result:
                json_data.append(dict(zip(row_headers,res)))
            main_orderid = json_data[0]["idtblorderTracker"]
            json["table_id"]=main_orderid
            ordertracker_id = result[0][0]
            if ordertracker_sql == "":
                ordertracker_id=1
            OrderItemDetailsList = json["OrderItemDetailsList"]   
            OrderItemDetailsList_details=  OrderItemDetailsList
            temp_ordertime =""
            temp_ItemName =""
            temp_Quantity=0
            temp_Modifications= ""
            temp_AvgPrepTime =""
            temp_itemprice=""
            temp_orderType=""
            for i in OrderItemDetailsList_details:
                for j in i:
                    if j == "orderTime":
                        temp_ordertime= i[j]
                    if j == "ItemName":
                        temp_ItemName=i[j]
                    if j == "Quantity":
                        temp_Quantity = i[j]
                    if j == "ItemName":
                        temp_ItemName = i[j]
                    if j =="AveragePrepTime":
                        temp_AvgPrepTime =i[j]
                    if j =="Modifications":
                        temp_Modifications =i[j]
                    if j =="item_price":
                        temp_itemprice = i[j]
                    if j =="category":
                        temp_orderType=i[j]
                orderdetails_sql =f"""INSERT INTO tblorderTracker_Details (orderedAt,ItemName,completedAt,TotalTime,Quantity,Modification,orderTrackerID,AvgPrepTime,item_price,category) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                cursor.execute(orderdetails_sql,(temp_ordertime,temp_ItemName,completedAt,TotalTime,temp_Quantity,temp_Modifications,ordertracker_id,temp_AvgPrepTime,temp_itemprice,temp_orderType,),)
                mydb.commit()
                get_id_subitem=f"""select idtblorderTracker_Details from tblorderTracker_Details where orderedAt=%s and ItemName=%s and completedAt=%s and TotalTime=%s and Quantity=%s and Modification=%s and orderTrackerID=%s"""
                cursor.execute(get_id_subitem,(temp_ordertime,temp_ItemName,completedAt,TotalTime,temp_Quantity,temp_Modifications,ordertracker_id,),)
                sub_temp_sql_data= cursor.fetchall()
                row_headers=[x[0] for x in cursor.description] 
                subitem_json_data=[]
                for result in sub_temp_sql_data:
                    subitem_json_data.append(dict(zip(row_headers,result)))
                sub_id = subitem_json_data[0]["idtblorderTracker_Details"]
                i["item_id"]=sub_id
            cursor.close()
            mydb.close()
            roomid = "{}".format(perm_outlet_Name)
            encoded = jwt.encode({"outletName": roomid},'test@123', algorithm="HS256")
            # socketio.emit(encoded, json,broadcast=True)
            # socketio.emit("initial_load", json,broadcast=True)
            return json,200
        
        
        except Exception as error:
            data ={'error':str(error)}
            return data,400




from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from flask_mail import Mail, Message
import pytz
import os
from datetime import datetime, date

# Configuring Flask-Mail
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')  # or another SMTP server
app.config['MAIL_PORT'] = os.getenv('MAIL_PORT')
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS')
# app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL')
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')  # Replace with your email
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD') # Replace with your email password
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

mail = Mail(app)
from collections import defaultdict

def send_email():
    with app.app_context():
        mydb = mysql.connector.connect(host=os.getenv('host'), user=os.getenv('user'), password=os.getenv('password'))
        cursor = mydb.cursor(buffered=True)
        database_sql = "USE {};".format(os.getenv('database'))
        cursor.execute(database_sql)

        # Get the email recipients
        query = """SELECT email FROM mailrecipient WHERE status = TRUE;"""
        cursor.execute(query)
        recipients = [row[0] for row in cursor.fetchall()]

        # Get today's date
        today_date = datetime.today().strftime('%Y-%m-%d')

        # Query to get purchase requisition and item details by outlet and vendor
        query = """
            SELECT 
                b.Outlet_Name,
                b.Company_Name, 
                a.GroupName, 
                a.Name, 
                SUM(a.UnitsOrdered) AS TotalUnitsOrdered,
                a.Rate,
                (SUM(a.UnitsOrdered) * a.Rate) AS TotalAmount,
                a.Taxable,
                a.UOM,
                (
                    SELECT 
                        Rate 
                    FROM 
                        intbl_purchaserequisition_contract 
                    WHERE 
                        ItemID = a.ItemID 
                        AND PurchaseReqID != a.PurchaseReqID 
                    ORDER BY 
                        PurchaseReqID DESC 
                    LIMIT 1
                ) AS LastPurchaseRate,
                b.ReceivedDate
            FROM intbl_purchaserequisition_contract a
            JOIN intbl_purchaserequisition b 
            ON a.PurchaseReqID = b.IDIntbl_PurchaseRequisition
            WHERE b.ServerReceivedDate = %s
            GROUP BY b.Outlet_Name, b.ReceivedDate,  b.Company_Name, a.GroupName, a.Name, a.Rate
            ORDER BY b.Outlet_Name, b.ReceivedDate DESC, b.Company_Name, a.GroupName, a.Name;
        """
        cursor.execute(query, (today_date,))
        results = cursor.fetchall()

        # Organize the results by outlet and vendor
        outlets_data = {}

        for row in results:
            outlet = row[0]
            vendor = row[1]
            group_name = row[2]
            item_name = row[3]
            total_units = row[4]
            rate = row[5]
            total_amount = round(row[6], 2)
            taxable = row[7]
            uom = row[8]
            last_purchase_rate = row[9]
            received_date = row[10]

            if received_date not in outlets_data:
                # outlets_data[outlet] = {}
                outlets_data[received_date] = {"vendorwise_data": {}, "deleted_purchase": [], "deleted_storereq": [], "outlet_wise": {}}

            # Initialize the date inside the outlet if not present
            if outlet not in outlets_data[received_date]['outlet_wise']:
                outlets_data[received_date]['outlet_wise'][outlet] = {"vendorwise_data": {}}

            if vendor not in outlets_data[received_date]['outlet_wise'][outlet]["vendorwise_data"]:
                outlets_data[received_date]['outlet_wise'][outlet]["vendorwise_data"][vendor] = []

            outlets_data[received_date]['outlet_wise'][outlet]["vendorwise_data"][vendor].append((group_name, item_name, total_units, rate, total_amount, taxable, uom, last_purchase_rate))

        query_non_grouped = """
            SELECT 
                b.Outlet_Name,
                a.GroupName, 
                a.Name, 
                SUM(a.UnitsOrdered) AS TotalUnitsOrdered,
                a.Rate,
                (SUM(a.UnitsOrdered) * a.Rate) AS TotalAmount,
                a.Taxable,
                a.UOM,
                (
                    SELECT 
                        Rate 
                    FROM 
                        intbl_purchaserequisition_contract 
                    WHERE 
                        ItemID = a.ItemID 
                        AND PurchaseReqID != a.PurchaseReqID 
                    ORDER BY 
                        PurchaseReqID DESC 
                    LIMIT 1
                ) AS LastPurchaseRate,
                b.ReceivedDate
            FROM intbl_purchaserequisition_contract a
            JOIN intbl_purchaserequisition b 
            ON a.PurchaseReqID = b.IDIntbl_PurchaseRequisition
            WHERE b.ServerReceivedDate = %s
            GROUP BY b.Outlet_Name, a.GroupName, a.Name, a.Rate, b.ReceivedDate
            ORDER BY b.Outlet_Name, b.ReceivedDate, a.GroupName, a.Name;
        """

        cursor.execute(query_non_grouped, (today_date,))
        non_grouped_results = cursor.fetchall()

        # Append non-grouped data to outlets_data
        for row in non_grouped_results:
            outlet = row[0]
            group_name = row[1]
            item_name = row[2]
            total_units = row[3]
            rate = row[4]
            total_amount = round(row[5], 2)
            taxable = row[6]
            uom = row[7]
            last_purchase_rate = row[8]
            received_date = row[9]

            # If outlet is not in outlets_data, initialize it
            if received_date not in outlets_data:
                outlets_data[received_date] = {"vendorwise_data": {}, "deleted_purchase": [], "deleted_storereq": [], 'outlet_wise': {}}
            
            # Initialize the date inside the outlet if not present
            if outlet not in outlets_data[received_date]['outlet_wise']:
                outlets_data[received_date]['outlet_wise'][outlet] = {"vendorwise_data": {}}

            # For the non-vendor data, we use a generic vendor name like "All purchase Items"
            vendor = "All purchase Items"

            # If the vendor does not exist in the outlet, initialize it
            if vendor not in outlets_data[received_date]['outlet_wise'][outlet]["vendorwise_data"]:
                outlets_data[received_date]['outlet_wise'][outlet]["vendorwise_data"][vendor] = []

            # Append the non-vendor item to the respective outlet and received_date
            outlets_data[received_date]['outlet_wise'][outlet]["vendorwise_data"][vendor].append((
                group_name, 
                item_name, 
                total_units, 
                rate, 
                total_amount, 
                taxable, 
                uom, 
                last_purchase_rate
            ))

        # Query to get the total amount and tax for each outlet
        query_for_total_and_tax = """
            SELECT 
                a.Outlet_Name,
                SUM(a.TotalAmount) AS TotalAmount,
                SUM(a.TaxAmount) AS TotalTax,
                a.ReceivedDate
            FROM intbl_purchaserequisition a
            WHERE a.ServerReceivedDate = %s
            GROUP BY a.Outlet_Name, a.ReceivedDate
            ORDER BY a.Outlet_Name, a.ReceivedDate;
        """
        cursor.execute(query_for_total_and_tax, (today_date,))
        total_tax_for_specific_outlet = cursor.fetchall()


        outlet_totals = {}
        for row in total_tax_for_specific_outlet:
            outlet_name = row[0]
            total_amount = row[1]
            total_tax = row[2]
            received_date = row[3]

            # Ensure outlet_name exists in outlet_totals
            if received_date not in outlet_totals:
                outlet_totals[received_date] = {}  # Initialize dictionary for outlet

            # Ensure received_date exists for the outlet in the outlet_totals
            if outlet_name not in outlet_totals[received_date]:
                outlet_totals[received_date][outlet_name]= {
                    "total_amount": 0,  # Initialize total_amount for this received_date
                    "total_tax": 0      # Initialize total_tax for this received_date
                }

            # Add the total amount and total tax to the respective received_date
            outlet_totals[received_date][outlet_name]["total_amount"] += total_amount
            outlet_totals[received_date][outlet_name]["total_tax"] += total_tax



        # Query to get the deleted purchase items for today
        query_deleted_purchase = """
            SELECT 
                b.Outlet_Name,
                a.GroupName, 
                a.Name, 
                SUM(a.UnitsOrdered) AS TotalUnitsOrdered,
                a.Rate,
                (SUM(a.UnitsOrdered) * a.Rate) AS TotalAmount,
                a.Taxable,
                a.UOM, 
                b.deleted_date
            FROM deleted_purchaserequisition_contract a
            JOIN deleted_purchaserequisition b 
            ON a.DeletedPurchaseReqID = b.IDdeleted_PurchaseRequisition
            WHERE DATE(b.deleted_date)  = %s
            GROUP BY b.Outlet_Name, a.GroupName, a.Name
            ORDER BY b.Outlet_Name, a.GroupName, a.Name;
        """
        cursor.execute(query_deleted_purchase, (today_date,))
        deleted_items = cursor.fetchall()

        # Organize the deleted items
        for row in deleted_items:
            outlet = row[0]
            group_name = row[1]
            item_name = row[2]
            total_units = row[3]
            rate = row[4]
            total_amount = round(row[5], 2)
            taxable = row[6]
            uom = row[7]
            deleted_date = row[8]

            # Add deleted items to the respective outlet
            if deleted_date not in outlets_data:
                outlets_data[deleted_date] = {"vendorwise_data": {}, "deleted_purchase": [], "deleted_storereq": []}

            # Append to the deleted_purchase list (not grouped by vendor)
            outlets_data[deleted_date]["deleted_purchase"].append((group_name, item_name, total_units, rate, total_amount, taxable, uom))
        
        
        # Query to get the deleted storereq items for today
        query_deleted_storereq = """
            SELECT 
                b.Outlet,
                a.GroupName, 
                a.ItemName, 
                SUM(a.Amount) AS TotalUnitsOrdered,
                a.Rate,
                (SUM(a.Amount) * a.Rate) AS TotalAmount,
                a.UOM, 
                b.deleted_date
            FROM deletedstorereqdetails a
            JOIN deleted_storerequisition b 
            ON a.DeletedStoreReqID = b.iddeletedStoreRequisition
            WHERE DATE(b.deleted_date)  = %s
            GROUP BY b.Outlet, a.GroupName, a.ItemName
            ORDER BY b.Outlet, a.GroupName, a.ItemName;
        """
        cursor.execute(query_deleted_storereq, (today_date,))
        deleted_storereq = cursor.fetchall()

        # Organize the deleted items
        for row in deleted_storereq:
            outlet = row[0]
            group_name = row[1]
            item_name = row[2]
            total_units = row[3]
            rate = row[4]
            total_amount = round(row[5], 2)
            uom = row[6]
            deleted_date = row[7]

            # Add deleted items to the respective outlet
            if deleted_date not in outlets_data:
                outlets_data[deleted_date]= {"vendorwise_data": {}, "deleted_purchase": [], "deleted_storereq": []}

            # Append to the deleted_purchase list (not grouped by vendor)
            outlets_data[deleted_date]["deleted_storereq"].append((group_name, item_name, total_units, rate, total_amount,uom))




        # Prepare the email body
        email_body = ""

        # Loop through the outlets and vendors to format the email body
        print(outlets_data)
        # import datetime
        for received_date, date_data in outlets_data.items():
            if isinstance(received_date, date):  # Ensure it's a date field
                email_body += f"<h3>Received Date: {received_date}</h3><br>"
                for outlet, outlet_data in date_data.get("outlet_wise", {}).items():
                    email_body += f"<h4>Outlet: {outlet}</h4><br>"

                    if received_date in outlet_totals and outlet in outlet_totals[received_date]:
                        total_amount = outlet_totals[received_date][outlet]["total_amount"]
                        total_tax = outlet_totals[received_date][outlet]["total_tax"]
                        email_body += f"<strong>Total Amount : {total_amount}</strong><br>"
                        email_body += f"<strong>Total Tax : {total_tax}</strong><br><br>"
                    
                    vendors = outlet_data.get("vendorwise_data", {})

                    if vendors != {}:
                        for vendor, items in vendors.items():
                            if vendor != "All purchase Items":
                                email_body += f"<h3>Vendor: {vendor}</h3><br>"
                            else:
                                email_body += f"<h3>{vendor}</h3><br>"
                                    
                            email_body += """
                            <table border='1'>
                                    <tr>
                                        <th>Name</th>
                                        <th>Group Name</th>
                                        <th>Total Units Ordered</th>
                                        <th>Rate</th>
                                        <th>Total Amount</th>
                                        <th>Taxable</th>
                                        <th>UOM</th>
                                        <th>Last Purchase Rate</th>
                                </tr>"""
                            vendors_total_amount = 0
                            for item in items:
                                group_name, name, total_units, rate, total_amount, taxable, uom, last_purchase_rate = item
                                vendors_total_amount += total_amount
                                email_body += f"<tr><td>{name}</td><td>{group_name}</td><td>{total_units}</td><td>{rate}</td><td>{total_amount}</td><td>{taxable}</td><td>{uom}</td><td>{last_purchase_rate}</td></tr>"
                                
                            if vendor != "All purchase Items":
                                email_body += f"<tr><td>Total</td><td></td><td></td><td></td><td>{vendors_total_amount}</td><td></td><td></td><td></td></tr>"
                            

                            email_body += "</table><br>"
                    else:
                        email_body += f"No items purchased for {outlet}<br>"                


            # Adding deleted purchase items to the email body
            deleted_items = date_data.get("deleted_purchase", [])
            if deleted_items:
                email_body += f"<h3>Deleted Purchase Items for {outlet}</h3><br>"
                email_body += """
                <table border='1'>
                    <tr>
                        <th>Name</th>
                        <th>Group Name</th>
                        <th>Total Units Ordered</th>
                        <th>Rate</th>
                        <th>Total Amount</th>
                        <th>Taxable</th>
                        <th>UOM</th>
                    </tr>"""
                deleted_total_amount = 0
                for item in deleted_items:
                    group_name, name, total_units, rate, total_amount, taxable, uom = item
                    deleted_total_amount += total_amount
                    email_body += f"<tr><td>{name}</td><td>{group_name}</td><td>{total_units}</td><td>{rate}</td><td>{total_amount}</td><td>{taxable}</td><td>{uom}</td></tr>"
                email_body += f"<tr><td>Total</td><td></td><td></td><td></td><td>{deleted_total_amount}</td><td></td><td></td><td></td></tr>"
                email_body += "</table><br>"
            else:
                email_body += f"No Purchase items deleted for {outlet}<br>"

            # Adding deleted storereq items to the email body
            deleted_storereq = date_data.get("deleted_storereq", [])
            if deleted_storereq:
                email_body += f"<h3>Deleted Store Items for {outlet}</h3><br>"
                email_body += """
                <table border='1'>
                    <tr>
                        <th>Name</th>
                        <th>Group Name</th>
                        <th>Total Units Ordered</th>
                        <th>Rate</th>
                        <th>Total Amount</th>
                        <th>UOM</th>
                    </tr>"""
                deleted_total_amount = 0
                for item in deleted_storereq:
                    group_name, name, total_units, rate, total_amount, uom = item
                    deleted_total_amount += total_amount
                    email_body += f"<tr><td>{name}</td><td>{group_name}</td><td>{total_units}</td><td>{rate}</td><td>{total_amount}</td><td>{uom}</td></tr>"
                email_body += f"<tr><td>Total</td><td></td><td></td><td></td><td>{deleted_total_amount}</td><td></td><td></td><td></td></tr>"
                email_body += "</table><br>"
            else:
                email_body += f"No Store items deleted for {outlet}<br>"

        # Send the email
        msg = Message(f"Purchasing Report For CoreFood: {today_date}", recipients=recipients)
        # if email_body != "":
        msg.html = email_body
        # else:
        #     msg.html = "No purchases found for today"
        try:
            mail.send(msg)
            print("Email sent successfully!")
        except Exception as e:
            print(f"Error sending email: {e}")        



# import random
# from flask import request

# @app.route("/test-email", methods=["GET", "POST"])
# def test_email():
#     print("I am in bulk sending email function")
    
#     # Check if the random_custom flag is passed
#     random_custom = request.args.get("random_custom", default=False, type=bool)
#     sample_size = 500  # number of random customers to email

#     mydb = mysql.connector.connect(
#         host=os.getenv('host'),
#         user=os.getenv('user'),
#         password=os.getenv('password'),
#         database=os.getenv('database')
#     )
    
#     cursor = mydb.cursor(dictionary=True)
#     cursor.execute("SELECT name, email FROM customers")
#     customers = cursor.fetchall()
    
#     # If random_custom is True, pick random sample
#     if random_custom and len(customers) > sample_size:
#         customers = random.sample(customers, sample_size)
    
#     emails = [
#         {
#             "email": c['email'],
#             "subject": f"Hello {c['name']}, Test Email from Celery",
#             "html": f"<h1>Hello {c['name']}!</h1><p>This is a test email.</p>"
#         } for c in customers
#     ]
    
#     send_bulk_emails.delay(emails)
    
#     cursor.close()
#     mydb.close()
    
#     return f"Email task sent to {len(emails)} customers!"

# import random
# from flask import request
# from tasks import send_bulk_emails
# import os

# @app.route("/test-email", methods=["POST"])
# def test_email():
#     print("I am in bulk sending email function")
    
#     data = request.get_json()
#     if not data:
#         return {"error": "JSON body required"}, 400

#     random_custom = data.get("random_custom", False)
#     sample_size = data.get("sample_size", 500)
#     subject_template = data.get("subject", "Hello {{name}}, Test Email from Alice Restaurant")
#     html_template = data.get("html", "<h1>Hello {{name}}!</h1><p>This is a test email.</p>")
#     sender_name = data.get("from_name", "Alice Restaurant")  # custom "from" name

#     mydb = mysql.connector.connect(
#         host=os.getenv('host'),
#         user=os.getenv('user'),
#         password=os.getenv('password'),
#         database=os.getenv('database')
#     )
    
#     cursor = mydb.cursor(dictionary=True)
#     cursor.execute("SELECT name, email FROM customers")
#     customers = cursor.fetchall()
    
#     if random_custom and len(customers) > sample_size:
#         customers = random.sample(customers, sample_size)
    
#     emails = [
#         {
#             "email": c['email'],
#             "subject": subject_template.replace("{{name}}", c['name']),
#             "html": html_template.replace("{{name}}", c['name']),
#             "from_name": sender_name  # pass custom "from" name
#         }
#         for c in customers
#     ]
    
#     send_bulk_emails.delay(emails)
    
#     cursor.close()
#     mydb.close()
    
#     return {"message": f"Email task sent to {len(emails)} customers!"}



# from flask import request
# import os
# import random
# from tasks import send_bulk_emails
# import mysql.connector
# from werkzeug.utils import secure_filename

# UPLOAD_FOLDER = "/tmp/email_attachments"
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# @app.route("/test-email", methods=["POST"])
# def test_email():
#     print("I am in bulk sending email function")
    
#     # Get form fields
#     subject_template = request.form.get("subject", "Hello {{name}}, Test Email from Alice Restaurant")
#     html_template = request.form.get("html", "<h1>Hello {{name}}!</h1><p>This is a test email.</p>")
#     sender_name = request.form.get("from_name", "Alice Restaurant")
#     random_custom = request.form.get("random_custom", "false").lower() == "true"
#     sample_size = int(request.form.get("sample_size", 500))
    
#     # Handle uploaded files
#     attachments = []
#     for f in request.files.getlist("files"):
#         filename = secure_filename(f.filename)
#         filepath = os.path.join(UPLOAD_FOLDER, filename)
#         f.save(filepath)
#         attachments.append(filepath)
    
#     # Fetch customers
#     mydb = mysql.connector.connect(
#         host=os.getenv('host'),
#         user=os.getenv('user'),
#         password=os.getenv('password'),
#         database=os.getenv('database')
#     )
#     cursor = mydb.cursor(dictionary=True)
#     cursor.execute("SELECT name, email FROM customers")
#     customers = cursor.fetchall()
    
#     if random_custom and len(customers) > sample_size:
#         customers = random.sample(customers, sample_size)
    
#     emails = [
#         {
#             "email": c['email'],
#             "subject": subject_template.replace("{{name}}", c['name']),
#             "html": html_template.replace("{{name}}", c['name']),
#             "from_name": sender_name,
#             "attachments": attachments  # Pass attachments to Celery
#         }
#         for c in customers
#     ]
    
#     send_bulk_emails.delay(emails)
    
#     cursor.close()
#     mydb.close()
    
#     return {"message": f"Email task sent to {len(emails)} customers!"}


# from flask import request
# import os, mysql.connector, random
# from tasks import send_bulk_emails

# @app.route("/send-email", methods=["POST"])
# def send_email():
#     sender_name = request.form.get("from_name", "Alice Restaurant")
#     subject_template = request.form.get("subject", "Hello {{name}}")
#     html_template = request.form.get("html", "<p>Hello {{name}}</p>")
#     sample_size = int(request.form.get("sample_size", 0))
    
#     # attachments (list of FileStorage objects)
#     attachments = request.files.getlist("attachments")

#     # Save attachments temporarily
#     saved_files = []
#     for file in attachments:
#         save_path = f"/tmp/{file.filename}"
#         file.save(save_path)
#         saved_files.append(save_path)

#     # Get customers
#     db = mysql.connector.connect(
#         host=os.getenv('host'),
#         user=os.getenv('user'),
#         password=os.getenv('password'),
#         database=os.getenv('database')
#     )
#     cursor = db.cursor(dictionary=True)
#     cursor.execute("SELECT name, email FROM customers")
#     customers = cursor.fetchall()

#     if sample_size > 0 and len(customers) > sample_size:
#         customers = random.sample(customers, sample_size)

#     # Prepare email batch
#     emails = [
#         {
#             "email": c["email"],
#             "subject": subject_template.replace("{{name}}", c["name"]),
#             "html": html_template.replace("{{name}}", c["name"]),
#             "from_name": sender_name,
#             "attachments": saved_files
#         }
#         for c in customers
#     ]

#     send_bulk_emails.delay(emails)

#     cursor.close()
#     db.close()

#     return {"message": f"Queued {len(emails)} emails!"}, 200



# from flask import request
# import os, mysql.connector, random
# from tasks import send_bulk_emails  # Celery task

# @app.route("/send-email", methods=["POST"])
# def send_email():
#     sender_name = request.form.get("from_name", "Alice Restaurant")
#     subject_template = request.form.get("subject", "Hello {{name}}")
#     html_template = request.form.get("html", "<p>Hello {{name}}</p>")
#     sample_size = int(request.form.get("sample_size", 0))
    
#     # attachments (list of FileStorage objects)
#     attachments = request.files.getlist("attachments")

#     # Save attachments temporarily
#     saved_files = []
#     for file in attachments:
#         save_path = f"/tmp/{file.filename}"
#         file.save(save_path)
#         saved_files.append({
#             "filename": file.filename,
#             "data": open(save_path, "rb").read(),  # read bytes
#             "content_type": file.content_type
#         })

#     # Get customers
#     db = mysql.connector.connect(
#         host=os.getenv('host'),
#         user=os.getenv('user'),
#         password=os.getenv('password'),
#         database=os.getenv('database')
#     )
#     cursor = db.cursor(dictionary=True)
#     cursor.execute("SELECT name, email FROM customers")
#     customers = cursor.fetchall()

#     if sample_size > 0 and len(customers) > sample_size:
#         customers = random.sample(customers, sample_size)

#     # Prepare email batch
#     emails = [
#         {
#             "email": c["email"],
#             "subject": subject_template.replace("{{name}}", c["name"]),
#             "html": html_template.replace("{{name}}", c["name"]),
#             "from_name": sender_name,
#             "attachments": saved_files
#         }
#         for c in customers
#     ]

#     # Async send via Celery
#     send_bulk_emails.delay(emails, subject_template, html_template, sender_name, sender_name, sample_size)

#     cursor.close()
#     db.close()

#     return {"message": f"Queued {len(emails)} emails!"}, 200


from flask import request
import os, mysql.connector, random, json
from tasks import send_bulk_emails

@app.route("/send-email", methods=["POST"])
def send_email():
    sender_name = request.form.get("from_name", "Alice Restaurant")
    subject_template = request.form.get("subject", "Hello {{name}}")
    html_template = request.form.get("html", "<p>Hello {{name}}</p>")
    sample_size = int(request.form.get("sample_size", 0))

    # Attachments
    attachments = request.files.getlist("attachments")
    saved_files = []

    for file in attachments:
        if not file or file.filename == "":
            continue  # skip empty uploads

        path = os.path.join("/tmp", file.filename)
        file.save(path)

        saved_files.append({
            "filename": file.filename,
            "data": open(path, "rb").read(),
            "content_type": file.content_type
        })

    # for file in attachments:
    #     path = f"/tmp/{file.filename}"
    #     file.save(path)
    #     saved_files.append({
    #         "filename": file.filename,
    #         "data": open(path, "rb").read(),
    #         "content_type": file.content_type
    #     })




    # Get customers from DB
    db = mysql.connector.connect(
        host=os.getenv('host'),
        user=os.getenv('user'),
        password=os.getenv('password'),
        database=os.getenv('database')
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT name, email FROM customers")
    # cursor.execute("SELECT GuestName, guestEmail FROM customers")
    customers = cursor.fetchall()
    cursor.close()
    db.close()

    # # ----- NEW: Parse additional emails -----
    # additional_emails = []
    # additional_raw = request.form.get("additional_emails")

    # if additional_raw:
    #     try:
    #         # Should be JSON list of objects:
    #         # [{"name": "...", "email": "..."}, ...]
    #         additional_emails = json.loads(additional_raw)
    #     except Exception:
    #         return {"error": "Invalid JSON in additional_emails"}, 400

    # # Merge DB + additional list
    # customers.extend(additional_emails)

    # # Apply sampling after merging
    # if sample_size > 0 and len(customers) > sample_size:
    #     customers = random.sample(customers, sample_size)

    # ----- NEW: Parse additional emails -----
    additional_emails = []
    additional_raw = request.form.get("additional_emails")

    if additional_raw:
        try:
            additional_emails = json.loads(additional_raw)
        except Exception:
            return {"error": "Invalid JSON in additional_emails"}, 400

    # ---- APPLY CORRECT LOGIC ----
    # 1. Random sample DB customers first
    if sample_size > 0:
        customers = random.sample(customers, min(sample_size, len(customers)))
    else:
        customers = []  # no DB customers if sample_size = 0

    # 2. Append additional emails
    customers.extend(additional_emails)

    # Prepare emails
    emails = [
        {
            "email": c["email"],
            "subject": subject_template.replace("{{name}}", c["name"]),
            "html": html_template.replace("{{name}}", c["name"]),
            "from_name": sender_name,
            "attachments": saved_files
        }
        for c in customers
    ]

    # Send with Celery
    send_bulk_emails.delay(
        emails,
        subject_template,
        html_template,
        sender_name,
        sender_name,
        sample_size
    )

    return {"message": f"Queued {len(emails)} emails!"}, 200




# # Initialize the scheduler
# scheduler = BackgroundScheduler(daemon=True)

# # Define Nepal Timezone
# nepal_tz = pytz.timezone("Asia/Kathmandu")

# # Schedule the task to run at 8:30 PM Nepal Time every day
# scheduler.add_job(
#     send_email,
#     CronTrigger(hour=20, minute=30, timezone=nepal_tz),  # 8:30 PM Nepal Time (UTC+5:45)
#     id='send_email_at_830pm',
#     name='Send daily email at 8:30 PM Nepal Time',
#     replace_existing=True
# )

# from root.flask_routes.send_email_report import monthly_report

# def send_monthly_report_email():

#     with app.app_context():
#         report, recipients = monthly_report()

#         # Send the email
#         msg = Message(f"Last Three Months Report", recipients=recipients)
#         # if email_body != "":
#         msg.html = report

#         try:
#             mail.send(msg)
#             print("Email sent successfully!")
#         except Exception as e:
#             print(f"Error sending email: {e}")

# scheduler.add_job(
#     send_monthly_report_email,
#     CronTrigger(day=1, hour=4, minute=2, timezone=nepal_tz),  # Executes on the 19th of the month at 11:50 AM Nepal Time
#     id='send_monthly_report_1st',
#     name='Send monthly report on the 1st of each month at 4:00 AM Nepal Time',
#     replace_existing=True
# )

# scheduler.start()


# from datetime import datetime 
# from datetime import datetime
# from zoneinfo import ZoneInfo

# def send_review_email(review_data):
#     with app.app_context():
#         mydb = mysql.connector.connect(
#             host=os.getenv('host'),
#             user=os.getenv('user'),
#             password=os.getenv('password')
#         )
#         cursor = mydb.cursor(buffered=True)
#         cursor.execute(f"USE {os.getenv('database')}")
#         cursor.execute("SELECT email FROM mailrecipient WHERE status = 1")
#         recipients = [row[0] for row in cursor.fetchall() if row[0]]

#         if recipients:
#             review_type = review_data.get('type', 'restaurant')

#             if review_type == 'banquet':
#                 email_html = f"""
#                     <h2 style="font-family: Arial, sans-serif; color: #333;">New Customer Review Submitted (Banquet)</h2>
#                     <h4 style="font-family: Arial, sans-serif; color: #333;">Outlet: {review_data.get('outlet_name')}</h4>
#                     <h4 style="font-family: Arial, sans-serif; color: #333;">Date: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</h4>
#                     <br/>

#                     <table style="border-collapse: collapse; width: 100%; font-family: Arial, sans-serif;">
#                         <thead>
#                             <tr>
#                                 <th style="text-align: left; padding: 8px; background-color: #f2f2f2;">Field</th>
#                                 <th style="text-align: left; padding: 8px; background-color: #f2f2f2;">Value</th>
#                             </tr>
#                         </thead>
#                         <tbody>
#                             <tr><td style="padding: 8px;">Name</td><td style="padding: 8px;">{review_data['customer_name']}</td></tr>
#                             <tr><td style="padding: 8px;">Email</td><td style="padding: 8px;">{review_data.get('customer_email')}</td></tr>
#                             <tr><td style="padding: 8px;">Phone Number</td><td style="padding: 8px;">{review_data.get('phonenumber')}</td></tr>
#                             <tr><td style="padding: 8px;">Service</td><td style="padding: 8px;">{review_data['service']}</td></tr>
#                             <tr><td style="padding: 8px;">Staff Friendliness</td><td style="padding: 8px;">{review_data['staff_friendliness']}</td></tr>
#                             <tr><td style="padding: 8px;">Food Quality</td><td style="padding: 8px;">{review_data['food_quality']}</td></tr>
#                             <tr><td style="padding: 8px;">Atmosphere</td><td style="padding: 8px;">{review_data['atmosphere']}</td></tr>
#                             <tr><td style="padding: 8px;">Cleanliness</td><td style="padding: 8px;">{review_data['cleanliness']}</td></tr>
#                             <tr><td style="padding: 8px;">Experience</td><td style="padding: 8px;">{review_data.get('experience')}</td></tr>
#                             <tr><td style="padding: 8px;">Comments</td><td style="padding: 8px;">{review_data.get('comments')}</td></tr>
#                             <tr><td style="padding: 8px;">Consent to Post</td><td style="padding: 8px;">{"Yes" if review_data.get('post_review_consent') else "No"}</td></tr>
#                         </tbody>
#                     </table>
#                 """
#             else:
#                 # Restaurant layout
#                 email_html = f"""
#                     <h2 style="font-family: Arial, sans-serif; color: #333;">New Customer Review Submitted (Restaurant)</h2>
#                     <h4 style="font-family: Arial, sans-serif; color: #333;">Outlet: {review_data.get('outlet_name')}</h4>
#                     <h4 style="font-family: Arial, sans-serif; color: #333;">Date: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</h4>
#                     <br/>

#                     <table style="border-collapse: collapse; width: 100%; font-family: Arial, sans-serif; font-size: 14px;">
#                         <thead>
#                             <tr>
#                                 <th style="padding: 8px; background-color: #f2f2f2; text-align: left;">Field</th>
#                                 <th style="padding: 8px; background-color: #f2f2f2; text-align: left;">Value</th>
#                             </tr>
#                         </thead>
#                         <tbody>
#                             <tr><td style="padding: 8px;">Name</td><td style="padding: 8px;">{review_data['customer_name']}</td></tr>
#                             <tr><td style="padding: 8px;">Email</td><td style="padding: 8px;">{review_data.get('customer_email')}</td></tr>
#                             <tr><td style="padding: 8px;">Phone Number</td><td style="padding: 8px;">{review_data.get('phonenumber')}</td></tr>
#                             <tr><td style="padding: 8px;">Outlet</td><td style="padding: 8px;">{review_data.get('outlet_name')}</td></tr>
#                             <tr><td style="padding: 8px;">Experience Today</td><td style="padding: 8px;">{review_data.get('experience_today')}</td></tr>
#                             <tr><td style="padding: 8px;">Most Enjoyed</td><td style="padding: 8px;">{review_data.get('most_enjoyed')}</td></tr>
#                             <tr><td style="padding: 8px;">Improvement Suggestions</td><td style="padding: 8px;">{review_data.get('improvement_suggestions')}</td></tr>
#                             <tr><td style="padding: 8px;">Would Recommend</td><td style="padding: 8px;">{review_data.get('would_recommend')}</td></tr>
#                             <tr><td style="padding: 8px;">Visit Type</td><td style="padding: 8px;">{review_data.get('visit_type')}</td></tr>
#                             <tr><td style="padding: 8px;">Experience</td><td style="padding: 8px;">{review_data.get('experience')}</td></tr>
#                             <tr><td style="padding: 8px;">Comments</td><td style="padding: 8px;">{review_data.get('comments')}</td></tr>
#                             <tr><td style="padding: 8px;">Consent to Post</td><td style="padding: 8px;">{"Yes" if review_data.get('post_review_consent') else "No"}</td></tr>
#                         </tbody>
#                     </table>
#                 """

#             msg = Message("New Customer Review", recipients=recipients)
#             msg.html = email_html
#             try:
#                 mail.send(msg)
#                 print("Email sent successfully!")
#             except Exception as e:
#                 print(f"Error sending email: {e}")

#         cursor.close()
#         mydb.close()

from flask import send_from_directory

basedir = os.path.abspath(os.path.dirname(__file__))  # this is the 'root' folder
UPLOAD_FOLDER = os.path.join(basedir, 'uploads')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/")
def index():
    return "working"






