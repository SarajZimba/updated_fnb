# from flask import Blueprint, jsonify, request
# import mysql.connector
# import os
# from dotenv import load_dotenv
# from flask_cors import cross_origin
# from root.auth.check import token_auth
# from decimal import Decimal, ROUND_HALF_UP
# from datetime import datetime
# from datetime import datetime
# load_dotenv()

# app_file115 = Blueprint('app_file115', __name__)

# def get_db_connection():
#     return mysql.connector.connect(
#         host=os.getenv("host"),
#         user=os.getenv("user"),
#         password=os.getenv("password"),
#         database=os.getenv("database")
#     )
# from datetime import datetime,timedelta
# @app_file115.route("/inventory-summary", methods=["POST"])
# @cross_origin()
# def inventory_summary():
#     try:
#         data = request.get_json()
#         token = data.get("token")
#         if not token or not token_auth(token):
#             return jsonify({"error": "Invalid or missing token."}), 400

#         outlet = data.get("outlet")
#         include_sub_recipe_items = data.get("includeSubRecipeItems", True)

#         if not outlet:
#             return jsonify({"error": "Missing outlet."}), 400

#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)

#         cursor.execute("SELECT use_same_recipe FROM master_featured ORDER BY id DESC LIMIT 1")
#         flag_row = cursor.fetchone()
#         use_same_recipe = flag_row["use_same_recipe"] if flag_row else 0

#         # Step 1: Determine start_date and end_date
#         cursor.execute("""
#             SELECT id, end_date FROM inventory_snapshot_master
#             WHERE outlet_name = %s
#             ORDER BY end_date DESC LIMIT 1
#         """, (outlet,))
#         snapshot = cursor.fetchone()

#         if snapshot:
#             snapshot_id = snapshot["id"]
#             # start_date = snapshot["end_date"] + timedelta(days=1)
#             # start_date = start_date.strftime("%Y-%m-%d")
#         else:
#             snapshot_id = None
#             # start_date = '2000-01-01'

#         # end_date = datetime.today().strftime('%Y-%m-%d')
#         start_date = data.get("startDate")
#         end_date = data.get("endDate")

#         if not start_date or not end_date or not outlet:
#             return jsonify({"error": "Missing startDate, endDate, or outlet."}), 400


#         # Step 2: Load opening balances
#         opening_balances = {}
#         if snapshot_id:
#             cursor.execute("""
#                 SELECT item_name, physical_count
#                 FROM inventory_snapshot_items
#                 WHERE snapshot_id = %s
#             """, (snapshot_id,))
#             for row in cursor.fetchall():
#                 opening_balances[row["item_name"]] = float(row["physical_count"])

#         # Step 3: Calculate consumption
#         all_consumed_items = {}
#         cursor.execute("SELECT DISTINCT ItemType FROM tblorder_detailshistory")
#         item_types = [row["ItemType"] for row in cursor.fetchall()]

#         for item_type in item_types:
#             cursor.execute("""
#                 SELECT d.ItemName, SUM(d.count) AS total_sold
#                 FROM tblorder_detailshistory d
#                 JOIN tblorderhistory o ON o.idtblorderHistory = d.order_ID
#                 WHERE o.Date BETWEEN %s AND %s AND o.Outlet_Name = %s AND d.ItemType = %s
#                 GROUP BY d.ItemName
#             """, (start_date, end_date, outlet, item_type))

#             for sold_item in cursor.fetchall():
#                 item_name = sold_item["ItemName"]
#                 quantity_sold = sold_item["total_sold"]

#                 # cursor.execute("""
#                 #     SELECT id FROM recipe
#                 #     WHERE outlet = %s AND name = %s AND ItemType = %s
#                 # """, (outlet, item_name, item_type))

#                 if use_same_recipe == 1:
#                     cursor.execute("""
#                         SELECT id FROM recipe
#                         WHERE name = %s AND ItemType = %s
#                         LIMIT 1
#                     """, (item_name, item_type))
#                 else:
#                     cursor.execute("""
#                         SELECT id FROM recipe
#                         WHERE outlet = %s AND name = %s AND ItemType = %s
#                     """, (outlet, item_name, item_type))



#                 recipe_info = cursor.fetchone()

#                 if recipe_info:
#                     recipe_id = recipe_info["id"]

#                     cursor.execute("""
#                         SELECT name, quantity, uom, new_uom
#                         FROM recipe_items WHERE recipe_id = %s
#                     """, (recipe_id,))
#                     for ri in cursor.fetchall():
#                         name = ri["name"]
#                         consumed = float(ri["quantity"]) * float(quantity_sold)
#                         if name not in all_consumed_items:
#                             all_consumed_items[name] = {
#                                 "total_consumed": 0,
#                                 "real_consumed": 0,
#                                 "uom": ri["uom"],
#                                 "new_uom": ri["new_uom"],
#                                 "unitdefinition": {"unit": "", "uom": ""}

#                             }
#                         all_consumed_items[name]["total_consumed"] += consumed

#                     if include_sub_recipe_items:
#                         cursor.execute("""
#                             SELECT rs.sub_recipe_id, rs.quantity AS sr_qty, s.id
#                             FROM recipe_subrecipes rs
#                             JOIN sub_recipe s ON rs.sub_recipe_id = s.id
#                             WHERE rs.recipe_id = %s
#                         """, (recipe_id,))
#                         for sr in cursor.fetchall():
#                             cursor.execute("""
#                                 SELECT name, quantity, uom, new_uom
#                                 FROM sub_recipe_items WHERE sub_recipe_id = %s
#                             """, (sr["id"],))
#                             for sri in cursor.fetchall():
#                                 name = sri["name"]
#                                 consumed = float(sri["quantity"]) * float(sr["sr_qty"]) * float(quantity_sold)
#                                 if name not in all_consumed_items:
#                                     all_consumed_items[name] = {
#                                         "total_consumed": 0,
#                                         "uom": sri["uom"],
#                                         "new_uom": sri["new_uom"],
#                                         "unitdefinition": {"unit": "", "uom": ""},
#                                         "real_consumed": 0
#                                     }
#                                 all_consumed_items[name]["total_consumed"] += consumed
#         print(all_consumed_items)

#         # Step 3.1: Convert consumption using unitdefinition
#         for item_name, details in all_consumed_items.items():
#             # uom = details["uom"]
#             # new_uom = details["new_uom"]
#             total_consumed = details["total_consumed"]

#             # Default real_consumed is same as total_consumed
#             real_consumed = total_consumed
#             unitdefinition_dict = None  # Initialize to None
#             # cursor.execute("""
#             #     SELECT unit, uom FROM tblunitdefinition
#             #     WHERE name = %s and outlet = %s
#             # """, (item_name, outlet))

#             if use_same_recipe == 1:
#                 # Look up globally (ignore outlet) since recipe is shared
#                 cursor.execute("""
#                     SELECT unit, uom FROM tblunitdefinition
#                     WHERE name = %s
#                     LIMIT 1
#                 """, (item_name,))
#             else:
#                 # Look up per outlet
#                 cursor.execute("""
#                     SELECT unit, uom FROM tblunitdefinition
#                     WHERE name = %s AND outlet = %s
#                 """, (item_name, outlet))
#             result = cursor.fetchone()

#             if result:
#                 factor = 1/float(result["unit"])
#                 real_consumed = float(total_consumed) * factor
#                 unitdefinition_dict = {
#                     "unit": result["unit"],
#                     "uom": result["uom"]
#                 }

#             all_consumed_items[item_name]["total_consumed"] = round(real_consumed, 2)
#             all_consumed_items[item_name]["unitdefinition"] = unitdefinition_dict

#         # Step 4: Get received items
#         # cursor.execute("""
#         #     SELECT item_name, SUM(quantity) as total_received, uom
#         #     FROM received_items
#         #     WHERE outlet_name = %s AND received_date BETWEEN %s AND %s
#         #     GROUP BY item_name, uom
#         # """, (outlet, start_date, end_date))

#         # Step 4: Get received items from the new store requisition tables
#         cursor.execute("""
#             SELECT 
#                 d.ItemName as item_name,
#                 SUM(d.Amount) as total_received,
#                 d.UOM as uom
#             FROM intblstorereqdetails d
#             JOIN intblstorerequisition r ON d.StoreReqID = r.idintblStoreRequisition
#             WHERE r.Outlet = %s 
#                 AND DATE(r.Date) BETWEEN %s AND %s
#             GROUP BY d.ItemName, d.UOM
#         """, (outlet, start_date, end_date))
#         received_items = cursor.fetchall()

#         # Step 5: Get wastage items
#         cursor.execute("""
#             SELECT item_name, SUM(quantity) as total_wasted
#             FROM wastage_items
#             WHERE outlet_name = %s AND received_date BETWEEN %s AND %s
#             GROUP BY item_name
#         """, (outlet, start_date, end_date))
#         wastage_data = {row["item_name"]: float(row["total_wasted"]) for row in cursor.fetchall()}

#         # Step 5.1: Get physical items
#         cursor.execute("""
#             SELECT item_name, SUM(quantity) as total_physical, uom
#             FROM physical_items
#             WHERE outlet_name = %s AND received_date BETWEEN %s AND %s
#             GROUP BY item_name, uom
#         """, (outlet, start_date, end_date))
#         physical_data = {row["item_name"]: float(row["total_physical"]) for row in cursor.fetchall()}



#         # # Step 6: Get stock items
#         # cursor.execute("""
#         #     SELECT ItemName, GroupName, Type, UOM
#         #     FROM stock_statement WHERE OutletName = %s
#         # """, (outlet,))

#         if use_same_recipe == 1:
#             # Fetch all stock items, ignoring outlet
#             cursor.execute("""
#                 SELECT ItemName, GroupName, Type, UOM
#                 FROM stock_statement
#             """)
#         else:
#             # Fetch stock items for this outlet only
#             cursor.execute("""
#                 SELECT ItemName, GroupName, Type, UOM
#                 FROM stock_statement WHERE OutletName = %s
#             """, (outlet,))
#         all_stock_items = cursor.fetchall()

#         # Step 7: Combine all into summary
#         item_data = {}

#         for stock_item in all_stock_items:
#             name = stock_item["ItemName"]
#             item_data[name] = {
#                 "total_consumed": 0.0,
#                 "total_received": 0.0,
#                 "total_wasted": 0.0,
#                 "total_physical": 0.0,
#                 "opening": opening_balances.get(name, 0.0),
#                 "uom": stock_item["UOM"],
#                 "new_uom": stock_item["UOM"],
#                 "group_name": stock_item["GroupName"] or "Group Not Found",
#                 "type": stock_item["Type"] or "Type Not Found",
#                 "real_consumed" : 0.0,
#                 "unitdefinition" : {
#                     "unit" : "",
#                     "uom": ""
#                 }
#             }

#         for name, info in all_consumed_items.items():
#             if name not in item_data:
#                 item_data[name] = {
#                     "total_consumed": 0.0,
#                     "total_received": 0.0,
#                     "total_wasted": 0.0,
#                     "total_physical": 0.0,
#                     "opening": opening_balances.get(name, 0.0),
#                     "uom": info["uom"],
#                     "new_uom": info["new_uom"],
#                     "group_name": "Group Not Found",
#                     "type": "Type Not Found",
#                     "real_consumed" : 0.0,
#                     "unitdefinition" : {
#                         "unit" : "",
#                         "uom": ""
#                     }
#                 }
#             item_data[name]["total_consumed"] = float(info["total_consumed"])
#             item_data[name]["unitdefinition"] = info["unitdefinition"]
#             # item_data[name]["uom"] = info["uom"]
#             item_data[name]["new_uom"] = info["new_uom"]

#         for item in received_items:
#             name = item["item_name"]
#             if name not in item_data:
#                 item_data[name] = {
#                     "total_consumed": 0.0,
#                     "total_received": 0.0,
#                     "total_wasted": 0.0,
#                     "total_physical": 0.0,
#                     "opening": opening_balances.get(name, 0.0),
#                     "uom": item["uom"],
#                     "new_uom": item["uom"],
#                     "group_name": "Group Not Found",
#                     "type": "Type Not Found",
#                     "real_consumed" : 0.0,
#                     "unitdefinition" : {
#                         "unit" : "",
#                         "uom": ""
#                     }
#                 }
#             item_data[name]["total_received"] = float(item["total_received"])

#         for name, wasted_qty in wastage_data.items():
#             if name not in item_data:
#                 item_data[name] = {
#                     "total_consumed": 0.0,
#                     "total_received": 0.0,
#                     "total_wasted": 0.0,
#                     "total_physical": 0.0,
#                     "opening": opening_balances.get(name, 0.0),
#                     "uom": "UOM",
#                     "new_uom": "UOM",
#                     "group_name": "Group Not Found",
#                     "type": "Type Not Found",
#                     "unitdefinition" : {
#                         "unit" : "",
#                         "uom": ""
#                     }
#                 }
#             item_data[name]["total_wasted"] = float(wasted_qty)

#         for name, physical_qty in physical_data.items():
#             if name not in item_data:
#                 item_data[name] = {
#                     "total_consumed": 0.0,
#                     "total_received": 0.0,
#                     "total_wasted": 0.0,
#                     "total_physical": 0.0,
#                     "opening": opening_balances.get(name, 0.0),
#                     "uom": "UOM",
#                     "new_uom": "UOM",
#                     "group_name": "Group Not Found",
#                     "type": "Type Not Found",
#                     "unitdefinition" : {
#                         "unit" : "",
#                         "uom": ""
#                     }
#                 }
#             item_data[name]["total_physical"] = float(physical_qty)

#         # Step 8: Final nested summary
#         nested_summary = {}
#         for name, info in item_data.items():
#             consumed = Decimal(info["total_consumed"])
#             received = Decimal(info["total_received"])
#             wasted = Decimal(info["total_wasted"])
#             physical = Decimal(info["total_physical"])
#             opening = Decimal(info["opening"])
#             closing = opening + received - consumed - wasted

#             item_type = info["type"]
#             group_name = info["group_name"]

#             if item_type not in nested_summary:
#                 nested_summary[item_type] = {}

#             if group_name not in nested_summary[item_type]:
#                 nested_summary[item_type][group_name] = []

#             nested_summary[item_type][group_name].append({
#                 "name": name,
#                 "uom": info["uom"],
#                 "new_uom": info["new_uom"],
#                 "opening": float(opening),
#                 "total_consumed": float(consumed),
#                 "total_received": float(received),
#                 "total_wasted": float(wasted),
#                 "total_physical": float(physical),
#                 "closing_balance": float(closing) if float(closing) > 0 else 0,
#                 'unitdefinition': info['unitdefinition']
#             })

#         # Step 5.2: Check if there are any physical items entries before the start_date
#         cursor.execute("""
#             SELECT COUNT(*) as count
#             FROM physical_items
#             WHERE outlet_name = %s AND received_date < %s
#             LIMIT 1
#         """, (outlet, start_date))
#         result = cursor.fetchone()
#         has_physical_before_start = result["count"] > 0 if result else False

#         cursor.execute("""
#             SELECT start_date, end_date
#             FROM inventory_snapshot_master
#             WHERE outlet_name = %s order by id asc
#             LIMIT 1
#         """, (outlet,))
#         opening_date_result = cursor.fetchone()

#         if opening_date_result:
#             opening_start_date = opening_date_result["start_date"]
#             opening_end_date = opening_date_result["end_date"]


#             # ✅ FORMAT HERE
#             opening_start_date = opening_start_date.strftime("%Y-%m-%d") if opening_start_date else None
#             opening_end_date = opening_end_date.strftime("%Y-%m-%d") if opening_end_date else None
#         else:
#             opening_start_date = None
#             opening_end_date = None

#         cursor.close()
#         conn.close()

#         return jsonify({
#             "status": "success",
#             "summary": nested_summary,
#             "period": {
#                 "start_date": start_date,
#                 "end_date": end_date
#             },
#             "outlet": outlet,
#             "has_physical_before_start": has_physical_before_start,
#             "first_opening_dates": {
#                 "start_date" : opening_start_date,
#                 "end_date" : opening_end_date,
#             }

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
from datetime import datetime
from datetime import datetime
load_dotenv()

app_file115 = Blueprint('app_file115', __name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("host"),
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )
from datetime import datetime,timedelta
@app_file115.route("/inventory-summary", methods=["POST"])
@cross_origin()
def inventory_summary():
    try:
        data = request.get_json()
        token = data.get("token")
        if not token or not token_auth(token):
            return jsonify({"error": "Invalid or missing token."}), 400

        outlet = data.get("outlet")
        include_sub_recipe_items = data.get("includeSubRecipeItems", True)

        if not outlet:
            return jsonify({"error": "Missing outlet."}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Step 1: Determine start_date and end_date
        cursor.execute("""
            SELECT id, end_date FROM inventory_snapshot_master
            WHERE outlet_name = %s
            ORDER BY end_date DESC LIMIT 1
        """, (outlet,))
        snapshot = cursor.fetchone()

        if snapshot:
            snapshot_id = snapshot["id"]
            # start_date = snapshot["end_date"] + timedelta(days=1)
            # start_date = start_date.strftime("%Y-%m-%d")
        else:
            snapshot_id = None
            # start_date = '2000-01-01'

        # end_date = datetime.today().strftime('%Y-%m-%d')
        start_date = data.get("startDate")
        end_date = data.get("endDate")

        if not start_date or not end_date or not outlet:
            return jsonify({"error": "Missing startDate, endDate, or outlet."}), 400


        # Step 2: Load opening balances
        opening_balances = {}
        if snapshot_id:
            cursor.execute("""
                SELECT item_name, physical_count
                FROM inventory_snapshot_items
                WHERE snapshot_id = %s
            """, (snapshot_id,))
            for row in cursor.fetchall():
                opening_balances[row["item_name"]] = float(row["physical_count"])

        # Step 3: Calculate consumption
        all_consumed_items = {}
        cursor.execute("SELECT DISTINCT ItemType FROM tblorder_detailshistory")
        item_types = [row["ItemType"] for row in cursor.fetchall()]

        for item_type in item_types:
            cursor.execute("""
                SELECT d.ItemName, SUM(d.count) AS total_sold
                FROM tblorder_detailshistory d
                JOIN tblorderhistory o ON o.idtblorderHistory = d.order_ID
                WHERE o.Date BETWEEN %s AND %s AND o.Outlet_Name = %s AND d.ItemType = %s
                GROUP BY d.ItemName
            """, (start_date, end_date, outlet, item_type))

            for sold_item in cursor.fetchall():
                item_name = sold_item["ItemName"]
                quantity_sold = sold_item["total_sold"]

                cursor.execute("""
                    SELECT id FROM recipe
                    WHERE outlet = %s AND name = %s AND ItemType = %s
                """, (outlet, item_name, item_type))
                recipe_info = cursor.fetchone()

                if recipe_info:
                    recipe_id = recipe_info["id"]

                    cursor.execute("""
                        SELECT name, quantity, uom, new_uom
                        FROM recipe_items WHERE recipe_id = %s
                    """, (recipe_id,))
                    for ri in cursor.fetchall():
                        name = ri["name"]
                        consumed = float(ri["quantity"]) * float(quantity_sold)
                        if name not in all_consumed_items:
                            all_consumed_items[name] = {
                                "total_consumed": 0,
                                "real_consumed": 0,
                                "uom": ri["uom"],
                                "new_uom": ri["new_uom"],
                                "unitdefinition": {"unit": "", "uom": ""}

                            }
                        all_consumed_items[name]["total_consumed"] += consumed

                    if include_sub_recipe_items:
                        cursor.execute("""
                            SELECT rs.sub_recipe_id, rs.quantity AS sr_qty, s.id
                            FROM recipe_subrecipes rs
                            JOIN sub_recipe s ON rs.sub_recipe_id = s.id
                            WHERE rs.recipe_id = %s
                        """, (recipe_id,))
                        for sr in cursor.fetchall():
                            cursor.execute("""
                                SELECT name, quantity, uom, new_uom
                                FROM sub_recipe_items WHERE sub_recipe_id = %s
                            """, (sr["id"],))
                            for sri in cursor.fetchall():
                                name = sri["name"]
                                consumed = float(sri["quantity"]) * float(sr["sr_qty"]) * float(quantity_sold)
                                if name not in all_consumed_items:
                                    all_consumed_items[name] = {
                                        "total_consumed": 0,
                                        "uom": sri["uom"],
                                        "new_uom": sri["new_uom"],
                                        "unitdefinition": {"unit": "", "uom": ""},
                                        "real_consumed": 0
                                    }
                                all_consumed_items[name]["total_consumed"] += consumed
        print(all_consumed_items)

        # Step 3.1: Convert consumption using unitdefinition
        for item_name, details in all_consumed_items.items():
            # uom = details["uom"]
            # new_uom = details["new_uom"]
            total_consumed = details["total_consumed"]

            # Default real_consumed is same as total_consumed
            real_consumed = total_consumed

            cursor.execute("""
                SELECT unit, uom FROM tblunitdefinition
                WHERE name = %s and outlet = %s
            """, (item_name, outlet))
            result = cursor.fetchone()

            unitdefinition_dict = {
                    "unit": None,
                    "uom": None
                }

            if result:
                factor = 1/float(result["unit"])
                real_consumed = float(total_consumed) * factor
                unitdefinition_dict = {
                    "unit": result["unit"],
                    "uom": result["uom"]
                }

            all_consumed_items[item_name]["total_consumed"] = real_consumed
            all_consumed_items[item_name]["unitdefinition"] = unitdefinition_dict

        # Step 4: Get received items from the new store requisition tables
        cursor.execute("""
            SELECT 
                d.ItemName as item_name,
                SUM(d.Amount) as total_received,
                d.UOM as uom
            FROM intblstorereqdetails d
            JOIN intblstorerequisition r ON d.StoreReqID = r.idintblStoreRequisition
            WHERE r.Outlet = %s 
                AND DATE(r.Date) BETWEEN %s AND %s
            GROUP BY d.ItemName, d.UOM
        """, (outlet, start_date, end_date))
        received_items = cursor.fetchall()

        # Step 5: Get wastage items
        cursor.execute("""
            SELECT item_name, SUM(quantity) as total_wasted
            FROM wastage_items
            WHERE outlet_name = %s AND received_date BETWEEN %s AND %s
            GROUP BY item_name
        """, (outlet, start_date, end_date))
        wastage_data = {row["item_name"]: float(row["total_wasted"]) for row in cursor.fetchall()}

        # Step 5.1: Get physical items
        cursor.execute("""
            SELECT item_name, SUM(quantity) as total_physical, uom
            FROM physical_items
            WHERE outlet_name = %s AND received_date BETWEEN %s AND %s
            GROUP BY item_name, uom
        """, (outlet, start_date, end_date))
        physical_data = {row["item_name"]: float(row["total_physical"]) for row in cursor.fetchall()}



        # Step 6: Get stock items
        cursor.execute("""
            SELECT ItemName, GroupName, Type, UOM
            FROM stock_statement WHERE OutletName = %s
        """, (outlet,))
        all_stock_items = cursor.fetchall()

        # Step 7: Combine all into summary
        item_data = {}

        for stock_item in all_stock_items:
            name = stock_item["ItemName"]
            item_data[name] = {
                "total_consumed": 0.0,
                "total_received": 0.0,
                "total_wasted": 0.0,
                "total_physical": 0.0,
                "opening": opening_balances.get(name, 0.0),
                "uom": stock_item["UOM"],
                "new_uom": stock_item["UOM"],
                "group_name": stock_item["GroupName"] or "Group Not Found",
                "type": stock_item["Type"] or "Type Not Found",
                "real_consumed" : 0.0,
                "unitdefinition" : {
                    "unit" : "",
                    "uom": ""
                }
            }

        for name, info in all_consumed_items.items():
            if name not in item_data:
                item_data[name] = {
                    "total_consumed": 0.0,
                    "total_received": 0.0,
                    "total_wasted": 0.0,
                    "total_physical": 0.0,
                    "opening": opening_balances.get(name, 0.0),
                    "uom": info["uom"],
                    "new_uom": info["new_uom"],
                    "group_name": "Group Not Found",
                    "type": "Type Not Found",
                    "real_consumed" : 0.0,
                    "unitdefinition" : {
                        "unit" : "",
                        "uom": ""
                    }
                }
            item_data[name]["total_consumed"] = float(info["total_consumed"])
            item_data[name]["unitdefinition"] = info["unitdefinition"]
            # item_data[name]["uom"] = info["uom"]
            item_data[name]["new_uom"] = info["new_uom"]

        for item in received_items:
            name = item["item_name"]
            if name not in item_data:
                item_data[name] = {
                    "total_consumed": 0.0,
                    "total_received": 0.0,
                    "total_wasted": 0.0,
                    "total_physical": 0.0,
                    "opening": opening_balances.get(name, 0.0),
                    "uom": item["uom"],
                    "new_uom": item["uom"],
                    "group_name": "Group Not Found",
                    "type": "Type Not Found",
                    "real_consumed" : 0.0,
                    "unitdefinition" : {
                        "unit" : "",
                        "uom": ""
                    }
                }
            item_data[name]["total_received"] = float(item["total_received"])

        for name, wasted_qty in wastage_data.items():
            if name not in item_data:
                item_data[name] = {
                    "total_consumed": 0.0,
                    "total_received": 0.0,
                    "total_wasted": 0.0,
                    "total_physical": 0.0,
                    "opening": opening_balances.get(name, 0.0),
                    "uom": "UOM",
                    "new_uom": "UOM",
                    "group_name": "Group Not Found",
                    "type": "Type Not Found",
                    "unitdefinition" : {
                        "unit" : "",
                        "uom": ""
                    }
                }
            item_data[name]["total_wasted"] = float(wasted_qty)

        for name, physical_qty in physical_data.items():
            if name not in item_data:
                item_data[name] = {
                    "total_consumed": 0.0,
                    "total_received": 0.0,
                    "total_wasted": 0.0,
                    "total_physical": 0.0,
                    "opening": opening_balances.get(name, 0.0),
                    "uom": "UOM",
                    "new_uom": "UOM",
                    "group_name": "Group Not Found",
                    "type": "Type Not Found",
                    "unitdefinition" : {
                        "unit" : "",
                        "uom": ""
                    }
                }
            item_data[name]["total_physical"] = float(physical_qty)

        # Step 8: Final nested summary
        nested_summary = {}
        for name, info in item_data.items():
            consumed = Decimal(info["total_consumed"])
            received = Decimal(info["total_received"])
            wasted = Decimal(info["total_wasted"])
            physical = Decimal(info["total_physical"])
            opening = Decimal(info["opening"])
            closing = opening + received - consumed - wasted

            item_type = info["type"]
            group_name = info["group_name"]

            if item_type not in nested_summary:
                nested_summary[item_type] = {}

            if group_name not in nested_summary[item_type]:
                nested_summary[item_type][group_name] = []

            nested_summary[item_type][group_name].append({
                "name": name,
                "uom": info["uom"],
                "new_uom": info["new_uom"],
                "opening": float(opening),
                "total_consumed": float(consumed),
                "total_received": float(received),
                "total_wasted": float(wasted),
                "total_physical": float(physical),
                "closing_balance": float(closing) if float(closing) > 0 else 0,
                'unitdefinition': info['unitdefinition']
            })


        # Step 5.2: Check if there are any physical items entries before the start_date
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM physical_items
            WHERE outlet_name = %s AND received_date < %s
            LIMIT 1
        """, (outlet, start_date))
        result = cursor.fetchone()
        has_physical_before_start = result["count"] > 0 if result else False

        cursor.execute("""
            SELECT start_date, end_date
            FROM inventory_snapshot_master
            WHERE outlet_name = %s order by id asc
            LIMIT 1
        """, (outlet,))
        opening_date_result = cursor.fetchone()

        if opening_date_result:
            opening_start_date = result["start_date"]
            opening_end_date = result["end_date"]
        else:
            opening_start_date = None
            opening_end_date = None
        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "summary": nested_summary,
            "period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "has_physical_before_start": has_physical_before_start,
            "outlet": outlet,
            "first_opening_dates": {
                "start_date" : opening_start_date,
                "end_date" : opening_end_date,
            }
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    

@app_file115.route("/inventory-summary-food", methods=["POST"])
@cross_origin()
def inventory_summary_food():
    try:
        data = request.get_json()
        token = data.get("token")
        if not token or not token_auth(token):
            return jsonify({"error": "Invalid or missing token."}), 400

        outlet = data.get("outlet")
        include_sub_recipe_items = data.get("includeSubRecipeItems", True)

        if not outlet:
            return jsonify({"error": "Missing outlet."}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Step 1: Determine start_date and end_date
        cursor.execute("""
            SELECT id, end_date FROM inventory_snapshot_master_food
            WHERE outlet_name = %s
            ORDER BY end_date DESC LIMIT 1
        """, (outlet,))
        snapshot = cursor.fetchone()

        if snapshot:
            snapshot_id = snapshot["id"]
            # start_date = snapshot["end_date"] + timedelta(days=1)
            # start_date = start_date.strftime("%Y-%m-%d")
        else:
            snapshot_id = None
            # start_date = '2000-01-01'

        # end_date = datetime.today().strftime('%Y-%m-%d')
        start_date = data.get("startDate")
        end_date = data.get("endDate")

        if not start_date or not end_date or not outlet:
            return jsonify({"error": "Missing startDate, endDate, or outlet."}), 400


        # Step 2: Load opening balances
        opening_balances = {}
        if snapshot_id:
            cursor.execute("""
                SELECT item_name, physical_count
                FROM inventory_snapshot_items_food
                WHERE snapshot_id = %s
            """, (snapshot_id,))
            for row in cursor.fetchall():
                opening_balances[row["item_name"]] = float(row["physical_count"])

        # Step 3: Calculate consumption
        all_consumed_items = {}
        # cursor.execute("SELECT DISTINCT ItemType FROM tblorder_detailshistory AND ItemType='Food' ")
        # item_types = [row["ItemType"] for row in cursor.fetchall()]

        item_types = ["Food", 'food']

        for item_type in item_types:
            cursor.execute("""
                SELECT d.ItemName, SUM(d.count) AS total_sold
                FROM tblorder_detailshistory d
                JOIN tblorderhistory o ON o.idtblorderHistory = d.order_ID
                WHERE o.Date BETWEEN %s AND %s AND o.Outlet_Name = %s AND d.ItemType = %s
                GROUP BY d.ItemName
            """, (start_date, end_date, outlet, item_type))

            for sold_item in cursor.fetchall():
                item_name = sold_item["ItemName"]
                quantity_sold = sold_item["total_sold"]

                cursor.execute("""
                    SELECT id FROM recipe
                    WHERE outlet = %s AND name = %s AND ItemType = %s
                """, (outlet, item_name, item_type))
                recipe_info = cursor.fetchone()

                if recipe_info:
                    recipe_id = recipe_info["id"]

                    cursor.execute("""
                        SELECT name, quantity, uom, new_uom
                        FROM recipe_items WHERE recipe_id = %s
                    """, (recipe_id,))
                    for ri in cursor.fetchall():
                        name = ri["name"]
                        consumed = float(ri["quantity"]) * float(quantity_sold)
                        if name not in all_consumed_items:
                            all_consumed_items[name] = {
                                "total_consumed": 0,
                                "real_consumed": 0,
                                "uom": ri["uom"],
                                "new_uom": ri["new_uom"],
                                "unitdefinition": {"unit": "", "uom": ""}

                            }
                        all_consumed_items[name]["total_consumed"] += consumed

                    if include_sub_recipe_items:
                        cursor.execute("""
                            SELECT rs.sub_recipe_id, rs.quantity AS sr_qty, s.id
                            FROM recipe_subrecipes rs
                            JOIN sub_recipe s ON rs.sub_recipe_id = s.id
                            WHERE rs.recipe_id = %s
                        """, (recipe_id,))
                        for sr in cursor.fetchall():
                            cursor.execute("""
                                SELECT name, quantity, uom, new_uom
                                FROM sub_recipe_items WHERE sub_recipe_id = %s
                            """, (sr["id"],))
                            for sri in cursor.fetchall():
                                name = sri["name"]
                                consumed = float(sri["quantity"]) * float(sr["sr_qty"]) * float(quantity_sold)
                                if name not in all_consumed_items:
                                    all_consumed_items[name] = {
                                        "total_consumed": 0,
                                        "uom": sri["uom"],
                                        "new_uom": sri["new_uom"],
                                        "unitdefinition": {"unit": "", "uom": ""},
                                        "real_consumed": 0
                                    }
                                all_consumed_items[name]["total_consumed"] += consumed
        print(all_consumed_items)

        # Step 3.1: Convert consumption using unitdefinition
        for item_name, details in all_consumed_items.items():
            # uom = details["uom"]
            # new_uom = details["new_uom"]
            total_consumed = details["total_consumed"]

            # Default real_consumed is same as total_consumed
            real_consumed = total_consumed

            cursor.execute("""
                SELECT unit, uom FROM tblunitdefinition
                WHERE name = %s and outlet = %s
            """, (item_name, outlet))
            result = cursor.fetchone()

            unitdefinition_dict = {
                    "unit": None,
                    "uom": None
                }

            if result:
                factor = 1/float(result["unit"])
                real_consumed = float(total_consumed) * factor
                unitdefinition_dict = {
                    "unit": result["unit"],
                    "uom": result["uom"]
                }

            all_consumed_items[item_name]["total_consumed"] = real_consumed
            all_consumed_items[item_name]["unitdefinition"] = unitdefinition_dict

        # Step 4: Get received items from the new store requisition tables
        cursor.execute("""
            SELECT 
                d.ItemName as item_name,
                SUM(d.Amount) as total_received,
                d.UOM as uom
            FROM intblstorereqdetails d
            JOIN intblstorerequisition r ON d.StoreReqID = r.idintblStoreRequisition
            WHERE r.Outlet = %s 
                AND DATE(r.Date) BETWEEN %s AND %s
            GROUP BY d.ItemName, d.UOM
        """, (outlet, start_date, end_date))
        received_items = cursor.fetchall()

        # Step 5: Get wastage items
        cursor.execute("""
            SELECT item_name, SUM(quantity) as total_wasted
            FROM wastage_items
            WHERE outlet_name = %s AND received_date BETWEEN %s AND %s
            GROUP BY item_name
        """, (outlet, start_date, end_date))
        wastage_data = {row["item_name"]: float(row["total_wasted"]) for row in cursor.fetchall()}

        # Step 5.1: Get physical items
        cursor.execute("""
            SELECT item_name, SUM(quantity) as total_physical, uom
            FROM physical_items
            WHERE outlet_name = %s AND received_date BETWEEN %s AND %s
            GROUP BY item_name, uom
        """, (outlet, start_date, end_date))
        physical_data = {row["item_name"]: float(row["total_physical"]) for row in cursor.fetchall()}



        # Step 6: Get stock items
        cursor.execute("""
            SELECT ItemName, GroupName, Type, UOM
            FROM stock_statement WHERE OutletName = %s AND Type='Food'
        """, (outlet,))
        all_stock_items = cursor.fetchall()

        # Step 7: Combine all into summary
        item_data = {}

        for stock_item in all_stock_items:
            name = stock_item["ItemName"]
            item_data[name] = {
                "total_consumed": 0.0,
                "total_received": 0.0,
                "total_wasted": 0.0,
                "total_physical": 0.0,
                "opening": opening_balances.get(name, 0.0),
                "uom": stock_item["UOM"],
                "new_uom": stock_item["UOM"],
                "group_name": stock_item["GroupName"] or "Group Not Found",
                "type": stock_item["Type"] or "Type Not Found",
                "real_consumed" : 0.0,
                "unitdefinition" : {
                    "unit" : "",
                    "uom": ""
                }
            }

        for name, info in all_consumed_items.items():
            if name not in item_data:
                item_data[name] = {
                    "total_consumed": 0.0,
                    "total_received": 0.0,
                    "total_wasted": 0.0,
                    "total_physical": 0.0,
                    "opening": opening_balances.get(name, 0.0),
                    "uom": info["uom"],
                    "new_uom": info["new_uom"],
                    "group_name": "Group Not Found",
                    "type": "Type Not Found",
                    "real_consumed" : 0.0,
                    "unitdefinition" : {
                        "unit" : "",
                        "uom": ""
                    }
                }
            item_data[name]["total_consumed"] = float(info["total_consumed"])
            item_data[name]["unitdefinition"] = info["unitdefinition"]
            # item_data[name]["uom"] = info["uom"]
            item_data[name]["new_uom"] = info["new_uom"]

        for item in received_items:
            name = item["item_name"]
            if name not in item_data:
                item_data[name] = {
                    "total_consumed": 0.0,
                    "total_received": 0.0,
                    "total_wasted": 0.0,
                    "total_physical": 0.0,
                    "opening": opening_balances.get(name, 0.0),
                    "uom": item["uom"],
                    "new_uom": item["uom"],
                    "group_name": "Group Not Found",
                    "type": "Type Not Found",
                    "real_consumed" : 0.0,
                    "unitdefinition" : {
                        "unit" : "",
                        "uom": ""
                    }
                }
            item_data[name]["total_received"] = float(item["total_received"])

        for name, wasted_qty in wastage_data.items():
            if name not in item_data:
                item_data[name] = {
                    "total_consumed": 0.0,
                    "total_received": 0.0,
                    "total_wasted": 0.0,
                    "total_physical": 0.0,
                    "opening": opening_balances.get(name, 0.0),
                    "uom": "UOM",
                    "new_uom": "UOM",
                    "group_name": "Group Not Found",
                    "type": "Type Not Found",
                    "unitdefinition" : {
                        "unit" : "",
                        "uom": ""
                    }
                }
            item_data[name]["total_wasted"] = float(wasted_qty)

        for name, physical_qty in physical_data.items():
            if name not in item_data:
                item_data[name] = {
                    "total_consumed": 0.0,
                    "total_received": 0.0,
                    "total_wasted": 0.0,
                    "total_physical": 0.0,
                    "opening": opening_balances.get(name, 0.0),
                    "uom": "UOM",
                    "new_uom": "UOM",
                    "group_name": "Group Not Found",
                    "type": "Type Not Found",
                    "unitdefinition" : {
                        "unit" : "",
                        "uom": ""
                    }
                }
            item_data[name]["total_physical"] = float(physical_qty)

        # Step 8: Final nested summary
        nested_summary = {}
        for name, info in item_data.items():
            consumed = Decimal(info["total_consumed"])
            received = Decimal(info["total_received"])
            wasted = Decimal(info["total_wasted"])
            physical = Decimal(info["total_physical"])
            opening = Decimal(info["opening"])
            closing = opening + received - consumed - wasted

            item_type = info["type"]
            group_name = info["group_name"]

            if item_type not in nested_summary:
                nested_summary[item_type] = {}

            if group_name not in nested_summary[item_type]:
                nested_summary[item_type][group_name] = []

            nested_summary[item_type][group_name].append({
                "name": name,
                "uom": info["uom"],
                "new_uom": info["new_uom"],
                "opening": float(opening),
                "total_consumed": float(consumed),
                "total_received": float(received),
                "total_wasted": float(wasted),
                "total_physical": float(physical),
                "closing_balance": float(closing) if float(closing) > 0 else 0,
                'unitdefinition': info['unitdefinition']
            })


        # Step 5.2: Check if there are any physical items entries before the start_date
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM physical_items
            WHERE outlet_name = %s AND received_date < %s
            LIMIT 1
        """, (outlet, start_date))
        result = cursor.fetchone()
        has_physical_before_start = result["count"] > 0 if result else False

        cursor.execute("""
            SELECT start_date, end_date
            FROM inventory_snapshot_master_food
            WHERE outlet_name = %s order by id asc
            LIMIT 1
        """, (outlet,))
        opening_date_result = cursor.fetchone()

        if opening_date_result:
            opening_start_date = result["start_date"]
            opening_end_date = result["end_date"]
        else:
            opening_start_date = None
            opening_end_date = None
        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "summary": nested_summary,
            "period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "has_physical_before_start": has_physical_before_start,
            "outlet": outlet,
            "first_opening_dates": {
                "start_date" : opening_start_date,
                "end_date" : opening_end_date,
            }
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    

@app_file115.route("/inventory-summary-beverage", methods=["POST"])
@cross_origin()
def inventory_summary_beverage():
    try:
        data = request.get_json()
        token = data.get("token")
        if not token or not token_auth(token):
            return jsonify({"error": "Invalid or missing token."}), 400

        outlet = data.get("outlet")
        include_sub_recipe_items = data.get("includeSubRecipeItems", True)

        if not outlet:
            return jsonify({"error": "Missing outlet."}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Step 1: Determine start_date and end_date
        cursor.execute("""
            SELECT id, end_date FROM inventory_snapshot_master_beverage
            WHERE outlet_name = %s
            ORDER BY end_date DESC LIMIT 1
        """, (outlet,))
        snapshot = cursor.fetchone()

        if snapshot:
            snapshot_id = snapshot["id"]
            # start_date = snapshot["end_date"] + timedelta(days=1)
            # start_date = start_date.strftime("%Y-%m-%d")
        else:
            snapshot_id = None
            # start_date = '2000-01-01'

        # end_date = datetime.today().strftime('%Y-%m-%d')
        start_date = data.get("startDate")
        end_date = data.get("endDate")

        if not start_date or not end_date or not outlet:
            return jsonify({"error": "Missing startDate, endDate, or outlet."}), 400


        # Step 2: Load opening balances
        opening_balances = {}
        if snapshot_id:
            cursor.execute("""
                SELECT item_name, physical_count
                FROM inventory_snapshot_items_beverage
                WHERE snapshot_id = %s
            """, (snapshot_id,))
            for row in cursor.fetchall():
                opening_balances[row["item_name"]] = float(row["physical_count"])

        # Step 3: Calculate consumption
        all_consumed_items = {}
        # cursor.execute("SELECT DISTINCT ItemType FROM tblorder_detailshistory where ItemType='Beverage'")
        # item_types = [row["ItemType"] for row in cursor.fetchall()]

        item_types = ["beverage", "Beverage"]

        for item_type in item_types:
            cursor.execute("""
                SELECT d.ItemName, SUM(d.count) AS total_sold
                FROM tblorder_detailshistory d
                JOIN tblorderhistory o ON o.idtblorderHistory = d.order_ID
                WHERE o.Date BETWEEN %s AND %s AND o.Outlet_Name = %s AND d.ItemType = %s
                GROUP BY d.ItemName
            """, (start_date, end_date, outlet, item_type))

            for sold_item in cursor.fetchall():
                item_name = sold_item["ItemName"]
                quantity_sold = sold_item["total_sold"]

                cursor.execute("""
                    SELECT id FROM recipe
                    WHERE outlet = %s AND name = %s AND ItemType = %s
                """, (outlet, item_name, item_type))
                recipe_info = cursor.fetchone()

                if recipe_info:
                    recipe_id = recipe_info["id"]

                    cursor.execute("""
                        SELECT name, quantity, uom, new_uom
                        FROM recipe_items WHERE recipe_id = %s
                    """, (recipe_id,))
                    for ri in cursor.fetchall():
                        name = ri["name"]
                        consumed = float(ri["quantity"]) * float(quantity_sold)
                        if name not in all_consumed_items:
                            all_consumed_items[name] = {
                                "total_consumed": 0,
                                "real_consumed": 0,
                                "uom": ri["uom"],
                                "new_uom": ri["new_uom"],
                                "unitdefinition": {"unit": "", "uom": ""}

                            }
                        all_consumed_items[name]["total_consumed"] += consumed

                    if include_sub_recipe_items:
                        cursor.execute("""
                            SELECT rs.sub_recipe_id, rs.quantity AS sr_qty, s.id
                            FROM recipe_subrecipes rs
                            JOIN sub_recipe s ON rs.sub_recipe_id = s.id
                            WHERE rs.recipe_id = %s
                        """, (recipe_id,))
                        for sr in cursor.fetchall():
                            cursor.execute("""
                                SELECT name, quantity, uom, new_uom
                                FROM sub_recipe_items WHERE sub_recipe_id = %s
                            """, (sr["id"],))
                            for sri in cursor.fetchall():
                                name = sri["name"]
                                consumed = float(sri["quantity"]) * float(sr["sr_qty"]) * float(quantity_sold)
                                if name not in all_consumed_items:
                                    all_consumed_items[name] = {
                                        "total_consumed": 0,
                                        "uom": sri["uom"],
                                        "new_uom": sri["new_uom"],
                                        "unitdefinition": {"unit": "", "uom": ""},
                                        "real_consumed": 0
                                    }
                                all_consumed_items[name]["total_consumed"] += consumed
        print(all_consumed_items)

        # Step 3.1: Convert consumption using unitdefinition
        for item_name, details in all_consumed_items.items():
            # uom = details["uom"]
            # new_uom = details["new_uom"]
            total_consumed = details["total_consumed"]

            # Default real_consumed is same as total_consumed
            real_consumed = total_consumed

            cursor.execute("""
                SELECT unit, uom FROM tblunitdefinition
                WHERE name = %s and outlet = %s
            """, (item_name, outlet))
            result = cursor.fetchone()
            unitdefinition_dict = {
                    "unit": None,
                    "uom": None
                }
            if result:
                factor = 1/float(result["unit"])
                real_consumed = float(total_consumed) * factor
                unitdefinition_dict = {
                    "unit": result["unit"],
                    "uom": result["uom"]
                }

            all_consumed_items[item_name]["total_consumed"] = real_consumed
            all_consumed_items[item_name]["unitdefinition"] = unitdefinition_dict

        # Step 4: Get received items from the new store requisition tables
        cursor.execute("""
            SELECT 
                d.ItemName as item_name,
                SUM(d.Amount) as total_received,
                d.UOM as uom
            FROM intblstorereqdetails d
            JOIN intblstorerequisition r ON d.StoreReqID = r.idintblStoreRequisition
            WHERE r.Outlet = %s 
                AND DATE(r.Date) BETWEEN %s AND %s
            GROUP BY d.ItemName, d.UOM
        """, (outlet, start_date, end_date))
        received_items = cursor.fetchall()

        # Step 5: Get wastage items
        cursor.execute("""
            SELECT item_name, SUM(quantity) as total_wasted
            FROM wastage_items
            WHERE outlet_name = %s AND received_date BETWEEN %s AND %s
            GROUP BY item_name
        """, (outlet, start_date, end_date))
        wastage_data = {row["item_name"]: float(row["total_wasted"]) for row in cursor.fetchall()}

        # Step 5.1: Get physical items
        cursor.execute("""
            SELECT item_name, SUM(quantity) as total_physical, uom
            FROM physical_items
            WHERE outlet_name = %s AND received_date BETWEEN %s AND %s
            GROUP BY item_name, uom
        """, (outlet, start_date, end_date))
        physical_data = {row["item_name"]: float(row["total_physical"]) for row in cursor.fetchall()}



        # Step 6: Get stock items
        cursor.execute("""
            SELECT ItemName, GroupName, Type, UOM
            FROM stock_statement WHERE OutletName = %s and Type= 'Beverage'
        """, (outlet,))
        all_stock_items = cursor.fetchall()

        # Step 7: Combine all into summary
        item_data = {}

        for stock_item in all_stock_items:
            name = stock_item["ItemName"]
            item_data[name] = {
                "total_consumed": 0.0,
                "total_received": 0.0,
                "total_wasted": 0.0,
                "total_physical": 0.0,
                "opening": opening_balances.get(name, 0.0),
                "uom": stock_item["UOM"],
                "new_uom": stock_item["UOM"],
                "group_name": stock_item["GroupName"] or "Group Not Found",
                "type": stock_item["Type"] or "Type Not Found",
                "real_consumed" : 0.0,
                "unitdefinition" : {
                    "unit" : "",
                    "uom": ""
                }
            }

        for name, info in all_consumed_items.items():
            if name not in item_data:
                item_data[name] = {
                    "total_consumed": 0.0,
                    "total_received": 0.0,
                    "total_wasted": 0.0,
                    "total_physical": 0.0,
                    "opening": opening_balances.get(name, 0.0),
                    "uom": info["uom"],
                    "new_uom": info["new_uom"],
                    "group_name": "Group Not Found",
                    "type": "Type Not Found",
                    "real_consumed" : 0.0,
                    "unitdefinition" : {
                        "unit" : "",
                        "uom": ""
                    }
                }
            item_data[name]["total_consumed"] = float(info["total_consumed"])
            item_data[name]["unitdefinition"] = info["unitdefinition"]
            # item_data[name]["uom"] = info["uom"]
            item_data[name]["new_uom"] = info["new_uom"]

        for item in received_items:
            name = item["item_name"]
            if name not in item_data:
                item_data[name] = {
                    "total_consumed": 0.0,
                    "total_received": 0.0,
                    "total_wasted": 0.0,
                    "total_physical": 0.0,
                    "opening": opening_balances.get(name, 0.0),
                    "uom": item["uom"],
                    "new_uom": item["uom"],
                    "group_name": "Group Not Found",
                    "type": "Type Not Found",
                    "real_consumed" : 0.0,
                    "unitdefinition" : {
                        "unit" : "",
                        "uom": ""
                    }
                }
            item_data[name]["total_received"] = float(item["total_received"])

        for name, wasted_qty in wastage_data.items():
            if name not in item_data:
                item_data[name] = {
                    "total_consumed": 0.0,
                    "total_received": 0.0,
                    "total_wasted": 0.0,
                    "total_physical": 0.0,
                    "opening": opening_balances.get(name, 0.0),
                    "uom": "UOM",
                    "new_uom": "UOM",
                    "group_name": "Group Not Found",
                    "type": "Type Not Found",
                    "unitdefinition" : {
                        "unit" : "",
                        "uom": ""
                    }
                }
            item_data[name]["total_wasted"] = float(wasted_qty)

        for name, physical_qty in physical_data.items():
            if name not in item_data:
                item_data[name] = {
                    "total_consumed": 0.0,
                    "total_received": 0.0,
                    "total_wasted": 0.0,
                    "total_physical": 0.0,
                    "opening": opening_balances.get(name, 0.0),
                    "uom": "UOM",
                    "new_uom": "UOM",
                    "group_name": "Group Not Found",
                    "type": "Type Not Found",
                    "unitdefinition" : {
                        "unit" : "",
                        "uom": ""
                    }
                }
            item_data[name]["total_physical"] = float(physical_qty)

        # Step 8: Final nested summary
        nested_summary = {}
        for name, info in item_data.items():
            consumed = Decimal(info["total_consumed"])
            received = Decimal(info["total_received"])
            wasted = Decimal(info["total_wasted"])
            physical = Decimal(info["total_physical"])
            opening = Decimal(info["opening"])
            closing = opening + received - consumed - wasted

            item_type = info["type"]
            group_name = info["group_name"]

            if item_type not in nested_summary:
                nested_summary[item_type] = {}

            if group_name not in nested_summary[item_type]:
                nested_summary[item_type][group_name] = []

            nested_summary[item_type][group_name].append({
                "name": name,
                "uom": info["uom"],
                "new_uom": info["new_uom"],
                "opening": float(opening),
                "total_consumed": float(consumed),
                "total_received": float(received),
                "total_wasted": float(wasted),
                "total_physical": float(physical),
                "closing_balance": float(closing) if float(closing) > 0 else 0,
                'unitdefinition': info['unitdefinition']
            })


        # Step 5.2: Check if there are any physical items entries before the start_date
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM physical_items
            WHERE outlet_name = %s AND received_date < %s
            LIMIT 1
        """, (outlet, start_date))
        result = cursor.fetchone()
        has_physical_before_start = result["count"] > 0 if result else False

        cursor.execute("""
            SELECT start_date, end_date
            FROM inventory_snapshot_master_beverage
            WHERE outlet_name = %s order by id asc
            LIMIT 1
        """, (outlet,))
        opening_date_result = cursor.fetchone()

        if opening_date_result:
            opening_start_date = result["start_date"]
            opening_end_date = result["end_date"]
        else:
            opening_start_date = None
            opening_end_date = None
        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "summary": nested_summary,
            "period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "has_physical_before_start": has_physical_before_start,
            "outlet": outlet,
            "first_opening_dates": {
                "start_date" : opening_start_date,
                "end_date" : opening_end_date,
            }
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400