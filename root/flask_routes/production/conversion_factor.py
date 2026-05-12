from flask import Blueprint, jsonify, request
import mysql.connector
import os
from dotenv import load_dotenv
from flask_cors import cross_origin
from root.auth.check import token_auth

load_dotenv()

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("host"),
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )

app_file232 = Blueprint('app_file232', __name__)

@app_file232.route("/conversionfactor", methods=["POST"])
@cross_origin()
def create_conversion_factor():

    mydb = None
    cursor = None

    try:

        data = request.get_json()

        token = data.get("token")

        if not token or not token_auth(token):
            return jsonify({"error": "Invalid or missing token"}), 400

        outlet = data.get("outlet")
        conversion_factors = data.get("conversion_factors", [])

        if not outlet:
            return jsonify({"error": "Outlet is required"}), 400

        if not conversion_factors or not isinstance(conversion_factors, list):
            return jsonify({"error": "conversion_factors must be a list"}), 400

        mydb = get_db_connection()
        cursor = mydb.cursor(dictionary=True)

        results = []

        for item in conversion_factors:

            production_item_id = item.get("production_item_id")
            production_recipe_id = item.get("production_recipe_id")
            factor = item.get("factor")

            # Validation
            if not production_item_id or not production_recipe_id or factor is None:
                results.append({
                    "production_item_id": production_item_id,
                    "status": "failed",
                    "message": "Missing required fields"
                })
                continue

            if float(factor) <= 0:
                results.append({
                    "production_item_id": production_item_id,
                    "status": "failed",
                    "message": "Factor must be greater than 0"
                })
                continue

            # Validate stock item
            cursor.execute("""
                SELECT id, CurrentLevel
                FROM stock_statement
                WHERE id = %s
            """, (production_item_id,))

            stock_item = cursor.fetchone()

            if not stock_item:
                results.append({
                    "production_item_id": production_item_id,
                    "status": "failed",
                    "message": "Invalid production_item_id"
                })
                continue

            # Validate recipe
            cursor.execute("""
                SELECT id, SellingPrice
                FROM recipe
                WHERE id = %s
            """, (production_recipe_id,))

            recipe_data = cursor.fetchone()

            if not recipe_data:
                results.append({
                    "production_recipe_id": production_recipe_id,
                    "status": "failed",
                    "message": "Invalid production_recipe_id"
                })
                continue

            # Check existing
            cursor.execute("""
                SELECT id
                FROM conversionfactor
                WHERE production_item_id = %s
                AND production_recipe_id = %s
                AND outlet = %s
            """, (
                production_item_id,
                production_recipe_id,
                outlet
            ))

            existing = cursor.fetchone()

            if existing:

                cursor.execute("""
                    UPDATE conversionfactor
                    SET factor = %s
                    WHERE id = %s
                """, (
                    factor,
                    existing["id"]
                ))

                action = "updated"

            else:

                cursor.execute("""
                    INSERT INTO conversionfactor
                    (
                        production_item_id,
                        production_recipe_id,
                        factor,
                        outlet
                    )
                    VALUES (%s, %s, %s, %s)
                """, (
                    production_item_id,
                    production_recipe_id,
                    factor,
                    outlet
                ))

                action = "created"

            # -----------------------------
            # UPDATE STOCK RATE + TOTAL
            # -----------------------------

            selling_price = float(recipe_data.get("SellingPrice") or 0)

            calculated_rate = round(
                selling_price / float(factor),
                2
            )

            current_level = float(stock_item.get("CurrentLevel") or 0)

            total = round(
                calculated_rate * current_level,
                2
            )

            cursor.execute("""
                UPDATE stock_statement
                SET
                    Rate = %s,
                    Total = %s
                WHERE id = %s
            """, (
                calculated_rate,
                total,
                production_item_id
            ))

            results.append({
                "production_item_id": production_item_id,
                "production_recipe_id": production_recipe_id,
                "status": "success",
                "message": f"Conversion factor {action}",
                "rate": calculated_rate,
                "total": total
            })

        mydb.commit()

        return jsonify({
            "message": "Conversion factors processed successfully",
            "results": results
        }), 201

    except Exception as e:

        if mydb:
            mydb.rollback()

        return jsonify({"error": str(e)}), 400

    finally:

        if cursor:
            cursor.close()

        if mydb:
            mydb.close()


# @app_file232.route("/conversionfactor", methods=["GET"])
# @cross_origin()
# def get_conversion_factors():
#     mydb = None
#     cursor = None

#     try:
#         mydb = get_db_connection()
#         cursor = mydb.cursor(dictionary=True)

#         production_item_id = request.args.get("production_item_id")  # Changed from menu_recipe_id
#         production_recipe_id = request.args.get("production_recipe_id")

#         query = "SELECT * FROM conversionfactor WHERE 1=1"
#         params = []

#         if production_item_id:
#             query += " AND production_item_id = %s"
#             params.append(production_item_id)

#         if production_recipe_id:
#             query += " AND production_recipe_id = %s"
#             params.append(production_recipe_id)

#         cursor.execute(query, params)
#         result = cursor.fetchall()

#         return jsonify(result), 200

#     except Exception as e:
#         return jsonify({"error": str(e)}), 400

#     finally:
#         if cursor:
#             cursor.close()
#         if mydb:
#             mydb.close()


# @app_file232.route("/conversionfactor", methods=["GET"])
# @cross_origin()
# def get_conversion_factors():

#     mydb = None
#     cursor = None

#     try:

#         mydb = get_db_connection()
#         cursor = mydb.cursor(dictionary=True)

#         production_item_id = request.args.get("production_item_id")
#         production_recipe_id = request.args.get("production_recipe_id")
#         outlet = request.args.get("outlet")

#         query = """
#             SELECT *
#             FROM conversionfactor
#             WHERE 1=1
#         """

#         params = []

#         # Filter by outlet
#         if outlet:
#             query += " AND outlet = %s"
#             params.append(outlet)

#         # Filter by production item
#         if production_item_id:
#             query += " AND production_item_id = %s"
#             params.append(production_item_id)

#         # Filter by production recipe
#         if production_recipe_id:
#             query += " AND production_recipe_id = %s"
#             params.append(production_recipe_id)

#         query += " ORDER BY id DESC"

#         cursor.execute(query, params)

#         result = cursor.fetchall()

#         return jsonify(result), 200

#     except Exception as e:

#         return jsonify({"error": str(e)}), 400

#     finally:

#         if cursor:
#             cursor.close()

#         if mydb:
#             mydb.close()


@app_file232.route("/conversionfactor", methods=["GET"])
@cross_origin()
def get_conversion_factors():

    mydb = None
    cursor = None

    try:

        mydb = get_db_connection()
        cursor = mydb.cursor(dictionary=True)

        production_item_id = request.args.get("production_item_id")
        production_recipe_id = request.args.get("production_recipe_id")
        outlet = request.args.get("outlet")
        include_recipe_details = request.args.get("include_recipe_details", "true").lower() == "true"

        # Main query for conversion factors
        query = """
            SELECT
                cf.*,
                ss.ItemName AS production_item_name,
                ss.UOM AS production_item_uom,
                ss.CurrentLevel AS production_item_current_stock,
                r.name AS production_recipe_name,
                r.SellingPrice AS production_recipe_selling_price,
                r.costprice AS production_recipe_cost_price,
                r.ItemType AS production_recipe_item_type
            FROM conversionfactor cf
            LEFT JOIN stock_statement ss ON ss.id = cf.production_item_id
            LEFT JOIN recipe r ON r.id = cf.production_recipe_id
            WHERE 1=1
        """

        params = []

        if outlet:
            query += " AND cf.outlet = %s"
            params.append(outlet)

        if production_item_id:
            query += " AND cf.production_item_id = %s"
            params.append(production_item_id)

        if production_recipe_id:
            query += " AND cf.production_recipe_id = %s"
            params.append(production_recipe_id)

        query += " ORDER BY cf.id DESC"

        cursor.execute(query, params)
        conversion_factors = cursor.fetchall()

        # If recipe details are requested, fetch them for each conversion factor
        if include_recipe_details and conversion_factors:
            for cf in conversion_factors:
                recipe_id = cf.get("production_recipe_id")
                factor = float(cf.get("factor", 1))
                
                if recipe_id:
                    # Fetch recipe items (ingredients)
                    cursor.execute("""
                        SELECT 
                            ri.id,
                            ri.name,
                            ri.quantity,
                            ri.uom,
                            ri.new_uom,
                            ri.rate,
                            ri.cost,
                            ri.unit
                        FROM recipe_items ri
                        WHERE ri.recipe_id = %s
                        ORDER BY ri.name
                    """, (recipe_id,))
                    
                    recipe_items = cursor.fetchall()
                    
                    # Divide quantities by conversion factor
                    for item in recipe_items:
                        original_quantity = float(item.get("quantity", 0))
                        item["original_quantity"] = original_quantity
                        item["quantity_per_unit"] = round(original_quantity / factor, 6) if factor > 0 else 0
                        item["quantity"] = item["quantity_per_unit"]  # Replace with divided value
                        
                        # Also adjust cost if needed
                        if item.get("cost"):
                            item["cost_per_unit"] = round(float(item["cost"]) / factor, 6) if factor > 0 else 0
                    
                    # Fetch sub-recipes links
                    cursor.execute("""
                        SELECT 
                            rs.id,
                            rs.sub_recipe_id,
                            rs.quantity,
                            rs.uom,
                            rs.new_uom,
                            rs.unit,
                            rs.costprice,
                            rs.rate,
                            sr.name AS sub_recipe_name,
                            sr.uom AS sub_recipe_uom
                        FROM recipe_subrecipes rs
                        JOIN sub_recipe sr ON rs.sub_recipe_id = sr.id
                        WHERE rs.recipe_id = %s
                    """, (recipe_id,))
                    
                    sub_recipes = cursor.fetchall()
                    
                    # Process sub-recipes and their items
                    for sub_recipe in sub_recipes:
                        sub_recipe_id = sub_recipe.get("sub_recipe_id")
                        sub_recipe_qty = float(sub_recipe.get("quantity", 0))
                        
                        # Adjust sub-recipe quantity by conversion factor
                        sub_recipe["original_quantity"] = sub_recipe_qty
                        sub_recipe["quantity_per_unit"] = round(sub_recipe_qty / factor, 6) if factor > 0 else 0
                        sub_recipe["quantity"] = sub_recipe["quantity_per_unit"]
                        
                        # Fetch items from sub-recipe
                        cursor.execute("""
                            SELECT 
                                sri.id,
                                sri.name,
                                sri.quantity,
                                sri.uom,
                                sri.new_uom,
                                sri.rate,
                                sri.cost,
                                sri.unit
                            FROM sub_recipe_items sri
                            WHERE sri.sub_recipe_id = %s
                            ORDER BY sri.name
                        """, (sub_recipe_id,))
                        
                        sub_recipe_items_data = cursor.fetchall()
                        
                        # Divide sub-recipe item quantities by conversion factor
                        for item in sub_recipe_items_data:
                            original_quantity = float(item.get("quantity", 0))
                            item["original_quantity"] = original_quantity
                            # Multiply by sub-recipe quantity first, then divide by factor
                            item["quantity_per_unit"] = round((original_quantity * sub_recipe_qty) / factor, 6) if factor > 0 else 0
                            item["quantity"] = item["quantity_per_unit"]
                        
                        sub_recipe["items"] = sub_recipe_items_data
                    
                    # Add all recipe details to the conversion factor response
                    cf["recipe_details"] = {
                        "recipe_id": recipe_id,
                        "recipe_name": cf.get("production_recipe_name"),
                        "conversion_factor": factor,
                        "items": recipe_items,
                        "sub_recipes": sub_recipes,
                        "total_ingredients": len(recipe_items),
                        "total_sub_recipes": len(sub_recipes)
                    }

        return jsonify(conversion_factors), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

    finally:
        if cursor:
            cursor.close()
        if mydb:
            mydb.close()


@app_file232.route("/conversionfactor/<int:id>", methods=["PUT"])
@cross_origin()
def update_conversion_factor(id):
    mydb = None
    cursor = None

    try:
        data = request.get_json()

        token = data.get("token")
        if not token or not token_auth(token):
            return jsonify({"error": "Invalid or missing token"}), 400

        production_item_id = data.get("production_item_id")  # Changed from menu_recipe_id
        production_recipe_id = data.get("production_recipe_id")
        factor = data.get("factor")
        outlet = data.get("outlet")

        if not production_item_id or not production_recipe_id or factor is None or not outlet:
            return jsonify({"error": "Missing required fields"}), 400

        mydb = get_db_connection()
        cursor = mydb.cursor(dictionary=True)

        # ✅ Validate record exists
        cursor.execute("SELECT id FROM conversionfactor WHERE id = %s", (id,))
        existing = cursor.fetchone()

        if not existing:
            return jsonify({"error": "Conversion factor not found"}), 404

        # Optional: validate recipe IDs
        cursor.execute("SELECT id FROM recipe WHERE id = %s", (production_item_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Invalid production_item_id"}), 400

        cursor.execute("SELECT id FROM recipe WHERE id = %s", (production_recipe_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Invalid production_recipe_id"}), 400

        # Update
        cursor.execute("""
            UPDATE conversionfactor
            SET production_item_id = %s,
                production_recipe_id = %s,
                factor = %s,
                outlet = %s
            WHERE id = %s
        """, (
            production_item_id,
            production_recipe_id,
            factor,
            outlet,
            id
        ))

        mydb.commit()

        return jsonify({"message": "Conversion factor updated successfully"}), 200

    except Exception as e:
        if mydb:
            mydb.rollback()
        return jsonify({"error": str(e)}), 400

    finally:
        if cursor:
            cursor.close()
        if mydb:
            mydb.close()


@app_file232.route("/conversionfactor/<int:id>", methods=["DELETE"])
@cross_origin()
def delete_conversion_factor(id):
    mydb = None
    cursor = None

    try:
        data = request.get_json()

        token = data.get("token")
        if not token or not token_auth(token):
            return jsonify({"error": "Invalid or missing token"}), 400

        mydb = get_db_connection()
        cursor = mydb.cursor()

        # Check if exists
        cursor.execute("SELECT id FROM conversionfactor WHERE id = %s", (id,))
        existing = cursor.fetchone()

        if not existing:
            return jsonify({"error": "Conversion factor not found"}), 404

        # Delete
        cursor.execute("DELETE FROM conversionfactor WHERE id = %s", (id,))

        mydb.commit()

        return jsonify({"message": "Conversion factor deleted successfully"}), 200

    except Exception as e:
        if mydb:
            mydb.rollback()
        return jsonify({"error": str(e)}), 400

    finally:
        if cursor:
            cursor.close()
        if mydb:
            mydb.close()