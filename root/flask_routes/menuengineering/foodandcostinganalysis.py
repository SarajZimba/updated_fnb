from flask import Blueprint, jsonify, request
import mysql.connector
import os
from dotenv import load_dotenv
from flask_cors import cross_origin
from root.auth.check import token_auth

load_dotenv()

app_file125 = Blueprint('app_file125', __name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("host"),
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )


@app_file125.route("/food-and-costing-analysis", methods=["POST"])
@cross_origin()
def receive_snapshot_details():
    try:
        data = request.get_json()
        token = data.get("token")
        snapshot_id = data.get("snapshot_id")

        if not token or not token_auth(token):
            return jsonify({"error": "Invalid or missing token."}), 400

        if not snapshot_id:
            return jsonify({"error": "Missing required parameter: snapshot_id"}), 400

        mydb = get_db_connection()
        cursor = mydb.cursor(dictionary=True)

        # Snapshot info
        cursor.execute("""
            SELECT outlet_name, start_date, end_date 
            FROM inventory_snapshot_master 
            WHERE id = %s
        """, (snapshot_id,))
        snapshot = cursor.fetchone()
        if not snapshot:
            return jsonify({"error": "Snapshot not found"}), 404

        outlet_name = snapshot['outlet_name']
        start_date = snapshot['start_date']
        end_date = snapshot['end_date']

        # Distinct item types
        cursor.execute("""
            SELECT DISTINCT item_type 
            FROM inventory_snapshot_items 
            WHERE snapshot_id = %s
        """, (snapshot_id,))
        item_types = [row['item_type'] for row in cursor.fetchall()]

        # STEP 1: Get all orders with their discount percentages and complimentary status
        cursor.execute("""
            SELECT 
                idtblorderHistory as order_id,
                Total,
                VAT,
                DiscountAmt,
                bill_no,
                PaymentMode,
                (DiscountAmt / (Total - VAT)) * 100 AS discount_percent
            FROM tblorderhistory
            WHERE Outlet_Name = %s 
                AND Date BETWEEN %s AND %s
                AND Total > 0
                AND (Total - VAT) > 0
        """, (outlet_name, start_date, end_date))
        
        orders = cursor.fetchall()
        
        # Create dictionaries to store item-type-wise calculations
        type_wise_discount = {}
        type_wise_complementary = {}
        type_wise_gross_sale = {}
        type_wise_gross_cost = {}
        
        # Initialize for each item type
        for itype in item_types:
            type_wise_discount[itype] = 0.0
            type_wise_complementary[itype] = 0.0
            type_wise_gross_sale[itype] = 0.0
            type_wise_gross_cost[itype] = 0.0
        
        # STEP 2: Process each order
        for order in orders:
            order_id = order['order_id']
            discount_percent = order['discount_percent'] if order['discount_percent'] else 0
            is_complimentary = order['bill_no'] == '' and order['PaymentMode'] in ['Complimentary', 'Non Chargeable']
            
            # Get order details (items)
            cursor.execute("""
                SELECT 
                    ItemName,
                    ItemType,
                    Total,
                    count,
                    discountExempt
                FROM tblorder_detailshistory
                WHERE order_ID = %s
            """, (order_id,))
            
            items = cursor.fetchall()
            
            for item in items:
                item_type = item['ItemType']
                if not item_type or item_type not in item_types:
                    continue
                
                item_total = float(item['Total'] or 0)
                item_count = float(item['count'] or 1)
                
                # Get recipe cost
                cursor.execute("""
                    SELECT costprice
                    FROM recipe
                    WHERE name = %s AND outlet = %s
                    LIMIT 1
                """, (item['ItemName'], outlet_name))
                
                recipe = cursor.fetchone()
                # item_cost = float(recipe['costprice'] or 0) * item_count if recipe else item_total * 0.6  # 60% fallback
                item_cost = float(recipe['costprice'] or 0) * item_count if recipe else 0  # 60% fallback
                
                # Add to gross sale and cost
                type_wise_gross_sale[item_type] += item_total
                type_wise_gross_cost[item_type] += item_cost
                
                # Handle complimentary
                if is_complimentary:
                    type_wise_complementary[item_type] += item_total
                
                # Handle discount (if not discount exempt)
                if discount_percent > 0 and item.get('discountExempt') != 'Yes':
                    discount_amount = float(item_total) * (float(discount_percent) / 100)
                    type_wise_discount[item_type] += discount_amount
        
        type_wise_data = []

        for itype in item_types:
            # Actual costing from inventory
            cursor.execute("""
                SELECT 
                    item_name, item_type, group_name, uom, new_uom,
                    opening_count, total_received, total_consumed,
                    closing_balance, wastage_count, physical_count, discrepancy_count,
                    rate, received_cost, consumption_cost, wastage_cost, actual_consumption_cost,
                    opening_cost, physical_cost,
                    (closing_balance * rate) AS closing_value
                FROM inventory_snapshot_items
                WHERE snapshot_id = %s AND item_type = %s
                ORDER BY item_name ASC
            """, (snapshot_id, itype))
            items = cursor.fetchall()

            # Summary of cost fields
            cursor.execute("""
                SELECT 
                    SUM(opening_cost) AS total_opening_cost,
                    SUM(physical_cost) AS total_physical_cost,
                    SUM(wastage_cost) AS total_wastage_cost,
                    SUM(actual_consumption_cost) AS total_actual_consumption_cost
                FROM inventory_snapshot_items
                WHERE snapshot_id = %s AND item_type = %s
            """, (snapshot_id, itype))
            summary = cursor.fetchone()

            # Get gross sale, discount, and complementary for this item type
            gross_sale = type_wise_gross_sale.get(itype, 0)
            gross_cost = type_wise_gross_cost.get(itype, 0)
            total_discount = type_wise_discount.get(itype, 0)
            total_complementary = type_wise_complementary.get(itype, 0)
            
            # Calculate percentages
            gross_cost_percent = round((gross_cost / gross_sale) * 100, 2) if gross_sale else 0
            net_sale = gross_sale - total_discount - total_complementary
            net_cost_percent = round((gross_cost / net_sale) * 100, 2) if net_sale else 0

            # Get detailed sales items for this type
            cursor.execute("""
                SELECT 
                    d.ItemName, 
                    SUM(d.count) AS qty, 
                    SUM(d.Total) AS total_sale,
                    r.costprice AS unit_cost,
                    SUM(d.count * COALESCE(r.costprice, 0)) AS total_cost
                FROM tblorder_detailshistory d
                JOIN tblorderhistory o ON d.order_ID = o.idtblorderHistory
                LEFT JOIN recipe r ON r.name = d.ItemName AND r.outlet = o.Outlet_Name
                WHERE o.Outlet_Name = %s 
                    AND o.Date BETWEEN %s AND %s 
                    AND d.ItemType = %s
                GROUP BY d.ItemName, r.costprice
            """, (outlet_name, str(start_date), str(end_date), itype))
            sales_items = cursor.fetchall()

            # PURCHASES
            cursor.execute("""
                SELECT DISTINCT item_name
                FROM inventory_snapshot_items
                WHERE snapshot_id = %s AND item_type = %s
            """, (snapshot_id, itype))
            item_names = [row['item_name'] for row in cursor.fetchall()]

            purchase_items = []
            total_purchase = 0.0

            if item_names:
                format_strings = ','.join(['%s'] * len(item_names))
                params = [outlet_name, start_date, end_date] + item_names

                cursor.execute(f"""
                    SELECT 
                        c.Name AS item_name,
                        c.UnitsOrdered AS quantity,
                        c.UOM AS uom,
                        c.Rate AS rate,
                        ROUND(c.UnitsOrdered * c.Rate, 2) AS total
                    FROM intbl_purchaserequisition_contract c
                    JOIN intbl_purchaserequisition r
                        ON c.PurchaseReqID = r.IDIntbl_PurchaseRequisition
                    WHERE r.Outlet_Name = %s
                        AND r.ReceivedDate BETWEEN %s AND %s
                        AND c.Name IN ({format_strings})
                    ORDER BY c.Name ASC
                """, params)

                purchase_items = cursor.fetchall()
                total_purchase = sum(item['total'] or 0 for item in purchase_items)

            # Final JSON for this item_type
            type_wise_data.append({
                "item_type": itype,
                "summary": summary,
                "items_actual_food_costing": items,
                "sales_summary": {
                    "gross_sale": round(gross_sale, 2),
                    "gross_cost": round(gross_cost, 2),
                    "gross_cost_percent": gross_cost_percent,
                    "discount": round(total_discount, 2),
                    "complementary": round(total_complementary, 2),
                    "net_sale": round(net_sale, 2),
                    "net_cost_percent": net_cost_percent,
                    "items_sold": sales_items
                },
                "purchase_summary": {
                    "total_purchase": round(total_purchase, 2),
                    "items": purchase_items
                }
            })

        cursor.close()
        mydb.close()

        return jsonify({
            "status": "success",
            "snapshot_id": snapshot_id,
            "outlet_name": outlet_name,
            "start_date": str(start_date),
            "end_date": str(end_date),
            "data": type_wise_data
        }), 200

    except Exception as e:
        if 'mydb' in locals():
            mydb.rollback()
            mydb.close()
        return jsonify({"error": str(e)}), 400


from root.flask_routes.menuengineering.received.utils_fnb import calculate_other_cost
@app_file125.route("/fnb-costing-reports", methods=["POST"])
@cross_origin()
def get_fnb_costing_reports():
    try:
        data = request.get_json()
        token = data.get("token")
        outlet = data.get("outlet")
        start_date = data.get("start_date")
        end_date = data.get("end_date")

        if not token or not token_auth(token):
            return jsonify({"error": "Invalid or missing token."}), 400

        if not outlet:
            return jsonify({"error": "Missing required parameter: outlet"}), 400
        if not start_date or not end_date:
            return jsonify({"error": "Missing required parameters: start_date or end_date"}), 400

        mydb = get_db_connection()
        cursor = mydb.cursor(dictionary=True)

        # Query for fnb costing details
        query = """
            SELECT *
            FROM tblfnbcostingdetails
            WHERE outlet_name = %s
              AND from_date = %s
              AND to_date = %s
            ORDER BY from_date DESC, to_date DESC
        """
        cursor.execute(query, (outlet, start_date, end_date))
        fnb_results = cursor.fetchall()

        # Process sales data once for Food and once for Beverage
        sales_data = {}
        
        for report_type in ["Food", "Beverage"]:
            # Get all orders with their discount percentages and complimentary status
            cursor.execute("""
                SELECT 
                    idtblorderHistory as order_id,
                    Total,
                    VAT,
                    DiscountAmt,
                    bill_no,
                    PaymentMode,
                    CASE 
                        WHEN (Total - VAT) > 0 THEN (DiscountAmt / (Total - VAT)) * 100 
                        ELSE 0 
                    END AS discount_percent
                FROM tblorderhistory
                WHERE Outlet_Name = %s 
                    AND Date BETWEEN %s AND %s
                    AND Total > 0
            """, (outlet, start_date, end_date))
            
            orders = cursor.fetchall()
            
            # Initialize sales tracking variables
            gross_sale = 0.0
            gross_cost = 0.0
            total_discount = 0.0
            total_complementary = 0.0
            items_sold_dict = {}
            
            # Process each order
            for order in orders:
                order_id = order['order_id']
                discount_percent = order['discount_percent'] if order['discount_percent'] else 0
                is_complimentary = order['bill_no'] == '' and order['PaymentMode'] in ['Complimentary', 'Non Chargeable']
                
                # Get order details (items)
                cursor.execute("""
                    SELECT 
                        ItemName,
                        ItemType,
                        Total,
                        count,
                        discountExempt
                    FROM tblorder_detailshistory
                    WHERE order_ID = %s
                """, (order_id,))
                
                items = cursor.fetchall()
                
                for item in items:
                    item_type = item['ItemType']
                    
                    # Only process items matching the report_type
                    if item_type != report_type:
                        continue
                    
                    item_name = item['ItemName']
                    item_total = float(item['Total'] or 0)
                    item_count = float(item['count'] or 1)
                    
                    # Get recipe cost
                    cursor.execute("""
                        SELECT costprice
                        FROM recipe
                        WHERE name = %s AND outlet = %s
                        LIMIT 1
                    """, (item_name, outlet))
                    
                    recipe = cursor.fetchone()
                    item_cost = float(recipe['costprice'] or 0) * item_count if recipe else 0
                    
                    # Add to gross totals
                    gross_sale += item_total
                    gross_cost += item_cost
                    
                    # Handle complimentary
                    if is_complimentary:
                        total_complementary += item_total
                    
                    # Handle discount (if not discount exempt)
                    if discount_percent > 0 and item.get('discountExempt') != 'Yes':
                        discount_amount = item_total * (discount_percent / 100)
                        total_discount += discount_amount
                    
                    # Aggregate items sold
                    if item_name not in items_sold_dict:
                        items_sold_dict[item_name] = {
                            "item_name": item_name,
                            "quantity": 0,
                            "total_sale": 0,
                            "total_cost": 0,
                            "unit_cost": float(recipe['costprice'] or 0) if recipe else 0
                        }
                    
                    items_sold_dict[item_name]["quantity"] += item_count
                    items_sold_dict[item_name]["total_sale"] += item_total
                    items_sold_dict[item_name]["total_cost"] += item_cost
            
            # Calculate percentages
            gross_cost_percent = round((gross_cost / gross_sale) * 100, 2) if gross_sale else 0
            net_sale = gross_sale - total_discount - total_complementary
            net_cost_percent = round((gross_cost / net_sale) * 100, 2) if net_sale else 0
            
            # Put items_sold inside sales_summary
            sales_data[report_type] = {
                "sales_summary": {
                    "gross_sale": round(gross_sale, 2),
                    "gross_cost": round(gross_cost, 2),
                    "gross_cost_percent": gross_cost_percent,
                    "discount": round(total_discount, 2),
                    "complementary": round(total_complementary, 2),
                    "net_sale": round(net_sale, 2),
                    "net_cost_percent": net_cost_percent,
                    "items_sold": list(items_sold_dict.values())
                }
            }

        # Process store requisition items (deployed items) for Food and Beverage
        store_requisition_data = {}
        
        for report_type in ["Food", "Beverage"]:
            # Query to get items deployed from store requisition
            cursor.execute("""
                SELECT 
                    d.ItemName,
                    d.GroupName,
                    d.BrandName,
                    d.UOM,
                    d.Rate,
                    d.Amount,
                    d.itemtype,
                    (d.Amount * d.Rate) AS total_amount
                FROM intblstorereqdetails d
                INNER JOIN intblstorerequisition r ON d.StoreReqID = r.idintblStoreRequisition
                WHERE r.Outlet = %s
                    AND DATE(r.Date) BETWEEN %s AND %s
                    AND d.itemtype = %s
                ORDER BY d.ItemName
            """, (outlet, start_date, end_date, report_type))
            
            requisition_items = cursor.fetchall()
            
            # Group by item name and calculate average rate
            items_dict = {}
            
            for item in requisition_items:
                item_name = item['ItemName']
                
                if item_name not in items_dict:
                    items_dict[item_name] = {
                        "item_name": item_name,
                        "group_name": item['GroupName'],
                        "brand_name": item['BrandName'],
                        "uom": item['UOM'],
                        "item_type": item['itemtype'],
                        "total_quantity": 0,
                        "total_amount": 0,
                        "entries": []  # Store individual entries for average calculation
                    }
                
                # Add to totals
                items_dict[item_name]["total_quantity"] += float(item['Amount'] or 0)
                items_dict[item_name]["total_amount"] += float(item['total_amount'] or 0)
                items_dict[item_name]["entries"].append({
                    "quantity": float(item['Amount'] or 0),
                    "rate": float(item['Rate'] or 0),
                    "total": float(item['total_amount'] or 0)
                })
            
            # Calculate average rate and prepare final list
            deployed_items_list = []
            for item_name, item_data in items_dict.items():
                avg_rate = item_data["total_amount"] / item_data["total_quantity"] if item_data["total_quantity"] > 0 else 0
                
                deployed_items_list.append({
                    "item_name": item_data["item_name"],
                    "group_name": item_data["group_name"],
                    "brand_name": item_data["brand_name"],
                    "uom": item_data["uom"],
                    "item_type": item_data["item_type"],
                    "total_quantity": round(item_data["total_quantity"], 3),
                    "average_rate": round(avg_rate, 2),
                    "total_amount": round(item_data["total_amount"], 2),
                    "transaction_count": len(item_data["entries"])
                })
            
            store_requisition_data[report_type] = {
                "deployed_items": deployed_items_list,
                "summary": {
                    "total_items_deployed": len(deployed_items_list),
                    "total_quantity": round(sum(item["total_quantity"] for item in deployed_items_list), 3),
                    "total_value": round(sum(item["total_amount"] for item in deployed_items_list), 2)
                }
            }

        # For each fnb record, fetch the corresponding inventory snapshot data
        for fnb_record in fnb_results:
            report_for = fnb_record.get("report_for")
            fnb_from_date = fnb_record.get("from_date")
            fnb_to_date = fnb_record.get("to_date")
            
            # Initialize inventory snapshot fields
            fnb_record["inventory_snapshot"] = None
            fnb_record["items_actual_costing"] = []
            fnb_record["sales_summary"] = {}
            fnb_record["purchase_items"] = {}  # New field for deployed items
            
            if report_for == "Food":
                master_table = "inventory_snapshot_master_food"
                items_table = "inventory_snapshot_items_food"
            elif report_for == "Beverage":
                master_table = "inventory_snapshot_master_beverage"
                items_table = "inventory_snapshot_items_beverage"
            else:
                continue
            
            # Add sales data from pre-processed data
            if report_for in sales_data:
                fnb_record["sales_summary"] = sales_data[report_for]["sales_summary"]
            
            # Add deployed items data from store requisition
            if report_for in store_requisition_data:
                fnb_record["purchase_items"] = store_requisition_data[report_for]
            
            # Query the master snapshot table
            master_query = f"""
                SELECT *
                FROM {master_table}
                WHERE outlet_name = %s
                  AND start_date = %s
                  AND end_date = %s AND is_opening = False
                ORDER BY created_at DESC
                LIMIT 1
            """
            cursor.execute(master_query, (outlet, fnb_from_date, fnb_to_date))
            master_result = cursor.fetchone()
            
            if master_result:
                fnb_record["inventory_snapshot"] = master_result
                snapshot_id = master_result.get("id")
                
                # Query the items table for this snapshot
                items_query = f"""
                    SELECT *
                    FROM {items_table}
                    WHERE snapshot_id = %s
                    ORDER BY item_name
                """
                cursor.execute(items_query, (snapshot_id,))
                items_results = cursor.fetchall()
                fnb_record["items_actual_costing"] = items_results

        other_cost_food = calculate_other_cost(outlet, start_date, end_date, "Food")
        other_cost_beverage = calculate_other_cost(outlet, start_date, end_date, "Beverage")

        cursor.close()
        mydb.close()

        return jsonify({
            "status": "success",
            "outlet": outlet,
            "start_date": start_date,
            "end_date": end_date,
            "fnb_costing_reports": fnb_results,
            "other_cost_food" : other_cost_food,
            "other_cost_beverage" : other_cost_beverage
        }), 200

    except Exception as e:
        if 'mydb' in locals():
            mydb.rollback()
            mydb.close()
        return jsonify({"error": str(e)}), 400