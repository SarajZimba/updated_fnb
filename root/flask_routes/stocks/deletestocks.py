# from flask import Blueprint, jsonify, request
# import mysql.connector
# from flask_cors import cross_origin
# import os
# from dotenv import load_dotenv

# load_dotenv()

# app_file123 = Blueprint('app_file123', __name__)

# @app_file123.route("/deletestocks", methods=["POST"])
# @cross_origin()
# def delete_stocks():
#     try:
#         mydb = mysql.connector.connect(
#             host=os.getenv('host'),
#             user=os.getenv('user'),
#             password=os.getenv('password')
#         )
#         cursor = mydb.cursor(buffered=True)
#         cursor.execute(f"USE {os.getenv('database')}")

#         data = request.get_json()

#         if not data or "outlet_name" not in data or "items" not in data:
#             return jsonify({"error": "Please provide 'outlet_name' and 'items' list"}), 400

#         outlet_name = data["outlet_name"]
#         items = data["items"]

#         deleted_count = 0
#         deleted_recipe_items = 0
#         deleted_subrecipe_items = 0
#         undeleted_items = []

#         for item_name in items:
#             # Check in received_items
#             cursor.execute("""
#                 SELECT COUNT(*) FROM received_items
#                 WHERE item_name = %s AND outlet_name = %s
#             """, (item_name, outlet_name))
#             if cursor.fetchone()[0] > 0:
#                 undeleted_items.append(f"{item_name} used in received_items")
#                 continue

#             # Check in wastage_items
#             cursor.execute("""
#                 SELECT COUNT(*) FROM wastage_items
#                 WHERE item_name = %s AND outlet_name = %s
#             """, (item_name, outlet_name))
#             if cursor.fetchone()[0] > 0:
#                 undeleted_items.append(f"{item_name} used in wastage_items")
#                 continue

#             # Check in physical_items
#             cursor.execute("""
#                 SELECT COUNT(*) FROM physical_items
#                 WHERE item_name = %s AND outlet_name = %s
#             """, (item_name, outlet_name))
#             if cursor.fetchone()[0] > 0:
#                 undeleted_items.append(f"{item_name} used in physical_items")
#                 continue

#             # Check in recipe_items
#             cursor.execute("""
#                 SELECT COUNT(*) FROM recipe_items
#                 WHERE name = %s
#             """, (item_name,))
#             if cursor.fetchone()[0] > 0:
#                 undeleted_items.append(f"{item_name} used in recipe_items")
#                 continue

#             # Check in sub_recipe_items
#             cursor.execute("""
#                 SELECT COUNT(*) FROM sub_recipe_items
#                 WHERE name = %s
#             """, (item_name,))
#             if cursor.fetchone()[0] > 0:
#                 undeleted_items.append(f"{item_name} used in sub_recipe_items")
#                 continue

#             # Passed all checks — delete from stock_statement
#             cursor.execute("""
#                 DELETE FROM stock_statement
#                 WHERE ItemName = %s AND OutletName = %s
#             """, (item_name, outlet_name))
#             deleted_count += cursor.rowcount

#             # Optionally clean up from recipe_items and sub_recipe_items (if empty)
#             cursor.execute("DELETE FROM recipe_items WHERE name = %s", (item_name,))
#             deleted_recipe_items += cursor.rowcount

#             cursor.execute("DELETE FROM sub_recipe_items WHERE name = %s", (item_name,))
#             deleted_subrecipe_items += cursor.rowcount

#         mydb.commit()

#         return jsonify({
#             "status": "success",
#             "message": f"{deleted_count} stock records deleted.",
#             "recipe_items_deleted": deleted_recipe_items,
#             "sub_recipe_items_deleted": deleted_subrecipe_items,
#             "not_deleted": undeleted_items
#         }), 200

#     except mysql.connector.Error as db_error:
#         return jsonify({"error": f"Database error: {str(db_error)}"}), 500
#     except Exception as e:
#         return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
#     finally:
#         if 'mydb' in locals():
#             mydb.close()

# from flask import Blueprint, jsonify, request
# import mysql.connector
# from flask_cors import cross_origin
# import os
# from dotenv import load_dotenv

# load_dotenv()

# app_file123 = Blueprint('app_file123', __name__)

# @app_file123.route("/deletestocks", methods=["POST"])
# @cross_origin()
# def delete_stocks():
#     try:
#         mydb = mysql.connector.connect(
#             host=os.getenv('host'),
#             user=os.getenv('user'),
#             password=os.getenv('password')
#         )
#         cursor = mydb.cursor(buffered=True)
#         cursor.execute(f"USE {os.getenv('database')}")

#         data = request.get_json()

#         if not data or "outlet_name" not in data or "items" not in data:
#             return jsonify({"error": "Please provide 'outlet_name' and 'items' list"}), 400

#         outlet_name = data["outlet_name"]
#         items = data["items"]

#         deleted_count = 0
#         deleted_recipe_items = 0
#         deleted_subrecipe_items = 0
#         undeleted_items = []

#         for item_name in items:
#             # Check in received_items
#             cursor.execute("""
#                 SELECT COUNT(*) FROM received_items
#                 WHERE item_name = %s AND outlet_name = %s
#             """, (item_name, outlet_name))
#             if cursor.fetchone()[0] > 0:
#                 undeleted_items.append(f"{item_name} used in received_items")
#                 continue

#             # # Check in wastage_items
#             # cursor.execute("""
#             #     SELECT COUNT(*) FROM wastage_items
#             #     WHERE item_name = %s AND outlet_name = %s
#             # """, (item_name, outlet_name))
#             # if cursor.fetchone()[0] > 0:
#             #     undeleted_items.append(f"{item_name} used in wastage_items")
#             #     continue

#             # # Check in physical_items
#             # cursor.execute("""
#             #     SELECT COUNT(*) FROM physical_items
#             #     WHERE item_name = %s AND outlet_name = %s
#             # """, (item_name, outlet_name))
#             # if cursor.fetchone()[0] > 0:
#             #     undeleted_items.append(f"{item_name} used in physical_items")
#             #     continue

#             # Check in recipe_items
#             cursor.execute("""
#                 SELECT COUNT(*) FROM recipe_items
#                 WHERE name = %s
#             """, (item_name,))
#             if cursor.fetchone()[0] > 0:
#                 undeleted_items.append(f"{item_name} used in recipe_items")
#                 continue

#             # Check in sub_recipe_items
#             cursor.execute("""
#                 SELECT COUNT(*) FROM sub_recipe_items
#                 WHERE name = %s
#             """, (item_name,))
#             if cursor.fetchone()[0] > 0:
#                 undeleted_items.append(f"{item_name} used in sub_recipe_items")
#                 continue

#             # Passed all checks — delete from stock_statement
#             cursor.execute("""
#                 DELETE FROM stock_statement
#                 WHERE ItemName = %s AND OutletName = %s
#             """, (item_name, outlet_name))
#             deleted_count += cursor.rowcount

#             # Optionally clean up from recipe_items and sub_recipe_items (if empty)
#             cursor.execute("DELETE FROM recipe_items WHERE name = %s", (item_name,))
#             deleted_recipe_items += cursor.rowcount

#             cursor.execute("DELETE FROM sub_recipe_items WHERE name = %s", (item_name,))
#             deleted_subrecipe_items += cursor.rowcount

#         mydb.commit()

#         return jsonify({
#             "status": "success",
#             "message": f"{deleted_count} stock records deleted.",
#             "recipe_items_deleted": deleted_recipe_items,
#             "sub_recipe_items_deleted": deleted_subrecipe_items,
#             "not_deleted": undeleted_items
#         }), 200

#     except mysql.connector.Error as db_error:
#         return jsonify({"error": f"Database error: {str(db_error)}"}), 500
#     except Exception as e:
#         return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
#     finally:
#         if 'mydb' in locals():
#             mydb.close()

from flask import Blueprint, jsonify, request
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv

load_dotenv()

app_file123 = Blueprint('app_file123', __name__)

@app_file123.route("/deletestocks", methods=["POST"])
@cross_origin()
def delete_stocks():
    try:
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password')
        )
        cursor = mydb.cursor(buffered=True)
        cursor.execute(f"USE {os.getenv('database')}")

        data = request.get_json()

        if not data or "outlet_name" not in data or "items" not in data:
            return jsonify({"error": "Please provide 'outlet_name' and 'items' list"}), 400

        outlet_name = data["outlet_name"]
        items = data["items"]

        deleted_count = 0
        deleted_recipe_items = 0
        deleted_subrecipe_items = 0
        undeleted_items = []

        for item_name in items:
            # Check in received_items
            cursor.execute("""
                SELECT COUNT(*) FROM received_items
                WHERE item_name = %s AND outlet_name = %s
            """, (item_name, outlet_name))
            if cursor.fetchone()[0] > 0:
                undeleted_items.append(f"{item_name} used in received_items")
                continue

            # Check in recipe_items
            cursor.execute("""
                SELECT COUNT(*) FROM recipe_items
                WHERE name = %s
            """, (item_name,))
            if cursor.fetchone()[0] > 0:
                undeleted_items.append(f"{item_name} used in recipe_items")
                continue

            # Check in sub_recipe_items
            cursor.execute("""
                SELECT COUNT(*) FROM sub_recipe_items
                WHERE name = %s
            """, (item_name,))
            if cursor.fetchone()[0] > 0:
                undeleted_items.append(f"{item_name} used in sub_recipe_items")
                continue

            # Passed all checks — delete from stock_statement
            cursor.execute("""
                DELETE FROM stock_statement
                WHERE ItemName = %s AND OutletName = %s
            """, (item_name, outlet_name))
            deleted_count += cursor.rowcount

            # Optionally delete orphaned entries in recipe_items/sub_recipe_items
            cursor.execute("DELETE FROM recipe_items WHERE name = %s", (item_name,))
            deleted_recipe_items += cursor.rowcount

            cursor.execute("DELETE FROM sub_recipe_items WHERE name = %s", (item_name,))
            deleted_subrecipe_items += cursor.rowcount

        mydb.commit()

        # Decide response status code
        if deleted_count == 0:
            return jsonify({
                "status": "failed",
                "message": "No stock items deleted. All items are in use.",
                "not_deleted": undeleted_items
            }), 400
        else:
            return jsonify({
                "status": "success",
                "message": f"{deleted_count} stock records deleted.",
                "recipe_items_deleted": deleted_recipe_items,
                "sub_recipe_items_deleted": deleted_subrecipe_items,
                "not_deleted": undeleted_items
            }), 200

    except mysql.connector.Error as db_error:
        return jsonify({"error": f"Database error: {str(db_error)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
    finally:
        if 'mydb' in locals():
            mydb.close()
