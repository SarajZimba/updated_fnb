from flask import Blueprint, jsonify, request
import mysql.connector
import os
from dotenv import load_dotenv
from flask_cors import cross_origin
from root.auth.check import token_auth
from decimal import Decimal

load_dotenv()

app_file118 = Blueprint('app_file118', __name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("host"),
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )

@app_file118.route("/itemconsumefromsale", methods=["POST"])
@cross_origin()
def item_consumption_details():
    try:
        data = request.get_json()
        token = data.get("token")
        if not token or not token_auth(token):
            return jsonify({"error": "Invalid or missing token."}), 400

        outlet = data.get("outlet")
        item_name = data.get("item_name")
        start_date = data.get("startDate")
        end_date = data.get("endDate")

        if not all([outlet, item_name, start_date, end_date]):
            return jsonify({"error": "Missing required parameters (outlet, item_name, startDate, endDate)."}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        result = {
            "details": [],
            "summary": {
                "total_consumed": 0.0,
                # "total_converted": 0.0,
                "uom": None
            }
        }

        # Fetch unit definition
        cursor.execute("""
            SELECT unit, uom FROM tblunitdefinition
            WHERE name = %s AND outlet = %s
        """, (item_name, outlet))
        unit_def = cursor.fetchone()
        conversion_factor = 1.0
        if unit_def:
            conversion_factor = 1.0 / float(unit_def['unit'])
            result['summary']['uom'] = unit_def['uom']

        # Get all recipes that use this item directly or via sub-recipe
        cursor.execute("""
            SELECT DISTINCT r.id AS recipe_id, r.name AS menu_item, r.ItemType
            FROM recipe r
            LEFT JOIN recipe_items ri ON r.id = ri.recipe_id AND ri.name = %s
            LEFT JOIN recipe_subrecipes rs ON r.id = rs.recipe_id
            LEFT JOIN sub_recipe_items sri ON rs.sub_recipe_id = sri.sub_recipe_id AND sri.name = %s
            WHERE r.outlet = %s AND (ri.name IS NOT NULL OR sri.name IS NOT NULL)
        """, (item_name, item_name, outlet))

        recipes = cursor.fetchall()

        for recipe in recipes:
            recipe_id = recipe['recipe_id']
            menu_item = recipe['menu_item']
            item_type = recipe['ItemType']

            # Get total sold
            cursor.execute("""
                SELECT SUM(d.count) as total_sold
                FROM tblorder_detailshistory d
                JOIN tblorderhistory o ON o.idtblorderHistory = d.order_ID
                WHERE o.Date BETWEEN %s AND %s 
                AND o.Outlet_Name = %s 
                AND d.ItemName = %s
                AND d.ItemType = %s
            """, (start_date, end_date, outlet, menu_item, item_type))
            sold_data = cursor.fetchone()
            total_sold = float(sold_data['total_sold']) if sold_data['total_sold'] else 0.0

            if total_sold == 0:
                continue

            # Direct usage
            cursor.execute("""
                SELECT quantity FROM recipe_items
                WHERE recipe_id = %s AND name = %s
            """, (recipe_id, item_name))
            ri = cursor.fetchone()
            direct_qty = float(ri['quantity']) if ri else 0.0

            # Sub-recipe usage breakdown
            cursor.execute("""
                SELECT rs.quantity as sub_qty, sri.quantity as item_qty, sr.name as sub_recipe_name
                FROM recipe_subrecipes rs
                JOIN sub_recipe_items sri ON rs.sub_recipe_id = sri.sub_recipe_id
                JOIN sub_recipe sr ON sr.id = rs.sub_recipe_id
                WHERE rs.recipe_id = %s AND sri.name = %s
            """, (recipe_id, item_name))
            sub_items = cursor.fetchall()

            sub_total = 0.0
            sub_recipe_details = []
            for row in sub_items:
                sub_qty = float(row['sub_qty'])
                item_qty = float(row['item_qty'])
                calculated_quantity = sub_qty * item_qty
                sub_total += calculated_quantity
                sub_recipe_details.append({
                    "sub_recipe_name": row['sub_recipe_name'],
                    "sub_qty_in_recipe": sub_qty,
                    "item_qty_in_sub_recipe": item_qty,
                    "calculated_quantity": calculated_quantity
                })

            total_consumed = total_sold * (direct_qty + sub_total)
            total_converted = total_consumed * conversion_factor

            result['details'].append({
                "recipe_item": menu_item,
                "item_type": item_type,
                "total_sold": total_sold,
                "direct_usage_recipe_per_unit": direct_qty,
                "total_direct_recipe_usage": total_sold * direct_qty,
                "sub_recipe_usage_per_unit": sub_total,
                "total_sub_recipe_usage": total_sold * sub_total,
                "total_consumed": total_consumed,
                # "converted_quantity": total_converted,
                "converted_uom": result['summary']['uom'],
                "sub_recipes": sub_recipe_details
            })

            result['summary']['total_consumed'] += total_consumed
            # result['summary']['total_converted'] += total_converted

        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "item_name": item_name,
            "outlet": outlet,
            "start_date": start_date,
            "end_date": end_date,
            "consumption_details": result
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400