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

production_wastage = Blueprint('production_wastage', __name__)

# @production_wastage.route("/production-wastage", methods=["POST"])
# @cross_origin()
# def create_production_wastage():
#     mydb = None
#     cursor = None
    
#     try:
#         data = request.get_json()
        
#         # Validate token
#         token = data.get("token")
#         if not token or not token_auth(token):
#             return jsonify({"error": "Invalid or missing token"}), 400
        
#         # Get wastage data
#         item_name = data.get("item_name")
#         outlet_name = data.get("outlet_name")
#         quantity = data.get("quantity")
#         price = data.get("price")
#         uom = data.get("uom")
#         received_date = data.get("received_date")
#         costcenter = data.get("costcenter", "Bar")  # Default to Bar if not provided
        
#         # Validation
#         if not all([item_name, outlet_name, quantity, price, uom, received_date]):
#             return jsonify({"error": "Missing required fields"}), 400
        
#         # Convert quantity to float for calculation
#         quantity = float(quantity)
#         price = float(price)
        
#         mydb = get_db_connection()
#         cursor = mydb.cursor(dictionary=True)
        
#         # Start transaction
#         mydb.start_transaction()
        
#         # Step 1: Check current stock level from stock_statement
#         cursor.execute("""
#             SELECT ItemName, CurrentLevel, Rate, UOM, GroupName, BrandName, Type, OutletName
#             FROM stock_statement 
#             WHERE ItemName = %s AND OutletName = %s
#         """, (item_name, outlet_name))
        
#         stock_record = cursor.fetchone()
        
#         if not stock_record:
#             return jsonify({
#                 "error": f"Item '{item_name}' not found in stock statement for outlet '{outlet_name}'"
#             }), 404
        
#         current_stock = float(stock_record['CurrentLevel']) if stock_record['CurrentLevel'] else 0
        
#         # Step 2: Check if sufficient stock is available
#         if current_stock < quantity:
#             return jsonify({
#                 "error": f"Insufficient stock. Available: {current_stock} {uom}, Requested wastage: {quantity} {uom}"
#             }), 400
        
#         # Step 3: Calculate new stock level
#         new_stock_level = current_stock - quantity
#         new_total = new_stock_level * price
        
#         # Step 4: Insert wastage record
#         cursor.execute("""
#             INSERT INTO production_wastage_items 
#             (item_name, outlet_name, quantity, price, uom, received_date, costcenter)
#             VALUES (%s, %s, %s, %s, %s, %s, %s)
#         """, (item_name, outlet_name, quantity, price, uom, received_date, costcenter))
        
#         wastage_id = cursor.lastrowid
        
#         # Step 5: Update stock statement - deduct wastage quantity
#         cursor.execute("""
#             UPDATE stock_statement 
#             SET CurrentLevel = %s,
#                 Total = %s
#             WHERE ItemName = %s AND OutletName = %s
#         """, (new_stock_level, new_total, item_name, outlet_name))
        
#         # Step 6: Commit transaction
#         mydb.commit()
        
#         return jsonify({
#             "message": "Wastage recorded and stock deducted successfully",
#             "wastage_id": wastage_id,
#             "item_name": item_name,
#             "outlet_name": outlet_name,
#             "wastage_quantity": quantity,
#             "previous_stock": current_stock,
#             "current_stock": new_stock_level,
#             "uom": uom,
#             "costcenter": costcenter
#         }), 201
        
#     except Exception as e:
#         if mydb:
#             mydb.rollback()
#         return jsonify({"error": str(e)}), 400
        
#     finally:
#         if cursor:
#             cursor.close()
#         if mydb:
#             mydb.close()


@production_wastage.route("/production-wastage", methods=["POST"])
@cross_origin()
def create_production_wastage():
    mydb = None
    cursor = None
    
    try:
        data = request.get_json()
        
        # Validate token
        token = data.get("token")
        if not token or not token_auth(token):
            return jsonify({"error": "Invalid or missing token"}), 400
        
        # Get wastage items list
        wastage_items = data.get("wastage_items", [])
        
        # If single item is sent (backward compatibility), convert to list
        if not wastage_items and all(k in data for k in ["item_name", "outlet_name", "quantity", "price", "uom", "received_date"]):
            wastage_items = [{
                "item_name": data.get("item_name"),
                "outlet_name": data.get("outlet_name"),
                "quantity": data.get("quantity"),
                "price": data.get("price"),
                "uom": data.get("uom"),
                "received_date": data.get("received_date"),
                "costcenter": data.get("costcenter", "Central Kitchen")
            }]
        
        # Validation
        if not wastage_items or len(wastage_items) == 0:
            return jsonify({"error": "No wastage items provided"}), 400
        
        mydb = get_db_connection()
        cursor = mydb.cursor(dictionary=True)
        
        # Start transaction
        mydb.start_transaction()
        
        results = []
        errors = []
        
        # Process each wastage item
        for idx, item in enumerate(wastage_items):
            try:
                # Get item data
                item_name = item.get("item_name")
                outlet_name = item.get("outlet_name")
                quantity = item.get("quantity")
                price = item.get("price")
                uom = item.get("uom")
                received_date = item.get("received_date")
                costcenter = item.get("costcenter", "Bar")
                
                # Validate required fields
                if not all([item_name, outlet_name, quantity, price, uom, received_date]):
                    errors.append({
                        "index": idx,
                        "item": item,
                        "error": "Missing required fields (item_name, outlet_name, quantity, price, uom, received_date)"
                    })
                    continue
                
                # Convert quantity and price to float
                quantity = float(quantity)
                price = float(price)
                
                # Step 1: Check current stock level from stock_statement
                cursor.execute("""
                    SELECT ItemName, CurrentLevel, Rate, UOM, GroupName, BrandName, Type, OutletName
                    FROM stock_statement 
                    WHERE ItemName = %s AND OutletName = %s and GroupName = "Finished Goods"
                """, (item_name, outlet_name))
                
                stock_record = cursor.fetchone()
                
                # Clear any remaining results
                while cursor.nextset():
                    pass
                
                if not stock_record:
                    errors.append({
                        "index": idx,
                        "item_name": item_name,
                        "outlet_name": outlet_name,
                        "error": f"Item '{item_name}' not found in stock statement for outlet '{outlet_name}'"
                    })
                    continue
                
                current_stock = float(stock_record['CurrentLevel']) if stock_record['CurrentLevel'] else 0
                
                # Step 2: Check if sufficient stock is available
                if current_stock < quantity:
                    errors.append({
                        "index": idx,
                        "item_name": item_name,
                        "outlet_name": outlet_name,
                        "error": f"Insufficient stock. Available: {current_stock} {uom}, Requested wastage: {quantity} {uom}"
                    })
                    continue
                
                # Step 3: Calculate new stock level
                new_stock_level = current_stock - quantity
                new_total = new_stock_level * price
                
                # Step 4: Insert wastage record
                cursor.execute("""
                    INSERT INTO production_wastage_items 
                    (item_name, outlet_name, quantity, price, uom, received_date, costcenter)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (item_name, outlet_name, quantity, price, uom, received_date, costcenter))
                
                wastage_id = cursor.lastrowid
                
                # Clear any remaining results
                while cursor.nextset():
                    pass
                
                # Step 5: Update stock statement - deduct wastage quantity
                cursor.execute("""
                    UPDATE stock_statement 
                    SET CurrentLevel = %s,
                        Total = %s
                    WHERE ItemName = %s AND OutletName = %s and GroupName = "Finished Goods"
                """, (new_stock_level, new_total, item_name, outlet_name))
                
                # Clear any remaining results
                while cursor.nextset():
                    pass
                
                # Record success
                results.append({
                    "index": idx,
                    "wastage_id": wastage_id,
                    "item_name": item_name,
                    "outlet_name": outlet_name,
                    "wastage_quantity": quantity,
                    "previous_stock": current_stock,
                    "current_stock": new_stock_level,
                    "uom": uom,
                    "costcenter": costcenter,
                    "status": "success"
                })
                
            except Exception as item_error:
                errors.append({
                    "index": idx,
                    "item": item,
                    "error": str(item_error)
                })
        
        # Check if any items were processed successfully
        if len(results) == 0:
            # No successful items, rollback everything
            mydb.rollback()
            return jsonify({
                "error": "No wastage items were processed successfully",
                "errors": errors
            }), 400
        
        # Commit transaction if at least one item succeeded
        mydb.commit()
        
        return jsonify({
            "message": f"Processed {len(results)} wastage items successfully",
            "total_items": len(wastage_items),
            "successful": len(results),
            "failed": len(errors),
            "results": results,
            "errors": errors if errors else None
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


@production_wastage.route("/production-wastage", methods=["GET"])
@cross_origin()
def get_production_wastage():
    mydb = None
    cursor = None
    
    try:
        outlet_name = request.args.get("outlet_name")
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        costcenter = request.args.get("costcenter")
        item_name = request.args.get("item_name")
        
        mydb = get_db_connection()
        cursor = mydb.cursor(dictionary=True)
        
        query = """
            SELECT w.*, 
                   s.CurrentLevel as current_stock_level,
                   s.Rate as current_rate
            FROM production_wastage_items w
            LEFT JOIN stock_statement s ON w.item_name = s.ItemName AND w.outlet_name = s.OutletName
            WHERE 1=1
        """
        params = []
        
        if outlet_name:
            query += " AND w.outlet_name = %s"
            params.append(outlet_name)
        
        if start_date:
            query += " AND w.received_date >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND w.received_date <= %s"
            params.append(end_date)
        
        if costcenter:
            query += " AND w.costcenter = %s"
            params.append(costcenter)
        
        if item_name:
            query += " AND w.item_name = %s"
            params.append(item_name)
        
        query += " ORDER BY w.received_date DESC, w.created_at DESC"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        # Convert Decimal to float for JSON serialization
        for result in results:
            if result.get('quantity'):
                result['quantity'] = float(result['quantity'])
            if result.get('price'):
                result['price'] = float(result['price'])
            if result.get('current_stock_level'):
                result['current_stock_level'] = float(result['current_stock_level'])
            if result.get('current_rate'):
                result['current_rate'] = float(result['current_rate'])
        
        return jsonify(results), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400
        
    finally:
        if cursor:
            cursor.close()
        if mydb:
            mydb.close()


@production_wastage.route("/production-wastage/<int:wastage_id>", methods=["DELETE"])
@cross_origin()
def delete_production_wastage(wastage_id):
    mydb = None
    cursor = None
    
    try:
        data = request.get_json()
        
        # Validate token
        token = data.get("token")
        if not token or not token_auth(token):
            return jsonify({"error": "Invalid or missing token"}), 400
        
        mydb = get_db_connection()
        cursor = mydb.cursor(dictionary=True)
        
        # Get wastage record before deletion
        cursor.execute("""
            SELECT item_name, outlet_name, quantity, uom
            FROM production_wastage_items
            WHERE id = %s
        """, (wastage_id,))
        
        wastage_record = cursor.fetchone()
        
        if not wastage_record:
            return jsonify({"error": "Wastage record not found"}), 404
        
        # Start transaction
        mydb.start_transaction()
        
        # Restore stock level
        item_name = wastage_record['item_name']
        outlet_name = wastage_record['outlet_name']
        wastage_quantity = float(wastage_record['quantity'])
        
        cursor.execute("""
            SELECT CurrentLevel, Rate
            FROM stock_statement
            WHERE ItemName = %s AND OutletName = %s
        """, (item_name, outlet_name))
        
        stock_record = cursor.fetchone()
        
        if stock_record:
            current_stock = float(stock_record['CurrentLevel']) if stock_record['CurrentLevel'] else 0
            restored_stock = current_stock + wastage_quantity
            new_total = restored_stock * float(stock_record['Rate']) if stock_record['Rate'] else 0
            
            # Update stock
            cursor.execute("""
                UPDATE stock_statement
                SET CurrentLevel = %s, Total = %s
                WHERE ItemName = %s AND OutletName = %s
            """, (restored_stock, new_total, item_name, outlet_name))
        
        # Delete wastage record
        cursor.execute("DELETE FROM production_wastage_items WHERE id = %s", (wastage_id,))
        
        mydb.commit()
        
        return jsonify({
            "message": "Wastage record deleted and stock restored successfully",
            "restored_quantity": wastage_quantity
        }), 200
        
    except Exception as e:
        if mydb:
            mydb.rollback()
        return jsonify({"error": str(e)}), 400
        
    finally:
        if cursor:
            cursor.close()
        if mydb:
            mydb.close()