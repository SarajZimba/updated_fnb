from flask import Blueprint, request
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv
from decimal import Decimal

load_dotenv()
app_file112 = Blueprint('app_file112', __name__)

@app_file112.route("/syncmenu", methods=["POST"])
@cross_origin()
def sync_menu():
    try:
        # Get outlet from request payload
        data = request.get_json()
        outlet = data.get('outlet')
        token = data.get('token')  # You can add token validation if needed

        if not outlet:
            return {"error": "Outlet parameter is required"}, 400

        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password'),
            database=os.getenv('database')
        )
        cursor = mydb.cursor(buffered=True)

        # Delete existing tblmenu data for this outlet
        cursor.execute("DELETE FROM tblmenu WHERE Restaurant = %s", (outlet,))
        mydb.commit()

        # Fetch unique items from tblorder_detailshistory for this outlet
        cursor.execute("""
            SELECT DISTINCT
                d.ItemName, 
                MIN(d.itemRate) AS itemRate, 
                MIN(d.ItemType) AS ItemType, 
                MIN(d.Description) AS Description, 
                MIN(d.discountExempt) AS discountExempt
            FROM tblorder_detailshistory d
            JOIN tblorderhistory o ON d.order_ID = o.idtblorderHistory
            WHERE d.ItemName IS NOT NULL 
              AND TRIM(d.ItemName) != ''
              AND o.Outlet_Name = %s
            GROUP BY d.ItemName
        """, (outlet,))
        unique_items = cursor.fetchall()

        insert_sql = """
            INSERT INTO tblmenu (Name, Description, Type, Price, Restaurant, state, discountExempt)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        for item in unique_items:
            item_name = item[0]
            item_rate = Decimal(item[1]) if item[1] else Decimal("0.0")
            item_type = item[2] or ""
            description = item[3] or ""
            discount_exempt = item[4] or ""

            cursor.execute(insert_sql, (
                item_name,
                description,
                item_type,
                item_rate,
                outlet,  # Set restaurant to the outlet from payload
                "active",
                discount_exempt
            ))

        mydb.commit()
        cursor.close()
        mydb.close()
        
        return {
            "success": f"Menu synced for outlet {outlet}",
            "items_added": len(unique_items)
        }, 200

    except Exception as e:
        return {"error": str(e)}, 500