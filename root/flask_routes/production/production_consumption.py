from flask import Blueprint, jsonify, request
import mysql.connector
import os
from dotenv import load_dotenv
from flask_cors import cross_origin
from root.auth.check import token_auth
from decimal import Decimal, ROUND_HALF_UP
import re

load_dotenv()

app_file237 = Blueprint('app_file237', __name__)

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


@app_file237.route("/production-consumption", methods=["POST"])
@cross_origin()
def production_consumption():
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

        # 1. Get all sold items with their conversion factors and recipes in a single query
        cursor.execute("""
            SELECT 
                d.ItemName AS finished_item_name,
                SUM(d.Amount) AS quantity_sold,
                s.id AS stock_item_id,
                s.Type AS item_type,
                cf.factor,
                cf.production_recipe_id,
                r.name AS recipe_name
            FROM intblstorereqdetails d
            JOIN intblstorerequisition rq ON rq.idintblStoreRequisition = d.StoreReqID
            JOIN stock_statement s ON s.ItemName = d.ItemName 
                AND s.OutletName = rq.Outlet
                AND s.GroupName = 'Finished Goods'
            JOIN conversionfactor cf ON cf.production_item_id = s.id AND cf.outlet = rq.Outlet
            JOIN recipe r ON r.id = cf.production_recipe_id AND r.recipe_type = 'Production'
            WHERE rq.Date BETWEEN %s AND %s 
                AND rq.Outlet = %s 
                AND rq.CostCenter != 'Wastage'
            GROUP BY d.ItemName, s.id, s.Type, cf.factor, cf.production_recipe_id, r.name
        """, (start_date, end_date, outlet))
        
        sold_items = cursor.fetchall()
        
        if not sold_items:
            return jsonify({
                "message": "No production items found for the selected period",
                "processed_items": [],
                "all_consumed_items": {},
                "consumption_summary": {}
            }), 200
        
        # 2. Get all recipe items and sub-recipes in batch
        recipe_ids = [item["production_recipe_id"] for item in sold_items]
        placeholders = ','.join(['%s'] * len(recipe_ids))
        
        # Fetch all recipe items at once
        cursor.execute(f"""
            SELECT 
                ri.recipe_id,
                ri.name,
                ri.quantity,
                ri.uom,
                ri.new_uom,
                'recipe_item' AS source_type
            FROM recipe_items ri
            WHERE ri.recipe_id IN ({placeholders})
        """, recipe_ids)
        recipe_items = cursor.fetchall()
        
        # Fetch all sub-recipes links
        cursor.execute(f"""
            SELECT 
                rs.recipe_id,
                rs.sub_recipe_id,
                rs.quantity AS sr_qty,
                s.name AS sub_name,
                'sub_recipe_link' AS source_type
            FROM recipe_subrecipes rs
            JOIN sub_recipe s ON rs.sub_recipe_id = s.id
            WHERE rs.recipe_id IN ({placeholders})
        """, recipe_ids)
        sub_recipe_links = cursor.fetchall()
        
        # Fetch sub-recipe items if needed
        sub_recipe_items = {}
        if include_sub_recipe_items and sub_recipe_links:
            sub_recipe_ids = list(set([link["sub_recipe_id"] for link in sub_recipe_links]))
            sub_placeholders = ','.join(['%s'] * len(sub_recipe_ids))
            cursor.execute(f"""
                SELECT 
                    sri.sub_recipe_id,
                    sri.name,
                    sri.quantity,
                    sri.uom,
                    sri.new_uom
                FROM sub_recipe_items sri
                WHERE sri.sub_recipe_id IN ({sub_placeholders})
            """, sub_recipe_ids)
            
            for item in cursor.fetchall():
                sub_recipe_id = item["sub_recipe_id"]
                if sub_recipe_id not in sub_recipe_items:
                    sub_recipe_items[sub_recipe_id] = []
                sub_recipe_items[sub_recipe_id].append(item)
        
        # 3. Get stock statement info for all consumed items
        cursor.execute("SELECT ItemName, GroupName, Type FROM stock_statement")
        stock_info_lookup = {
            row["ItemName"]: {
                "GroupName": row["GroupName"] or "Group Not Found",
                "Type": row["Type"] or "Type Not Found"
            }
            for row in cursor.fetchall()
        }
        
        # 4. Build lookup dictionaries for quick access
        recipe_items_lookup = {}
        for item in recipe_items:
            recipe_id = item["recipe_id"]
            if recipe_id not in recipe_items_lookup:
                recipe_items_lookup[recipe_id] = []
            recipe_items_lookup[recipe_id].append(item)
        
        sub_recipe_links_lookup = {}
        for link in sub_recipe_links:
            recipe_id = link["recipe_id"]
            if recipe_id not in sub_recipe_links_lookup:
                sub_recipe_links_lookup[recipe_id] = []
            sub_recipe_links_lookup[recipe_id].append(link)
        
        # 5. Process all sold items
        processed_items = []
        all_consumed_items = {}
        inappropriate_uom_items = []
        
        for sold_item in sold_items:
            item_name = sold_item["finished_item_name"]
            quantity_sold = float(sold_item["quantity_sold"])
            factor = float(sold_item["factor"])
            production_recipe_id = sold_item["production_recipe_id"]
            recipe_name = sold_item["recipe_name"]
            item_type = sold_item.get("item_type", "Unknown")
            
            # Calculate actual production quantity
            actual_production_quantity = quantity_sold / factor if factor != 0 else 0
            
            # Track processed item
            processed_items.append({
                "item_name": item_name,
                "quantity_sold": quantity_sold,
                "factor": factor,
                "actual_production_quantity": actual_production_quantity,
                "recipe_id": production_recipe_id,
                "recipe_name": recipe_name,
                "item_type": item_type
            })
            
            # Process recipe items
            if production_recipe_id in recipe_items_lookup:
                for ri in recipe_items_lookup[production_recipe_id]:
                    name = ri["name"]
                    recipe_quantity = float(ri["quantity"])
                    consumed = recipe_quantity * actual_production_quantity
                    uom = ri["uom"]
                    new_uom = ri["new_uom"]
                    
                    # UOM validation
                    is_standard = is_standard_uom(uom)
                    if not is_standard:
                        inappropriate_uom_items.append({
                            "item_name": name,
                            "uom": uom,
                            "source": "recipe_items",
                            "recipe": item_name
                        })
                    
                    # Aggregate consumption
                    if name not in all_consumed_items:
                        all_consumed_items[name] = {
                            "total_quantity": 0,
                            "uom": uom,
                            "new_uom": new_uom,
                            "is_standard_uom": is_standard
                        }
                    all_consumed_items[name]["total_quantity"] += consumed
                    if not is_standard:
                        all_consumed_items[name]["is_standard_uom"] = False
            
            # Process sub-recipes
            if include_sub_recipe_items and production_recipe_id in sub_recipe_links_lookup:
                for sr in sub_recipe_links_lookup[production_recipe_id]:
                    sub_recipe_qty = float(sr["sr_qty"])
                    sub_recipe_id = sr["sub_recipe_id"]
                    sub_name = sr["sub_name"]
                    
                    if sub_recipe_id in sub_recipe_items:
                        for sri in sub_recipe_items[sub_recipe_id]:
                            name = sri["name"]
                            item_quantity = float(sri["quantity"])
                            consumed = item_quantity * sub_recipe_qty * actual_production_quantity
                            uom = sri["uom"]
                            new_uom = sri["new_uom"]
                            
                            # UOM validation
                            is_standard = is_standard_uom(uom)
                            if not is_standard:
                                inappropriate_uom_items.append({
                                    "item_name": name,
                                    "uom": uom,
                                    "source": "sub_recipe_items",
                                    "sub_recipe": sub_name,
                                    "recipe": item_name
                                })
                            
                            # Aggregate consumption
                            if name not in all_consumed_items:
                                all_consumed_items[name] = {
                                    "total_quantity": 0,
                                    "uom": uom,
                                    "new_uom": new_uom,
                                    "is_standard_uom": is_standard
                                }
                            all_consumed_items[name]["total_quantity"] += consumed
                            if not is_standard:
                                all_consumed_items[name]["is_standard_uom"] = False
        
        # 6. Round quantities
        for name, info in all_consumed_items.items():
            info["total_quantity"] = float(Decimal(str(info["total_quantity"])).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
            info["rounded_quantity"] = info["total_quantity"]  # For backward compatibility
        
        # 7. Build grouped response
        nested_consumed_group = {}
        for name, info in all_consumed_items.items():
            total_quantity = info["total_quantity"]
            uom = info.get("uom")
            new_uom = info.get("new_uom")
            is_standard_uom_flag = info.get("is_standard_uom", False)
            
            stock_info = stock_info_lookup.get(name, {"GroupName": "Uncategorized", "Type": "Unknown"})
            group_name = stock_info["GroupName"]
            item_type = stock_info["Type"]
            
            if group_name not in nested_consumed_group:
                nested_consumed_group[group_name] = []
            
            nested_consumed_group[group_name].append({
                "name": name,
                "item_type": item_type,
                "uom": uom,
                "new_uom": new_uom,
                "total_quantity": total_quantity,
                "is_standard_uom": is_standard_uom_flag
            })
        
        # 8. Calculate statistics
        grand_total_items_sold = sum([item["quantity_sold"] for item in processed_items])
        grand_unique_items_sold = len(set([item["item_name"] for item in processed_items]))
        grand_total_menu_items = len(set([item["recipe_id"] for item in processed_items]))
        
        # 9. Prepare response
        response = {
            "success": True,
            "period": {
                "start_date": start_date,
                "end_date": end_date,
                "outlet": outlet
            },
            "summary": {
                "total_quantity_sold": round(grand_total_items_sold, 2),
                "unique_items_sold": grand_unique_items_sold,
                "total_production_recipes": grand_total_menu_items,
                "total_raw_materials_consumed": len(all_consumed_items)
            },
            "processed_items": processed_items,
            # "all_consumed_items": nested_consumed_group,
            "consumption_details": all_consumed_items,
            "uom_validation": {
                "has_inappropriate_uoms": len(inappropriate_uom_items) > 0,
                "total_inappropriate_items": len(inappropriate_uom_items),
                "inappropriate_items": inappropriate_uom_items[:50]  # Limit to 50 items
            }
        }
        
        cursor.close()
        conn.close()
        
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 400