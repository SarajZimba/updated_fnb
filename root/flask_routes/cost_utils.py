
import mysql.connector

import os
from datetime import datetime
import pytz

def calculate_food_and_beverage_purchase(startDate, endDate, outletName, cursor):
    try:
        # mydb = mysql.connector.connect(
        #     host=os.getenv('host'),
        #     user=os.getenv('user'),
        #     password=os.getenv('password')
        # )
        # cursor = mydb.cursor(buffered=True)
        # database_sql = "USE {};".format(os.getenv('database'))
        # cursor.execute(database_sql)
        query = """SELECT a.Department, sum(a.UnitsOrdered*a.Rate) as Total FROM intbl_purchaserequisition_contract a, intbl_purchaserequisition b where a.PurchaseReqID= b.IDIntbl_PurchaseRequisition and b.Date between %s and %s and b.Outlet_Name=%s GROUP BY a.Department;"""

        cursor.execute(query, (startDate, endDate, outletName,))

        result = cursor.fetchall()        

        # Get column names from cursor description
        column_names = [desc[0] for desc in cursor.description]

        # Convert result to a list of dictionaries
        formatted_result = [dict(zip(column_names, row)) for row in result]

        food_total = 0.0
        beverage_total = 0.0
        for result in formatted_result:
            if result["Department"] == "Beverage" or result["Department"] == "Dairy Product":
                beverage_total += float(result["Total"])
            if result["Department"] == "Food":
                food_total += float(result["Total"])

        
            



        print(formatted_result)
        print(f"food_total {food_total}")
        print(f"beverage total {beverage_total}")

        return food_total, beverage_total

    except mysql.connector.Error as db_error:
        raise db_error
    except Exception as e:
        raise e


import mysql.connector

import os
from datetime import datetime
import pytz

def calculate_food_and_beverage_stockstatement(cursor, outlet):
    try:
        # mydb = mysql.connector.connect(
        #     host=os.getenv('host'),
        #     user=os.getenv('user'),
        #     password=os.getenv('password')
        # )
        # cursor = mydb.cursor(buffered=True)
        # database_sql = "USE {};".format(os.getenv('database'))
        # cursor.execute(database_sql)

        query = """SELECT `Type`, sum(`Total`) as Total FROM `stock_statement` WHERE OutletName=%s GROUP BY `Type`"""

        cursor.execute(query, (outlet,))

        results = cursor.fetchall()

        column_names = [column_name[0] for column_name in cursor.description]

        formatted_result = [dict(zip(column_names, result)) for result in results]

        beverage_total = 0.0
        food_total = 0.0
        print(formatted_result)
        for result in formatted_result:
            if result["Type"] == "Beverage" :
                beverage_total += float(result["Total"])
            if result["Type"] == "Food":
                food_total += float(result["Total"])
        print(f"food_total {food_total}")
        print(f"beverage total {beverage_total}")

        return food_total, beverage_total

    except mysql.connector.Error as db_error:
        raise db_error
    except Exception as e:
        raise e

def insert_into_tblcosttracker(date, purchasetotal, openingtotal, closingtotal, outlet, type):

    try:
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password')
            )
        cursor = mydb.cursor(buffered=True)
        database_sql = "USE {};".format(os.getenv('database'))
        cursor.execute(database_sql)
        # food_cost = purchasefoodtotal + openingfoodtotal - closingfoodtotal
        # beverage_cost = purchasebeveragetotal + openingbeveragetotal - closingbeveragetotal
        # food_type = 'Food'
        # beverage_type = 'Beverage'
        # Calculate the costs
        # costs = [
        #     (food_type, openingfoodtotal, purchasefoodtotal, closingfoodtotal, outlet),
        #     (beverage_type, openingbeveragetotal, purchasebeveragetotal, closingbeveragetotal, outlet)
        # ]




        query = """INSERT INTO `tblcosttracker` (`date`, `opening`, `purchase`, `expense`, `closing`, `type`, `outlet`) VALUES (%s, %s, %s, %s, %s, %s, %s )"""



        expense = purchasetotal + openingtotal - closingtotal
        cursor.execute(query, (date, openingtotal, purchasetotal, expense, closingtotal, type, outlet))
        # Commit the transaction
        mydb.commit()
        print("Food and Beverage data inserted successfully!")
    except mysql.connector.Error as db_error:
        mydb.rollback()  # Rollback on error
        raise db_error
    except Exception as e:
        mydb.rollback()  # Rollback on unexpected error
        raise e
    finally:
        if mydb:
            mydb.close()

# insert_into_tblcosttracker('2025-02-18', 100, 100, 100, 100, 50, 50)



def calculate_food_and_beverage_from_newposted_stockstatement(posted_data):
    data = posted_data
    
    closing_foodtotal = 0.0
    closing_beveragetotal = 0.0
    for item in data["ItemDetailsList"]:
        if item["Department"] == "Food":
            closing_foodtotal += item["Total"]
        if item["Department"] == "Beverage":
            closing_beveragetotal += item["Total"]

    return closing_foodtotal, closing_beveragetotal