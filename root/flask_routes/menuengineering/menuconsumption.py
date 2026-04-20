# from flask import Blueprint, jsonify, request
# import mysql.connector
# import os
# from dotenv import load_dotenv
# from flask_cors import cross_origin
# from root.auth.check import token_auth
# from decimal import Decimal, ROUND_HALF_UP

# load_dotenv()

# app_file110 = Blueprint('app_file110', __name__)

# def get_db_connection():
#     return mysql.connector.connect(
#         host=os.getenv("host"),
#         user=os.getenv("user"),
#         password=os.getenv("password"),
#         database=os.getenv("database")
#     )

# @app_file110.route("/menu-consumption", methods=["POST"])
# @cross_origin()
# def menu_consumption():
#     try:
#         data = request.get_json()
#         token = data.get("token")
#         if not token or not token_auth(token):
#             return jsonify({"error": "Invalid or missing token."}), 400

#         start_date = data.get("startDate")
#         end_date = data.get("endDate")
#         outlet = data.get("outlet")
#         include_sub_recipe_items = data.get("includeSubRecipeItems", True)

#         if not start_date or not end_date or not outlet:
#             return jsonify({"error": "Missing startDate, endDate, or outlet."}), 400

#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)

#         cursor.execute("SELECT use_same_recipe FROM master_featured ORDER BY id DESC LIMIT 1")
#         flag_row = cursor.fetchone()
#         use_same_recipe = flag_row["use_same_recipe"] if flag_row else 0

#         # First get all item types from recipe table for this outlet
#         cursor.execute("SELECT DISTINCT ItemType FROM tblorder_detailshistory")
#         item_types = [row["ItemType"] for row in cursor.fetchall()]

#         result = {}
#         grand_total_items_sold = 0
#         grand_unique_items_sold = 0
#         grand_total_menu_items = 0
#         type_wise_consumption = {}
#         all_consumed_items = {}

#         for item_type in item_types:
#             type_wise_consumption[item_type] = {}

#             # # Get total menu items for this type
#             # cursor.execute("SELECT COUNT(*) AS total_menu_items FROM recipe WHERE outlet = %s AND ItemType = %s", 
#             #              (outlet, item_type))

#             if use_same_recipe == 1:
#                 cursor.execute(
#                     "SELECT COUNT(DISTINCT name) AS total_menu_items FROM recipe WHERE ItemType = %s",
#                     (item_type,)
#                 )
#             else:
#                 cursor.execute(
#                     "SELECT COUNT(*) AS total_menu_items FROM recipe WHERE outlet = %s AND ItemType = %s",
#                     (outlet, item_type)
#                 )
#             total_menu_item = cursor.fetchone()["total_menu_items"]
#             grand_total_menu_items += total_menu_item

#             # Get all sold items of this type from order history
#             cursor.execute("""
#                 SELECT 
#                     d.ItemName,
#                     SUM(d.count) AS total_sold
#                 FROM tblorder_detailshistory d
#                 JOIN tblorderhistory o ON o.idtblorderHistory = d.order_ID
#                 WHERE o.Date BETWEEN %s AND %s
#                   AND o.Outlet_Name = %s
#                   AND d.ItemType = %s
#                 GROUP BY d.ItemName
#             """, (start_date, end_date, outlet, item_type))

#             sold_items = cursor.fetchall()
#             itemwise = []

#             total_sold = 0
#             unique_items_sold = 0

#             for sold_item in sold_items:
#                 item_name = sold_item["ItemName"]
#                 quantity_sold = sold_item["total_sold"]
#                 total_sold += quantity_sold
#                 if quantity_sold > 0:
#                     unique_items_sold += 1

#                 if use_same_recipe == 1:
#                     cursor.execute("""
#                         SELECT id, sellingprice, costprice 
#                         FROM recipe 
#                         WHERE name = %s AND ItemType = %s
#                         LIMIT 1
#                     """, (item_name, item_type))
#                 else:
#                     cursor.execute("""
#                         SELECT id, sellingprice, costprice 
#                         FROM recipe 
#                         WHERE outlet = %s AND name = %s AND ItemType = %s
#                     """, (outlet, item_name, item_type))
#                 recipe_info = cursor.fetchone()

#                 item_data = {
#                     "ItemName": item_name,
#                     "ItemType": item_type,
#                     "total_sold": quantity_sold,
#                     "has_recipe": bool(recipe_info)
#                 }

#                 if recipe_info:
#                     item_data["recipe_id"] = recipe_info["id"]
#                     recipe_id = recipe_info["id"]

#                     # Get recipe items and calculate consumption
#                     cursor.execute("SELECT name, quantity, uom, new_uom FROM recipe_items WHERE recipe_id = %s", (recipe_id,))
#                     recipe_items = cursor.fetchall()
#                     for ri in recipe_items:
#                         ingredient_name = ri["name"]
#                         total_consumed = float(ri["quantity"]) * float(quantity_sold)
#                         uom = ri["uom"]
#                         new_uom = ri["new_uom"]

#                         # Type-wise consumption
#                         if ingredient_name not in type_wise_consumption[item_type]:
#                             type_wise_consumption[item_type][ingredient_name] = {
#                                 "total_quantity": 0, 
#                                 "uom": uom, 
#                                 "new_uom": new_uom
#                             }
#                         type_wise_consumption[item_type][ingredient_name]["total_quantity"] += total_consumed

#                         # Global consumption
#                         if ingredient_name not in all_consumed_items:
#                             all_consumed_items[ingredient_name] = {
#                                 "total_quantity": 0, 
#                                 "uom": uom, 
#                                 "new_uom": new_uom
#                             }
#                         all_consumed_items[ingredient_name]["total_quantity"] += total_consumed

#                     # Handle sub-recipes
#                     cursor.execute("""
#                         SELECT rs.sub_recipe_id as sub_id, rs.quantity AS sr_qty, s.name AS sub_name, s.uom, s.unit, s.id, rs.new_uom AS new_uom
#                         FROM recipe_subrecipes rs
#                         JOIN sub_recipe s ON rs.sub_recipe_id = s.id
#                         WHERE rs.recipe_id = %s
#                     """, (recipe_id,))
#                     sub_recipes = cursor.fetchall()

#                     for sr in sub_recipes:
#                         if include_sub_recipe_items:
#                             cursor.execute("SELECT name, quantity, uom, new_uom FROM sub_recipe_items WHERE sub_recipe_id = %s", (sr["sub_id"],))
#                             sub_recipe_items = cursor.fetchall()
#                             for sri in sub_recipe_items:
#                                 ingredient_name = sri["name"]
#                                 total_consumed = float(sri["quantity"]) * float(sr["sr_qty"]) * float(quantity_sold)
#                                 uom = sri["uom"]
#                                 new_uom = sri["new_uom"]

#                                 # Type-wise consumption
#                                 if ingredient_name not in type_wise_consumption[item_type]:
#                                     type_wise_consumption[item_type][ingredient_name] = {
#                                         "total_quantity": 0, 
#                                         "uom": uom, 
#                                         "new_uom": new_uom
#                                     }
#                                 type_wise_consumption[item_type][ingredient_name]["total_quantity"] += total_consumed

#                                 # Global consumption
#                                 if ingredient_name not in all_consumed_items:
#                                     all_consumed_items[ingredient_name] = {
#                                         "total_quantity": 0, 
#                                         "uom": uom, 
#                                         "new_uom": new_uom
#                                     }
#                                 all_consumed_items[ingredient_name]["total_quantity"] += total_consumed
#                         else:
#                             sub_recipe_name = sr["sub_name"]
#                             total_consumed = float(sr["sr_qty"]) * float(quantity_sold)
#                             uom = sr["uom"]
#                             new_uom = sr.get("new_uom", "")

#                             if sub_recipe_name not in type_wise_consumption[item_type]:
#                                 type_wise_consumption[item_type][sub_recipe_name] = {
#                                     "total_quantity": 0,
#                                     "uom": uom,
#                                     "new_uom": new_uom,
#                                     "is_sub_recipe": True
#                                 }
#                             type_wise_consumption[item_type][sub_recipe_name]["total_quantity"] += total_consumed

#                             if sub_recipe_name not in all_consumed_items:
#                                 all_consumed_items[sub_recipe_name] = {
#                                     "total_quantity": 0,
#                                     "uom": uom,
#                                     "new_uom": new_uom
#                                 }
#                             all_consumed_items[sub_recipe_name]["total_quantity"] += total_consumed

#                 itemwise.append(item_data)

#             grand_total_items_sold += total_sold
#             grand_unique_items_sold += unique_items_sold

#             result[item_type] = {
#                 "itemwise_summary": itemwise,
#                 "total_items_sold": total_sold,
#                 "unique_items_sold": unique_items_sold,
#                 "total_menu_items": total_menu_item,
#             }

#         # Rest of your code for rounding and grouping remains the same...
#         for item_type, ingredients in type_wise_consumption.items():
#             for ingredient in ingredients.values():
#                 ingredient["total_quantity"] = float(Decimal(ingredient["total_quantity"]).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

#         nested_consumed_group = {}
#         cursor = conn.cursor(dictionary=True)
#         cursor.execute("SELECT ItemName, GroupName, Type FROM stock_statement")
#         stock_info_lookup = {
#             row["ItemName"]: {
#                 "GroupName": row["GroupName"] or "Group Not Found",
#                 "Type": row["Type"] or "Type Not Found"
#             }
#             for row in cursor.fetchall()
#         }
#         cursor.close()

#         for name, info in all_consumed_items.items():
#             total_quantity = float(Decimal(info["total_quantity"]).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
#             uom = info.get("uom")
#             new_uom = info.get("new_uom")

#             stock_info = stock_info_lookup.get(name, {"GroupName": "Group Not Found", "Type": "Type Not Found"})
#             group_name = stock_info["GroupName"]
#             item_type = stock_info["Type"]

#             if item_type not in nested_consumed_group:
#                 nested_consumed_group[item_type] = {}

#             if group_name not in nested_consumed_group[item_type]:
#                 nested_consumed_group[item_type][group_name] = []

#             nested_consumed_group[item_type][group_name].append({
#                 "name": name,
#                 "uom": uom,
#                 "new_uom": new_uom,
#                 "total_quantity": total_quantity
#             })

#         cursor.close()
#         conn.close()
#         return jsonify({
#             "grouped_by_item_type": result,
#             "grand_total_items_sold": grand_total_items_sold,
#             "grand_unique_items_sold": grand_unique_items_sold,
#             "grand_total_menu_items": grand_total_menu_items,
#             "type_wise_consumption": type_wise_consumption,
#             "all_consumed_items": nested_consumed_group
#         }), 200

#     except Exception as e:
#         return jsonify({"error": str(e)}), 400


from flask import Blueprint, jsonify, request
import mysql.connector
import os
from dotenv import load_dotenv
from flask_cors import cross_origin
from root.auth.check import token_auth
from decimal import Decimal, ROUND_HALF_UP
import re

load_dotenv()

app_file110 = Blueprint('app_file110', __name__)

# Define standard UOMs
STANDARD_UOMS = {
    'kg', 'kilogram', 'kilograms',
    'g', 'gram', 'grams', 'gms', 'gm', 'grm',
    'ounce', 'ounces', 'oz',
    'litre', 'litres', 'liter', 'liters', 'l', 'ltr',
    'ml', 'millilitre', 'millilitres', 'milliliter', 'milliliters',
    'lb', 'pound', 'pounds',
    'mg', 'milligram', 'milligrams'
}

def is_standard_uom(uom):
    """Check if UOM is a standard unit"""
    if not uom:
        return False
    uom_lower = str(uom).lower().strip()
    return uom_lower in STANDARD_UOMS

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("host"),
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )

@app_file110.route("/menu-consumption", methods=["POST"])
@cross_origin()
def menu_consumption():
    try:
        data = request.get_json()
        token = data.get("token")
        if not token or not token_auth(token):
            return jsonify({"error": "Invalid or missing token."}), 400

        start_date = data.get("startDate")
        end_date = data.get("endDate")
        outlet = data.get("outlet")
        include_sub_recipe_items = data.get("includeSubRecipeItems", True)

        if not start_date or not end_date or not outlet:
            return jsonify({"error": "Missing startDate, endDate, or outlet."}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT use_same_recipe FROM master_featured ORDER BY id DESC LIMIT 1")
        flag_row = cursor.fetchone()
        use_same_recipe = flag_row["use_same_recipe"] if flag_row else 0

        # First get all item types from recipe table for this outlet
        cursor.execute("SELECT DISTINCT ItemType FROM tblorder_detailshistory")
        item_types = [row["ItemType"] for row in cursor.fetchall()]

        result = {}
        grand_total_items_sold = 0
        grand_unique_items_sold = 0
        grand_total_menu_items = 0
        type_wise_consumption = {}
        all_consumed_items = {}
        inappropriate_uom_items = []  # Track items with inappropriate UOMs

        for item_type in item_types:
            type_wise_consumption[item_type] = {}

            if use_same_recipe == 1:
                cursor.execute(
                    "SELECT COUNT(DISTINCT name) AS total_menu_items FROM recipe WHERE ItemType = %s",
                    (item_type,)
                )
            else:
                cursor.execute(
                    "SELECT COUNT(*) AS total_menu_items FROM recipe WHERE outlet = %s AND ItemType = %s",
                    (outlet, item_type)
                )
            total_menu_item = cursor.fetchone()["total_menu_items"]
            grand_total_menu_items += total_menu_item

            # Get all sold items of this type from order history
            cursor.execute("""
                SELECT 
                    d.ItemName,
                    SUM(d.count) AS total_sold
                FROM tblorder_detailshistory d
                JOIN tblorderhistory o ON o.idtblorderHistory = d.order_ID
                WHERE o.Date BETWEEN %s AND %s
                  AND o.Outlet_Name = %s
                  AND d.ItemType = %s
                GROUP BY d.ItemName
            """, (start_date, end_date, outlet, item_type))

            sold_items = cursor.fetchall()
            itemwise = []

            total_sold = 0
            unique_items_sold = 0

            for sold_item in sold_items:
                item_name = sold_item["ItemName"]
                quantity_sold = sold_item["total_sold"]
                total_sold += quantity_sold
                if quantity_sold > 0:
                    unique_items_sold += 1

                if use_same_recipe == 1:
                    cursor.execute("""
                        SELECT id, sellingprice, costprice 
                        FROM recipe 
                        WHERE name = %s AND ItemType = %s
                        LIMIT 1
                    """, (item_name, item_type))
                else:
                    cursor.execute("""
                        SELECT id, sellingprice, costprice 
                        FROM recipe 
                        WHERE outlet = %s AND name = %s AND ItemType = %s
                    """, (outlet, item_name, item_type))
                recipe_info = cursor.fetchone()

                item_data = {
                    "ItemName": item_name,
                    "ItemType": item_type,
                    "total_sold": quantity_sold,
                    "has_recipe": bool(recipe_info)
                }

                if recipe_info:
                    item_data["recipe_id"] = recipe_info["id"]
                    recipe_id = recipe_info["id"]

                    # Get recipe items and calculate consumption
                    cursor.execute("SELECT name, quantity, uom, new_uom FROM recipe_items WHERE recipe_id = %s", (recipe_id,))
                    recipe_items = cursor.fetchall()
                    for ri in recipe_items:
                        ingredient_name = ri["name"]
                        total_consumed = float(ri["quantity"]) * float(quantity_sold)
                        uom = ri["uom"]
                        new_uom = ri["new_uom"]
                        
                        # Check if UOM is standard
                        is_standard = is_standard_uom(uom)
                        if not is_standard:
                            inappropriate_uom_items.append({
                                "item_name": ingredient_name,
                                "uom": uom,
                                "source": "recipe_items",
                                "recipe": item_name,
                                "item_type": item_type
                            })

                        # Type-wise consumption
                        if ingredient_name not in type_wise_consumption[item_type]:
                            type_wise_consumption[item_type][ingredient_name] = {
                                "total_quantity": 0, 
                                "uom": uom, 
                                "new_uom": new_uom,
                                "is_standard_uom": is_standard  # Add flag
                            }
                        type_wise_consumption[item_type][ingredient_name]["total_quantity"] += total_consumed
                        type_wise_consumption[item_type][ingredient_name]["is_standard_uom"] = type_wise_consumption[item_type][ingredient_name].get("is_standard_uom", True) and is_standard

                        # Global consumption
                        if ingredient_name not in all_consumed_items:
                            all_consumed_items[ingredient_name] = {
                                "total_quantity": 0, 
                                "uom": uom, 
                                "new_uom": new_uom,
                                "is_standard_uom": is_standard  # Add flag
                            }
                        all_consumed_items[ingredient_name]["total_quantity"] += total_consumed
                        # Update flag if any occurrence is non-standard
                        if not is_standard:
                            all_consumed_items[ingredient_name]["is_standard_uom"] = False

                    # Handle sub-recipes
                    cursor.execute("""
                        SELECT rs.sub_recipe_id as sub_id, rs.quantity AS sr_qty, s.name AS sub_name, s.uom, s.unit, s.id, rs.new_uom AS new_uom
                        FROM recipe_subrecipes rs
                        JOIN sub_recipe s ON rs.sub_recipe_id = s.id
                        WHERE rs.recipe_id = %s
                    """, (recipe_id,))
                    sub_recipes = cursor.fetchall()

                    for sr in sub_recipes:
                        if include_sub_recipe_items:
                            cursor.execute("SELECT name, quantity, uom, new_uom FROM sub_recipe_items WHERE sub_recipe_id = %s", (sr["sub_id"],))
                            sub_recipe_items = cursor.fetchall()
                            for sri in sub_recipe_items:
                                ingredient_name = sri["name"]
                                total_consumed = float(sri["quantity"]) * float(sr["sr_qty"]) * float(quantity_sold)
                                uom = sri["uom"]
                                new_uom = sri["new_uom"]
                                
                                # Check if UOM is standard
                                is_standard = is_standard_uom(uom)
                                if not is_standard:
                                    inappropriate_uom_items.append({
                                        "item_name": ingredient_name,
                                        "uom": uom,
                                        "source": "sub_recipe_items",
                                        "sub_recipe": sr["sub_name"],
                                        "recipe": item_name,
                                        "item_type": item_type
                                    })

                                # Type-wise consumption
                                if ingredient_name not in type_wise_consumption[item_type]:
                                    type_wise_consumption[item_type][ingredient_name] = {
                                        "total_quantity": 0, 
                                        "uom": uom, 
                                        "new_uom": new_uom,
                                        "is_standard_uom": is_standard
                                    }
                                type_wise_consumption[item_type][ingredient_name]["total_quantity"] += total_consumed
                                if not is_standard:
                                    type_wise_consumption[item_type][ingredient_name]["is_standard_uom"] = False

                                # Global consumption
                                if ingredient_name not in all_consumed_items:
                                    all_consumed_items[ingredient_name] = {
                                        "total_quantity": 0, 
                                        "uom": uom, 
                                        "new_uom": new_uom,
                                        "is_standard_uom": is_standard
                                    }
                                all_consumed_items[ingredient_name]["total_quantity"] += total_consumed
                                if not is_standard:
                                    all_consumed_items[ingredient_name]["is_standard_uom"] = False
                        else:
                            sub_recipe_name = sr["sub_name"]
                            total_consumed = float(sr["sr_qty"]) * float(quantity_sold)
                            uom = sr["uom"]
                            new_uom = sr.get("new_uom", "")
                            
                            # Check if UOM is standard
                            is_standard = is_standard_uom(uom)
                            if not is_standard:
                                inappropriate_uom_items.append({
                                    "item_name": sub_recipe_name,
                                    "uom": uom,
                                    "source": "sub_recipe",
                                    "recipe": item_name,
                                    "item_type": item_type
                                })

                            if sub_recipe_name not in type_wise_consumption[item_type]:
                                type_wise_consumption[item_type][sub_recipe_name] = {
                                    "total_quantity": 0,
                                    "uom": uom,
                                    "new_uom": new_uom,
                                    "is_sub_recipe": True,
                                    "is_standard_uom": is_standard
                                }
                            type_wise_consumption[item_type][sub_recipe_name]["total_quantity"] += total_consumed
                            if not is_standard:
                                type_wise_consumption[item_type][sub_recipe_name]["is_standard_uom"] = False

                            if sub_recipe_name not in all_consumed_items:
                                all_consumed_items[sub_recipe_name] = {
                                    "total_quantity": 0,
                                    "uom": uom,
                                    "new_uom": new_uom,
                                    "is_standard_uom": is_standard
                                }
                            all_consumed_items[sub_recipe_name]["total_quantity"] += total_consumed
                            if not is_standard:
                                all_consumed_items[sub_recipe_name]["is_standard_uom"] = False

                itemwise.append(item_data)

            grand_total_items_sold += total_sold
            grand_unique_items_sold += unique_items_sold

            result[item_type] = {
                "itemwise_summary": itemwise,
                "total_items_sold": total_sold,
                "unique_items_sold": unique_items_sold,
                "total_menu_items": total_menu_item,
            }

        # Round the quantities
        for item_type, ingredients in type_wise_consumption.items():
            for ingredient in ingredients.values():
                ingredient["total_quantity"] = float(Decimal(ingredient["total_quantity"]).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

        nested_consumed_group = {}
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT ItemName, GroupName, Type FROM stock_statement")
        stock_info_lookup = {
            row["ItemName"]: {
                "GroupName": row["GroupName"] or "Group Not Found",
                "Type": row["Type"] or "Type Not Found"
            }
            for row in cursor.fetchall()
        }
        cursor.close()

        for name, info in all_consumed_items.items():
            total_quantity = float(Decimal(info["total_quantity"]).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
            uom = info.get("uom")
            new_uom = info.get("new_uom")
            is_standard_uom_flag = info.get("is_standard_uom", False)

            stock_info = stock_info_lookup.get(name, {"GroupName": "Group Not Found", "Type": "Type Not Found"})
            group_name = stock_info["GroupName"]
            item_type = stock_info["Type"]

            if item_type not in nested_consumed_group:
                nested_consumed_group[item_type] = {}

            if group_name not in nested_consumed_group[item_type]:
                nested_consumed_group[item_type][group_name] = []

            nested_consumed_group[item_type][group_name].append({
                "name": name,
                "uom": uom,
                "new_uom": new_uom,
                "total_quantity": total_quantity,
                "is_standard_uom": is_standard_uom_flag  # Add flag to final output
            })

        cursor.close()
        conn.close()
        
        # Prepare warning summary
        inappropriate_uom_summary = {
            "has_inappropriate_uoms": len(inappropriate_uom_items) > 0,
            "total_inappropriate_items": len(inappropriate_uom_items),
            "inappropriate_items": inappropriate_uom_items
        }
        
        return jsonify({
            "grouped_by_item_type": result,
            "grand_total_items_sold": grand_total_items_sold,
            "grand_unique_items_sold": grand_unique_items_sold,
            "grand_total_menu_items": grand_total_menu_items,
            "type_wise_consumption": type_wise_consumption,
            "all_consumed_items": nested_consumed_group,
            "uom_validation": inappropriate_uom_summary  # Add UOM validation summary
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400