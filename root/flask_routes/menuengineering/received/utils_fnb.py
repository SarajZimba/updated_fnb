from flask import Blueprint, jsonify, request
import mysql.connector
import os
from dotenv import load_dotenv
from flask_cors import cross_origin
from root.auth.check import token_auth
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime

def get_db_connection_fnb():
    return mysql.connector.connect(
        host=os.getenv("host"),
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )

def get_sales_data_for_snapshot(cursor, outlet_name, from_date, to_date):
    """Get food and beverage sales data for snapshot"""

    def to_float(value):
        if value is None:
            return 0.0
        return float(value)
    
    query = """
        SELECT 
            COALESCE(SUM(CASE WHEN oh.PaymentMode IN ('Complimentary', 'Non Chargeable') THEN oh.Total END), 0) AS complimentary_sales,
            COALESCE(SUM(CASE WHEN oh.Type = 'Banquet' THEN oh.Total END), 0) AS banquet_sales,
            COALESCE(SUM(oh.DiscountAmt), 0) AS discounts_sales
        FROM tblorderhistory oh
        WHERE oh.Outlet_Name = %s 
            AND oh.Date BETWEEN %s AND %s 
            AND oh.bill_no != ''
    """
    
    cursor.execute(query, (outlet_name, from_date, to_date))
    result = cursor.fetchone()
    
    # Get food sales
    food_query = """
        SELECT COALESCE(SUM(od.Total), 0) AS food_sales
        FROM tblorder_detailshistory od
        WHERE od.ItemType = 'Food'
        AND od.order_ID IN (
            SELECT idtblorderHistory 
            FROM tblorderhistory 
            WHERE Outlet_Name = %s AND Date BETWEEN %s AND %s AND bill_no != ''
        )
    """
    
    cursor.execute(food_query, (outlet_name, from_date, to_date))
    food_result = cursor.fetchone()
    
    # Get beverage sales
    beverage_query = """
        SELECT COALESCE(SUM(od.Total), 0) AS beverage_sales
        FROM tblorder_detailshistory od
        WHERE od.ItemType = 'Beverage'
        AND od.order_ID IN (
            SELECT idtblorderHistory 
            FROM tblorderhistory 
            WHERE Outlet_Name = %s AND Date BETWEEN %s AND %s AND bill_no != ''
        )
    """

    
    cursor.execute(beverage_query, (outlet_name, from_date, to_date))
    beverage_result = cursor.fetchone()



    gross_query = """
        SELECT 
            COALESCE(SUM(od.Total), 0) AS gross_sales,
            COALESCE(SUM(
                CASE 
                    WHEN r.costprice IS NOT NULL THEN r.costprice * od.count
                    ELSE 0
                END
            ), 0) AS gross_cost
        FROM tblorder_detailshistory od
        JOIN tblorderhistory oh 
            ON od.order_ID = oh.idtblorderHistory
        LEFT JOIN recipe r 
            ON r.name = od.ItemName 
            AND r.outlet = oh.Outlet_Name
        WHERE oh.Outlet_Name = %s
            AND oh.Date BETWEEN %s AND %s
            AND oh.bill_no != ''
            AND od.ItemType IN ('Food', 'Beverage')
    """
    
    cursor.execute(gross_query, (outlet_name, from_date, to_date))
    gross_result = cursor.fetchone()

    gross_sales = to_float(gross_result['gross_sales'])
    gross_cost = to_float(gross_result['gross_cost'])

    gross_cost_percent = (gross_cost / gross_sales * 100) if gross_sales > 0 else 0
    
    return {
        'complimentary_sales': to_float(result['complimentary_sales']),
        'banquet_sales': to_float(result['banquet_sales']),
        'discounts_sales': to_float(result['discounts_sales']),
        'food_sales': to_float(food_result['food_sales']),
        'beverage_sales': to_float(beverage_result['beverage_sales']),
        'gross_cost': gross_cost,
        'gross_cost_percent': gross_cost_percent,
        'gross_sales': gross_sales
    }


def calculate_complimentary_cost_for_snapshot(cursor, outlet_name, from_date, to_date):
    """Calculate complimentary cost by matching items with recipe costs"""
    
    query = """
        SELECT oh.idtblorderHistory, oh.Total as bill_total
        FROM tblorderhistory oh
        WHERE oh.Outlet_Name = %s 
            AND oh.Date BETWEEN %s AND %s 
            AND oh.bill_no = ''
            AND oh.PaymentMode IN ('Complimentary', 'Non Chargeable')
    """
    
    cursor.execute(query, (outlet_name, from_date, to_date))
    complimentary_orders = cursor.fetchall()
    
    if not complimentary_orders:
        return 0.0
    
    total_complimentary_cost = 0.0
    
    for order in complimentary_orders:
        order_id = order['idtblorderHistory']
        
        items_query = """
            SELECT od.ItemName, od.Total as sale_total, od.count
            FROM tblorder_detailshistory od
            WHERE od.order_ID = %s
        """
        
        cursor.execute(items_query, (order_id,))
        items = cursor.fetchall()
        
        for item in items:
            item_name = item['ItemName']
            
            recipe_query = """
                SELECT costprice, sellingprice
                FROM recipe
                WHERE name = %s AND outlet = %s
                LIMIT 1
            """
            
            cursor.execute(recipe_query, (item_name, outlet_name))
            recipe = cursor.fetchone()
            
            def to_float(val):
                if val is None:
                    return 0.0
                return float(val)
            
            if recipe:
                quantity = to_float(item.get('count', 1))
                item_cost = to_float(recipe['costprice']) * quantity
                total_complimentary_cost += item_cost
            else:
                sale_total = to_float(item['sale_total'])
                total_complimentary_cost += sale_total * 0.6
    
    return total_complimentary_cost


# def calculate_employee_meal_cost(outlet_name, from_date, to_date, itemtype):
#     """Calculate employee meal cost from Staff Consumption cost center"""
#     try:
#         mydb = get_db_connection_fnb()
#         cursor = mydb.cursor(dictionary=True)
        
#         query_storerequisition = """
#             SELECT idintblStoreRequisition, Date, CostCenter
#             FROM intblstorerequisition
#             WHERE Date BETWEEN %s AND %s 
#             AND Outlet = %s 
#             AND CostCenter = 'Staff Consumption'
#         """
#         cursor.execute(query_storerequisition, (from_date, to_date, outlet_name))
#         store_requisitions = cursor.fetchall()
        
#         if not store_requisitions:
#             return 0.0
        
#         total_employee_meal_cost = 0.0
        
#         for store_req in store_requisitions:
#             store_req_id = store_req['idintblStoreRequisition']
            
#             query_storereqdetails = """
#                 SELECT ItemName, GroupName, BrandName, Amount, UOM, Rate
#                 FROM intblstorereqdetails
#                 WHERE StoreReqID = %s
#             """
#             cursor.execute(query_storereqdetails, (store_req_id,))
#             items = cursor.fetchall()
            
#             for item in items:
#                 amount = float(item['Amount'] or 0)
#                 rate = float(item['Rate'] or 0)
#                 total = amount * rate
#                 total_employee_meal_cost += total
        
#         cursor.close()
#         mydb.close()
        
#         return round(total_employee_meal_cost, 2)
        
#     except Exception as e:
#         print(f"Error calculating employee meal cost: {str(e)}")
#         return 0.0


def calculate_employee_meal_cost(outlet_name, from_date, to_date, itemtype):
    """Calculate employee meal cost (Food/Beverage wise) from Staff Consumption"""
    try:
        mydb = get_db_connection_fnb()
        cursor = mydb.cursor(dictionary=True)

        query = """
            SELECT SUM(d.Amount * d.Rate) AS total_cost
            FROM intblstorerequisition r
            JOIN intblstorereqdetails d 
                ON r.idintblStoreRequisition = d.StoreReqID
            JOIN stock_statement s 
                ON s.ItemName = d.ItemName 
                AND s.OutletName = r.Outlet
            WHERE r.Date BETWEEN %s AND %s
              AND r.Outlet = %s
              AND r.CostCenter IN ('Staff Consumption', 'Staff Meal')
              AND s.Type = %s
        """

        cursor.execute(query, (from_date, to_date, outlet_name, itemtype))
        result = cursor.fetchone()

        total_cost = float(result["total_cost"] or 0)

        cursor.close()
        mydb.close()

        return round(total_cost, 2)

    except Exception as e:
        print(f"Error calculating employee meal cost: {str(e)}")
        return 0.0
    

# def calculate_other_cost(outlet_name, from_date, to_date):
#     """Calculate cost excluding Kitchen and Bar (Other Cost)"""
#     try:
#         mydb = get_db_connection_fnb()
#         cursor = mydb.cursor(dictionary=True)

#         query = """
#             SELECT SUM(d.Amount * d.Rate) AS total_cost
#             FROM intblstorerequisition r
#             JOIN intblstorereqdetails d 
#                 ON r.idintblStoreRequisition = d.StoreReqID
#             WHERE r.Date BETWEEN %s AND %s
#               AND r.Outlet = %s
#               AND r.CostCenter NOT IN ('Kitchen', 'Bar', 'Staff Consumption')
#         """

#         cursor.execute(query, (from_date, to_date, outlet_name))
#         result = cursor.fetchone()

#         total_cost = float(result["total_cost"] or 0)

#         cursor.close()
#         mydb.close()

#         return round(total_cost, 2)

#     except Exception as e:
#         print(f"Error calculating other cost: {str(e)}")
#         return 0.0


def calculate_other_cost(outlet_name, from_date, to_date, itemtype):
    """Calculate Other Cost (Food/Beverage wise) excluding Kitchen, Bar, Staff Consumption"""
    try:
        mydb = get_db_connection_fnb()
        cursor = mydb.cursor(dictionary=True)

        query = """
            SELECT SUM(d.Amount * d.Rate) AS total_cost
            FROM intblstorerequisition r
            JOIN intblstorereqdetails d 
                ON r.idintblStoreRequisition = d.StoreReqID
            JOIN (
                SELECT ItemName, OutletName, MAX(Type) AS Type
                FROM stock_statement
                GROUP BY ItemName, OutletName
            ) s 
                ON s.ItemName = d.ItemName 
                AND s.OutletName = r.Outlet
            WHERE r.Date BETWEEN %s AND %s
              AND r.Outlet = %s
              AND r.CostCenter NOT IN ('Kitchen', 'Bar', 'Staff Consumption')
              AND LOWER(s.Type) = LOWER(%s)
        """

        cursor.execute(query, (from_date, to_date, outlet_name, itemtype))
        result = cursor.fetchone()

        total_cost = float(result["total_cost"] or 0)

        cursor.close()
        mydb.close()

        return round(total_cost, 2)

    except Exception as e:
        print(f"Error calculating other cost: {str(e)}")
        return 0.0