# from flask import Blueprint, request, jsonify
# import mysql.connector
# from flask_cors import cross_origin
# import os
# from dotenv import load_dotenv
# from root.auth.check import token_auth

# load_dotenv()

# app_file215 = Blueprint('app_file215', __name__)

# @app_file215.route("/salesitems-itemwise-alloutlets", methods=["POST"])
# @cross_origin()
# def sales_items_itemwise_alloutlets():
#     mydb = None
#     cursor = None

#     try:
#         payload = request.get_json()

#         # ------------------------
#         # Token validation
#         # ------------------------
#         if not payload or not payload.get("token"):
#             return {"error": "No token provided"}, 400

#         if not token_auth(payload["token"]):
#             return {"error": "Invalid token"}, 400

#         start_date = payload.get("dateStart")
#         end_date = payload.get("dateEnd")

#         if not start_date or not end_date:
#             return {"error": "dateStart and dateEnd are required"}, 400

#         # ------------------------
#         # DB connection
#         # ------------------------
#         mydb = mysql.connector.connect(
#             host=os.getenv("host"),
#             user=os.getenv("user"),
#             password=os.getenv("password"),
#             database=os.getenv("database")
#         )
#         cursor = mydb.cursor(dictionary=True)

#         # ------------------------
#         # Get all outlets
#         # ------------------------
#         cursor.execute("SELECT DISTINCT Outlet FROM outetNames")
#         outlets = [row["Outlet"] for row in cursor.fetchall()]

#         # ------------------------
#         # Get sales data (all outlets)
#         # ------------------------
#         sql = """
#             SELECT
#                 h.Outlet_Name,
#                 d.ItemType,
#                 d.Description,
#                 d.ItemName,
#                 d.itemRate,
#                 SUM(d.count) AS qty,
#                 SUM(d.count * d.itemRate) AS total
#             FROM tblorderhistory h
#             JOIN tblorder_detailshistory d
#                 ON h.idtblorderHistory = d.order_ID
#             WHERE
#                 h.Date BETWEEN %s AND %s
#                 AND h.bill_no != ''
#             GROUP BY
#                 h.Outlet_Name,
#                 d.ItemType,
#                 d.Description,
#                 d.ItemName,
#                 d.itemRate
#         """
#         cursor.execute(sql, (start_date, end_date))
#         rows = cursor.fetchall()

#         # ------------------------
#         # Build structure:
#         # ItemType -> Description -> Items
#         # ------------------------
#         result = {}

#         for row in rows:
#             item_type = row["ItemType"] or "Others"
#             description = row["Description"] or "Others"

#             if item_type not in result:
#                 result[item_type] = {}

#             if description not in result[item_type]:
#                 result[item_type][description] = []

#             # Find existing item
#             existing_item = next(
#                 (
#                     item for item in result[item_type][description]
#                     if item["item_name"] == row["ItemName"]
#                     and item["rate"] == float(row["itemRate"])
#                 ),
#                 None
#             )

#             if not existing_item:
#                 existing_item = {
#                     "item_name": row["ItemName"],
#                     "rate": float(row["itemRate"]),
#                     "outlets": {
#                         outlet: {"qty": 0, "total": 0}
#                         for outlet in outlets
#                     }
#                 }
#                 result[item_type][description].append(existing_item)

#             # Fill outlet data
#             existing_item["outlets"][row["Outlet_Name"]] = {
#                 "qty": int(row["qty"]),
#                 "total": float(row["total"])
#             }

#         # ------------------------
#         # Order ItemType: Food -> Beverage -> Others
#         # ------------------------
#         ordered_result = {}

#         if "Food" in result:
#             ordered_result["Food"] = result["Food"]

#         if "Beverage" in result:
#             ordered_result["Beverage"] = result["Beverage"]

#         for key in result:
#             if key not in ordered_result:
#                 ordered_result[key] = result[key]

#         # ------------------------
#         # Final response
#         # ------------------------
#         response = {
#             "date_range": {
#                 "start": start_date,
#                 "end": end_date
#             },
#             "outlets": outlets,
#             "items": ordered_result
#         }

#         return jsonify(response), 200

#     except Exception as e:
#         return {"error": str(e)}, 500

#     finally:
#         if cursor:
#             cursor.close()
#         if mydb:
#             mydb.close()


from flask import Blueprint, request, jsonify
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv
from root.auth.check import token_auth

load_dotenv()

app_file215 = Blueprint('app_file215', __name__)

@app_file215.route("/salesitems-itemwise-alloutlets", methods=["POST"])
@cross_origin()
def sales_items_itemwise_alloutlets():
    mydb = None
    cursor = None

    try:
        payload = request.get_json()

        # ------------------------
        # Token validation
        # ------------------------
        if not payload or not payload.get("token"):
            return {"error": "No token provided"}, 400

        if not token_auth(payload["token"]):
            return {"error": "Invalid token"}, 400

        start_date = payload.get("dateStart")
        end_date = payload.get("dateEnd")
        employee_id = payload.get("employee_id")

        if not start_date or not end_date:
            return {"error": "dateStart and dateEnd are required"}, 400
        if not employee_id:
            return {"error": "employee_id is required"}, 400

        # ------------------------
        # DB connection
        # ------------------------
        mydb = mysql.connector.connect(
            host=os.getenv("host"),
            user=os.getenv("user"),
            password=os.getenv("password"),
            database=os.getenv("database")
        )
        cursor = mydb.cursor(dictionary=True)

        # ------------------------
        # Get outlets employee has access to
        # ------------------------
        cursor.execute("""
            SELECT o.Outlet
            FROM outetNames o
            JOIN employeeoutlets eo ON eo.outlet_id = o.id
            WHERE eo.employee_id = %s AND eo.status = TRUE
        """, (employee_id,))
        accessible_outlet_result = cursor.fetchall()
        accessible_outlets = [row["Outlet"] for row in accessible_outlet_result]

        if not accessible_outlets:
            return {"error": "Employee has no accessible outlets"}, 400

        # ------------------------
        # Get sales data for accessible outlets only
        # ------------------------
        placeholders = ','.join(['%s'] * len(accessible_outlets))  # SQL placeholders
        sql = f"""
            SELECT
                h.Outlet_Name,
                d.ItemType,
                d.Description,
                d.ItemName,
                d.itemRate,
                SUM(d.count) AS qty,
                SUM(d.count * d.itemRate) AS total
            FROM tblorderhistory h
            JOIN tblorder_detailshistory d
                ON h.idtblorderHistory = d.order_ID
            WHERE
                h.Date BETWEEN %s AND %s
                AND h.bill_no != ''
                AND h.Outlet_Name IN ({placeholders})
            GROUP BY
                h.Outlet_Name,
                d.ItemType,
                d.Description,
                d.ItemName,
                d.itemRate
        """
        cursor.execute(sql, [start_date, end_date] + accessible_outlets)
        rows = cursor.fetchall()

        # ------------------------
        # Build structure:
        # ItemType -> Description -> Items
        # ------------------------
        result = {}

        for row in rows:
            item_type = row["ItemType"] or "Others"
            description = row["Description"] or "Others"

            if item_type not in result:
                result[item_type] = {}

            if description not in result[item_type]:
                result[item_type][description] = []

            # Find existing item
            existing_item = next(
                (
                    item for item in result[item_type][description]
                    if item["item_name"] == row["ItemName"]
                    and item["rate"] == float(row["itemRate"])
                ),
                None
            )

            if not existing_item:
                existing_item = {
                    "item_name": row["ItemName"],
                    "rate": float(row["itemRate"]),
                    "outlets": {
                        outlet: {"qty": 0, "total": 0}
                        for outlet in accessible_outlets
                    }
                }
                result[item_type][description].append(existing_item)

            # Fill outlet data
            existing_item["outlets"][row["Outlet_Name"]] = {
                "qty": int(row["qty"]),
                "total": float(row["total"])
            }

        # ------------------------
        # Order ItemType: Food -> Beverage -> Others
        # ------------------------
        ordered_result = {}
        if "Food" in result:
            ordered_result["Food"] = result["Food"]
        if "Beverage" in result:
            ordered_result["Beverage"] = result["Beverage"]
        for key in result:
            if key not in ordered_result:
                ordered_result[key] = result[key]

        # ------------------------
        # Final response
        # ------------------------
        response = {
            "date_range": {"start": start_date, "end": end_date},
            "outlets": accessible_outlets,
            "items": ordered_result
        }

        return jsonify(response), 200

    except Exception as e:
        return {"error": str(e)}, 500

    finally:
        if cursor:
            cursor.close()
        if mydb:
            mydb.close()