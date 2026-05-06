from flask import Blueprint, jsonify, request
import mysql.connector
import os
from dotenv import load_dotenv
from flask_cors import cross_origin
from root.auth.check import token_auth

load_dotenv()

app_file108 = Blueprint('app_file108', __name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("host"),
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )


@app_file108.route("/recipe", methods=["POST"])
@cross_origin()
def create_recipe():
    try:
        data = request.get_json()
        token = data.get("token")
        if not token or not token_auth(token):
            return jsonify({"error": "Invalid or missing token."}), 400

        name = data.get("name")
        outlet = data.get("outlet")
        cost_price = data.get("cost_price")
        selling_price = data.get("selling_price")
        cost_percent = data.get("cost_percent")
        item_type = data.get("item_type")
        items = data.get("items", [])
        sub_recipes = data.get("sub_recipes", [])

        if (
            not name or
            not outlet or
            cost_price is None or
            selling_price is None or
            cost_percent is None or
            not item_type or
            not isinstance(items, list) or
            not isinstance(sub_recipes, list)
        ):
            return jsonify({"error": "Missing fields or invalid format for items, sub_recipes, or cost fields"}), 400

        mydb = get_db_connection()
        cursor = mydb.cursor()

        # Check if recipe already exists
        cursor.execute(
            "SELECT id FROM recipe WHERE name = %s AND outlet = %s",
            (name, outlet)
        )
        existing_recipe = cursor.fetchone()

        # If recipe exists, delete it (and its related items/sub-recipes)
        if existing_recipe:
            recipe_id_to_delete = existing_recipe[0]
            
            # Delete related items
            cursor.execute(
                "DELETE FROM recipe_items WHERE recipe_id = %s",
                (recipe_id_to_delete,)
            )
            
            # Delete related sub-recipes
            cursor.execute(
                "DELETE FROM recipe_subrecipes WHERE recipe_id = %s",
                (recipe_id_to_delete,)
            )
            
            # Finally, delete the recipe itself
            cursor.execute(
                "DELETE FROM recipe WHERE id = %s",
                (recipe_id_to_delete,)
            )
            mydb.commit()  # Commit deletions before proceeding

        # Insert new recipe (same as before)
        cursor.execute(
            """
            INSERT INTO recipe (name, outlet, costprice, sellingprice, cost_percent, ItemType)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (name, outlet, cost_price, selling_price, cost_percent, item_type)
        )
        new_recipe_id = cursor.lastrowid

        # Insert recipe items
        for item in items:
            item_name = item.get("name")
            rate = item.get("rate")
            uom = item.get("uom")
            new_uom = item.get("new_uom")
            quantity = item.get("quantity")
            cost = item.get("cost")
            unit = item.get("unit", 1)

            if not all([item_name, rate, uom, quantity, cost]):
                continue

            cursor.execute("""
                INSERT INTO recipe_items (recipe_id, name, rate, uom, new_uom, unit, quantity, cost)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (new_recipe_id, item_name, rate, uom, new_uom, unit, quantity, cost))

        # Insert sub-recipes
        for sr in sub_recipes:
            sub_recipe_id = sr.get("sub_recipe_id")
            quantity = sr.get("quantity", 0)
            uom = sr.get("uom")
            unit = sr.get("unit")
            new_uom = sr.get("new_uom")
            costprice = sr.get("costprice")
            rate = sr.get("rate")

            if not sub_recipe_id:
                continue

            cursor.execute("""
                INSERT INTO recipe_subrecipes (recipe_id, sub_recipe_id, quantity, uom, unit, costprice, rate, new_uom)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (new_recipe_id, sub_recipe_id, quantity, uom, unit, costprice, rate, new_uom))

        mydb.commit()
        cursor.close()
        mydb.close()

        return jsonify({"message": "Recipe created successfully with sub-recipes."}), 201

    except Exception as e:
        mydb.rollback()  # Rollback in case of error
        return jsonify({"error": str(e)}), 400
    


# @app_file108.route("/recipe-by-name", methods=["POST"])
# @cross_origin()
# def create_recipe_by_name():
#     try:
#         data = request.get_json()
#         token = data.get("token")
#         if not token or not token_auth(token):
#             return jsonify({"error": "Invalid or missing token."}), 400

#         name = data.get("name")
#         outlet = data.get("outlet")
#         cost_price = data.get("cost_price")
#         selling_price = data.get("selling_price")
#         cost_percent = data.get("cost_percent")
#         item_type = data.get("item_type")
#         items = data.get("items", [])
#         sub_recipes = data.get("sub_recipes", [])

#         if (
#             not name or
#             not outlet or
#             cost_price is None or
#             selling_price is None or
#             cost_percent is None or
#             not item_type or
#             not isinstance(items, list) or
#             not isinstance(sub_recipes, list)
#         ):
#             return jsonify({"error": "Missing fields or invalid format"}), 400

#         mydb = get_db_connection()
#         cursor = mydb.cursor(dictionary=True)

#         # First, validate all sub-recipe names exist
#         missing_sub_recipes = []
#         valid_sub_recipes = []
        
#         for sr in sub_recipes:
#             sub_recipe_name = sr.get("sub_recipe_name")
#             if not sub_recipe_name:
#                 continue
                
#             cursor.execute(
#                 "SELECT id, name FROM sub_recipe WHERE name = %s",
#                 (sub_recipe_name,)
#             )
#             sub_recipe = cursor.fetchone()
            
#             if not sub_recipe:
#                 missing_sub_recipes.append(sub_recipe_name)
#             else:
#                 valid_sub_recipes.append({
#                     **sr,
#                     "sub_recipe_id": sub_recipe["id"]
#                 })
        
#         if missing_sub_recipes:
#             return jsonify({
#                 "error": "Some sub-recipes not found",
#                 "missing_sub_recipes": missing_sub_recipes
#             }), 400

#         # Check if recipe already exists
#         cursor.execute(
#             "SELECT id FROM recipe WHERE name = %s AND outlet = %s",
#             (name, outlet)
#         )
#         existing_recipe = cursor.fetchone()

#         if existing_recipe:
#             recipe_id_to_delete = existing_recipe["id"]
#             cursor.execute("DELETE FROM recipe_items WHERE recipe_id = %s", (recipe_id_to_delete,))
#             cursor.execute("DELETE FROM recipe_subrecipes WHERE recipe_id = %s", (recipe_id_to_delete,))
#             cursor.execute("DELETE FROM recipe WHERE id = %s", (recipe_id_to_delete,))
#             mydb.commit()

#         # Insert new recipe
#         cursor.execute(
#             """
#             INSERT INTO recipe (name, outlet, costprice, sellingprice, cost_percent, ItemType)
#             VALUES (%s, %s, %s, %s, %s, %s)
#             """,
#             (name, outlet, cost_price, selling_price, cost_percent, item_type)
#         )
#         new_recipe_id = cursor.lastrowid

#         # Insert recipe items
#         for item in items:
#             item_name = item.get("name")
#             rate = item.get("rate")
#             uom = item.get("uom")
#             new_uom = item.get("new_uom")
#             quantity = item.get("quantity")
#             cost = item.get("cost")
#             unit = item.get("unit", 1)

#             if not all([item_name, rate, uom, quantity, cost]):
#                 continue

#             cursor.execute("""
#                 INSERT INTO recipe_items (recipe_id, name, rate, uom, new_uom, unit, quantity, cost)
#                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
#             """, (new_recipe_id, item_name, rate, uom, new_uom, unit, quantity, cost))

#         # Insert sub-recipes using the validated IDs
#         for sr in valid_sub_recipes:
#             cursor.execute("""
#                 INSERT INTO recipe_subrecipes (recipe_id, sub_recipe_id, quantity, uom, unit, costprice, rate, new_uom)
#                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
#             """, (
#                 new_recipe_id, 
#                 sr["sub_recipe_id"], 
#                 sr.get("quantity", 0), 
#                 sr.get("uom"), 
#                 sr.get("unit"), 
#                 sr.get("costprice"), 
#                 sr.get("rate"), 
#                 sr.get("new_uom")
#             ))

#         mydb.commit()
#         cursor.close()
#         mydb.close()

#         return jsonify({
#             "message": "Recipe created successfully with sub-recipes.",
#             "recipe_id": new_recipe_id,
#             "sub_recipes_used": len(valid_sub_recipes)
#         }), 201

#     except Exception as e:
#         mydb.rollback()
#         return jsonify({"error": str(e)}), 400


# @app_file108.route("/recipe-by-name", methods=["POST"])
# @cross_origin()
# def create_recipe_by_name():
#     try:
#         data = request.get_json()
#         token = data.get("token")
#         if not token or not token_auth(token):
#             return jsonify({"error": "Invalid or missing token."}), 400

#         name = data.get("name")
#         outlet = data.get("outlet")
#         cost_price = data.get("cost_price")
#         selling_price = data.get("selling_price")
#         cost_percent = data.get("cost_percent")
#         item_type = data.get("item_type")
#         items = data.get("items", [])
#         sub_recipes = data.get("sub_recipes", [])

#         if (
#             not name or
#             not outlet or
#             cost_price is None or
#             selling_price is None or
#             cost_percent is None or
#             not item_type
#         ):
#             return jsonify({"error": "Missing required fields: name, outlet, cost_price, selling_price, cost_percent, item_type"}), 400
        
#         if not isinstance(items, list):
#             return jsonify({"error": "Items must be a list"}), 400
        
#         if not isinstance(sub_recipes, list):
#             return jsonify({"error": "Sub-recipes must be a list"}), 400

#         mydb = get_db_connection()
#         cursor = mydb.cursor(dictionary=True)

#         # ------------------------
#         # Validate sub-recipes and skip invalid ones
#         # ------------------------
#         missing_sub_recipes = []
#         valid_sub_recipes = []
#         skipped_sub_recipes = []
        
#         for idx, sr in enumerate(sub_recipes):
#             sub_recipe_name = sr.get("sub_recipe_name")
            
#             if not sub_recipe_name:
#                 skipped_sub_recipes.append({
#                     "index": idx,
#                     "error": "Missing sub_recipe_name",
#                     "data": sr
#                 })
#                 continue
                
#             cursor.execute(
#                 "SELECT id, name, costprice FROM sub_recipe WHERE name = %s and outlet=%s",
#                 (sub_recipe_name,outlet,)
#             )
#             sub_recipe = cursor.fetchone()
            
#             if not sub_recipe:
#                 missing_sub_recipes.append({
#                     "index": idx,
#                     "sub_recipe_name": sub_recipe_name,
#                     "error": "Sub-recipe not found in database"
#                 })
#             else:
#                 # Validate required fields for sub-recipe
#                 quantity = sr.get("quantity")
#                 uom = sr.get("uom")
#                 unit = sr.get("unit")
#                 costprice = sr.get("costprice")
#                 rate = sr.get("rate")
#                 new_uom = sr.get("new_uom")
                
#                 if quantity is None or uom is None or unit is None:
#                     skipped_sub_recipes.append({
#                         "index": idx,
#                         "sub_recipe_name": sub_recipe_name,
#                         "error": "Missing required fields: quantity, uom, or unit",
#                         "data": sr
#                     })
#                     continue
                
#                 valid_sub_recipes.append({
#                     **sr,
#                     "sub_recipe_id": sub_recipe["id"],
#                     "sub_recipe_costprice": sub_recipe["costprice"]
#                 })
        
#         # If all sub-recipes are invalid, continue with empty list
#         if missing_sub_recipes and not valid_sub_recipes:
#             # Don't return error, just continue with warning
#             pass

#         # ------------------------
#         # Check if recipe already exists
#         # ------------------------
#         cursor.execute(
#             "SELECT id FROM recipe WHERE name = %s AND outlet = %s",
#             (name, outlet)
#         )
#         existing_recipe = cursor.fetchone()

#         if existing_recipe:
#             recipe_id_to_delete = existing_recipe["id"]
#             cursor.execute("DELETE FROM recipe_items WHERE recipe_id = %s", (recipe_id_to_delete,))
#             cursor.execute("DELETE FROM recipe_subrecipes WHERE recipe_id = %s", (recipe_id_to_delete,))
#             cursor.execute("DELETE FROM recipe WHERE id = %s", (recipe_id_to_delete,))
#             mydb.commit()

#         # ------------------------
#         # Insert new recipe
#         # ------------------------
#         cursor.execute(
#             """
#             INSERT INTO recipe (name, outlet, costprice, sellingprice, cost_percent, ItemType)
#             VALUES (%s, %s, %s, %s, %s, %s)
#             """,
#             (name, outlet, cost_price, selling_price, cost_percent, item_type)
#         )
#         new_recipe_id = cursor.lastrowid

#         # ------------------------
#         # Insert recipe items (skip invalid ones)
#         # ------------------------
#         valid_items = []
#         skipped_items = []
        
#         for idx, item in enumerate(items):
#             item_name = item.get("name")
#             rate = item.get("rate")
#             uom = item.get("uom")
#             new_uom = item.get("new_uom")
#             quantity = item.get("quantity")
#             cost = item.get("cost")
#             unit = item.get("unit", 1)
            
#             # Check for missing or empty item name
#             if not item_name or str(item_name).strip() == "":
#                 skipped_items.append({
#                     "index": idx,
#                     "error": "Item name is missing or empty",
#                     "item_data": item
#                 })
#                 continue
            
#             # Check other required fields
#             missing_fields = []
#             if rate is None:
#                 missing_fields.append("rate")
#             if uom is None or str(uom).strip() == "":
#                 missing_fields.append("uom")
#             if quantity is None:
#                 missing_fields.append("quantity")
#             if cost is None:
#                 missing_fields.append("cost")
            
#             if missing_fields:
#                 skipped_items.append({
#                     "index": idx,
#                     "item_name": item_name,
#                     "missing_fields": missing_fields,
#                     "error": f"Missing required fields: {', '.join(missing_fields)}"
#                 })
#                 continue
            
#             # Validate numeric values
#             try:
#                 rate = float(rate)
#                 quantity = float(quantity)
#                 cost = float(cost)
#                 unit = float(unit)
                
#                 if rate <= 0:
#                     skipped_items.append({
#                         "index": idx,
#                         "item_name": item_name,
#                         "error": "Rate must be greater than 0"
#                     })
#                     continue
                    
#                 if quantity <= 0:
#                     skipped_items.append({
#                         "index": idx,
#                         "item_name": item_name,
#                         "error": "Quantity must be greater than 0"
#                     })
#                     continue
                    
#                 if cost <= 0:
#                     skipped_items.append({
#                         "index": idx,
#                         "item_name": item_name,
#                         "error": "Cost must be greater than 0"
#                     })
#                     continue
                    
#                 if unit <= 0:
#                     skipped_items.append({
#                         "index": idx,
#                         "item_name": item_name,
#                         "error": "Unit must be greater than 0"
#                     })
#                     continue
                    
#             except (ValueError, TypeError):
#                 skipped_items.append({
#                     "index": idx,
#                     "item_name": item_name,
#                     "error": "Invalid numeric value for rate, quantity, cost, or unit"
#                 })
#                 continue
            
#             # All validations passed
#             valid_items.append({
#                 "name": item_name,
#                 "rate": rate,
#                 "uom": uom,
#                 "new_uom": new_uom,
#                 "quantity": quantity,
#                 "cost": cost,
#                 "unit": unit
#             })
        
#         # Insert valid items
#         items_inserted = 0
#         for item in valid_items:
#             cursor.execute("""
#                 INSERT INTO recipe_items (recipe_id, name, rate, uom, new_uom, unit, quantity, cost)
#                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
#             """, (
#                 new_recipe_id, 
#                 item["name"], 
#                 item["rate"], 
#                 item["uom"], 
#                 item["new_uom"], 
#                 item["unit"], 
#                 item["quantity"], 
#                 item["cost"]
#             ))
#             items_inserted += 1

#         # ------------------------
#         # Insert sub-recipes (skip invalid ones)
#         # ------------------------
#         sub_recipes_inserted = 0
#         for sr in valid_sub_recipes:
#             cursor.execute("""
#                 INSERT INTO recipe_subrecipes (recipe_id, sub_recipe_id, quantity, uom, unit, costprice, rate, new_uom)
#                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
#             """, (
#                 new_recipe_id, 
#                 sr["sub_recipe_id"], 
#                 sr.get("quantity", 0), 
#                 sr.get("uom"), 
#                 sr.get("unit"), 
#                 sr.get("costprice", 0), 
#                 sr.get("rate", 0), 
#                 sr.get("new_uom")
#             ))
#             sub_recipes_inserted += 1

#         mydb.commit()
        
#         # ------------------------
#         # Prepare response
#         # ------------------------
#         response = {
#             "message": "Recipe created successfully",
#             "recipe_id": new_recipe_id,
#             "recipe_name": name,
#             "outlet": outlet,
#             "items_inserted": items_inserted,
#             "total_items_received": len(items),
#             "sub_recipes_inserted": sub_recipes_inserted,
#             "total_sub_recipes_received": len(sub_recipes)
#         }
        
#         # Add warnings if there were skipped items
#         if skipped_items:
#             response["warning"] = f"{len(skipped_items)} item(s) were skipped due to validation errors"
#             response["skipped_items"] = skipped_items
        
#         if skipped_sub_recipes:
#             response["warning_sub_recipes"] = f"{len(skipped_sub_recipes)} sub-recipe(s) were skipped due to validation errors"
#             response["skipped_sub_recipes"] = skipped_sub_recipes
        
#         if missing_sub_recipes:
#             response["warning_missing_sub_recipes"] = f"{len(missing_sub_recipes)} sub-recipe(s) were not found in database"
#             response["missing_sub_recipes"] = missing_sub_recipes
        
#         cursor.close()
#         mydb.close()
        
#         # Check if any items or sub-recipes were actually inserted
#         if items_inserted == 0 and sub_recipes_inserted == 0:
#             response["warning"] = "Recipe created but no items or sub-recipes were added. Please add valid items or sub-recipes."
        
#         return jsonify(response), 201

#     except Exception as e:
#         if mydb:
#             mydb.rollback()
#         return jsonify({"error": str(e)}), 400


@app_file108.route("/recipe-by-name", methods=["POST"])
@cross_origin()
def create_recipe_by_name():
    try:
        data = request.get_json()
        token = data.get("token")
        if not token or not token_auth(token):
            return jsonify({"error": "Invalid or missing token."}), 400

        name = data.get("name")
        outlet = data.get("outlet")
        cost_price = data.get("cost_price")
        selling_price = data.get("selling_price")
        cost_percent = data.get("cost_percent")
        item_type = data.get("item_type")
        items = data.get("items", [])
        sub_recipes = data.get("sub_recipes", [])

        if (
            not name or
            not outlet or
            cost_price is None or
            selling_price is None or
            cost_percent is None or
            not item_type
        ):
            return jsonify({"error": "Missing required fields: name, outlet, cost_price, selling_price, cost_percent, item_type"}), 400
        
        if not isinstance(items, list):
            return jsonify({"error": "Items must be a list"}), 400
        
        if not isinstance(sub_recipes, list):
            return jsonify({"error": "Sub-recipes must be a list"}), 400

        mydb = get_db_connection()
        cursor = mydb.cursor(dictionary=True)

        # Helper function to normalize unit names
        def normalize_unit(unit):
            if not unit:
                return None
            unit_lower = str(unit).lower().strip()
            # Gram variants
            if unit_lower in ['g', 'gm', 'gram', 'grams', 'grm', 'grms', 'gs']:
                return 'g'
            # Kilogram variants
            elif unit_lower in ['kg', 'kgs', 'kilogram', 'kilograms', 'kilo']:
                return 'kg'
            # Millilitre variants
            elif unit_lower in ['ml', 'milliliter', 'millilitre', 'mls']:
                return 'ml'
            # Litre variants
            elif unit_lower in ['l', 'lt', 'ltr', 'liter', 'litre', 'ltrs']:
                return 'l'
            # Unit/piece variants
            elif unit_lower in ['unit', 'units', 'pcs', 'pc', 'piece', 'pieces', 'nos', 'no', 'pkt', 'pkts', 'jar', 'btl', 'bottle']:
                return 'unit'
            else:
                return unit_lower

        def calculate_converted_quantity(quantity, from_unit, to_unit, unit_value=1):
            """
            Convert quantity from from_unit to to_unit
            quantity: amount in from_unit
            from_unit: unit to convert from (user's entered unit - new_uom)
            to_unit: unit to convert to (system base unit - uom)
            unit_value: conversion factor (e.g., 1000 for g to kg, or grams per packet)
            """
            if not quantity:
                return 0
            
            try:
                qty = float(quantity)
                from_norm = normalize_unit(from_unit)
                to_norm = normalize_unit(to_unit)
                
                # If same unit, no conversion needed
                if from_norm == to_norm:
                    return qty
                
                # Handle Unit/Piece conversions (including Pkt, Jar, Btl, etc.)
                if from_norm == 'unit' or to_norm == 'unit':
                    if unit_value and unit_value != 0:
                        if from_norm == 'unit' and to_norm != 'unit':
                            # Converting from unit (e.g., Pkt) to weight/volume (e.g., Grms)
                            return qty * float(unit_value)
                        elif from_norm != 'unit' and to_norm == 'unit':
                            # Converting from weight/volume (e.g., Grms) to unit (e.g., Pkt)
                            return qty / float(unit_value)
                        else:
                            return qty
                
                # Weight conversions (g <-> kg)
                if from_norm == 'g' and to_norm == 'kg':
                    return qty / 1000
                elif from_norm == 'kg' and to_norm == 'g':
                    return qty * 1000
                
                # Volume conversions (ml <-> l)
                elif from_norm == 'ml' and to_norm == 'l':
                    return qty / 1000
                elif from_norm == 'l' and to_norm == 'ml':
                    return qty * 1000
                
                # If no conversion rule, return original
                return qty
                
            except Exception as e:
                print(f"Conversion error: {e}")
                return quantity

        # ------------------------
        # Validate sub-recipes and skip invalid ones
        # ------------------------
        missing_sub_recipes = []
        valid_sub_recipes = []
        skipped_sub_recipes = []
        
        for idx, sr in enumerate(sub_recipes):
            sub_recipe_name = sr.get("sub_recipe_name")
            
            if not sub_recipe_name:
                skipped_sub_recipes.append({
                    "index": idx,
                    "error": "Missing sub_recipe_name",
                    "data": sr
                })
                continue
                
            cursor.execute(
                "SELECT id, name, costprice FROM sub_recipe WHERE name = %s and outlet=%s",
                (sub_recipe_name, outlet,)
            )
            sub_recipe = cursor.fetchone()
            
            if not sub_recipe:
                missing_sub_recipes.append({
                    "index": idx,
                    "sub_recipe_name": sub_recipe_name,
                    "error": "Sub-recipe not found in database"
                })
            else:
                # Validate required fields for sub-recipe
                quantity = sr.get("quantity")
                uom = sr.get("uom")           # Base unit
                unit = sr.get("unit")
                costprice = sr.get("costprice")
                rate = sr.get("rate")
                new_uom = sr.get("new_uom")   # User's entered unit
                
                if quantity is None or uom is None or unit is None:
                    skipped_sub_recipes.append({
                        "index": idx,
                        "sub_recipe_name": sub_recipe_name,
                        "error": "Missing required fields: quantity, uom, or unit",
                        "data": sr
                    })
                    continue
                
                # Calculate converted quantity for sub-recipe
                if new_uom and uom:
                    converted_quantity = calculate_converted_quantity(
                        quantity,      # User's quantity
                        new_uom,       # FROM: user's unit
                        uom,           # TO: base unit
                        unit           # Conversion factor
                    )
                else:
                    converted_quantity = quantity
                
                valid_sub_recipes.append({
                    **sr,
                    "sub_recipe_id": sub_recipe["id"],
                    "sub_recipe_costprice": sub_recipe["costprice"],
                    "converted_quantity": converted_quantity  # Store converted quantity
                })
        
        # ------------------------
        # Check if recipe already exists
        # ------------------------
        cursor.execute(
            "SELECT id FROM recipe WHERE name = %s AND outlet = %s",
            (name, outlet)
        )
        existing_recipe = cursor.fetchone()

        if existing_recipe:
            recipe_id_to_delete = existing_recipe["id"]
            cursor.execute("DELETE FROM recipe_items WHERE recipe_id = %s", (recipe_id_to_delete,))
            cursor.execute("DELETE FROM recipe_subrecipes WHERE recipe_id = %s", (recipe_id_to_delete,))
            cursor.execute("DELETE FROM recipe WHERE id = %s", (recipe_id_to_delete,))
            mydb.commit()

        # ------------------------
        # Insert new recipe
        # ------------------------
        cursor.execute(
            """
            INSERT INTO recipe (name, outlet, costprice, sellingprice, cost_percent, ItemType)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (name, outlet, cost_price, selling_price, cost_percent, item_type)
        )
        new_recipe_id = cursor.lastrowid

        # ------------------------
        # Insert recipe items with conversion
        # ------------------------
        valid_items = []
        skipped_items = []
        
        for idx, item in enumerate(items):
            item_name = item.get("name")
            rate = item.get("rate")
            uom = item.get("uom")           # Base unit (e.g., "Kg", "Pkt")
            new_uom = item.get("new_uom")   # User's entered unit (e.g., "Grms")
            quantity = item.get("quantity") # Quantity in user's unit
            cost = item.get("cost")
            unit = item.get("unit", 1)      # Conversion factor
            
            # Check for missing or empty item name
            if not item_name or str(item_name).strip() == "":
                skipped_items.append({
                    "index": idx,
                    "error": "Item name is missing or empty",
                    "item_data": item
                })
                continue
            
            # Check other required fields
            missing_fields = []
            if rate is None:
                missing_fields.append("rate")
            if uom is None or str(uom).strip() == "":
                missing_fields.append("uom")
            if quantity is None:
                missing_fields.append("quantity")
            if cost is None:
                missing_fields.append("cost")
            
            if missing_fields:
                skipped_items.append({
                    "index": idx,
                    "item_name": item_name,
                    "missing_fields": missing_fields,
                    "error": f"Missing required fields: {', '.join(missing_fields)}"
                })
                continue
            
            # Validate numeric values
            try:
                rate = float(rate)
                quantity = float(quantity)
                cost = float(cost)
                unit = float(unit)
                
                if rate <= 0:
                    skipped_items.append({
                        "index": idx,
                        "item_name": item_name,
                        "error": "Rate must be greater than 0"
                    })
                    continue
                    
                if quantity <= 0:
                    skipped_items.append({
                        "index": idx,
                        "item_name": item_name,
                        "error": "Quantity must be greater than 0"
                    })
                    continue
                    
                if cost <= 0:
                    skipped_items.append({
                        "index": idx,
                        "item_name": item_name,
                        "error": "Cost must be greater than 0"
                    })
                    continue
                    
                if unit <= 0:
                    skipped_items.append({
                        "index": idx,
                        "item_name": item_name,
                        "error": "Unit must be greater than 0"
                    })
                    continue
                    
            except (ValueError, TypeError):
                skipped_items.append({
                    "index": idx,
                    "item_name": item_name,
                    "error": "Invalid numeric value for rate, quantity, cost, or unit"
                })
                continue
            
            # Calculate converted quantity - CONVERT FROM new_uom TO uom
            if new_uom and uom:
                converted_quantity = calculate_converted_quantity(
                    quantity,      # User's quantity
                    new_uom,       # FROM: user's unit
                    uom,           # TO: base unit
                    unit           # Conversion factor
                )
            else:
                converted_quantity = quantity
            
            # Debug print
            print(f"Item: {item_name}")
            print(f"  User entered: {quantity} {new_uom}")
            print(f"  Base unit: {uom}, unit_value: {unit}")
            print(f"  Converted quantity: {converted_quantity} {uom}")
            
            # All validations passed
            valid_items.append({
                "name": item_name,
                "rate": rate,
                "uom": uom,                 # Store base unit
                "new_uom": new_uom,         # Store user's unit
                "quantity": converted_quantity,  # Store converted quantity
                "cost": cost,
                "unit": unit
            })
        
        # Insert valid items
        items_inserted = 0
        for item in valid_items:
            cursor.execute("""
                INSERT INTO recipe_items (recipe_id, name, rate, uom, new_uom, unit, quantity, cost)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                new_recipe_id, 
                item["name"], 
                item["rate"], 
                item["uom"],      # Base unit
                item["new_uom"],  # User's unit
                item["unit"], 
                item["quantity"], # Converted quantity
                item["cost"]
            ))
            items_inserted += 1

        # ------------------------
        # Insert sub-recipes with conversion
        # ------------------------
        sub_recipes_inserted = 0
        for sr in valid_sub_recipes:
            cursor.execute("""
                INSERT INTO recipe_subrecipes (recipe_id, sub_recipe_id, quantity, uom, unit, costprice, rate, new_uom)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                new_recipe_id, 
                sr["sub_recipe_id"], 
                sr["converted_quantity"],  # Store converted quantity
                sr.get("uom"),             # Base unit
                sr.get("unit"), 
                sr.get("costprice", 0), 
                sr.get("rate", 0), 
                sr.get("new_uom")          # User's unit
            ))
            sub_recipes_inserted += 1

        mydb.commit()
        
        # ------------------------
        # Prepare response
        # ------------------------
        response = {
            "message": "Recipe created successfully",
            "recipe_id": new_recipe_id,
            "recipe_name": name,
            "outlet": outlet,
            "items_inserted": items_inserted,
            "total_items_received": len(items),
            "sub_recipes_inserted": sub_recipes_inserted,
            "total_sub_recipes_received": len(sub_recipes)
        }
        
        # Add conversion details for debugging
        if items_inserted > 0:
            response["items_conversion_summary"] = []
            for item in valid_items:
                response["items_conversion_summary"].append({
                    "name": item["name"],
                    "user_entered": f"{item['new_uom']} {item['quantity'] if item['new_uom'] else 'N/A'}",
                    "stored_as": f"{item['uom']} {item['quantity']}",
                    "conversion_factor": item["unit"]
                })
        
        # Add warnings if there were skipped items
        if skipped_items:
            response["warning"] = f"{len(skipped_items)} item(s) were skipped due to validation errors"
            response["skipped_items"] = skipped_items
        
        if skipped_sub_recipes:
            response["warning_sub_recipes"] = f"{len(skipped_sub_recipes)} sub-recipe(s) were skipped due to validation errors"
            response["skipped_sub_recipes"] = skipped_sub_recipes
        
        if missing_sub_recipes:
            response["warning_missing_sub_recipes"] = f"{len(missing_sub_recipes)} sub-recipe(s) were not found in database"
            response["missing_sub_recipes"] = missing_sub_recipes
        
        cursor.close()
        mydb.close()
        
        # Check if any items or sub-recipes were actually inserted
        if items_inserted == 0 and sub_recipes_inserted == 0:
            response["warning"] = "Recipe created but no items or sub-recipes were added. Please add valid items or sub-recipes."
        
        return jsonify(response), 201

    except Exception as e:
        if 'mydb' in locals() and mydb:
            mydb.rollback()
        return jsonify({"error": str(e)}), 400
    
# @app_file108.route("/recipes/bulk", methods=["POST"])
# @cross_origin()
# def create_bulk_recipes():
#     try:
#         data = request.get_json()
#         token = data.get("token")
#         if not token or not token_auth(token):
#             return jsonify({"error": "Invalid or missing token."}), 400

#         recipes = data.get("recipes_bulk", [])
        
#         if not isinstance(recipes, list) or len(recipes) == 0:
#             return jsonify({"error": "recipes must be a non-empty list"}), 400

#         mydb = get_db_connection()
#         cursor = mydb.cursor(dictionary=True)
        
#         created_recipes = []
        
#         try:
#             # First, validate all recipes and collect sub-recipe names
#             all_sub_recipe_names = set()
#             recipe_validation_errors = []
            
#             for idx, recipe_data in enumerate(recipes):
#                 name = recipe_data.get("name")
#                 outlet = recipe_data.get("outlet")
#                 cost_price = recipe_data.get("cost_price")
#                 selling_price = recipe_data.get("selling_price")
#                 cost_percent = recipe_data.get("cost_percent")
#                 item_type = recipe_data.get("item_type")
#                 items = recipe_data.get("bulk_recipe_items", [])
#                 sub_recipes = recipe_data.get("bulk_sub_recipes", [])

#                 if (
#                     not name or
#                     not outlet or
#                     cost_price is None or
#                     selling_price is None or
#                     cost_percent is None or
#                     not item_type or
#                     not isinstance(items, list) or
#                     not isinstance(sub_recipes, list)
#                 ):
#                     recipe_validation_errors.append({
#                         "index": idx,
#                         "recipe_name": name if name else "Unknown",
#                         "error": "Missing required fields or invalid format"
#                     })
#                     continue

#                 # Collect all sub-recipe names for validation
#                 for sr in sub_recipes:
#                     sub_recipe_name = sr.get("sub_recipe_name")
#                     if sub_recipe_name:
#                         all_sub_recipe_names.add(sub_recipe_name)
            
#             if recipe_validation_errors:
#                 return jsonify({
#                     "error": "Validation failed for some recipes",
#                     "validation_errors": recipe_validation_errors
#                 }), 400
            
#             # Validate all sub-recipe names exist
#             if all_sub_recipe_names:
#                 placeholders = ','.join(['%s'] * len(all_sub_recipe_names))
#                 cursor.execute(
#                     f"SELECT id, name FROM sub_recipe WHERE name IN ({placeholders})",
#                     tuple(all_sub_recipe_names)
#                 )
#                 existing_sub_recipes = cursor.fetchall()
#                 existing_names = {sr['name']: sr['id'] for sr in existing_sub_recipes}
                
#                 missing_sub_recipes = all_sub_recipe_names - set(existing_names.keys())
                
#                 if missing_sub_recipes:
#                     return jsonify({
#                         "error": "Some sub-recipes not found",
#                         "missing_sub_recipes": list(missing_sub_recipes)
#                     }), 400
            
#             # Process all recipes
#             for idx, recipe_data in enumerate(recipes):
#                 name = recipe_data.get("name")
#                 outlet = recipe_data.get("outlet")
#                 cost_price = recipe_data.get("cost_price")
#                 selling_price = recipe_data.get("selling_price")
#                 cost_percent = recipe_data.get("cost_percent")
#                 item_type = recipe_data.get("item_type")
#                 items = recipe_data.get("bulk_recipe_items", [])
#                 sub_recipes = recipe_data.get("bulk_sub_recipes", [])

#                 # Check if recipe already exists and delete if needed
#                 cursor.execute(
#                     "SELECT id FROM recipe WHERE name = %s AND outlet = %s",
#                     (name, outlet)
#                 )
#                 existing_recipe = cursor.fetchone()

#                 if existing_recipe:
#                     recipe_id_to_delete = existing_recipe["id"]
#                     cursor.execute("DELETE FROM recipe_items WHERE recipe_id = %s", (recipe_id_to_delete,))
#                     cursor.execute("DELETE FROM recipe_subrecipes WHERE recipe_id = %s", (recipe_id_to_delete,))
#                     cursor.execute("DELETE FROM recipe WHERE id = %s", (recipe_id_to_delete,))

#                 # Insert new recipe
#                 cursor.execute(
#                     """
#                     INSERT INTO recipe (name, outlet, costprice, sellingprice, cost_percent, ItemType)
#                     VALUES (%s, %s, %s, %s, %s, %s)
#                     """,
#                     (name, outlet, cost_price, selling_price, cost_percent, item_type)
#                 )
#                 new_recipe_id = cursor.lastrowid

#                 # Insert recipe items
#                 items_inserted = 0
#                 for item in items:
#                     item_name = item.get("name")
#                     rate = item.get("rate")
#                     uom = item.get("uom")
#                     new_uom = item.get("new_uom")
#                     quantity = item.get("quantity")
#                     cost = item.get("cost")
#                     unit = item.get("unit", 1)

#                     if not all([item_name, rate, uom, quantity, cost]):
#                         continue

#                     cursor.execute("""
#                         INSERT INTO recipe_items (recipe_id, name, rate, uom, new_uom, unit, quantity, cost)
#                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
#                     """, (new_recipe_id, item_name, rate, uom, new_uom, unit, quantity, cost))
#                     items_inserted += 1

#                 # Insert sub-recipes
#                 sub_recipes_inserted = 0
#                 for sr in sub_recipes:
#                     sub_recipe_name = sr.get("sub_recipe_name")
#                     if not sub_recipe_name:
#                         continue
                        
#                     sub_recipe_id = existing_names.get(sub_recipe_name)
#                     if not sub_recipe_id:
#                         continue

#                     cursor.execute("""
#                         INSERT INTO recipe_subrecipes (recipe_id, sub_recipe_id, quantity, uom, unit, costprice, rate, new_uom)
#                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
#                     """, (
#                         new_recipe_id, 
#                         sub_recipe_id, 
#                         sr.get("quantity", 0), 
#                         sr.get("uom"), 
#                         sr.get("unit"), 
#                         sr.get("costprice"), 
#                         sr.get("rate"), 
#                         sr.get("new_uom")
#                     ))
#                     sub_recipes_inserted += 1

#                 created_recipes.append({
#                     "index": idx,
#                     "recipe_id": new_recipe_id,
#                     "name": name,
#                     "outlet": outlet,
#                     "items_count": items_inserted,
#                     "sub_recipes_count": sub_recipes_inserted
#                 })

#             # Commit all changes
#             mydb.commit()
            
#         except Exception as e:
#             # Rollback if any error occurs
#             mydb.rollback()
#             return jsonify({
#                 "error": "Bulk creation failed",
#                 "details": str(e),
#                 "recipes_attempted": len(recipes)
#             }), 400
        
#         finally:
#             cursor.close()
#             mydb.close()

#         return jsonify({
#             "message": f"Successfully created {len(created_recipes)} recipes",
#             "created_recipes": created_recipes,
#             "total": len(created_recipes)
#         }), 201

#     except Exception as e:
#         return jsonify({"error": str(e)}), 400


# @app_file108.route("/recipes/bulk", methods=["POST"])
# @cross_origin()
# def create_bulk_recipes():
#     try:
#         data = request.get_json()
#         token = data.get("token")

#         if not token or not token_auth(token):
#             return jsonify({"error": "Invalid or missing token."}), 400

#         recipes = data.get("recipes_bulk", [])

#         if not isinstance(recipes, list) or len(recipes) == 0:
#             return jsonify({"error": "recipes must be a non-empty list"}), 400

#         mydb = get_db_connection()
#         cursor = mydb.cursor(dictionary=True)

#         created_recipes = []
#         duplicate_errors = []   # 🔥 track duplicates
#         validation_errors = []

#         try:
#             # ---------------- VALIDATION ---------------- #
#             all_sub_recipe_names = set()

#             for idx, recipe_data in enumerate(recipes):
#                 name = recipe_data.get("name")
#                 outlet = recipe_data.get("outlet")
#                 cost_price = recipe_data.get("cost_price")
#                 selling_price = recipe_data.get("selling_price")
#                 cost_percent = recipe_data.get("cost_percent")
#                 item_type = recipe_data.get("item_type")
#                 items = recipe_data.get("bulk_recipe_items", [])
#                 sub_recipes = recipe_data.get("bulk_sub_recipes", [])

#                 if (
#                     not name or
#                     not outlet or
#                     cost_price is None or
#                     selling_price is None or
#                     cost_percent is None or
#                     not item_type or
#                     not isinstance(items, list) or
#                     not isinstance(sub_recipes, list)
#                 ):
#                     validation_errors.append({
#                         "index": idx,
#                         "recipe_name": name if name else "Unknown",
#                         "error": "Missing required fields"
#                     })
#                     continue

#                 for sr in sub_recipes:
#                     sub_recipe_name = sr.get("sub_recipe_name")
#                     if sub_recipe_name:
#                         all_sub_recipe_names.add(sub_recipe_name)

#             if validation_errors:
#                 return jsonify({
#                     "error": "Validation failed",
#                     "validation_errors": validation_errors
#                 }), 400

#             # -------- VALIDATE SUB RECIPES EXIST -------- #
#             existing_names = {}
#             if all_sub_recipe_names:
#                 placeholders = ','.join(['%s'] * len(all_sub_recipe_names))
#                 cursor.execute(
#                     f"SELECT id, name FROM sub_recipe WHERE name IN ({placeholders})",
#                     tuple(all_sub_recipe_names)
#                 )
#                 existing = cursor.fetchall()
#                 existing_names = {sr['name']: sr['id'] for sr in existing}

#                 missing = all_sub_recipe_names - set(existing_names.keys())
#                 if missing:
#                     return jsonify({
#                         "error": "Missing sub recipes",
#                         "missing_sub_recipes": list(missing)
#                     }), 400

#             # ---------------- PROCESS ---------------- #
#             for idx, recipe_data in enumerate(recipes):
#                 name = recipe_data.get("name")
#                 outlet = recipe_data.get("outlet")
#                 cost_price = recipe_data.get("cost_price")
#                 selling_price = recipe_data.get("selling_price")
#                 cost_percent = recipe_data.get("cost_percent")
#                 item_type = recipe_data.get("item_type")
#                 items = recipe_data.get("bulk_recipe_items", [])
#                 sub_recipes = recipe_data.get("bulk_sub_recipes", [])

#                 # Delete existing recipe
#                 cursor.execute(
#                     "SELECT id FROM recipe WHERE name = %s AND outlet = %s",
#                     (name, outlet)
#                 )
#                 existing_recipe = cursor.fetchone()

#                 if existing_recipe:
#                     rid = existing_recipe["id"]
#                     cursor.execute("DELETE FROM recipe_items WHERE recipe_id = %s", (rid,))
#                     cursor.execute("DELETE FROM recipe_subrecipes WHERE recipe_id = %s", (rid,))
#                     cursor.execute("DELETE FROM recipe WHERE id = %s", (rid,))

#                 # Insert recipe
#                 cursor.execute("""
#                     INSERT INTO recipe 
#                     (name, outlet, costprice, sellingprice, cost_percent, ItemType)
#                     VALUES (%s, %s, %s, %s, %s, %s)
#                 """, (name, outlet, cost_price, selling_price, cost_percent, item_type))

#                 new_recipe_id = cursor.lastrowid

#                 # -------- INSERT ITEMS -------- #
#                 items_inserted = 0
#                 for item in items:
#                     if not all([
#                         item.get("name"),
#                         item.get("rate"),
#                         item.get("uom"),
#                         item.get("quantity"),
#                         item.get("cost")
#                     ]):
#                         continue

#                     cursor.execute("""
#                         INSERT INTO recipe_items 
#                         (recipe_id, name, rate, uom, new_uom, unit, quantity, cost)
#                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
#                     """, (
#                         new_recipe_id,
#                         item.get("name"),
#                         item.get("rate"),
#                         item.get("uom"),
#                         item.get("new_uom"),
#                         item.get("unit", 1),
#                         item.get("quantity"),
#                         item.get("cost")
#                     ))
#                     items_inserted += 1

#                 # -------- INSERT SUB RECIPES -------- #
#                 sub_recipes_inserted = 0
#                 seen_subrecipes = set()   # 🔥 detect duplicates before DB

#                 for sr in sub_recipes:
#                     sub_recipe_name = sr.get("sub_recipe_name")
#                     if not sub_recipe_name:
#                         continue

#                     sub_recipe_id = existing_names.get(sub_recipe_name)
#                     if not sub_recipe_id:
#                         continue

#                     key = (new_recipe_id, sub_recipe_id)

#                     # 🔥 Pre-check duplicate
#                     if key in seen_subrecipes:
#                         duplicate_errors.append({
#                             "recipe_name": name,
#                             "recipe_id": new_recipe_id,
#                             "sub_recipe_name": sub_recipe_name,
#                             "reason": "Duplicate in input"
#                         })
#                         continue

#                     seen_subrecipes.add(key)

#                     try:
#                         cursor.execute("""
#                             INSERT INTO recipe_subrecipes 
#                             (recipe_id, sub_recipe_id, quantity, uom, unit, costprice, rate, new_uom)
#                             VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
#                         """, (
#                             new_recipe_id,
#                             sub_recipe_id,
#                             sr.get("quantity", 0),
#                             sr.get("uom"),
#                             sr.get("unit"),
#                             sr.get("costprice"),
#                             sr.get("rate"),
#                             sr.get("new_uom")
#                         ))

#                         sub_recipes_inserted += 1

#                     except mysql.connector.Error as err:
#                         if err.errno == 1062:
#                             duplicate_errors.append({
#                                 "recipe_name": name,
#                                 "recipe_id": new_recipe_id,
#                                 "sub_recipe_name": sub_recipe_name,
#                                 "sub_recipe_id": sub_recipe_id,
#                                 "error": str(err)
#                             })
#                         else:
#                             raise err

#                 created_recipes.append({
#                     "index": idx,
#                     "recipe_id": new_recipe_id,
#                     "name": name,
#                     "items_count": items_inserted,
#                     "sub_recipes_count": sub_recipes_inserted
#                 })

#             mydb.commit()

#         except Exception as e:
#             mydb.rollback()
#             return jsonify({
#                 "error": "Bulk creation failed",
#                 "details": str(e)
#             }), 400

#         finally:
#             cursor.close()
#             mydb.close()

#         return jsonify({
#             "message": f"{len(created_recipes)} recipes processed",
#             "created_recipes": created_recipes,
#             "duplicate_issues": duplicate_errors,   # 🔥 key output
#             "total": len(created_recipes)
#         }), 201

#     except Exception as e:
#         return jsonify({"error": str(e)}), 400


# @app_file108.route("/recipes/bulk", methods=["POST"])
# @cross_origin()
# def create_bulk_recipes():
#     try:
#         data = request.get_json()
#         token = data.get("token")

#         if not token or not token_auth(token):
#             return jsonify({"error": "Invalid or missing token."}), 400

#         recipes = data.get("recipes_bulk", [])

#         if not isinstance(recipes, list) or len(recipes) == 0:
#             return jsonify({"error": "recipes must be a non-empty list"}), 400

#         mydb = get_db_connection()
#         cursor = mydb.cursor(dictionary=True)

#         created_recipes = []
#         duplicate_errors = []
#         validation_errors = []
#         missing_sub_recipes = []

#         try:
#             # ---------------- COLLECT ALL SUB-RECIPES WITH OUTLET ---------------- #
#             sub_recipe_lookup = {}  # Will store {(name, outlet): id}
#             all_sub_recipe_keys = set()

#             for idx, recipe_data in enumerate(recipes):
#                 name = recipe_data.get("name")
#                 outlet = recipe_data.get("outlet")
#                 cost_price = recipe_data.get("cost_price")
#                 selling_price = recipe_data.get("selling_price")
#                 cost_percent = recipe_data.get("cost_percent")
#                 item_type = recipe_data.get("item_type")
#                 items = recipe_data.get("bulk_recipe_items", [])
#                 sub_recipes = recipe_data.get("bulk_sub_recipes", [])

#                 if (
#                     not name or
#                     not outlet or
#                     cost_price is None or
#                     selling_price is None or
#                     cost_percent is None or
#                     not item_type or
#                     not isinstance(items, list) or
#                     not isinstance(sub_recipes, list)
#                 ):
#                     validation_errors.append({
#                         "index": idx,
#                         "recipe_name": name if name else "Unknown",
#                         "error": "Missing required fields"
#                     })
#                     continue

#                 # Collect sub-recipe names with their outlet
#                 for sr in sub_recipes:
#                     sub_recipe_name = sr.get("sub_recipe_name")
#                     if sub_recipe_name:
#                         # Use the recipe's outlet for the sub-recipe lookup
#                         all_sub_recipe_keys.add((sub_recipe_name, outlet))

#             if validation_errors:
#                 return jsonify({
#                     "error": "Validation failed",
#                     "validation_errors": validation_errors
#                 }), 400

#             # -------- VALIDATE SUB RECIPES EXIST FOR SPECIFIC OUTLET -------- #
#             if all_sub_recipe_keys:
#                 # Build query to fetch sub-recipes by name AND outlet
#                 placeholders = ','.join(['%s'] * len(all_sub_recipe_keys))
#                 # Create a query that matches (name, outlet) pairs
#                 query = """
#                     SELECT id, name, outlet 
#                     FROM sub_recipe 
#                     WHERE (name, outlet) IN (
#                         SELECT name, outlet FROM (
#                             SELECT %s as name, %s as outlet 
#                             UNION ALL 
#                     """
#                 # This approach is simpler: fetch all possible matches and filter in Python
#                 # Let me use a simpler approach:
                
#                 names = list(set([key[0] for key in all_sub_recipe_keys]))
#                 outlets = list(set([key[1] for key in all_sub_recipe_keys]))
                
#                 name_placeholders = ','.join(['%s'] * len(names))
#                 outlet_placeholders = ','.join(['%s'] * len(outlets))
                
#                 cursor.execute(f"""
#                     SELECT id, name, outlet 
#                     FROM sub_recipe 
#                     WHERE name IN ({name_placeholders})
#                 """, tuple(names))
                
#                 existing_sub_recipes = cursor.fetchall()
                
#                 # Create lookup dictionary with (name, outlet) as key
#                 for sr in existing_sub_recipes:
#                     sub_recipe_lookup[(sr['name'], sr['outlet'])] = sr['id']
                
#                 # Check for missing sub-recipes
#                 for sub_recipe_name, outlet_name in all_sub_recipe_keys:
#                     if (sub_recipe_name, outlet_name) not in sub_recipe_lookup:
#                         missing_sub_recipes.append({
#                             "sub_recipe_name": sub_recipe_name,
#                             "outlet": outlet_name,
#                             "error": f"Sub-recipe '{sub_recipe_name}' not found for outlet '{outlet_name}'"
#                         })
                
#                 if missing_sub_recipes:
#                     return jsonify({
#                         "error": "Missing sub-recipes for specified outlets",
#                         "missing_sub_recipes": missing_sub_recipes
#                     }), 400

#             # ---------------- PROCESS EACH RECIPE ---------------- #
#             for idx, recipe_data in enumerate(recipes):
#                 name = recipe_data.get("name")
#                 outlet = recipe_data.get("outlet")
#                 cost_price = recipe_data.get("cost_price")
#                 selling_price = recipe_data.get("selling_price")
#                 cost_percent = recipe_data.get("cost_percent")
#                 item_type = recipe_data.get("item_type")
#                 items = recipe_data.get("bulk_recipe_items", [])
#                 sub_recipes = recipe_data.get("bulk_sub_recipes", [])

#                 # Skip if already failed validation
#                 if any(ve.get("index") == idx for ve in validation_errors):
#                     continue

#                 # Delete existing recipe
#                 cursor.execute(
#                     "SELECT id FROM recipe WHERE name = %s AND outlet = %s",
#                     (name, outlet)
#                 )
#                 existing_recipe = cursor.fetchone()

#                 if existing_recipe:
#                     rid = existing_recipe["id"]
#                     cursor.execute("DELETE FROM recipe_items WHERE recipe_id = %s", (rid,))
#                     cursor.execute("DELETE FROM recipe_subrecipes WHERE recipe_id = %s", (rid,))
#                     cursor.execute("DELETE FROM recipe WHERE id = %s", (rid,))

#                 # Insert recipe
#                 cursor.execute("""
#                     INSERT INTO recipe 
#                     (name, outlet, costprice, sellingprice, cost_percent, ItemType)
#                     VALUES (%s, %s, %s, %s, %s, %s)
#                 """, (name, outlet, cost_price, selling_price, cost_percent, item_type))

#                 new_recipe_id = cursor.lastrowid

#                 # -------- INSERT ITEMS -------- #
#                 items_inserted = 0
#                 skipped_items = []
                
#                 for item_idx, item in enumerate(items):
#                     if not all([
#                         item.get("name"),
#                         item.get("rate"),
#                         item.get("uom"),
#                         item.get("quantity"),
#                         item.get("cost")
#                     ]):
#                         skipped_items.append({
#                             "item_index": item_idx,
#                             "item_name": item.get("name", "Unknown"),
#                             "reason": "Missing required fields"
#                         })
#                         continue

#                     cursor.execute("""
#                         INSERT INTO recipe_items 
#                         (recipe_id, name, rate, uom, new_uom, unit, quantity, cost)
#                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
#                     """, (
#                         new_recipe_id,
#                         item.get("name"),
#                         item.get("rate"),
#                         item.get("uom"),
#                         item.get("new_uom"),
#                         item.get("unit", 1),
#                         item.get("quantity"),
#                         item.get("cost")
#                     ))
#                     items_inserted += 1

#                 # -------- INSERT SUB RECIPES (WITH OUTLET FILTER) -------- #
#                 sub_recipes_inserted = 0
#                 seen_subrecipes = set()
#                 skipped_sub_recipes = []

#                 for sr_idx, sr in enumerate(sub_recipes):
#                     sub_recipe_name = sr.get("sub_recipe_name")
#                     if not sub_recipe_name:
#                         skipped_sub_recipes.append({
#                             "sub_recipe_index": sr_idx,
#                             "reason": "Missing sub_recipe_name"
#                         })
#                         continue

#                     # Get sub_recipe_id using both name AND outlet
#                     sub_recipe_id = sub_recipe_lookup.get((sub_recipe_name, outlet))
                    
#                     if not sub_recipe_id:
#                         skipped_sub_recipes.append({
#                             "sub_recipe_index": sr_idx,
#                             "sub_recipe_name": sub_recipe_name,
#                             "outlet": outlet,
#                             "reason": f"Sub-recipe '{sub_recipe_name}' not found for outlet '{outlet}'"
#                         })
#                         continue

#                     key = (new_recipe_id, sub_recipe_id)

#                     # Check for duplicate in current recipe
#                     if key in seen_subrecipes:
#                         duplicate_errors.append({
#                             "recipe_name": name,
#                             "recipe_id": new_recipe_id,
#                             "sub_recipe_name": sub_recipe_name,
#                             "sub_recipe_outlet": outlet,
#                             "reason": "Duplicate sub-recipe in input"
#                         })
#                         continue

#                     seen_subrecipes.add(key)

#                     try:
#                         cursor.execute("""
#                             INSERT INTO recipe_subrecipes 
#                             (recipe_id, sub_recipe_id, quantity, uom, unit, costprice, rate, new_uom)
#                             VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
#                         """, (
#                             new_recipe_id,
#                             sub_recipe_id,
#                             sr.get("quantity", 0),
#                             sr.get("uom"),
#                             sr.get("unit"),
#                             sr.get("costprice"),
#                             sr.get("rate"),
#                             sr.get("new_uom")
#                         ))

#                         sub_recipes_inserted += 1

#                     except mysql.connector.Error as err:
#                         if err.errno == 1062:  # Duplicate entry error
#                             duplicate_errors.append({
#                                 "recipe_name": name,
#                                 "recipe_id": new_recipe_id,
#                                 "sub_recipe_name": sub_recipe_name,
#                                 "sub_recipe_id": sub_recipe_id,
#                                 "error": str(err)
#                             })
#                         else:
#                             raise err

#                 created_recipes.append({
#                     "index": idx,
#                     "recipe_id": new_recipe_id,
#                     "name": name,
#                     "outlet": outlet,
#                     "items_inserted": items_inserted,
#                     "items_skipped": len(skipped_items),
#                     "sub_recipes_inserted": sub_recipes_inserted,
#                     "sub_recipes_skipped": len(skipped_sub_recipes)
#                 })

#                 # Add warnings for this recipe if any items were skipped
#                 if skipped_items or skipped_sub_recipes:
#                     created_recipes[-1]["warnings"] = {}
#                     if skipped_items:
#                         created_recipes[-1]["warnings"]["skipped_items"] = skipped_items
#                     if skipped_sub_recipes:
#                         created_recipes[-1]["warnings"]["skipped_sub_recipes"] = skipped_sub_recipes

#             mydb.commit()

#         except Exception as e:
#             mydb.rollback()
#             return jsonify({
#                 "error": "Bulk creation failed",
#                 "details": str(e)
#             }), 400

#         finally:
#             cursor.close()
#             mydb.close()

#         response = {
#             "message": f"{len(created_recipes)} recipes processed successfully",
#             "created_recipes": created_recipes,
#             "total_processed": len(created_recipes)
#         }
        
#         if duplicate_errors:
#             response["warning"] = "Some duplicate sub-recipes were skipped"
#             response["duplicate_issues"] = duplicate_errors
        
#         return jsonify(response), 201

#     except Exception as e:
#         return jsonify({"error": str(e)}), 400


@app_file108.route("/recipes/bulk", methods=["POST"])
@cross_origin()
def create_bulk_recipes():
    try:
        data = request.get_json()
        token = data.get("token")

        if not token or not token_auth(token):
            return jsonify({"error": "Invalid or missing token."}), 400

        recipes = data.get("recipes_bulk", [])

        if not isinstance(recipes, list) or len(recipes) == 0:
            return jsonify({"error": "recipes must be a non-empty list"}), 400

        mydb = get_db_connection()
        cursor = mydb.cursor(dictionary=True)

        created_recipes = []
        duplicate_errors = []
        validation_errors = []
        missing_sub_recipes = []

        # Helper function to normalize unit names
        def normalize_unit(unit):
            if not unit:
                return None
            unit_lower = str(unit).lower().strip()
            # Gram variants
            if unit_lower in ['g', 'gm', 'gram', 'grams', 'grm', 'grms', 'gs']:
                return 'g'
            # Kilogram variants
            elif unit_lower in ['kg', 'kgs', 'kilogram', 'kilograms', 'kilo']:
                return 'kg'
            # Millilitre variants
            elif unit_lower in ['ml', 'milliliter', 'millilitre', 'mls']:
                return 'ml'
            # Litre variants
            elif unit_lower in ['l', 'lt', 'ltr', 'liter', 'litre', 'ltrs']:
                return 'l'
            # Unit/piece variants
            elif unit_lower in ['unit', 'units', 'pcs', 'pc', 'piece', 'pieces', 'nos', 'no', 'pkt', 'pkts', 'jar', 'btl', 'bottle']:
                return 'unit'
            else:
                return unit_lower

        def calculate_converted_quantity(quantity, from_unit, to_unit, unit_value=1):
            """
            Convert quantity from from_unit to to_unit
            quantity: amount in from_unit
            from_unit: unit to convert from (user's entered unit - new_uom)
            to_unit: unit to convert to (system base unit - uom)
            unit_value: conversion factor (e.g., 1000 for g to kg, or grams per packet)
            """
            if not quantity:
                return 0
            
            try:
                qty = float(quantity)
                from_norm = normalize_unit(from_unit)
                to_norm = normalize_unit(to_unit)
                
                # If same unit, no conversion needed
                if from_norm == to_norm:
                    return qty
                
                # Handle Unit/Piece conversions (including Pkt, Jar, Btl, etc.)
                if from_norm == 'unit' or to_norm == 'unit':
                    if unit_value and unit_value != 0:
                        if from_norm == 'unit' and to_norm != 'unit':
                            # Converting from unit (e.g., Pkt) to weight/volume (e.g., Grms)
                            return qty * float(unit_value)
                        elif from_norm != 'unit' and to_norm == 'unit':
                            # Converting from weight/volume (e.g., Grms) to unit (e.g., Pkt)
                            return qty / float(unit_value)
                        else:
                            return qty
                
                # Weight conversions (g <-> kg)
                if from_norm == 'g' and to_norm == 'kg':
                    return qty / 1000
                elif from_norm == 'kg' and to_norm == 'g':
                    return qty * 1000
                
                # Volume conversions (ml <-> l)
                elif from_norm == 'ml' and to_norm == 'l':
                    return qty / 1000
                elif from_norm == 'l' and to_norm == 'ml':
                    return qty * 1000
                
                # If no conversion rule, return original
                return qty
                
            except Exception as e:
                print(f"Conversion error: {e}")
                return quantity

        try:
            # ---------------- COLLECT ALL SUB-RECIPES WITH OUTLET ---------------- #
            sub_recipe_lookup = {}  # Will store {(name, outlet): id}
            all_sub_recipe_keys = set()

            for idx, recipe_data in enumerate(recipes):
                name = recipe_data.get("name")
                outlet = recipe_data.get("outlet")
                cost_price = recipe_data.get("cost_price")
                selling_price = recipe_data.get("selling_price")
                cost_percent = recipe_data.get("cost_percent")
                item_type = recipe_data.get("item_type")
                items = recipe_data.get("bulk_recipe_items", [])
                sub_recipes = recipe_data.get("bulk_sub_recipes", [])

                if (
                    not name or
                    not outlet or
                    cost_price is None or
                    selling_price is None or
                    cost_percent is None or
                    not item_type or
                    not isinstance(items, list) or
                    not isinstance(sub_recipes, list)
                ):
                    validation_errors.append({
                        "index": idx,
                        "recipe_name": name if name else "Unknown",
                        "error": "Missing required fields"
                    })
                    continue

                # Collect sub-recipe names with their outlet
                for sr in sub_recipes:
                    sub_recipe_name = sr.get("sub_recipe_name")
                    if sub_recipe_name:
                        all_sub_recipe_keys.add((sub_recipe_name, outlet))

            if validation_errors:
                return jsonify({
                    "error": "Validation failed",
                    "validation_errors": validation_errors
                }), 400

            # -------- VALIDATE SUB RECIPES EXIST FOR SPECIFIC OUTLET -------- #
            if all_sub_recipe_keys:
                names = list(set([key[0] for key in all_sub_recipe_keys]))
                
                name_placeholders = ','.join(['%s'] * len(names))
                
                cursor.execute(f"""
                    SELECT id, name, outlet 
                    FROM sub_recipe 
                    WHERE name IN ({name_placeholders})
                """, tuple(names))
                
                existing_sub_recipes = cursor.fetchall()
                
                # Create lookup dictionary with (name, outlet) as key
                for sr in existing_sub_recipes:
                    sub_recipe_lookup[(sr['name'], sr['outlet'])] = sr['id']
                
                # Check for missing sub-recipes
                for sub_recipe_name, outlet_name in all_sub_recipe_keys:
                    if (sub_recipe_name, outlet_name) not in sub_recipe_lookup:
                        missing_sub_recipes.append({
                            "sub_recipe_name": sub_recipe_name,
                            "outlet": outlet_name,
                            "error": f"Sub-recipe '{sub_recipe_name}' not found for outlet '{outlet_name}'"
                        })
                
                if missing_sub_recipes:
                    return jsonify({
                        "error": "Missing sub-recipes for specified outlets",
                        "missing_sub_recipes": missing_sub_recipes
                    }), 400

            # ---------------- PROCESS EACH RECIPE ---------------- #
            for idx, recipe_data in enumerate(recipes):
                name = recipe_data.get("name")
                outlet = recipe_data.get("outlet")
                cost_price = recipe_data.get("cost_price")
                selling_price = recipe_data.get("selling_price")
                cost_percent = recipe_data.get("cost_percent")
                item_type = recipe_data.get("item_type")
                items = recipe_data.get("bulk_recipe_items", [])
                sub_recipes = recipe_data.get("bulk_sub_recipes", [])

                # Skip if already failed validation
                if any(ve.get("index") == idx for ve in validation_errors):
                    continue

                # Delete existing recipe
                cursor.execute(
                    "SELECT id FROM recipe WHERE name = %s AND outlet = %s",
                    (name, outlet)
                )
                existing_recipe = cursor.fetchone()

                if existing_recipe:
                    rid = existing_recipe["id"]
                    cursor.execute("DELETE FROM recipe_items WHERE recipe_id = %s", (rid,))
                    cursor.execute("DELETE FROM recipe_subrecipes WHERE recipe_id = %s", (rid,))
                    cursor.execute("DELETE FROM recipe WHERE id = %s", (rid,))

                # Insert recipe
                cursor.execute("""
                    INSERT INTO recipe 
                    (name, outlet, costprice, sellingprice, cost_percent, ItemType)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (name, outlet, cost_price, selling_price, cost_percent, item_type))

                new_recipe_id = cursor.lastrowid

                # -------- INSERT ITEMS WITH QUANTITY CONVERSION -------- #
                items_inserted = 0
                skipped_items = []
                
                for item_idx, item in enumerate(items):
                    if not all([
                        item.get("name"),
                        item.get("rate"),
                        item.get("uom"),
                        item.get("quantity"),
                        item.get("cost")
                    ]):
                        skipped_items.append({
                            "item_index": item_idx,
                            "item_name": item.get("name", "Unknown"),
                            "reason": "Missing required fields"
                        })
                        continue

                    # Get the values
                    user_quantity = item.get("quantity")  # Quantity in user's unit
                    base_unit = item.get("uom")          # System base unit (e.g., "Kg", "Pkt")
                    user_unit = item.get("new_uom")      # User's entered unit (e.g., "Grms", "ml")
                    unit_value = item.get("unit", 1)     # Conversion factor
                    
                    # Calculate converted quantity - CONVERT FROM user_unit TO base_unit
                    if user_unit and base_unit:
                        converted_quantity = calculate_converted_quantity(
                            user_quantity,    # 300 (user entered 300 grams)
                            user_unit,        # "Grms" (user's unit)
                            base_unit,        # "Kg" or "Pkt" (system base unit)
                            unit_value        # 1000 or 1
                        )
                    else:
                        converted_quantity = user_quantity

                    # Debug print
                    print(f"Item: {item.get('name')}")
                    print(f"  User entered: {user_quantity} {user_unit}")
                    print(f"  Base unit: {base_unit}, unit_value: {unit_value}")
                    print(f"  Converted quantity: {converted_quantity} {base_unit}")
                    print(f"  Rate: {item.get('rate')}, Cost: {item.get('cost')}")

                    cursor.execute("""
                        INSERT INTO recipe_items 
                        (recipe_id, name, rate, uom, new_uom, unit, quantity, cost)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        new_recipe_id,
                        item.get("name"),
                        item.get("rate"),
                        base_unit,           # Store base unit as uom
                        user_unit,           # Store user's unit as new_uom
                        unit_value,
                        converted_quantity,  # Store converted quantity (in base unit)
                        item.get("cost")
                    ))
                    items_inserted += 1

                # -------- INSERT SUB RECIPES WITH QUANTITY CONVERSION -------- #
                sub_recipes_inserted = 0
                seen_subrecipes = set()
                skipped_sub_recipes = []

                for sr_idx, sr in enumerate(sub_recipes):
                    sub_recipe_name = sr.get("sub_recipe_name")
                    if not sub_recipe_name:
                        skipped_sub_recipes.append({
                            "sub_recipe_index": sr_idx,
                            "reason": "Missing sub_recipe_name"
                        })
                        continue

                    # Get sub_recipe_id using both name AND outlet
                    sub_recipe_id = sub_recipe_lookup.get((sub_recipe_name, outlet))
                    
                    if not sub_recipe_id:
                        skipped_sub_recipes.append({
                            "sub_recipe_index": sr_idx,
                            "sub_recipe_name": sub_recipe_name,
                            "outlet": outlet,
                            "reason": f"Sub-recipe '{sub_recipe_name}' not found for outlet '{outlet}'"
                        })
                        continue

                    key = (new_recipe_id, sub_recipe_id)

                    # Check for duplicate in current recipe
                    if key in seen_subrecipes:
                        duplicate_errors.append({
                            "recipe_name": name,
                            "recipe_id": new_recipe_id,
                            "sub_recipe_name": sub_recipe_name,
                            "sub_recipe_outlet": outlet,
                            "reason": "Duplicate sub-recipe in input"
                        })
                        continue

                    seen_subrecipes.add(key)

                    # Get sub-recipe values
                    user_quantity = sr.get("quantity", 0)
                    base_unit = sr.get("uom")           # System base unit for sub-recipe
                    user_unit = sr.get("new_uom")       # User's entered unit for sub-recipe
                    unit_value = sr.get("unit", 1)
                    
                    # Calculate converted quantity - CONVERT FROM user_unit TO base_unit
                    if user_unit and base_unit:
                        converted_quantity = calculate_converted_quantity(
                            user_quantity,
                            user_unit,      # FROM: user's unit
                            base_unit,      # TO: base unit
                            unit_value
                        )
                    else:
                        converted_quantity = user_quantity

                    # Debug print for sub-recipes
                    print(f"Sub-recipe: {sub_recipe_name}")
                    print(f"  User entered: {user_quantity} {user_unit}")
                    print(f"  Base unit: {base_unit}, unit_value: {unit_value}")
                    print(f"  Converted quantity: {converted_quantity} {base_unit}")

                    try:
                        cursor.execute("""
                            INSERT INTO recipe_subrecipes 
                            (recipe_id, sub_recipe_id, quantity, uom, unit, costprice, rate, new_uom)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            new_recipe_id,
                            sub_recipe_id,
                            converted_quantity,  # Store converted quantity (in base unit)
                            base_unit,           # Store base unit as uom
                            unit_value,
                            sr.get("costprice"),
                            sr.get("rate"),
                            user_unit            # Store user's unit as new_uom
                        ))

                        sub_recipes_inserted += 1

                    except mysql.connector.Error as err:
                        if err.errno == 1062:  # Duplicate entry error
                            duplicate_errors.append({
                                "recipe_name": name,
                                "recipe_id": new_recipe_id,
                                "sub_recipe_name": sub_recipe_name,
                                "sub_recipe_id": sub_recipe_id,
                                "error": str(err)
                            })
                        else:
                            raise err

                created_recipes.append({
                    "index": idx,
                    "recipe_id": new_recipe_id,
                    "name": name,
                    "outlet": outlet,
                    "items_inserted": items_inserted,
                    "items_skipped": len(skipped_items),
                    "sub_recipes_inserted": sub_recipes_inserted,
                    "sub_recipes_skipped": len(skipped_sub_recipes)
                })

                # Add warnings for this recipe if any items were skipped
                if skipped_items or skipped_sub_recipes:
                    created_recipes[-1]["warnings"] = {}
                    if skipped_items:
                        created_recipes[-1]["warnings"]["skipped_items"] = skipped_items
                    if skipped_sub_recipes:
                        created_recipes[-1]["warnings"]["skipped_sub_recipes"] = skipped_sub_recipes

            mydb.commit()

        except Exception as e:
            mydb.rollback()
            return jsonify({
                "error": "Bulk creation failed",
                "details": str(e)
            }), 400

        finally:
            cursor.close()
            mydb.close()

        response = {
            "message": f"{len(created_recipes)} recipes processed successfully",
            "created_recipes": created_recipes,
            "total_processed": len(created_recipes)
        }
        
        if duplicate_errors:
            response["warning"] = "Some duplicate sub-recipes were skipped"
            response["duplicate_issues"] = duplicate_errors
        
        return jsonify(response), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app_file108.route("/recipe/<int:id>", methods=["GET", "PUT", "PATCH", "DELETE"])
@cross_origin()
def get_update_delete_recipe(id):
    try:
        if request.method == "GET":
            mydb = get_db_connection()
            cursor = mydb.cursor(dictionary=True)

            cursor.execute("SELECT * FROM recipe WHERE id = %s", (id,))
            recipe = cursor.fetchone()
            if not recipe:
                return jsonify({"error": "Recipe not found."}), 404

            cursor.execute("SELECT * FROM recipe_items WHERE recipe_id = %s", (id,))
            recipe["items"] = cursor.fetchall()

            cursor.execute("""
                SELECT rs.id AS link_id, sr.id AS sub_recipe_id, sr.name, sr.outlet,
                       rs.quantity, rs.uom, rs.unit, rs.costprice, rs.rate, rs.new_uom
                FROM recipe_subrecipes rs
                JOIN sub_recipe sr ON sr.id = rs.sub_recipe_id
                WHERE rs.recipe_id = %s
            """, (id,))
            sub_recipes = cursor.fetchall()

            for sub_recipe in sub_recipes:
                cursor.execute("SELECT * FROM sub_recipe_items WHERE sub_recipe_id = %s", (sub_recipe["sub_recipe_id"],))
                sub_recipe["items"] = cursor.fetchall()

            recipe["sub_recipes"] = sub_recipes

            cursor.close()
            mydb.close()
            return jsonify(recipe)

        # PUT / PATCH / DELETE below
        data = request.get_json()
        token = data.get("token")
        if not token or not token_auth(token):
            return jsonify({"error": "Invalid or missing token."}), 400

        mydb = get_db_connection()
        cursor = mydb.cursor()

        if request.method == "PUT":
            name = data.get("name")
            outlet = data.get("outlet")
            cost_price = data.get("cost_price")
            selling_price = data.get("selling_price")
            cost_percent = data.get("cost_percent")
            item_type = data.get("item_type")
            items = data.get("items", [])
            sub_recipes = data.get("sub_recipes", [])

            if not name or not outlet or cost_price is None or selling_price is None or cost_percent is None or not item_type:
                return jsonify({"error": "Missing required fields."}), 400

            cursor.execute("""
                UPDATE recipe SET name = %s, outlet = %s, costprice = %s, sellingprice = %s, cost_percent = %s, ItemType = %s
                WHERE id = %s
            """, (name, outlet, cost_price, selling_price, cost_percent, item_type, id))

            # Recipe Items
            cursor.execute("SELECT id FROM recipe_items WHERE recipe_id = %s", (id,))
            existing_item_ids = {row[0] for row in cursor.fetchall()}
            sent_item_ids = set()

            for item in items:
                item_id = item.get("id")
                if item_id and item_id in existing_item_ids:
                    cursor.execute("""
                        UPDATE recipe_items SET name=%s, rate=%s, uom=%s, new_uom=%s, unit=%s, quantity=%s, cost=%s
                        WHERE id=%s AND recipe_id=%s
                    """, (
                        item["name"], item["rate"], item["uom"], item.get("new_uom"),
                        item.get("unit", 1), item["quantity"], item["cost"], item_id, id
                    ))
                    sent_item_ids.add(item_id)
                else:
                    cursor.execute("""
                        INSERT INTO recipe_items (recipe_id, name, rate, uom, new_uom, unit, quantity, cost)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        id, item["name"], item["rate"], item["uom"], item.get("new_uom"),
                        item.get("unit", 1), item["quantity"], item["cost"]
                    ))

            to_delete = existing_item_ids - sent_item_ids
            if to_delete:
                cursor.execute(
                    f"DELETE FROM recipe_items WHERE id IN ({','.join(['%s']*len(to_delete))})",
                    tuple(to_delete)
                )

            # Sub Recipes
            cursor.execute("SELECT id FROM recipe_subrecipes WHERE recipe_id = %s", (id,))
            existing_links = {row[0] for row in cursor.fetchall()}
            sent_links = set()

            for sub in sub_recipes:
                link_id = sub.get("link_id")
                if link_id and link_id in existing_links:
                    cursor.execute("""
                        UPDATE recipe_subrecipes SET sub_recipe_id=%s, quantity=%s, uom=%s, unit=%s, costprice=%s, rate=%s, new_uom=%s
                        WHERE id=%s AND recipe_id=%s
                    """, (
                        sub["sub_recipe_id"], sub["quantity"], sub["uom"], sub["unit"],
                        sub["costprice"], sub["rate"], sub.get("new_uom"), link_id, id
                    ))
                    sent_links.add(link_id)
                else:
                    cursor.execute("""
                        INSERT INTO recipe_subrecipes (recipe_id, sub_recipe_id, quantity, uom, unit, costprice, rate, new_uom)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        id, sub["sub_recipe_id"], sub["quantity"], sub["uom"], sub["unit"],
                        sub["costprice"], sub["rate"], sub.get("new_uom")
                    ))

            to_delete = existing_links - sent_links
            if to_delete:
                cursor.execute(
                    f"DELETE FROM recipe_subrecipes WHERE recipe_id = %s AND id IN ({','.join(['%s']*len(to_delete))})",
                    (id, *to_delete)
                )

            mydb.commit()
            message = "Recipe updated."

        elif request.method == "PATCH":
            updates = []
            fields = ["name", "outlet", "costprice", "sellingprice", "cost_percent", "ItemType"]
            for field in fields:
                if field in data:
                    updates.append(f"{field} = %s")

            if updates:
                values = [data[field] for field in fields if field in data]
                values.append(id)
                cursor.execute(f"UPDATE recipe SET {', '.join(updates)} WHERE id = %s", values)

            if "items" in data:
                for item in data["items"]:
                    if "id" in item:
                        cursor.execute("""
                            UPDATE recipe_items SET name=%s, rate=%s, uom=%s, new_uom=%s, unit=%s, quantity=%s, cost=%s
                            WHERE id=%s AND recipe_id=%s
                        """, (
                            item["name"], item["rate"], item["uom"], item.get("new_uom"),
                            item.get("unit", 1), item["quantity"], item["cost"], item["id"], id
                        ))

            if "sub_recipes" in data:
                for sub in data["sub_recipes"]:
                    if "link_id" in sub:
                        cursor.execute("""
                            UPDATE recipe_subrecipes SET sub_recipe_id=%s, quantity=%s, uom=%s, unit=%s, costprice=%s, rate=%s, new_uom=%s
                            WHERE id=%s AND recipe_id=%s
                        """, (
                            sub["sub_recipe_id"], sub["quantity"], sub["uom"], sub["unit"],
                            sub["costprice"], sub["rate"], sub.get("new_uom"), sub["link_id"], id
                        ))

            mydb.commit()
            message = "Recipe partially updated."

        elif request.method == "DELETE":
            cursor.execute("DELETE FROM recipe_items WHERE recipe_id = %s", (id,))
            cursor.execute("DELETE FROM recipe_subrecipes WHERE recipe_id = %s", (id,))
            cursor.execute("DELETE FROM recipe WHERE id = %s", (id,))
            mydb.commit()
            message = "Recipe deleted."

        cursor.close()
        mydb.close()
        return jsonify({"message": message})

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app_file108.route("/recipes", methods=["GET"])
@cross_origin()
def get_all_recipes():
    try:
        outlet_filter = request.args.get("outlet")  # Get ?outlet=Kathmandu Outlet from URL

        mydb = get_db_connection()
        cursor = mydb.cursor(dictionary=True)

        # Base query
        if outlet_filter:
            cursor.execute("SELECT * FROM recipe WHERE outlet = %s", (outlet_filter,))
        else:
            cursor.execute("SELECT * FROM recipe")
        recipes = cursor.fetchall()

        for recipe in recipes:
            # Include ItemType (already fetched with main recipe record)
            # Get recipe items
            cursor.execute("SELECT * FROM recipe_items WHERE recipe_id = %s", (recipe["id"],))
            recipe["items"] = cursor.fetchall()

            # Get sub-recipes linked to this recipe along with all fields
            cursor.execute("""
                SELECT sr.id AS sub_recipe_id, sr.name, sr.outlet,
                       rs.quantity, rs.uom, rs.unit, rs.costprice, rs.rate, rs.new_uom
                FROM recipe_subrecipes rs
                JOIN sub_recipe sr ON sr.id = rs.sub_recipe_id
                WHERE rs.recipe_id = %s
            """, (recipe["id"],))
            sub_recipes = cursor.fetchall()

            # For each sub_recipe, get its items
            for sub_recipe in sub_recipes:
                cursor.execute("SELECT * FROM sub_recipe_items WHERE sub_recipe_id = %s", (sub_recipe["sub_recipe_id"],))
                sub_recipe["items"] = cursor.fetchall()

            recipe["sub_recipes"] = sub_recipes

        cursor.close()
        mydb.close()
        return jsonify(recipes)

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app_file108.route("/recipes", methods=["POST"])
@cross_origin()
def get_filtered_recipes_by_name():
    try:
        data = request.get_json()
        item_name = data.get("item_name")
        outlet_filter = data.get("outlet")

        if not item_name:
            return jsonify({"error": "Missing item_name in request body"}), 400

        mydb = get_db_connection()
        cursor = mydb.cursor(dictionary=True)

        # # Dynamic query construction with ItemType already selected
        # query = "SELECT * FROM recipe WHERE name = %s"
        # values = [f"%{item_name}%"]

        query = "SELECT * FROM recipe WHERE name = %s"
        values = [item_name]

        if outlet_filter:
            query += " AND outlet = %s"
            values.append(outlet_filter)

        cursor.execute(query, tuple(values))
        recipes = cursor.fetchall()

        for recipe in recipes:
            # Include ItemType (already fetched in base query)

            # Get recipe items
            cursor.execute("SELECT * FROM recipe_items WHERE recipe_id = %s", (recipe["id"],))
            recipe["items"] = cursor.fetchall()

            # Get linked sub-recipes
            cursor.execute("""
                SELECT 
                    rs.id AS link_id,
                    sr.id AS sub_recipe_id,
                    sr.name,
                    sr.outlet,
                    rs.quantity,
                    rs.uom,
                    rs.new_uom,
                    rs.unit,
                    rs.costprice,
                    rs.rate
                FROM recipe_subrecipes rs
                JOIN sub_recipe sr ON sr.id = rs.sub_recipe_id
                WHERE rs.recipe_id = %s
            """, (recipe["id"],))
            sub_recipes = cursor.fetchall()

            for sub_recipe in sub_recipes:
                cursor.execute("SELECT * FROM sub_recipe_items WHERE sub_recipe_id = %s", (sub_recipe["sub_recipe_id"],))
                sub_recipe["items"] = cursor.fetchall()

            recipe["sub_recipes"] = sub_recipes

        cursor.close()
        mydb.close()
        return jsonify(recipes)

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    

@app_file108.route("/recipe/update-name", methods=["PUT"])
@cross_origin()
def update_recipe_name():
    try:
        data = request.get_json()

        recipe_id = data.get("id")
        new_name = data.get("name")

        if not recipe_id or not new_name:
            return jsonify({"error": "id and name are required"}), 400

        mydb = get_db_connection()
        cursor = mydb.cursor()

        query = "UPDATE recipe SET name = %s WHERE id = %s"
        cursor.execute(query, (new_name, recipe_id))

        if cursor.rowcount == 0:
            return jsonify({"error": "Recipe not found"}), 404

        mydb.commit()

        cursor.close()
        mydb.close()

        return jsonify({"message": "Recipe name updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400