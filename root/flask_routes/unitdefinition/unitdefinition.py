from flask import Blueprint, jsonify, request
import mysql.connector
import os
from dotenv import load_dotenv
from flask_cors import cross_origin
from root.auth.check import token_auth

load_dotenv()

app_file200 = Blueprint('app_file200', __name__)

# Database connection helper
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("host"),
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )

# ----------------------- POST & GET ------------------------
# @app_file200.route("/unit-definitions", methods=["POST", "GET"])
# @cross_origin()
# def manage_unit_definitions():
#     try:
#         if request.method == "POST":
#             data = request.get_json()

#             token = data.get("token")
#             if not token or not token_auth(token):
#                 return jsonify({"error": "Invalid or missing token."}), 400

#             items = data.get("items")
#             if not isinstance(items, list):
#                 return jsonify({"error": "Expected 'items' to be a list."}), 400

#             mydb = get_db_connection()
#             cursor = mydb.cursor()

#             for item in items:
#                 name = item.get("name")
#                 unit = item.get("unit")
#                 uom = item.get("uom")
#                 rate = item.get("rate")

#                 if not all([name, unit, uom]):
#                     continue  # skip invalid item

#                 cursor.execute("""
#                     INSERT INTO tblunitdefinition (name, unit, uom, rate)
#                     VALUES (%s, %s, %s, %s)
#                 """, (name, unit, uom, rate))

#             mydb.commit()
#             cursor.close()
#             mydb.close()

#             return jsonify({"message": "Unit definitions added successfully."}), 201

#         elif request.method == "GET":
#             mydb = get_db_connection()
#             cursor = mydb.cursor(dictionary=True)

#             cursor.execute("SELECT * FROM tblunitdefinition")
#             result = cursor.fetchall()

#             cursor.close()
#             mydb.close()
#             return jsonify(result)

#     except Exception as e:
#         return jsonify({"error": str(e)}), 400


# # ----------------------- PUT & DELETE ------------------------
# @app_file200.route("/unit-definition/<int:id>", methods=["PUT", "DELETE"])
# @cross_origin()
# def update_or_delete_unit(id):
#     try:
#         data = request.get_json()
#         token = data.get("token")
#         if not token or not token_auth(token):
#             return jsonify({"error": "Invalid or missing token."}), 400

#         mydb = get_db_connection()
#         cursor = mydb.cursor()

#         if request.method == "PUT":
#             name = data.get("name")
#             unit = data.get("unit")
#             uom = data.get("uom")
#             rate = data.get("rate")

#             if not all([name, unit, uom, rate]):
#                 return jsonify({"error": "Missing fields"}), 400

#             cursor.execute("""
#                 UPDATE tblunitdefinition
#                 SET name = %s, unit = %s, uom = %s, rate = %s
#                 WHERE id = %s
#             """, (name, unit, uom, rate, id))
#             mydb.commit()
#             message = "Unit definition updated."

#         elif request.method == "DELETE":
#             cursor.execute("DELETE FROM tblunitdefinition WHERE id = %s", (id,))
#             mydb.commit()
#             message = "Unit definition deleted."

#         cursor.close()
#         mydb.close()
#         return jsonify({"message": message})

#     except Exception as e:
#         return jsonify({"error": str(e)}), 400


@app_file200.route("/unit-definitions", methods=["POST", "GET"])
@cross_origin()
def manage_unit_definitions():
    try:
        if request.method == "POST":
            data = request.get_json()

            token = data.get("token")
            if not token or not token_auth(token):
                return jsonify({"error": "Invalid or missing token."}), 400

            items = data.get("items")
            outlet = data.get("outlet")
            if not isinstance(items, list) or not outlet:
                return jsonify({"error": "Expected 'items' to be a list and 'outlet' to be provided."}), 400

            mydb = get_db_connection()
            cursor = mydb.cursor()

            for item in items:
                name = item.get("name")
                unit = item.get("unit")
                uom = item.get("uom")
                rate = item.get("rate")

                if not all([name, unit, uom]):
                    continue  # skip invalid item

                # cursor.execute("""
                #     INSERT INTO tblunitdefinition (name, unit, uom, rate, outlet)
                #     VALUES (%s, %s, %s, %s, %s)
                # """, (name, unit, uom, rate, outlet))

                item_check = """Select * from tblunitdefinition where name = %s"""

                cursor.execute(item_check, (name,) )

                item_check = cursor.fetchone()

                if not item_check:

                    cursor.execute("""
                        INSERT INTO tblunitdefinition (name, unit, uom, rate, outlet)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (name, unit, uom, rate, outlet))
                else:
                    return jsonify({"message": f"Unit Definition data  already exist for this item. {name}"}), 400                  


            mydb.commit()
            cursor.close()
            mydb.close()

            return jsonify({"message": "Unit definitions added successfully."}), 201

        elif request.method == "GET":
            outlet = request.args.get("outlet")  # optional filter
            mydb = get_db_connection()
            cursor = mydb.cursor(dictionary=True)

            if outlet:
                cursor.execute("SELECT * FROM tblunitdefinition WHERE outlet = %s", (outlet,))
            else:
                cursor.execute("SELECT * FROM tblunitdefinition")

            result = cursor.fetchall()
            cursor.close()
            mydb.close()
            return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 400



@app_file200.route("/unit-definition/<int:id>", methods=["PUT", "DELETE"])
@cross_origin()
def update_or_delete_unit(id):
    try:
        data = request.get_json()
        token = data.get("token")
        if not token or not token_auth(token):
            return jsonify({"error": "Invalid or missing token."}), 400

        mydb = get_db_connection()
        cursor = mydb.cursor()

        if request.method == "PUT":
            name = data.get("name")
            unit = data.get("unit")
            uom = data.get("uom")
            rate = data.get("rate")
            outlet = data.get("outlet")

            if not all([name, unit, uom, rate, outlet]):
                return jsonify({"error": "Missing fields"}), 400

            cursor.execute("""
                UPDATE tblunitdefinition
                SET name = %s, unit = %s, uom = %s, rate = %s, outlet = %s
                WHERE id = %s
            """, (name, unit, uom, rate, outlet, id))
            mydb.commit()
            message = "Unit definition updated."

        elif request.method == "DELETE":
            cursor.execute("DELETE FROM tblunitdefinition WHERE id = %s", (id,))
            mydb.commit()
            message = "Unit definition deleted."

        cursor.close()
        mydb.close()
        return jsonify({"message": message})

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# @app_file200.route("/unit-definition/check-usage", methods=["POST"])
# @cross_origin()
# def check_unit_usage():
#     try:

#         data = request.get_json()
#         name  = data.get('name')
#         token = data.get("token")
#         if not token or not token_auth(token):
#             return jsonify({"error": "Invalid or missing token."}), 400
#         mydb = get_db_connection()
#         cursor = mydb.cursor(dictionary=True)

#         # Check in recipe_items
#         cursor.execute("""
#             SELECT COUNT(*) AS count FROM recipe_items WHERE name = %s
#         """, (name,))
#         recipe_usage = cursor.fetchone()["count"]

#         # Check in sub_recipe_items
#         cursor.execute("""
#             SELECT COUNT(*) AS count FROM sub_recipe_items WHERE name = %s
#         """, (name,))
#         sub_recipe_usage = cursor.fetchone()["count"]

#         used_in_recipe = recipe_usage > 0
#         used_in_sub_recipe = sub_recipe_usage > 0

#         message = ""
#         if used_in_recipe and used_in_sub_recipe:
#             message = "Item is used in both recipes and sub-recipes. Please update them accordingly."
#         elif used_in_recipe:
#             message = "Item is used in recipes. Please update recipe entries accordingly."
#         elif used_in_sub_recipe:
#             message = "Item is used in sub-recipes. Please update sub-recipe entries accordingly."

#         cursor.close()
#         mydb.close()

#         return jsonify({
#             "used_in_recipe": used_in_recipe,
#             "used_in_sub_recipe": used_in_sub_recipe,
#             "message": message if (used_in_recipe or used_in_sub_recipe) else "Item is not used in any recipe."
#         })

#     except Exception as e:
#         return jsonify({"error": str(e)}), 400

@app_file200.route("/unit-definition/check-usage", methods=["POST"])
@cross_origin()
def check_unit_usage():
    try:
        data = request.get_json()
        name = data.get('name')
        outlet = data.get('outlet')
        token = data.get("token")

        if not token or not token_auth(token):
            return jsonify({"error": "Invalid or missing token."}), 400
        if not name or not outlet:
            return jsonify({"error": "Missing name or outlet."}), 400

        mydb = get_db_connection()
        cursor = mydb.cursor(dictionary=True)

        # Get recipe names where item is used for the given outlet
        cursor.execute("""
            SELECT r.name 
            FROM recipe_items ri
            JOIN recipe r ON ri.recipe_id = r.id
            WHERE ri.name = %s AND r.outlet = %s
        """, (name, outlet))
        recipe_names = [row["name"] for row in cursor.fetchall()]

        # Get sub-recipe names where item is used for the given outlet
        cursor.execute("""
            SELECT sr.name 
            FROM sub_recipe_items sri
            JOIN sub_recipe sr ON sri.sub_recipe_id = sr.id
            WHERE sri.name = %s AND sr.outlet = %s
        """, (name, outlet))
        sub_recipe_names = [row["name"] for row in cursor.fetchall()]

        used_in_recipe = len(recipe_names) > 0
        used_in_sub_recipe = len(sub_recipe_names) > 0

        if used_in_recipe and used_in_sub_recipe:
            message = "Item is used in both recipes and sub-recipes. Please update them accordingly."
        elif used_in_recipe:
            message = "Item is used in recipes. Please update recipe entries accordingly."
        elif used_in_sub_recipe:
            message = "Item is used in sub-recipes. Please update sub-recipe entries accordingly."
        else:
            message = "Item is not used in any recipe."

        cursor.close()
        mydb.close()

        return jsonify({
            "used_in_recipe": used_in_recipe,
            "used_in_sub_recipe": used_in_sub_recipe,
            "recipes": recipe_names,
            "sub_recipes": sub_recipe_names,
            "message": message
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400