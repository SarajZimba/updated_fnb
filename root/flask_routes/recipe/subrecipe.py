from flask import Blueprint, jsonify, request
import mysql.connector
import os
from dotenv import load_dotenv
from flask_cors import cross_origin
from root.auth.check import token_auth

load_dotenv()

app_file107 = Blueprint('app_file107', __name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("host"),
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )


# @app_file107.route("/sub-recipe", methods=["POST"])
# @cross_origin()
# def create_sub_recipe():
#     try:
#         data = request.get_json()
#         token = data.get("token")
#         if not token or not token_auth(token):
#             return jsonify({"error": "Invalid or missing token."}), 400

#         name = data.get("name")
#         outlet = data.get("outlet")
#         uom = data.get("uom")
#         unit = data.get("unit")
#         costprice = data.get("costprice", 0)
#         items = data.get("items", [])

#         if not name or not outlet or not isinstance(items, list):
#             return jsonify({"error": "Missing fields or invalid items format"}), 400

#         mydb = get_db_connection()
#         cursor = mydb.cursor()

#         # Insert into sub_recipe with new fields
#         cursor.execute("""
#             INSERT INTO sub_recipe (name, outlet, uom, unit, costprice)
#             VALUES (%s, %s, %s, %s, %s)
#         """, (name, outlet, uom, unit, costprice))
#         sub_recipe_id = cursor.lastrowid

#         for item in items:
#             item_name = item.get("name")
#             rate = item.get("rate")
#             item_uom = item.get("uom")
#             new_uom = item.get("new_uom")  # New field
#             quantity = item.get("quantity")
#             cost = item.get("cost")

#             if not all([item_name, rate, item_uom, new_uom, quantity, cost]):
#                 continue

#             cursor.execute("""
#                 INSERT INTO sub_recipe_items (sub_recipe_id, name, rate, uom, new_uom, quantity, cost)
#                 VALUES (%s, %s, %s, %s, %s, %s, %s)
#             """, (sub_recipe_id, item_name, rate, item_uom, new_uom, quantity, cost))

#         mydb.commit()
#         cursor.close()
#         mydb.close()

#         return jsonify({"message": "Sub recipe created successfully."}), 201

#     except Exception as e:
#         return jsonify({"error": str(e)}), 400

@app_file107.route("/sub-recipe", methods=["POST"])
@cross_origin()
def create_sub_recipe():
    try:
        data = request.get_json()
        token = data.get("token")
        if not token or not token_auth(token):
            return jsonify({"error": "Invalid or missing token."}), 400

        name = data.get("name")
        outlet = data.get("outlet")
        uom = data.get("uom")
        unit = data.get("unit")  # This is the unit for the main sub_recipe
        costprice = data.get("costprice", 0)
        items = data.get("items", [])

        if not name or not outlet or not isinstance(items, list):
            return jsonify({"error": "Missing fields or invalid items format"}), 400

        mydb = get_db_connection()
        cursor = mydb.cursor()

        # Insert into sub_recipe
        cursor.execute("""
            INSERT INTO sub_recipe (name, outlet, uom, unit, costprice)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, outlet, uom, unit, costprice))
        sub_recipe_id = cursor.lastrowid

        for item in items:
            item_name = item.get("name")
            rate = item.get("rate")
            item_uom = item.get("uom")
            new_uom = item.get("new_uom")
            quantity = item.get("quantity")
            cost = item.get("cost")
            item_unit = item.get("unit", 1)  # Default to 1 if not provided

            if not all([item_name, rate, item_uom, new_uom, quantity, cost]):
                continue

            cursor.execute("""
                INSERT INTO sub_recipe_items (sub_recipe_id, name, rate, uom, new_uom, quantity, cost, unit)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (sub_recipe_id, item_name, rate, item_uom, new_uom, quantity, cost, item_unit))

        mydb.commit()
        cursor.close()
        mydb.close()

        return jsonify({"message": "Sub recipe created successfully."}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# @app_file107.route("/sub-recipe/<int:id>", methods=["GET", "PUT", "DELETE", "PATCH"])
# @cross_origin()
# def get_update_delete_sub_recipe(id):
#     try:
#         print("this is the request", request.method)
#         if request.method == "GET":
#             mydb = get_db_connection()
#             cursor = mydb.cursor(dictionary=True)

#             cursor.execute("SELECT * FROM sub_recipe WHERE id = %s", (id,))
#             recipe = cursor.fetchone()
#             if not recipe:
#                 return jsonify({"error": "Sub recipe not found."}), 404

#             cursor.execute("SELECT * FROM sub_recipe_items WHERE sub_recipe_id = %s", (id,))
#             items = cursor.fetchall()
#             recipe["items"] = items

#             cursor.close()
#             mydb.close()
#             return jsonify(recipe)

#         # Shared logic for PUT / PATCH / DELETE
#         data = request.get_json()
#         token = data.get("token")
#         if not token or not token_auth(token):
#             return jsonify({"error": "Invalid or missing token."}), 400

#         mydb = get_db_connection()
#         cursor = mydb.cursor()

#         if request.method == "PUT":
#             name = data.get("name")
#             outlet = data.get("outlet")
#             items = data.get("items", [])

#             if not name or not outlet or not isinstance(items, list):
#                 return jsonify({"error": "Missing fields or invalid items format"}), 400

#             # Update sub_recipe main record
#             cursor.execute("UPDATE sub_recipe SET name = %s, outlet = %s WHERE id = %s", (name, outlet, id))

#             # Get existing item ids from database
#             cursor.execute("SELECT id FROM sub_recipe_items WHERE sub_recipe_id = %s", (id,))
#             existing_ids = {row[0] for row in cursor.fetchall()}
#             sent_ids = set()

#             for item in items:
#                 item_id = item.get("id")
#                 item_name = item.get("name")
#                 rate = item.get("rate")
#                 uom = item.get("uom")
#                 new_uom = item.get("new_uom")  # <-- New Field
#                 quantity = item.get("quantity")
#                 cost = item.get("cost")

#                 if not all([item_name, rate, uom, new_uom, quantity, cost]):
#                     continue

#                 if item_id and item_id in existing_ids:
#                     # Update existing item
#                     cursor.execute("""
#                         UPDATE sub_recipe_items
#                         SET name = %s, rate = %s, uom = %s, new_uom = %s, quantity = %s, cost = %s
#                         WHERE id = %s AND sub_recipe_id = %s
#                     """, (item_name, rate, uom, new_uom, quantity, cost, item_id, id))
#                     sent_ids.add(item_id)
#                 else:
#                     # Insert new item
#                     cursor.execute("""
#                         INSERT INTO sub_recipe_items (sub_recipe_id, name, rate, uom, new_uom, quantity, cost)
#                         VALUES (%s, %s, %s, %s, %s, %s, %s)
#                     """, (id, item_name, rate, uom, new_uom, quantity, cost))

#             # Delete removed items
#             to_delete = existing_ids - sent_ids
#             if to_delete:
#                 cursor.execute(
#                     f"DELETE FROM sub_recipe_items WHERE id IN ({','.join(['%s'] * len(to_delete))})",
#                     tuple(to_delete)
#                 )

#             mydb.commit()
#             message = "Sub recipe updated."

#         elif request.method == "PATCH":
#             fields = []
#             values = []
#             for field in ["name", "outlet", "uom", "unit", "costprice"]:
#                 if field in data:
#                     fields.append(f"{field} = %s")
#                     values.append(data[field])

#             if fields:
#                 query = f"UPDATE sub_recipe SET {', '.join(fields)} WHERE id = %s"
#                 values.append(id)
#                 cursor.execute(query, tuple(values))

#             # Partial update for items
#             items = data.get("items")
#             if isinstance(items, list):
#                 for item in items:
#                     item_id = item.get("id")
#                     item_fields = []
#                     item_values = []

#                     for field in ["name", "rate", "uom", "new_uom", "quantity", "cost"]:
#                         if field in item:
#                             item_fields.append(f"{field} = %s")
#                             item_values.append(item[field])

#                     if item_id and item_fields:
#                         query = f"UPDATE sub_recipe_items SET {', '.join(item_fields)} WHERE id = %s AND sub_recipe_id = %s"
#                         item_values.extend([item_id, id])
#                         cursor.execute(query, tuple(item_values))
#                     elif not item_id:
#                         # Insert if full details are present
#                         required = [item.get(f) for f in ["name", "rate", "uom", "new_uom", "quantity", "cost"]]
#                         if all(required):
#                             cursor.execute("""
#                                 INSERT INTO sub_recipe_items (sub_recipe_id, name, rate, uom, new_uom, quantity, cost)
#                                 VALUES (%s, %s, %s, %s, %s, %s, %s)
#                             """, (id, *required))

#             mydb.commit()
#             message = "Sub recipe patched."

#         elif request.method == "DELETE":
#             print("got delete request")
#             cursor.execute("DELETE FROM sub_recipe_items WHERE sub_recipe_id = %s", (id,))
#             cursor.execute("DELETE FROM sub_recipe WHERE id = %s", (id,))
#             mydb.commit()
#             message = "Sub recipe deleted."

#         cursor.close()
#         mydb.close()
#         return jsonify({"message": message})

#     except Exception as e:
#         return jsonify({"error": str(e)}), 400

@app_file107.route("/sub-recipe/<int:id>", methods=["GET", "PUT", "DELETE", "PATCH"])
@cross_origin()
def get_update_delete_sub_recipe(id):
    try:
        if request.method == "GET":
            mydb = get_db_connection()
            cursor = mydb.cursor(dictionary=True)

            cursor.execute("SELECT * FROM sub_recipe WHERE id = %s", (id,))
            recipe = cursor.fetchone()
            if not recipe:
                return jsonify({"error": "Sub recipe not found."}), 404

            cursor.execute("SELECT * FROM sub_recipe_items WHERE sub_recipe_id = %s", (id,))
            items = cursor.fetchall()
            recipe["items"] = items

            cursor.close()
            mydb.close()
            return jsonify(recipe)

        # Shared logic for PUT / PATCH / DELETE
        data = request.get_json()
        token = data.get("token")
        if not token or not token_auth(token):
            return jsonify({"error": "Invalid or missing token."}), 400

        mydb = get_db_connection()
        cursor = mydb.cursor()

        if request.method == "PUT":
            name = data.get("name")
            outlet = data.get("outlet")
            uom = data.get("uom")
            unit = data.get("unit")
            costprice = data.get("costprice", 0)
            items = data.get("items", [])

            if not name or not outlet or not isinstance(items, list):
                return jsonify({"error": "Missing fields or invalid items format"}), 400

            cursor.execute("""
                UPDATE sub_recipe SET name = %s, outlet = %s, uom = %s, unit = %s, costprice = %s
                WHERE id = %s
            """, (name, outlet, uom, unit, costprice, id))

            cursor.execute("SELECT id FROM sub_recipe_items WHERE sub_recipe_id = %s", (id,))
            existing_ids = {row[0] for row in cursor.fetchall()}
            sent_ids = set()

            for item in items:
                item_id = item.get("id")
                item_name = item.get("name")
                rate = item.get("rate")
                item_uom = item.get("uom")
                new_uom = item.get("new_uom")
                quantity = item.get("quantity")
                cost = item.get("cost")
                item_unit = item.get("unit", 1)

                if not all([item_name, rate, item_uom, new_uom, quantity, cost]):
                    continue

                if item_id and item_id in existing_ids:
                    cursor.execute("""
                        UPDATE sub_recipe_items
                        SET name = %s, rate = %s, uom = %s, new_uom = %s, quantity = %s, cost = %s, unit = %s
                        WHERE id = %s AND sub_recipe_id = %s
                    """, (item_name, rate, item_uom, new_uom, quantity, cost, item_unit, item_id, id))
                    sent_ids.add(item_id)
                else:
                    cursor.execute("""
                        INSERT INTO sub_recipe_items (sub_recipe_id, name, rate, uom, new_uom, quantity, cost, unit)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (id, item_name, rate, item_uom, new_uom, quantity, cost, item_unit))

            to_delete = existing_ids - sent_ids
            if to_delete:
                cursor.execute(
                    f"DELETE FROM sub_recipe_items WHERE id IN ({','.join(['%s'] * len(to_delete))})",
                    tuple(to_delete)
                )

            mydb.commit()
            message = "Sub recipe updated."

        elif request.method == "PATCH":
            fields = []
            values = []
            for field in ["name", "outlet", "uom", "unit", "costprice"]:
                if field in data:
                    fields.append(f"{field} = %s")
                    values.append(data[field])

            if fields:
                query = f"UPDATE sub_recipe SET {', '.join(fields)} WHERE id = %s"
                values.append(id)
                cursor.execute(query, tuple(values))

            items = data.get("items")
            if isinstance(items, list):
                for item in items:
                    item_id = item.get("id")
                    item_fields = []
                    item_values = []

                    for field in ["name", "rate", "uom", "new_uom", "quantity", "cost", "unit"]:
                        if field in item:
                            item_fields.append(f"{field} = %s")
                            item_values.append(item[field])

                    if item_id and item_fields:
                        query = f"UPDATE sub_recipe_items SET {', '.join(item_fields)} WHERE id = %s AND sub_recipe_id = %s"
                        item_values.extend([item_id, id])
                        cursor.execute(query, tuple(item_values))
                    elif not item_id:
                        required = [item.get(f) for f in ["name", "rate", "uom", "new_uom", "quantity", "cost"]]
                        item_unit = item.get("unit", 1)
                        if all(required):
                            cursor.execute("""
                                INSERT INTO sub_recipe_items (sub_recipe_id, name, rate, uom, new_uom, quantity, cost, unit)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            """, (id, *required, item_unit))

            mydb.commit()
            message = "Sub recipe patched."

        elif request.method == "DELETE":
            cursor.execute("DELETE FROM sub_recipe_items WHERE sub_recipe_id = %s", (id,))
            cursor.execute("DELETE FROM sub_recipe WHERE id = %s", (id,))
            mydb.commit()
            message = "Sub recipe deleted."

        cursor.close()
        mydb.close()
        return jsonify({"message": message})

    except Exception as e:
        return jsonify({"error": str(e)}), 400



@app_file107.route("/sub-recipes", methods=["GET"])
@cross_origin()
def get_all_sub_recipes():
    try:
        outlet_filter = request.args.get("outlet")  # e.g. ?outlet=Kathmandu Outlet

        mydb = get_db_connection()
        cursor = mydb.cursor(dictionary=True)

        # Apply filter if outlet is provided
        if outlet_filter:
            cursor.execute("SELECT * FROM sub_recipe WHERE outlet = %s", (outlet_filter,))
        else:
            cursor.execute("SELECT * FROM sub_recipe")

        recipes = cursor.fetchall()

        # For each recipe, fetch its items
        for recipe in recipes:
            cursor.execute("SELECT * FROM sub_recipe_items WHERE sub_recipe_id = %s", (recipe["id"],))
            items = cursor.fetchall()
            recipe["items"] = items

        cursor.close()
        mydb.close()
        return jsonify(recipes)

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# @app_file107.route("/sub-recipes/bulk", methods=["POST"])
# @cross_origin()
# def create_bulk_sub_recipes():
#     try:
#         data = request.get_json()
#         token = data.get("token")
#         if not token or not token_auth(token):
#             return jsonify({"error": "Invalid or missing token."}), 400

#         sub_recipes = data.get("sub_recipes_bulk", [])
        
#         if not isinstance(sub_recipes, list) or len(sub_recipes) == 0:
#             return jsonify({"error": "sub_recipes must be a non-empty list"}), 400

#         # Validate all recipes first
#         validation_errors = []
#         valid_recipes = []
        
#         for idx, recipe_data in enumerate(sub_recipes):
#             name = recipe_data.get("name")
#             outlet = recipe_data.get("outlet")
#             items = recipe_data.get("bulk_items", [])
            
#             if not name:
#                 validation_errors.append({"index": idx, "error": "Missing name"})
#                 continue
#             if not outlet:
#                 validation_errors.append({"index": idx, "error": "Missing outlet"})
#                 continue
#             if not isinstance(items, list):
#                 validation_errors.append({"index": idx, "error": "Items must be a list"})
#                 continue
#             if len(items) == 0:
#                 validation_errors.append({"index": idx, "error": "At least one item is required"})
#                 continue
                
#             # Validate items
#             item_errors = []
#             for item_idx, item in enumerate(items):
#                 if not item.get("name"):
#                     item_errors.append({"item_index": item_idx, "error": "Missing item name"})
#                 if not item.get("rate"):
#                     item_errors.append({"item_index": item_idx, "error": "Missing rate"})
#                 if not item.get("quantity"):
#                     item_errors.append({"item_index": item_idx, "error": "Missing quantity"})
                    
#             if item_errors:
#                 validation_errors.append({
#                     "index": idx, 
#                     "error": "Invalid items", 
#                     "item_errors": item_errors
#                 })
#                 continue
                
#             valid_recipes.append(recipe_data)
        
#         if validation_errors:
#             return jsonify({
#                 "error": "Validation failed for some recipes",
#                 "validation_errors": validation_errors,
#                 "total_recipes": len(sub_recipes),
#                 "valid_recipes": len(valid_recipes)
#             }), 400

#         mydb = get_db_connection()
#         cursor = mydb.cursor()
        
#         created_recipes = []
        
#         for recipe_data in valid_recipes:
#             name = recipe_data.get("name")
#             outlet = recipe_data.get("outlet")
#             uom = recipe_data.get("uom")
#             unit = recipe_data.get("unit")
#             costprice = recipe_data.get("costprice", 0)
#             items = recipe_data.get("bulk_items", [])

#             # Insert into sub_recipe
#             cursor.execute("""
#                 INSERT INTO sub_recipe (name, outlet, uom, unit, costprice)
#                 VALUES (%s, %s, %s, %s, %s)
#             """, (name, outlet, uom, unit, costprice))
#             sub_recipe_id = cursor.lastrowid

#             # Insert sub_recipe items
#             items_inserted = 0
#             for item in items:
#                 item_name = item.get("name")
#                 rate = item.get("rate")
#                 item_uom = item.get("uom")
#                 new_uom = item.get("new_uom")
#                 quantity = item.get("quantity")
#                 cost = item.get("cost")
#                 item_unit = item.get("unit", 1)

#                 cursor.execute("""
#                     INSERT INTO sub_recipe_items (sub_recipe_id, name, rate, uom, new_uom, quantity, cost, unit)
#                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
#                 """, (sub_recipe_id, item_name, rate, item_uom, new_uom, quantity, cost, item_unit))
#                 items_inserted += 1

#             created_recipes.append({
#                 "id": sub_recipe_id,
#                 "name": name,
#                 "outlet": outlet,
#                 "items_count": items_inserted
#             })

#         mydb.commit()
#         cursor.close()
#         mydb.close()

#         return jsonify({
#             "message": f"Successfully created {len(created_recipes)} sub-recipes",
#             "created_recipes": created_recipes,
#             "total": len(created_recipes)
#         }), 201

#     except Exception as e:
#         return jsonify({"error": str(e)}), 400


# @app_file107.route("/sub-recipes/bulk", methods=["POST"])
# @cross_origin()
# def create_bulk_sub_recipes():
#     try:
#         data = request.get_json()
#         token = data.get("token")
#         if not token or not token_auth(token):
#             return jsonify({"error": "Invalid or missing token."}), 400

#         sub_recipes = data.get("sub_recipes_bulk", [])
        
#         if not isinstance(sub_recipes, list) or len(sub_recipes) == 0:
#             return jsonify({"error": "sub_recipes must be a non-empty list"}), 400

#         # Validate all recipes first
#         validation_errors = []
#         valid_recipes = []
        
#         for idx, recipe_data in enumerate(sub_recipes):
#             name = recipe_data.get("name")
#             outlet = recipe_data.get("outlet")
#             items = recipe_data.get("bulk_items", [])
            
#             if not name:
#                 validation_errors.append({"index": idx, "error": "Missing name"})
#                 continue
#             if not outlet:
#                 validation_errors.append({"index": idx, "error": "Missing outlet"})
#                 continue
#             if not isinstance(items, list):
#                 validation_errors.append({"index": idx, "error": "Items must be a list"})
#                 continue
#             if len(items) == 0:
#                 validation_errors.append({"index": idx, "error": "At least one item is required"})
#                 continue
                
#             # Validate items
#             item_errors = []
#             for item_idx, item in enumerate(items):
#                 if not item.get("name"):
#                     item_errors.append({"item_index": item_idx, "error": "Missing item name"})
#                 if not item.get("rate"):
#                     item_errors.append({"item_index": item_idx, "error": "Missing rate"})
#                 if not item.get("quantity"):
#                     item_errors.append({"item_index": item_idx, "error": "Missing quantity"})
#                 if not item.get("uom"):
#                     item_errors.append({"item_index": item_idx, "error": "Missing uom"})
#                 if not item.get("new_uom"):
#                     item_errors.append({"item_index": item_idx, "error": "Missing new_uom"})
                    
#             if item_errors:
#                 validation_errors.append({
#                     "index": idx, 
#                     "error": "Invalid items", 
#                     "item_errors": item_errors
#                 })
#                 continue
                
#             valid_recipes.append(recipe_data)
        
#         if validation_errors:
#             return jsonify({
#                 "error": "Validation failed for some recipes",
#                 "validation_errors": validation_errors,
#                 "total_recipes": len(sub_recipes),
#                 "valid_recipes": len(valid_recipes)
#             }), 400

#         mydb = get_db_connection()
#         cursor = mydb.cursor()
        
#         created_recipes = []
        
#         for recipe_data in valid_recipes:
#             name = recipe_data.get("name")
#             outlet = recipe_data.get("outlet")
#             uom = recipe_data.get("uom")
#             unit = recipe_data.get("unit")
#             costprice = recipe_data.get("costprice", 0)
#             items = recipe_data.get("bulk_items", [])

#             # Insert into sub_recipe
#             cursor.execute("""
#                 INSERT INTO sub_recipe (name, outlet, uom, unit, costprice)
#                 VALUES (%s, %s, %s, %s, %s)
#             """, (name, outlet, uom, unit, costprice))
#             sub_recipe_id = cursor.lastrowid

#             # Insert sub_recipe items with quantity conversion
#             items_inserted = 0
#             for item in items:
#                 item_name = item.get("name")
#                 rate = item.get("rate")
#                 item_uom = item.get("uom")
#                 new_uom = item.get("new_uom")
#                 original_quantity = item.get("quantity")
#                 cost = item.get("cost")
#                 item_unit = item.get("unit", 1)
                
#                 # Convert quantity from new_uom to item_uom (parent recipe's uom)
#                 converted_quantity = convert_quantity(original_quantity, new_uom, item_uom)
                
#                 cursor.execute("""
#                     INSERT INTO sub_recipe_items (sub_recipe_id, name, rate, uom, new_uom, quantity, cost, unit)
#                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
#                 """, (sub_recipe_id, item_name, rate, item_uom, new_uom, converted_quantity, cost, item_unit))
#                 items_inserted += 1

#             created_recipes.append({
#                 "id": sub_recipe_id,
#                 "name": name,
#                 "outlet": outlet,
#                 "items_count": items_inserted
#             })

#         mydb.commit()
#         cursor.close()
#         mydb.close()

#         return jsonify({
#             "message": f"Successfully created {len(created_recipes)} sub-recipes",
#             "created_recipes": created_recipes,
#             "total": len(created_recipes)
#         }), 201

#     except Exception as e:
#         return jsonify({"error": str(e)}), 400


# def normalize_unit(unit):
#     """
#     Normalize various unit variations to standard unit names
#     """
#     if not unit:
#         return None
    
#     # Convert to lowercase for case-insensitive matching
#     unit_lower = str(unit).lower().strip()
    
#     # Weight units - Kilograms
#     kg_variations = ['kg', 'kgs', 'kilogram', 'kilograms']
#     if unit_lower in kg_variations:
#         return 'Kg'
    
#     # Weight units - Grams
#     gram_variations = ['g', 'gram', 'grams', 'gm', 'gms', 'grm', 'grms']
#     if unit_lower in gram_variations:
#         return 'Grms'
    
#     # Volume units - Liters
#     liter_variations = ['l', 'ltr', 'ltrs', 'liter', 'liters', 'litre', 'litres']
#     if unit_lower in liter_variations:
#         return 'LTR'
    
#     # Volume units - Milliliters
#     milliliter_variations = ['ml', 'milliliter', 'milliliters', 'millilitre', 'millilitres', 'mls']
#     if unit_lower in milliliter_variations:
#         return 'ml'
    
#     # If no match found, return original (will be handled by conversion)
#     return unit


# def convert_quantity(quantity, from_uom, to_uom):
#     """
#     Convert quantity from one unit to another with support for multiple unit variations
#     """
#     if not quantity:
#         return 0
    
#     # Normalize units to standard format
#     from_uom_normalized = normalize_unit(from_uom)
#     to_uom_normalized = normalize_unit(to_uom)
    
#     # If units are the same after normalization, no conversion needed
#     if from_uom_normalized == to_uom_normalized:
#         return quantity
    
#     # Conversion factors to base units (all weights to grams, all volumes to milliliters)
#     # Base units: 'Grms' for weight, 'ml' for volume
    
#     # Check if converting between weight and volume (not allowed)
#     weight_units = ['Kg', 'Grms']
#     volume_units = ['LTR', 'ml']
    
#     if (from_uom_normalized in weight_units and to_uom_normalized in volume_units) or \
#        (from_uom_normalized in volume_units and to_uom_normalized in weight_units):
#         # Cannot convert between weight and volume
#         print(f"Warning: Cannot convert between weight ({from_uom}) and volume ({to_uom})")
#         return quantity
    
#     # Define conversion to base units
#     def to_base_unit(value, unit):
#         if unit == 'Grms':  # Grams to grams
#             return value
#         elif unit == 'Kg':  # Kilograms to grams
#             return value * 1000
#         elif unit == 'ml':  # Milliliters to milliliters
#             return value
#         elif unit == 'LTR':  # Liters to milliliters
#             return value * 1000
#         else:
#             # Unknown unit, return as is
#             return value
    
#     def from_base_unit(value, unit):
#         if unit == 'Grms':  # Grams from grams
#             return value
#         elif unit == 'Kg':  # Kilograms from grams
#             return value / 1000
#         elif unit == 'ml':  # Milliliters from milliliters
#             return value
#         elif unit == 'LTR':  # Liters from milliliters
#             return value / 1000
#         else:
#             # Unknown unit, return as is
#             return value
    
#     # Convert to base unit first
#     base_quantity = to_base_unit(quantity, from_uom_normalized)
    
#     # Then convert from base unit to target unit
#     converted_quantity = from_base_unit(base_quantity, to_uom_normalized)
    
#     # Round to reasonable decimal places
#     return round(converted_quantity, 6)


# # Alternative: If you want to store the original quantity as well, modify the insert:
# def insert_with_both_quantities(cursor, sub_recipe_id, item):
#     """
#     Example of storing both original and converted quantities
#     """
#     item_name = item.get("name")
#     rate = item.get("rate")
#     item_uom = item.get("uom")
#     new_uom = item.get("new_uom")
#     original_quantity = item.get("quantity")
#     cost = item.get("cost")
#     item_unit = item.get("unit", 1)
    
#     # Convert quantity
#     converted_quantity = convert_quantity(original_quantity, new_uom, item_uom)
    
#     # Store both quantities (requires schema change)
#     cursor.execute("""
#         INSERT INTO sub_recipe_items (
#             sub_recipe_id, name, rate, uom, new_uom, 
#             quantity, original_quantity, original_uom, cost, unit
#         )
#         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#     """, (sub_recipe_id, item_name, rate, item_uom, new_uom, 
#           converted_quantity, original_quantity, new_uom, cost, item_unit))



# @app_file107.route("/sub-recipes/bulk", methods=["POST"])
# @cross_origin()
# def create_bulk_sub_recipes():
#     try:
#         data = request.get_json()
#         token = data.get("token")
#         if not token or not token_auth(token):
#             return jsonify({"error": "Invalid or missing token."}), 400

#         sub_recipes = data.get("sub_recipes_bulk", [])
        
#         if not isinstance(sub_recipes, list) or len(sub_recipes) == 0:
#             return jsonify({"error": "sub_recipes must be a non-empty list"}), 400

#         # Validate all recipes first
#         validation_errors = []
#         valid_recipes = []
        
#         for idx, recipe_data in enumerate(sub_recipes):
#             name = recipe_data.get("name")
#             outlet = recipe_data.get("outlet")
#             items = recipe_data.get("bulk_items", [])
            
#             if not name:
#                 validation_errors.append({"index": idx, "error": "Missing name"})
#                 continue
#             if not outlet:
#                 validation_errors.append({"index": idx, "error": "Missing outlet"})
#                 continue
#             if not isinstance(items, list):
#                 validation_errors.append({"index": idx, "error": "Items must be a list"})
#                 continue
#             if len(items) == 0:
#                 validation_errors.append({"index": idx, "error": "At least one item is required"})
#                 continue
                
#             # Validate items
#             item_errors = []
#             for item_idx, item in enumerate(items):
#                 if not item.get("name"):
#                     item_errors.append({"item_index": item_idx, "error": "Missing item name"})
#                 if not item.get("rate"):
#                     item_errors.append({"item_index": item_idx, "error": "Missing rate"})
#                 if not item.get("quantity"):
#                     item_errors.append({"item_index": item_idx, "error": "Missing quantity"})
#                 if not item.get("uom"):
#                     item_errors.append({"item_index": item_idx, "error": "Missing uom"})
#                 if not item.get("new_uom"):
#                     item_errors.append({"item_index": item_idx, "error": "Missing new_uom"})
#                 if not item.get("unit"):
#                     item_errors.append({"item_index": item_idx, "error": "Missing unit"})
                    
#             if item_errors:
#                 validation_errors.append({
#                     "index": idx, 
#                     "error": "Invalid items", 
#                     "item_errors": item_errors
#                 })
#                 continue
                
#             valid_recipes.append(recipe_data)
        
#         if validation_errors:
#             return jsonify({
#                 "error": "Validation failed for some recipes",
#                 "validation_errors": validation_errors,
#                 "total_recipes": len(sub_recipes),
#                 "valid_recipes": len(valid_recipes)
#             }), 400

#         mydb = get_db_connection()
#         cursor = mydb.cursor()
        
#         created_recipes = []
        
#         for recipe_data in valid_recipes:
#             name = recipe_data.get("name")
#             outlet = recipe_data.get("outlet")
#             uom = recipe_data.get("uom")
#             unit = recipe_data.get("unit")
#             items = recipe_data.get("bulk_items", [])
            
#             # Calculate total costprice for the recipe
#             total_costprice = 0
            
#             # First, calculate all items with their converted quantities and costs
#             processed_items = []
            
#             for item in items:
#                 item_name = item.get("name")
#                 rate = item.get("rate")  # Rate per unit (based on the item's unit)
#                 item_uom = item.get("uom")  # Parent recipe's uom (target unit)
#                 new_uom = item.get("new_uom")  # Original unit of the quantity
#                 original_quantity = item.get("quantity")  # Quantity in new_uom
#                 item_unit = item.get("unit", 1)  # Purchase unit (e.g., 1000 for 1kg package)
                
#                 # Step 1: Convert quantity from new_uom to item_uom if different
#                 converted_quantity = convert_quantity(original_quantity, new_uom, item_uom)
                
#                 # Step 2: Calculate rate per base unit (convert rate to per gram or per ml)
#                 # Rate is given for the purchase unit (item_unit)
#                 # For example: rate = 685.84 for unit = 1000 (1kg package)
#                 # So rate per gram = 685.84 / 1000 = 0.68584 per gram
#                 rate_per_base_unit = rate / item_unit if item_unit > 0 else rate
                
#                 # Step 3: Calculate cost for this item
#                 # Cost = rate_per_base_unit * converted_quantity
#                 calculated_cost = rate_per_base_unit * converted_quantity
                
#                 # Round to 2 decimal places for currency
#                 calculated_cost = round(calculated_cost, 2)
                
#                 # Add to total costprice
#                 total_costprice += calculated_cost
                
#                 # Store processed item with all details
#                 processed_items.append({
#                     "name": item_name,
#                     "rate": rate,
#                     "uom": item_uom,
#                     "new_uom": new_uom,
#                     "original_quantity": original_quantity,
#                     "converted_quantity": converted_quantity,
#                     "unit": item_unit,
#                     "rate_per_base_unit": rate_per_base_unit,
#                     "calculated_cost": calculated_cost
#                 })
            
#             # Round total costprice to 2 decimal places
#             total_costprice = round(total_costprice, 2)
            
#             # Insert into sub_recipe
#             cursor.execute("""
#                 INSERT INTO sub_recipe (name, outlet, uom, unit, costprice)
#                 VALUES (%s, %s, %s, %s, %s)
#             """, (name, outlet, uom, unit, total_costprice))
#             sub_recipe_id = cursor.lastrowid

#             # Insert sub_recipe items with calculated cost
#             items_inserted = 0
#             for processed_item in processed_items:
#                 cursor.execute("""
#                     INSERT INTO sub_recipe_items (
#                         sub_recipe_id, name, rate, uom, new_uom, 
#                         quantity, cost, unit
#                     )
#                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
#                 """, (
#                     sub_recipe_id, 
#                     processed_item["name"], 
#                     processed_item["rate"], 
#                     processed_item["uom"], 
#                     processed_item["new_uom"], 
#                     processed_item["converted_quantity"],  # Store converted quantity
#                     processed_item["calculated_cost"],  # Store calculated cost
#                     processed_item["unit"]
#                 ))
#                 items_inserted += 1

#             created_recipes.append({
#                 "id": sub_recipe_id,
#                 "name": name,
#                 "outlet": outlet,
#                 "items_count": items_inserted,
#                 "total_costprice": total_costprice
#             })

#         mydb.commit()
#         cursor.close()
#         mydb.close()

#         return jsonify({
#             "message": f"Successfully created {len(created_recipes)} sub-recipes",
#             "created_recipes": created_recipes,
#             "total": len(created_recipes)
#         }), 201

#     except Exception as e:
#         return jsonify({"error": str(e)}), 400


@app_file107.route("/sub-recipes/bulk-advanced", methods=["POST"])
@cross_origin()
def create_bulk_sub_recipes():
    try:
        data = request.get_json()
        token = data.get("token")
        if not token or not token_auth(token):
            return jsonify({"error": "Invalid or missing token."}), 400

        sub_recipes = data.get("sub_recipes_bulk", [])
        
        if not isinstance(sub_recipes, list) or len(sub_recipes) == 0:
            return jsonify({"error": "sub_recipes must be a non-empty list"}), 400

        # Get outlet from first recipe (assuming all recipes belong to same outlet)
        # Or you can pass outlet separately in request
        outlet = sub_recipes[0].get("outlet") if sub_recipes else None
        if not outlet:
            return jsonify({"error": "Outlet is required"}), 400

        mydb = get_db_connection()
        cursor = mydb.cursor()
        
        # ------------------------
        # DELETE existing sub-recipes for this outlet
        # ------------------------
        # First, get all sub_recipe ids for this outlet to delete their items
        cursor.execute("SELECT id FROM sub_recipe WHERE outlet = %s", (outlet,))
        existing_recipe_ids = cursor.fetchall()
        
        if existing_recipe_ids:
            # Delete items from sub_recipe_items for these recipes
            ids_tuple = tuple([id[0] for id in existing_recipe_ids])
            cursor.execute(f"DELETE FROM sub_recipe_items WHERE sub_recipe_id IN ({','.join(['%s']*len(ids_tuple))})", ids_tuple)
            
            # Delete the sub_recipes themselves
            cursor.execute(f"DELETE FROM sub_recipe WHERE outlet = %s", (outlet,))
        
        # ------------------------
        # Validate and prepare recipes (skip invalid items)
        # ------------------------
        valid_recipes = []
        skipped_items_summary = []
        
        for idx, recipe_data in enumerate(sub_recipes):
            name = recipe_data.get("name")
            recipe_outlet = recipe_data.get("outlet")
            uom = recipe_data.get("uom")
            unit = recipe_data.get("unit")
            items = recipe_data.get("bulk_items", [])
            
            # Skip if essential fields are missing
            if not name:
                skipped_items_summary.append({
                    "index": idx,
                    "recipe_name": "Unnamed",
                    "error": "Missing name, recipe skipped"
                })
                continue
                
            if not recipe_outlet:
                skipped_items_summary.append({
                    "index": idx,
                    "recipe_name": name,
                    "error": "Missing outlet, recipe skipped"
                })
                continue
            
            if recipe_outlet != outlet:
                skipped_items_summary.append({
                    "index": idx,
                    "recipe_name": name,
                    "error": f"Outlet mismatch. Expected {outlet}, got {recipe_outlet}, recipe skipped"
                })
                continue
            
            if not isinstance(items, list):
                skipped_items_summary.append({
                    "index": idx,
                    "recipe_name": name,
                    "error": "Items must be a list, recipe skipped"
                })
                continue
            
            # Process items - skip invalid ones
            valid_items = []
            skipped_items = []
            
            for item_idx, item in enumerate(items):
                item_name = item.get("name")
                rate = item.get("rate")
                quantity = item.get("quantity")
                item_uom = item.get("uom")  # Target UOM
                new_uom = item.get("new_uom")  # Source UOM
                item_unit = item.get("unit", 1)
                
                # Check required fields
                missing_fields = []
                if not item_name:
                    missing_fields.append("name")
                if not rate:
                    missing_fields.append("rate")
                if not quantity:
                    missing_fields.append("quantity")
                if not item_uom:
                    missing_fields.append("uom")
                if not new_uom:
                    missing_fields.append("new_uom")
                if not item_unit:
                    missing_fields.append("unit")
                
                if missing_fields:
                    skipped_items.append({
                        "item_index": item_idx,
                        "item_name": item_name or "Unknown",
                        "missing_fields": missing_fields,
                        "error": f"Missing required fields: {', '.join(missing_fields)}"
                    })
                    continue
                
                # Validate numeric values
                try:
                    rate = float(rate)
                    quantity = float(quantity)
                    item_unit = float(item_unit)
                    
                    if rate <= 0:
                        skipped_items.append({
                            "item_index": item_idx,
                            "item_name": item_name,
                            "error": "Rate must be greater than 0"
                        })
                        continue
                        
                    if quantity <= 0:
                        skipped_items.append({
                            "item_index": item_idx,
                            "item_name": item_name,
                            "error": "Quantity must be greater than 0"
                        })
                        continue
                        
                    if item_unit <= 0:
                        skipped_items.append({
                            "item_index": item_idx,
                            "item_name": item_name,
                            "error": "Unit must be greater than 0"
                        })
                        continue
                        
                except (ValueError, TypeError):
                    skipped_items.append({
                        "item_index": item_idx,
                        "item_name": item_name,
                        "error": "Invalid numeric value for rate, quantity, or unit"
                    })
                    continue
                
                # All validations passed
                valid_items.append({
                    "name": item_name,
                    "rate": rate,
                    "quantity": quantity,
                    "uom": item_uom,
                    "new_uom": new_uom,
                    "unit": item_unit
                })
            
            # Even if no valid items, we still create the recipe (just with zero cost)
            valid_recipes.append({
                "name": name,
                "outlet": recipe_outlet,
                "uom": uom,
                "unit": unit,
                "items": valid_items,
                "original_index": idx,
                "skipped_items": skipped_items
            })
            
            if skipped_items:
                skipped_items_summary.append({
                    "index": idx,
                    "recipe_name": name,
                    "skipped_items_count": len(skipped_items),
                    "skipped_items": skipped_items,
                    "valid_items_count": len(valid_items)
                })
        
        if not valid_recipes:
            cursor.close()
            mydb.close()
            return jsonify({
                "error": "No valid recipes to create",
                "skipped_recipes": skipped_items_summary
            }), 400

        # ------------------------
        # Insert new recipes
        # ------------------------
        created_recipes = []
        
        for recipe_data in valid_recipes:
            name = recipe_data["name"]
            recipe_outlet = recipe_data["outlet"]
            uom = recipe_data.get("uom")
            unit = recipe_data.get("unit", 1)
            items = recipe_data["items"]
            
            # Calculate total costprice for the recipe
            total_costprice = 0
            
            # Process all valid items
            processed_items = []
            
            for item in items:
                item_name = item["name"]
                rate = item["rate"]
                item_uom = item["uom"]
                new_uom = item["new_uom"]
                original_quantity = item["quantity"]
                item_unit = item["unit"]
                
                # Step 1: Convert quantity from new_uom to item_uom if different
                converted_quantity = convert_quantity(original_quantity, new_uom, item_uom)
                
                # Step 2: Calculate rate per base unit
                rate_per_base_unit = rate / item_unit if item_unit > 0 else rate
                
                # Step 3: Calculate cost for this item
                calculated_cost = rate_per_base_unit * converted_quantity
                calculated_cost = round(calculated_cost, 2)
                
                # Add to total costprice
                total_costprice += calculated_cost
                
                # Store processed item
                processed_items.append({
                    "name": item_name,
                    "rate": rate,
                    "uom": item_uom,
                    "new_uom": new_uom,
                    "original_quantity": original_quantity,
                    "converted_quantity": converted_quantity,
                    "unit": item_unit,
                    "rate_per_base_unit": rate_per_base_unit,
                    "calculated_cost": calculated_cost
                })
            
            # Round total costprice to 2 decimal places
            total_costprice = round(total_costprice, 2)
            
            # Insert into sub_recipe
            cursor.execute("""
                INSERT INTO sub_recipe (name, outlet, uom, unit, costprice)
                VALUES (%s, %s, %s, %s, %s)
            """, (name, recipe_outlet, uom, unit, total_costprice))
            sub_recipe_id = cursor.lastrowid
            
            # Insert sub_recipe items with calculated cost
            items_inserted = 0
            for processed_item in processed_items:
                cursor.execute("""
                    INSERT INTO sub_recipe_items (
                        sub_recipe_id, name, rate, uom, new_uom, 
                        quantity, cost, unit
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    sub_recipe_id, 
                    processed_item["name"], 
                    processed_item["rate"], 
                    processed_item["uom"], 
                    processed_item["new_uom"], 
                    processed_item["converted_quantity"],
                    processed_item["calculated_cost"],
                    processed_item["unit"]
                ))
                items_inserted += 1
            
            created_recipes.append({
                "id": sub_recipe_id,
                "name": name,
                "outlet": recipe_outlet,
                "items_count": items_inserted,
                "skipped_items_count": len(recipe_data.get("skipped_items", [])),
                "total_costprice": total_costprice
            })
        
        mydb.commit()
        cursor.close()
        mydb.close()
        
        response = {
            "message": f"Successfully created {len(created_recipes)} sub-recipes",
            "created_recipes": created_recipes,
            "total_created": len(created_recipes),
            "deleted_existing": len(existing_recipe_ids) if existing_recipe_ids else 0
        }
        
        if skipped_items_summary:
            response["warning"] = "Some items were skipped due to validation errors"
            response["skipped_items_summary"] = skipped_items_summary
        
        return jsonify(response), 201
        
    except Exception as e:
        if mydb:
            mydb.rollback()
        return jsonify({"error": str(e)}), 400





def normalize_unit(unit):
    """
    Normalize various unit variations to standard unit names
    """
    if not unit:
        return None
    
    # Convert to lowercase for case-insensitive matching
    unit_lower = str(unit).lower().strip()
    
    # Weight units - Kilograms
    kg_variations = ['kg', 'kgs', 'kilogram', 'kilograms']
    if unit_lower in kg_variations:
        return 'Kg'
    
    # Weight units - Grams
    gram_variations = ['g', 'gram', 'grams', 'gm', 'gms', 'grm', 'grms']
    if unit_lower in gram_variations:
        return 'Grms'
    
    # Volume units - Liters
    liter_variations = ['l', 'ltr', 'ltrs', 'liter', 'liters', 'litre', 'litres']
    if unit_lower in liter_variations:
        return 'LTR'
    
    # Volume units - Milliliters
    milliliter_variations = ['ml', 'milliliter', 'milliliters', 'millilitre', 'millilitres', 'mls']
    if unit_lower in milliliter_variations:
        return 'ml'
    
    # If no match found, return original (will be handled by conversion)
    return unit


def convert_quantity(quantity, from_uom, to_uom):
    """
    Convert quantity from one unit to another with support for multiple unit variations
    """
    if not quantity:
        return 0
    
    # Normalize units to standard format
    from_uom_normalized = normalize_unit(from_uom)
    to_uom_normalized = normalize_unit(to_uom)
    
    # If units are the same after normalization, no conversion needed
    if from_uom_normalized == to_uom_normalized:
        return quantity
    
    # Conversion factors to base units (all weights to grams, all volumes to milliliters)
    # Base units: 'Grms' for weight, 'ml' for volume
    
    # Check if converting between weight and volume (not allowed)
    weight_units = ['Kg', 'Grms']
    volume_units = ['LTR', 'ml']
    
    if (from_uom_normalized in weight_units and to_uom_normalized in volume_units) or \
       (from_uom_normalized in volume_units and to_uom_normalized in weight_units):
        # Cannot convert between weight and volume
        print(f"Warning: Cannot convert between weight ({from_uom}) and volume ({to_uom})")
        return quantity
    
    # Define conversion to base units
    def to_base_unit(value, unit):
        if unit == 'Grms':  # Grams to grams
            return value
        elif unit == 'Kg':  # Kilograms to grams
            return value * 1000
        elif unit == 'ml':  # Milliliters to milliliters
            return value
        elif unit == 'LTR':  # Liters to milliliters
            return value * 1000
        else:
            # Unknown unit, return as is
            return value
    
    def from_base_unit(value, unit):
        if unit == 'Grms':  # Grams from grams
            return value
        elif unit == 'Kg':  # Kilograms from grams
            return value / 1000
        elif unit == 'ml':  # Milliliters from milliliters
            return value
        elif unit == 'LTR':  # Liters from milliliters
            return value / 1000
        else:
            # Unknown unit, return as is
            return value
    
    # Convert to base unit first
    base_quantity = to_base_unit(quantity, from_uom_normalized)
    
    # Then convert from base unit to target unit
    converted_quantity = from_base_unit(base_quantity, to_uom_normalized)
    
    # Round to reasonable decimal places
    return round(converted_quantity, 6)


# Optional: Function to verify calculations
def verify_cost_calculation():
    """
    Test function to verify cost calculations
    """
    # Test Case 1: Moca powder
    # Coca Powder: rate=685.84, unit=1000 (1kg), quantity=1000grms, uom=Grms
    rate = 685.84
    unit = 1000
    quantity = 1000
    rate_per_gram = rate / unit  # 0.68584
    calculated_cost = rate_per_gram * quantity  # 685.84
    print(f"Moca Powder Cost: {calculated_cost}")  # Should be 685.84
    
    # Test Case 2: Icing Sugar
    # rate=148, unit=1000 (1kg), quantity=800grms, uom=Grms
    rate = 148
    unit = 1000
    quantity = 800
    rate_per_gram = rate / unit  # 0.148
    calculated_cost = rate_per_gram * quantity  # 118.4
    print(f"Icing Sugar Cost: {calculated_cost}")  # Should be 118.4
    
    # Test Case 3: Kikomen Sauce (with conversion)
    # rate=850, unit=1000 (1L), quantity=1000ml, new_uom=ml, uom=LTR
    # First convert: 1000ml to LTR = 1 LTR
    rate = 850
    unit = 1000
    original_quantity = 1000
    converted_quantity = convert_quantity(original_quantity, 'ml', 'LTR')  # 1.0
    rate_per_liter = rate / unit  # 0.85 per ml? Wait, careful!
    # Actually: rate=850 for 1000ml package, so rate per ml = 850/1000 = 0.85
    # Then cost = 0.85 * 1000ml = 850, OR cost = 850/L * 1L = 850
    rate_per_base = rate / unit  # 0.85 per ml
    calculated_cost = rate_per_base * converted_quantity * 1000  # Need to be careful
    # Better approach:
    # If converted to LTR, we need rate per LTR
    rate_per_liter = rate  # Since unit=1000ml = 1L, rate is already per liter
    calculated_cost_correct = rate_per_liter * converted_quantity  # 850 * 1 = 850
    print(f"Kikomen Sauce Cost: {calculated_cost_correct}")  # Should be 850
    
    return "Test complete"


@app_file107.route("/sub-recipes/bulk", methods=["POST"])
@cross_origin()
def create_bulk_sub_recipes_simple():
    """
    Simple bulk sub-recipe creation without any calculations.
    Frontend should provide all pre-calculated values.
    """
    mydb = None
    cursor = None
    try:
        data = request.get_json()
        token = data.get("token")
        if not token or not token_auth(token):
            return jsonify({"error": "Invalid or missing token."}), 400

        sub_recipes = data.get("sub_recipes_bulk", [])
        
        if not isinstance(sub_recipes, list) or len(sub_recipes) == 0:
            return jsonify({"error": "sub_recipes must be a non-empty list"}), 400

        # Get outlet from first recipe (assuming all recipes belong to same outlet)
        outlet = sub_recipes[0].get("outlet") if sub_recipes else None
        if not outlet:
            return jsonify({"error": "Outlet is required"}), 400

        mydb = get_db_connection()
        cursor = mydb.cursor()
        
        # ------------------------
        # DELETE existing sub-recipes for this outlet
        # ------------------------
        cursor.execute("SELECT id FROM sub_recipe WHERE outlet = %s", (outlet,))
        existing_recipe_ids = cursor.fetchall()
        
        if existing_recipe_ids:
            # Delete items from sub_recipe_items for these recipes
            ids_tuple = tuple([id[0] for id in existing_recipe_ids])
            cursor.execute(f"DELETE FROM sub_recipe_items WHERE sub_recipe_id IN ({','.join(['%s']*len(ids_tuple))})", ids_tuple)
            
            # Delete the sub_recipes themselves
            cursor.execute("DELETE FROM sub_recipe WHERE outlet = %s", (outlet,))
        
        # ------------------------
        # Validate and save recipes (no calculations)
        # ------------------------
        valid_recipes = []
        skipped_recipes_summary = []
        created_recipes = []
        
        for idx, recipe_data in enumerate(sub_recipes):
            name = recipe_data.get("name")
            recipe_outlet = recipe_data.get("outlet")
            uom = recipe_data.get("uom")
            unit = recipe_data.get("unit", 1)
            costprice = recipe_data.get("costprice", 0)  # Frontend provides total cost
            items = recipe_data.get("bulk_items", [])
            
            # Validate required fields
            if not name:
                skipped_recipes_summary.append({
                    "index": idx,
                    "recipe_name": "Unnamed",
                    "error": "Missing name, recipe skipped"
                })
                continue
                
            if not recipe_outlet:
                skipped_recipes_summary.append({
                    "index": idx,
                    "recipe_name": name,
                    "error": "Missing outlet, recipe skipped"
                })
                continue
            
            if recipe_outlet != outlet:
                skipped_recipes_summary.append({
                    "index": idx,
                    "recipe_name": name,
                    "error": f"Outlet mismatch. Expected {outlet}, got {recipe_outlet}, recipe skipped"
                })
                continue
            
            if not isinstance(items, list):
                skipped_recipes_summary.append({
                    "index": idx,
                    "recipe_name": name,
                    "error": "Items must be a list, recipe skipped"
                })
                continue
            
            # Validate items (basic validation only)
            valid_items = []
            skipped_items = []
            
            for item_idx, item in enumerate(items):
                item_name = item.get("name")
                rate = item.get("rate")
                quantity = item.get("quantity")  # This is already converted quantity
                cost = item.get("cost")  # Frontend provides pre-calculated cost
                uom = item.get("uom")
                new_uom = item.get("new_uom")
                unit = item.get("unit", 1)
                
                # Check required fields
                missing_fields = []
                if not item_name:
                    missing_fields.append("name")
                if rate is None:
                    missing_fields.append("rate")
                if quantity is None:
                    missing_fields.append("quantity")
                if cost is None:
                    missing_fields.append("cost")
                if not uom:
                    missing_fields.append("uom")
                if not new_uom:
                    missing_fields.append("new_uom")
                
                if missing_fields:
                    skipped_items.append({
                        "item_index": item_idx,
                        "item_name": item_name or "Unknown",
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
                    
                    if rate < 0:
                        skipped_items.append({
                            "item_index": item_idx,
                            "item_name": item_name,
                            "error": "Rate cannot be negative"
                        })
                        continue
                        
                    if quantity < 0:
                        skipped_items.append({
                            "item_index": item_idx,
                            "item_name": item_name,
                            "error": "Quantity cannot be negative"
                        })
                        continue
                        
                    if cost < 0:
                        skipped_items.append({
                            "item_index": item_idx,
                            "item_name": item_name,
                            "error": "Cost cannot be negative"
                        })
                        continue
                        
                except (ValueError, TypeError):
                    skipped_items.append({
                        "item_index": item_idx,
                        "item_name": item_name,
                        "error": "Invalid numeric value for rate, quantity, cost, or unit"
                    })
                    continue
                
                # All validations passed - store as-is
                valid_items.append({
                    "name": item_name,
                    "rate": rate,
                    "quantity": quantity,  # Already converted quantity
                    "cost": cost,  # Pre-calculated cost
                    "uom": uom,
                    "new_uom": new_uom,
                    "unit": unit
                })
            
            # Store recipe even if no items (just with zero cost)
            valid_recipes.append({
                "name": name,
                "outlet": recipe_outlet,
                "uom": uom,
                "unit": unit,
                "costprice": costprice,  # Frontend provides total cost
                "items": valid_items,
                "original_index": idx,
                "skipped_items": skipped_items
            })
            
            if skipped_items:
                skipped_recipes_summary.append({
                    "index": idx,
                    "recipe_name": name,
                    "skipped_items_count": len(skipped_items),
                    "skipped_items": skipped_items,
                    "valid_items_count": len(valid_items)
                })
        
        if not valid_recipes:
            cursor.close()
            mydb.close()
            return jsonify({
                "error": "No valid recipes to create",
                "skipped_recipes": skipped_recipes_summary
            }), 400

        # ------------------------
        # Insert recipes without calculations
        # ------------------------
        for recipe_data in valid_recipes:
            name = recipe_data["name"]
            recipe_outlet = recipe_data["outlet"]
            uom = recipe_data.get("uom")
            unit = recipe_data.get("unit", 1)
            costprice = recipe_data.get("costprice", 0)
            items = recipe_data["items"]
            
            # Insert into sub_recipe
            cursor.execute("""
                INSERT INTO sub_recipe (name, outlet, uom, unit, costprice)
                VALUES (%s, %s, %s, %s, %s)
            """, (name, recipe_outlet, uom, unit, costprice))
            sub_recipe_id = cursor.lastrowid
            
            # Insert sub_recipe items directly (no calculations)
            items_inserted = 0
            for item in items:
                cursor.execute("""
                    INSERT INTO sub_recipe_items (
                        sub_recipe_id, name, rate, uom, new_uom, 
                        quantity, cost, unit
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    sub_recipe_id, 
                    item["name"], 
                    item["rate"], 
                    item["uom"], 
                    item["new_uom"], 
                    item["quantity"],  # Direct use - no conversion
                    item["cost"],      # Direct use - no calculation
                    item["unit"]
                ))
                items_inserted += 1
            
            created_recipes.append({
                "id": sub_recipe_id,
                "name": name,
                "outlet": recipe_outlet,
                "items_count": items_inserted,
                "skipped_items_count": len(recipe_data.get("skipped_items", [])),
                "total_costprice": costprice
            })
        
        mydb.commit()
        cursor.close()
        mydb.close()
        
        response = {
            "message": f"Successfully created {len(created_recipes)} sub-recipes",
            "created_recipes": created_recipes,
            "total_created": len(created_recipes),
            "deleted_existing": len(existing_recipe_ids) if existing_recipe_ids else 0
        }
        
        if skipped_recipes_summary:
            response["warning"] = "Some items were skipped due to validation errors"
            response["skipped_items_summary"] = skipped_recipes_summary
        
        return jsonify(response), 201
        
    except Exception as e:
        if mydb:
            mydb.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        if cursor:
            cursor.close()
        if mydb:
            mydb.close()