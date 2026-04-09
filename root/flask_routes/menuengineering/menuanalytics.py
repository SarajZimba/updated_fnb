# from flask import Blueprint, jsonify, request
# import mysql.connector
# import os
# from dotenv import load_dotenv
# from flask_cors import cross_origin
# from root.auth.check import token_auth
# from decimal import Decimal, ROUND_HALF_UP

# load_dotenv()

# app_file109 = Blueprint('app_file109', __name__)

# def get_db_connection():
#     return mysql.connector.connect(
#         host=os.getenv("host"),
#         user=os.getenv("user"),
#         password=os.getenv("password"),
#         database=os.getenv("database")
#     )

# @app_file109.route("/menu-analytics", methods=["POST"])
# @cross_origin()
# def menu_analytics():
#     try:
#         data = request.get_json()
#         token = data.get("token")
#         if not token or not token_auth(token):
#             return jsonify({"error": "Invalid or missing token."}), 400

#         start_date = data.get("startDate")
#         end_date = data.get("endDate")
#         item_type = data.get("type")
#         outlet = data.get("outlet")

#         if not start_date or not end_date or not item_type or not outlet:
#             return jsonify({"error": "Missing startDate, endDate, type, or outlet."}), 400

#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)

#         # Get total number of items to compute desired mix
#         cursor.execute(
#             "SELECT COUNT(*) AS total_menu_items FROM recipe WHERE outlet = %s AND ItemType = %s",
#             (outlet, item_type)
#         )
#         total_menu_item = cursor.fetchone()["total_menu_items"]
#         desired_sales_mix_pct = ((100 / total_menu_item) * 0.7) if total_menu_item > 0 else 0

#         # Main Query: Get all items with LEFT JOIN and conditional SUM
#         cursor.execute("""
#             SELECT 
#                 r.name AS ItemName,
#                 r.sellingprice,
#                 r.costprice,
#                 IFNULL(SUM(
#                     CASE 
#                         WHEN o.Date BETWEEN %s AND %s AND o.Outlet_Name = %s 
#                         THEN d.count 
#                         ELSE 0 
#                     END
#                 ), 0) AS total_sold
#             FROM recipe r
#             LEFT JOIN tblorder_detailshistory d ON r.name = d.ItemName
#             LEFT JOIN tblorderhistory o ON o.idtblorderHistory = d.order_ID
#             WHERE r.outlet = %s AND r.ItemType = %s
#             GROUP BY r.name, r.sellingprice, r.costprice
#         """, (start_date, end_date, outlet, outlet, item_type))

#         itemwise = cursor.fetchall()

#         total_sold = sum(item["total_sold"] for item in itemwise)
#         unique_items_sold = sum(1 for item in itemwise if int(item["total_sold"]) > 0)

#         total_revenue = Decimal('0.00')
#         total_menu_cost = Decimal('0.00')
#         total_menu_cont_margin = Decimal('0.00')

#         for item in itemwise:
#             total_item_sold = Decimal(str(item["total_sold"]))
#             total_qty_sold = Decimal(str(total_sold)) if total_sold else Decimal('1')
#             percent = (total_item_sold / total_qty_sold) * 100
#             item["sales_mix_percent"] = float(percent.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
#             item["itemContmargin"] = Decimal(item["sellingprice"]) - Decimal(item["costprice"])
#             item["Revenue"] = total_item_sold * Decimal(item["sellingprice"])
#             item["MenuCost"] = total_item_sold * Decimal(item["costprice"])
#             item["MenuContMargin"] = total_item_sold * item["itemContmargin"]

#             total_revenue += item["Revenue"]
#             total_menu_cost += item["MenuCost"]
#             total_menu_cont_margin += item["MenuContMargin"]

#         avg_cont_margin = (total_menu_cont_margin / Decimal(total_sold)) if total_sold else Decimal('0.00')

#         classification_groups = {
#             "STAR": [],
#             "DOG": [],
#             "PUZZLE": [],
#             "PLOW HORSE": []
#         }

#         for item in itemwise:
#             if item["total_sold"] == 0:

#                 item["ContMarginCategory"] = "LOW"
#                 item["salesMixCategory"] = "LOW"
#             else:  
#                 item["ContMarginCategory"] = "HIGH" if item["itemContmargin"] > avg_cont_margin else "LOW"
#                 item["salesMixCategory"] = "HIGH" if item["sales_mix_percent"] > desired_sales_mix_pct else "LOW"

#             if item["ContMarginCategory"] == "LOW" and item["salesMixCategory"] == "LOW":
#                 classification = "DOG"
#             elif item["ContMarginCategory"] == "HIGH" and item["salesMixCategory"] == "HIGH":
#                 classification = "STAR"
#             elif item["ContMarginCategory"] == "LOW" and item["salesMixCategory"] == "HIGH":
#                 classification = "PLOW HORSE"
#             elif item["ContMarginCategory"] == "HIGH" and item["salesMixCategory"] == "LOW":
#                 classification = "PUZZLE"
#             else:
#                 classification = "UNCLASSIFIED"

#             item["MenuClassification"] = classification
#             if classification in classification_groups:
#                 classification_groups[classification].append(item)

#         cursor.close()
#         conn.close()

#         return jsonify({
#             "itemwise_summary": itemwise,
#             "menu_classification_summary": classification_groups,
#             "total_items_sold": total_sold,
#             "unique_items_sold": unique_items_sold,
#             "total_revenue": float(total_revenue.quantize(Decimal('0.01'))),
#             "total_menu_cost": float(total_menu_cost.quantize(Decimal('0.01'))),
#             "total_menu_cont_margin": float(total_menu_cont_margin.quantize(Decimal('0.01'))),
#             "avg_cont_margin": float(avg_cont_margin.quantize(Decimal('0.01'))),
#             "total_menu_items": total_menu_item,
#             "desired_sales_mix_percent": float(Decimal(desired_sales_mix_pct).quantize(Decimal('0.01')))
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

load_dotenv()

app_file109 = Blueprint('app_file109', __name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("host"),
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )

@app_file109.route("/menu-analytics", methods=["POST"])
@cross_origin()
def menu_analytics():
    try:
        data = request.get_json()
        token = data.get("token")

        if not token or not token_auth(token):
            return jsonify({"error": "Invalid or missing token."}), 400

        start_date = data.get("startDate")
        end_date = data.get("endDate")
        item_type = data.get("type")
        outlet = data.get("outlet")

        if not start_date or not end_date or not item_type or not outlet:
            return jsonify({"error": "Missing required fields."}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # ---------------- GET FLAG ---------------- #
        cursor.execute("SELECT use_same_recipe FROM master_featured ORDER BY id DESC LIMIT 1")
        flag_row = cursor.fetchone()
        use_same_recipe = flag_row["use_same_recipe"] if flag_row else 0

        # ---------------- TOTAL MENU ITEMS ---------------- #
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
        desired_sales_mix_pct = ((100 / total_menu_item) * 0.7) if total_menu_item > 0 else 0

        # ---------------- MAIN QUERY BUILD ---------------- #
        where_clause = "r.ItemType = %s"
        params = [start_date, end_date, outlet]

        if use_same_recipe == 0:
            where_clause += " AND r.outlet = %s"
            params.append(outlet)

        params.append(item_type)

        query = f"""
            SELECT 
                r.name AS ItemName,
                MIN(r.sellingprice) AS sellingprice,
                MIN(r.costprice) AS costprice,
                IFNULL(SUM(
                    CASE 
                        WHEN o.Date BETWEEN %s AND %s AND o.Outlet_Name = %s 
                        THEN d.count 
                        ELSE 0 
                    END
                ), 0) AS total_sold
            FROM recipe r
            LEFT JOIN tblorder_detailshistory d ON r.name = d.ItemName
            LEFT JOIN tblorderhistory o ON o.idtblorderHistory = d.order_ID
            WHERE {where_clause}
            GROUP BY r.name
        """

        cursor.execute(query, tuple(params))
        itemwise = cursor.fetchall()

        # ---------------- CALCULATIONS ---------------- #
        total_sold = sum(item["total_sold"] for item in itemwise)
        unique_items_sold = sum(1 for item in itemwise if int(item["total_sold"]) > 0)

        total_revenue = Decimal('0.00')
        total_menu_cost = Decimal('0.00')
        total_menu_cont_margin = Decimal('0.00')

        for item in itemwise:
            total_item_sold = Decimal(str(item["total_sold"]))
            total_qty_sold = Decimal(str(total_sold)) if total_sold else Decimal('1')

            percent = (total_item_sold / total_qty_sold) * 100
            item["sales_mix_percent"] = float(percent.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

            item["itemContmargin"] = Decimal(item["sellingprice"]) - Decimal(item["costprice"])
            item["Revenue"] = total_item_sold * Decimal(item["sellingprice"])
            item["MenuCost"] = total_item_sold * Decimal(item["costprice"])
            item["MenuContMargin"] = total_item_sold * item["itemContmargin"]

            total_revenue += item["Revenue"]
            total_menu_cost += item["MenuCost"]
            total_menu_cont_margin += item["MenuContMargin"]

        avg_cont_margin = (total_menu_cont_margin / Decimal(total_sold)) if total_sold else Decimal('0.00')

        # ---------------- CLASSIFICATION ---------------- #
        classification_groups = {
            "STAR": [],
            "DOG": [],
            "PUZZLE": [],
            "PLOW HORSE": []
        }

        for item in itemwise:
            if item["total_sold"] == 0:
                item["ContMarginCategory"] = "LOW"
                item["salesMixCategory"] = "LOW"
            else:
                item["ContMarginCategory"] = "HIGH" if item["itemContmargin"] > avg_cont_margin else "LOW"
                item["salesMixCategory"] = "HIGH" if item["sales_mix_percent"] > desired_sales_mix_pct else "LOW"

            if item["ContMarginCategory"] == "LOW" and item["salesMixCategory"] == "LOW":
                classification = "DOG"
            elif item["ContMarginCategory"] == "HIGH" and item["salesMixCategory"] == "HIGH":
                classification = "STAR"
            elif item["ContMarginCategory"] == "LOW" and item["salesMixCategory"] == "HIGH":
                classification = "PLOW HORSE"
            else:
                classification = "PUZZLE"

            item["MenuClassification"] = classification
            classification_groups[classification].append(item)

        cursor.close()
        conn.close()

        return jsonify({
            "itemwise_summary": itemwise,
            "menu_classification_summary": classification_groups,
            "total_items_sold": total_sold,
            "unique_items_sold": unique_items_sold,
            "total_revenue": float(total_revenue.quantize(Decimal('0.01'))),
            "total_menu_cost": float(total_menu_cost.quantize(Decimal('0.01'))),
            "total_menu_cont_margin": float(total_menu_cont_margin.quantize(Decimal('0.01'))),
            "avg_cont_margin": float(avg_cont_margin.quantize(Decimal('0.01'))),
            "total_menu_items": total_menu_item,
            "desired_sales_mix_percent": float(Decimal(desired_sales_mix_pct).quantize(Decimal('0.01'))),
            "use_same_recipe_flag": use_same_recipe   # 🔥 helpful for frontend/debug
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400