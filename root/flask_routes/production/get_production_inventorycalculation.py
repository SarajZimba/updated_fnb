from flask import Blueprint, jsonify, request
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv
from datetime import datetime
from decimal import Decimal

from root.auth.check import token_auth

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("host"),
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )

load_dotenv()

app_file234 = Blueprint('app_file234', __name__)

@app_file234.route("/inventory-summary-production", methods=["POST"])
@cross_origin()
def inventory_summary_production():
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
            SELECT id, end_date FROM production_inventorycalculation
            WHERE outlet_name = %s
            ORDER BY end_date DESC LIMIT 1
        """, (outlet,))
        snapshot = cursor.fetchone()

        if snapshot:
            snapshot_id = snapshot["id"]
        else:
            snapshot_id = None

        start_date = data.get("startDate")
        end_date = data.get("endDate")

        if not start_date or not end_date or not outlet:
            return jsonify({"error": "Missing startDate, endDate, or outlet."}), 400


        # Step 2: Load opening balances
        opening_balances = {}
        if snapshot_id:
            cursor.execute("""
                SELECT item_name, physical_count
                FROM production_inventorycalculation_items
                WHERE snapshot_id = %s
            """, (snapshot_id,))
            for row in cursor.fetchall():
                opening_balances[row["item_name"]] = float(row["physical_count"])

        # all_consumed_items = {}

        # # for item_type in item_types:
        # cursor.execute("""
        #     SELECT 
        #         d.ItemName, 
        #         SUM(d.Amount) AS total_sold
        #     FROM intblstorereqdetails d
        #     JOIN intblstorerequisition r ON r.idintblStoreRequisition = d.StoreReqID
        #     JOIN stock_statement s ON s.ItemName = d.ItemName 
        #         AND s.OutletName = r.Outlet
        #         AND s.GroupName = 'Finished Goods'
        #     WHERE r.Date BETWEEN %s AND %s 
        #         AND r.Outlet = %s 
        #     GROUP BY d.ItemName
        # """, (start_date, end_date, outlet))

        # for sold_item in cursor.fetchall():
        #     item_name = sold_item["ItemName"]
        #     quantity_sold = sold_item["total_sold"]

        #     cursor.execute("""
        #             SELECT id FROM recipe
        #             WHERE outlet = %s AND name = %s and recipe_type = 'Production' 
        #         """, (outlet, item_name))
        #     recipe_info = cursor.fetchone()

        #     if recipe_info:
        #         recipe_id = recipe_info["id"]

        #         cursor.execute("""
        #                 SELECT name, quantity, uom, new_uom
        #                 FROM recipe_items WHERE recipe_id = %s
        #             """, (recipe_id,))
        #         for ri in cursor.fetchall():
        #             name = ri["name"]
        #             consumed = float(ri["quantity"]) * float(quantity_sold)
        #             if name not in all_consumed_items:
        #                 all_consumed_items[name] = {
        #                         "total_consumed": 0,
        #                         "real_consumed": 0,
        #                         "uom": ri["uom"],
        #                         "new_uom": ri["new_uom"],
        #                         "unitdefinition": {"unit": "", "uom": ""}

        #                     }
        #             all_consumed_items[name]["total_consumed"] += consumed

        #         if include_sub_recipe_items:
        #             cursor.execute("""
        #                     SELECT rs.sub_recipe_id, rs.quantity AS sr_qty, s.id
        #                     FROM recipe_subrecipes rs
        #                     JOIN sub_recipe s ON rs.sub_recipe_id = s.id
        #                     WHERE rs.recipe_id = %s
        #                 """, (recipe_id,))
        #             for sr in cursor.fetchall():
        #                 cursor.execute("""
        #                         SELECT name, quantity, uom, new_uom
        #                         FROM sub_recipe_items WHERE sub_recipe_id = %s
        #                     """, (sr["id"],))
        #                 for sri in cursor.fetchall():
        #                     name = sri["name"]
        #                     consumed = float(sri["quantity"]) * float(sr["sr_qty"]) * float(quantity_sold)
        #                     if name not in all_consumed_items:
        #                         all_consumed_items[name] = {
        #                                 "total_consumed": 0,
        #                                 "uom": sri["uom"],
        #                                 "new_uom": sri["new_uom"],
        #                                 "unitdefinition": {"unit": "", "uom": ""},
        #                                 "real_consumed": 0
        #                         }
        #                     all_consumed_items[name]["total_consumed"] += consumed
        # print(all_consumed_items)

        all_consumed_items = {}

        # Get all sold/produced items (Finished Goods from stock_statement)
        cursor.execute("""
            SELECT 
                d.ItemName, 
                SUM(d.Amount) AS total_sold
            FROM intblstorereqdetails d
            JOIN intblstorerequisition r ON r.idintblStoreRequisition = d.StoreReqID
            JOIN stock_statement s ON s.ItemName = d.ItemName 
                AND s.OutletName = r.Outlet
                AND s.GroupName = 'Finished Goods'
            WHERE r.Date BETWEEN %s AND %s 
                AND r.Outlet = %s 
            GROUP BY d.ItemName
        """, (start_date, end_date, outlet))

        # print("sold items", cursor.fetchall())

        for sold_item in cursor.fetchall():
            item_name = sold_item["ItemName"]
            quantity_sold = float(sold_item["total_sold"])
            
            # First, get the ID from stock_statement for this finished good
            cursor.execute("""
                SELECT id, ItemName, GroupName, UOM, CurrentLevel
                FROM stock_statement 
                WHERE ItemName = %s AND OutletName = %s AND GroupName = 'Finished Goods'
            """, (item_name, outlet))
            
            stock_item = cursor.fetchone()
            
            if not stock_item:
                print(f"Item '{item_name}' not found in stock_statement")
                continue
            
            production_item_id = stock_item["id"]


            print("production item id", production_item_id)
            
            # Now get the conversion factor for this production_item_id and outlet
            cursor.execute("""
                SELECT factor, production_recipe_id
                FROM conversionfactor
                WHERE production_item_id = %s AND outlet = %s
            """, (production_item_id, outlet))
            
            conversion = cursor.fetchone()
            
            if not conversion:
                print(f"No conversion factor found for production_item_id: {production_item_id}")
                continue
            
            factor = float(conversion["factor"])
            production_recipe_id = conversion["production_recipe_id"]
            
            # Get the recipe details
            cursor.execute("""
                SELECT id, name, outlet, recipe_type
                FROM recipe
                WHERE id = %s AND recipe_type = 'Production'
            """, (production_recipe_id,))
            
            recipe_info = cursor.fetchone()
            
            if not recipe_info:
                print(f"No recipe found for production_recipe_id: {production_recipe_id}")
                continue
            
            # Calculate consumption considering the factor
            # Actual quantity to produce = quantity_sold / factor
            actual_production_quantity = quantity_sold / factor if factor != 0 else 0
            
            # Get recipe items
            cursor.execute("""
                SELECT name, quantity, uom, new_uom
                FROM recipe_items WHERE recipe_id = %s
            """, (production_recipe_id,))
            
            for ri in cursor.fetchall():
                name = ri["name"]
                recipe_quantity = float(ri["quantity"])
                
                # Consumption = recipe_quantity * actual_production_quantity
                consumed = recipe_quantity * actual_production_quantity
                
                if name not in all_consumed_items:
                    all_consumed_items[name] = {
                        "total_consumed": 0,
                        "real_consumed": 0,
                        "uom": ri["uom"],
                        "new_uom": ri["new_uom"],
                        "unitdefinition": {"unit": "", "uom": ""},
                        "production_quantity": actual_production_quantity,
                        "factor": factor
                    }
                all_consumed_items[name]["total_consumed"] += consumed
            
            # Handle sub-recipes if needed
            if include_sub_recipe_items:
                cursor.execute("""
                    SELECT rs.sub_recipe_id, rs.quantity AS sr_qty, s.id
                    FROM recipe_subrecipes rs
                    JOIN sub_recipe s ON rs.sub_recipe_id = s.id
                    WHERE rs.recipe_id = %s
                """, (production_recipe_id,))
                
                for sr in cursor.fetchall():
                    sub_recipe_qty = float(sr["sr_qty"])
                    sub_recipe_id = sr["id"]
                    
                    cursor.execute("""
                        SELECT name, quantity, uom, new_uom
                        FROM sub_recipe_items WHERE sub_recipe_id = %s
                    """, (sub_recipe_id,))
                    
                    for sri in cursor.fetchall():
                        name = sri["name"]
                        item_quantity = float(sri["quantity"])
                        
                        # Consumption = sub_recipe_item_quantity * sub_recipe_qty * actual_production_quantity
                        consumed = item_quantity * sub_recipe_qty * actual_production_quantity
                        
                        if name not in all_consumed_items:
                            all_consumed_items[name] = {
                                "total_consumed": 0,
                                "uom": sri["uom"],
                                "new_uom": sri["new_uom"],
                                "unitdefinition": {"unit": "", "uom": ""},
                                "real_consumed": 0,
                                "production_quantity": actual_production_quantity,
                                "factor": factor
                            }
                        all_consumed_items[name]["total_consumed"] += consumed

        # # Clear any remaining results
        # while cursor.nextset():
        #     pass

        print(f"all_consumed_items {all_consumed_items}")

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

                real_consumed = float(total_consumed) 
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
            WHERE r.Outlet = %s and r.CostCenter = 'Central Kitchen'
                AND DATE(r.Date) BETWEEN %s AND %s
            GROUP BY d.ItemName, d.UOM
        """, (outlet, start_date, end_date))
        received_items = cursor.fetchall()

        cursor.execute("""
            SELECT 
                item_name,
                SUM(quantity) AS total_wasted
            FROM production_wastage_items
            WHERE outlet_name = %s 
            AND received_date BETWEEN %s AND %s
            GROUP BY item_name
        """, (outlet, start_date, end_date))

        # Fetch all results
        results = cursor.fetchall()

        # Create wastage_data dictionary
        wastage_data = {
            row["item_name"]: float(row["total_wasted"])
            for row in results
        }


        print(f"wastage_data {wastage_data} for {outlet} and {start_date} and {end_date}")
        # Step 5.1: Get physical items
        cursor.execute("""
            SELECT item_name, SUM(quantity) as total_physical, uom
            FROM physical_items
            WHERE outlet_name = %s AND received_date BETWEEN %s AND %s
            GROUP BY item_name, uom
        """, (outlet, start_date, end_date))
        physical_data = {row["item_name"]: float(row["total_physical"]) for row in cursor.fetchall()}

        cursor.execute("""
            SELECT 
                d.ItemName AS ItemName,
                d.GroupName AS GroupName,
                d.itemtype AS Type,  -- Using itemtype from details table instead of fixed value
                d.UOM AS UOM,
                SUM(d.Amount) AS total_amount  -- Added sum of Amount
            FROM intblstorereqdetails d
            JOIN intblstorerequisition r 
                ON d.StoreReqID = r.idintblStoreRequisition
            WHERE r.Outlet = %s 
                AND EXISTS (
                    SELECT 1 
                    FROM stock_statement s 
                    WHERE s.ItemName = d.ItemName 
                        AND s.OutletName = r.Outlet 
                        AND s.GroupName = 'Finished Goods'
                )
            GROUP BY d.ItemName, d.GroupName, d.itemtype, d.UOM
        """, (outlet,))


        all_stock_items = cursor.fetchall()

        # Step 6.1: Get unit definitions for all items
        # First, get all item names from stock items
        item_names = [item["ItemName"] for item in all_stock_items]
        unit_definitions = {}

        if item_names:
            # Create placeholders for SQL query
            placeholders = ','.join(['%s'] * len(item_names))
            
            # Fetch unit definitions for these items
            cursor.execute(f"""
                SELECT name, unit, uom, rate, outlet
                FROM tblunitdefinition
                WHERE name IN ({placeholders}) AND (outlet = %s OR outlet IS NULL OR outlet = '')
            """, item_names + [outlet])
            
            unit_def_results = cursor.fetchall()
            
            # Create a dictionary for easy lookup
            for unit_def in unit_def_results:
                unit_definitions[unit_def["name"]] = {
                    "unit": float(unit_def["unit"]) if unit_def["unit"] else 0,
                    "uom": unit_def["uom"],
                    "rate": float(unit_def["rate"]) if unit_def["rate"] else 0
                }

        # Get all item names for opening_rate
        item_names = [item["ItemName"] for item in all_stock_items]

        stock_rates = {}

        if item_names:
            placeholders = ','.join(['%s'] * len(item_names))

            cursor.execute(f"""
                SELECT ItemName, Rate
                FROM stock_statement
                WHERE OutletName = %s
                AND ItemName IN ({placeholders})
            """, [outlet] + item_names)

            stock_results = cursor.fetchall()

            # Map item -> rate
            for row in stock_results:
                stock_rates[row["ItemName"]] = float(row["Rate"] or 0)

        # Step 7: Combine all into summary
        item_data = {}

        for stock_item in all_stock_items:
            name = stock_item["ItemName"]
            
            # Get unit definition for this item
            unit_def = unit_definitions.get(name, {})
            
            item_data[name] = {
                "total_consumed": 0.0,
                "total_received": 0.0,
                "total_wasted": 0.0,
                "total_physical": 0.0,
                "opening": opening_balances.get(name, 0.0),
                "opening_rate": stock_rates.get(name, 0.0),
                "uom": stock_item["UOM"],
                "new_uom": stock_item["UOM"],
                "group_name": stock_item["GroupName"] or "Group Not Found",
                "type": stock_item["Type"] or "Type Not Found",
                "real_consumed": 0.0,
                "unitdefinition": {
                    "unit": str(unit_def.get("unit", "")),
                    "uom": unit_def.get("uom", "")
                }
            }
        print(f"all_stock_items {all_stock_items}")
        for name, info in all_consumed_items.items():
            if name not in item_data:
                item_data[name] = {
                    "total_consumed": 0.0,
                    "total_received": 0.0,
                    "total_wasted": 0.0,
                    "total_physical": 0.0,
                    "opening": opening_balances.get(name, 0.0),
                    "opening_rate": stock_rates.get(name, 0.0),

                    "uom": info["uom"],
                    "new_uom": info["new_uom"],
                    "group_name": stock_item["GroupName"] or "Group Not Found",
                    "type": stock_item["Type"] or "Type Not Found",
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
                "opening_rate": stock_rates.get(name, 0.0),
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
                "opening_rate": stock_rates.get(name, 0.0),

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
                "opening_rate": stock_rates.get(name, 0.0),

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

        # # Step 8: Final nested summary
        # nested_summary = {}
        # for name, info in item_data.items():
        #     consumed = Decimal(info["total_consumed"])
        #     received = Decimal(info["total_received"])
        #     wasted = Decimal(info["total_wasted"])
        #     physical = Decimal(info["total_physical"])
        #     opening = Decimal(info["opening"])
        #     closing = opening + received - consumed - wasted

        #     item_type = info["type"]
        #     group_name = info["group_name"]

        #     if item_type not in nested_summary:
        #         nested_summary[item_type] = {}

        #     if group_name not in nested_summary[item_type]:
        #         nested_summary[item_type][group_name] = []

        #     nested_summary[item_type][group_name].append({
        #         "name": name,
        #         "uom": info["uom"],
        #         "new_uom": info["new_uom"],
        #         "opening": float(opening),
        #         "opening_rate": info["opening_rate"],

        #         "total_consumed": float(consumed),
        #         "total_received": float(received),
        #         "total_wasted": float(wasted),
        #         "total_physical": float(physical),
        #         "closing_balance": float(closing) if float(closing) > 0 else 0,
        #         'unitdefinition': info['unitdefinition']
        #     })

        # Step 8: Determine if physical items are added before
        cursor.execute("""
            SELECT COUNT(*) as count FROM production_inventorycalculation
            WHERE outlet_name = %s and physical_added=True and end_date < %s
            ORDER BY end_date DESC LIMIT 1
        """, (outlet, start_date))
        physical_added_result = cursor.fetchone()
        has_physical_before_start = physical_added_result["count"] > 0 if physical_added_result else False

        cursor.execute("""
            SELECT start_date, end_date
            FROM production_inventorycalculation
            WHERE outlet_name = %s order by id asc
            LIMIT 1
        """, (outlet,))
        opening_date_result = cursor.fetchone()

        if opening_date_result:
            opening_start_date = opening_date_result["start_date"]
            opening_end_date = opening_date_result["end_date"]
        else:
            opening_start_date = None
            opening_end_date = None
        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "summary": item_data,
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