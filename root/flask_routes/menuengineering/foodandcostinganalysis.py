# from flask import Blueprint, jsonify, request
# import mysql.connector
# import os
# from dotenv import load_dotenv
# from flask_cors import cross_origin
# from root.auth.check import token_auth

# load_dotenv()

# app_file125 = Blueprint('app_file125', __name__)

# def get_db_connection():
#     return mysql.connector.connect(
#         host=os.getenv("host"),
#         user=os.getenv("user"),
#         password=os.getenv("password"),
#         database=os.getenv("database")
#     )

# @app_file125.route("/food-and-costing-analysis", methods=["POST"])
# @cross_origin()
# def receive_snapshot_details():
#     try:
#         data = request.get_json()
#         token = data.get("token")
#         snapshot_id = data.get("snapshot_id")

#         if not token or not token_auth(token):
#             return jsonify({"error": "Invalid or missing token."}), 400

#         if not snapshot_id:
#             return jsonify({"error": "Missing required parameter: snapshot_id"}), 400

#         mydb = get_db_connection()
#         cursor = mydb.cursor(dictionary=True)

#         # Snapshot info
#         cursor.execute("""
#             SELECT outlet_name, start_date, end_date 
#             FROM inventory_snapshot_master 
#             WHERE id = %s
#         """, (snapshot_id,))
#         snapshot = cursor.fetchone()
#         if not snapshot:
#             return jsonify({"error": "Snapshot not found"}), 404

#         outlet_name = snapshot['outlet_name']
#         start_date = snapshot['start_date']
#         end_date = snapshot['end_date']

#         # Distinct item types
#         cursor.execute("""
#             SELECT DISTINCT item_type 
#             FROM inventory_snapshot_items 
#             WHERE snapshot_id = %s
#         """, (snapshot_id,))
#         item_types = [row['item_type'] for row in cursor.fetchall()]

#         type_wise_data = []

#         for itype in item_types:
#             # Actual costing
#             cursor.execute("""
#                 SELECT 
#                     item_name, item_type, group_name, uom, new_uom,
#                     opening_count, total_received, total_consumed,
#                     closing_balance, wastage_count, physical_count, discrepancy_count,
#                     rate, received_cost, consumption_cost, wastage_cost, actual_consumption_cost,
#                     opening_cost, physical_cost,
#                     (closing_balance * rate) AS closing_value
#                 FROM inventory_snapshot_items
#                 WHERE snapshot_id = %s AND item_type = %s
#                 ORDER BY item_name ASC
#             """, (snapshot_id, itype))
#             items = cursor.fetchall()

#             # Summary of cost fields
#             cursor.execute("""
#                 SELECT 
#                     SUM(opening_cost) AS total_opening_cost,
#                     SUM(physical_cost) AS total_physical_cost,
#                     SUM(wastage_cost) AS total_wastage_cost,
#                     SUM(actual_consumption_cost) AS total_actual_consumption_cost
#                 FROM inventory_snapshot_items
#                 WHERE snapshot_id = %s AND item_type = %s
#             """, (snapshot_id, itype))
#             summary = cursor.fetchone()

#             # SALES
#             cursor.execute("""
#                 SELECT 
#                     d.ItemName, SUM(d.count) AS qty, SUM(d.itemRate * d.count) AS total_sale,
#                     r.costprice AS unit_cost,
#                     SUM(d.count * r.costprice) AS total_cost
#                 FROM tblorder_detailshistory d
#                 JOIN tblorderhistory o ON d.order_ID = o.idtblorderHistory
#                 LEFT JOIN recipe r ON r.name = d.ItemName AND r.outlet = o.Outlet_Name
#                 WHERE o.Outlet_Name = %s AND o.Date BETWEEN %s AND %s AND d.ItemType = %s
#                 GROUP BY d.ItemName, r.costprice
#             """, (outlet_name, str(start_date), str(end_date), itype))
#             sales_items = cursor.fetchall()
#             print(outlet_name)
#             print(itype)
#             print("sales items", sales_items)
#             gross_sale = sum(row["total_sale"] or 0 for row in sales_items)
#             gross_cost = sum(row["total_cost"] or 0 for row in sales_items)
#             gross_cost_percent = round((gross_cost / gross_sale) * 100, 2) if gross_sale else 0

#             # Discounts and Complementary
#             cursor.execute("""
#                 SELECT 
#                     SUM(CASE WHEN Discounts != '' AND Discounts IS NOT NULL THEN DiscountAmt ELSE 0 END) AS total_discount,
#                     SUM(CASE WHEN bill_no = '' THEN Total ELSE 0 END) AS total_complementary
#                 FROM tblorderhistory
#                 WHERE Outlet_Name = %s AND Date BETWEEN %s AND %s
#             """, (outlet_name, start_date, end_date))
#             discount_data = cursor.fetchone()
#             total_discount = discount_data['total_discount'] or 0
#             total_complementary = discount_data['total_complementary'] or 0

#             net_sale = gross_sale - total_discount - total_complementary
#             net_cost_percent = round((gross_cost / net_sale) * 100, 2) if net_sale else 0

#             # PURCHASES
#             # Get item names for this item_type from snapshot
#             cursor.execute("""
#                 SELECT DISTINCT item_name
#                 FROM inventory_snapshot_items
#                 WHERE snapshot_id = %s AND item_type = %s
#             """, (snapshot_id, itype))
#             item_names = [row['item_name'] for row in cursor.fetchall()]

#             purchase_items = []
#             total_purchase = 0.0

#             # if item_names:
#             #     format_strings = ','.join(['%s'] * len(item_names))
#             #     params = [outlet_name, start_date, end_date] + item_names

#                 # # Get purchase details for display
#                 # cursor.execute(f"""
#                 #     SELECT 
#                 #         item_name, quantity, uom, price AS rate,
#                 #         ROUND(quantity * price, 2) AS total
#                 #     FROM received_items
#                 #     WHERE outlet_name = %s
#                 #     AND received_date BETWEEN %s AND %s
#                 #     AND item_name IN ({format_strings})
#                 #     ORDER BY item_name ASC
#                 # """, params)
#             if item_names:
#                 format_strings = ','.join(['%s'] * len(item_names))
#                 params = [outlet_name, start_date, end_date] + item_names

#                 # Get purchase details from purchase requisition tables
#                 cursor.execute(f"""
#                     SELECT 
#                         c.Name AS item_name,
#                         c.UnitsOrdered AS quantity,
#                         c.UOM AS uom,
#                         c.Rate AS rate,
#                         ROUND(c.UnitsOrdered * c.Rate, 2) AS total
#                     FROM intbl_purchaserequisition_contract c
#                     JOIN intbl_purchaserequisition r
#                         ON c.PurchaseReqID = r.IDIntbl_PurchaseRequisition
#                     WHERE r.Outlet_Name = %s
#                     AND r.ReceivedDate BETWEEN %s AND %s
#                     AND c.Name IN ({format_strings})
#                     ORDER BY c.Name ASC
#                 """, params)

#                 purchase_items = cursor.fetchall()
#                 total_purchase = sum(item['total'] or 0 for item in purchase_items)

#             # Final JSON for this item_type
#             type_wise_data.append({
#                 "item_type": itype,
#                 "summary": summary,
#                 "items_actual_food_costing": items,
#                 "sales_summary": {
#                     "gross_sale": gross_sale,
#                     "gross_cost": gross_cost,
#                     "gross_cost_percent": gross_cost_percent,
#                     "discount": total_discount,
#                     "complementary": total_complementary,
#                     "net_sale": net_sale,
#                     "net_cost_percent": net_cost_percent,
#                     "items_sold": sales_items
#                 },
#                 "purchase_summary": {
#                     "total_purchase": total_purchase,
#                     "items": purchase_items
#                 }
#             })

#         cursor.close()
#         mydb.close()

#         return jsonify({
#             "status": "success",
#             "snapshot_id": snapshot_id,
#             "outlet_name": outlet_name,
#             "start_date": str(start_date),
#             "end_date": str(end_date),
#             "data": type_wise_data
#         }), 200

#     except Exception as e:
#         if 'mydb' in locals():
#             mydb.rollback()
#             mydb.close()
#         return jsonify({"error": str(e)}), 400


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