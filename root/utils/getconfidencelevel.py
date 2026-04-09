from flask import  Blueprint,request
import mysql.connector
import os

def getconfidencelevel(outlet):
    try:
        mydb = mysql.connector.connect(host=os.getenv('host'), user=os.getenv('user'), password=os.getenv('password'))
        cursor = mydb.cursor(buffered=True)
        database_sql = "USE {};".format(os.getenv('database'))
        cursor.execute(database_sql)
        get_outlet_sql =f"""select confidencelevel from outetNames where Outlet=%s"""
        cursor.execute(get_outlet_sql, (outlet,))
        result = cursor.fetchall()
        if result == []:
            return 0.0
        # Extract the confidence level from the result
        confidence_level = result[0][0]
        mydb.close()
        return round(float(confidence_level/100), 2)
    except Exception as error:
        print("error fetching confidence level")

