from flask import Blueprint, jsonify, request
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app_file231 = Blueprint('app_file231', __name__)

# @app_file231.route("/postcentralkitchenproduction", methods=["POST"])
# @cross_origin()
# def post_central_kitchen_production():
#     mydb = None
#     cursor = None

#     try:
#         mydb = mysql.connector.connect(
#             host=os.getenv('host'),
#             user=os.getenv('user'),
#             password=os.getenv('password')
#         )

#         cursor = mydb.cursor(buffered=True, dictionary=True)

#         # Select DB
#         cursor.execute(f"USE {os.getenv('database')}")

#         data = request.get_json()

#         # =========================
#         # VALIDATIONS
#         # =========================

#         if not data:
#             return jsonify({"error": "No data provided"}), 400

#         production_date = data.get("date")
#         outlet = data.get("outlet")
#         total = data.get("total", 0)
#         items = data.get("items", [])

#         if not production_date:
#             return jsonify({"error": "date is required"}), 400

#         if not outlet:
#             return jsonify({"error": "outlet is required"}), 400

#         if not items or len(items) == 0:
#             return jsonify({"error": "items are required"}), 400

#         # =========================
#         # INSERT MASTER TABLE
#         # =========================

#         master_sql = """
#         INSERT INTO centralkitchen_production
#         (
#             production_date,
#             outlet,
#             total
#         )
#         VALUES
#         (
#             %s,
#             %s,
#             %s
#         )
#         """

#         cursor.execute(master_sql, (
#             production_date,
#             outlet,
#             total
#         ))

#         production_id = cursor.lastrowid

#         # =========================
#         # INSERT ITEMS
#         # =========================

#         item_sql = """
#         INSERT INTO centralkitchen_productionitems
#         (
#             production_id,
#             itemname,
#             quantity,
#             uom,
#             rate,
#             total
#         )
#         VALUES
#         (
#             %s,
#             %s,
#             %s,
#             %s,
#             %s,
#             %s
#         )
#         """

#         # =========================
#         # STOCK UPDATE
#         # =========================

#         for item in items:

#             itemname = item.get("ItemName")
#             quantity = float(item.get("Quantity", 0))
#             uom = item.get("UOM")
#             rate = float(item.get("Rate", 0))
#             item_total = float(item.get("Total", 0))
#             group_name =  "Finished Goods"
#             brand_name = item.get("BrandName")

#             # -------------------------
#             # INSERT ITEM
#             # -------------------------

#             cursor.execute(item_sql, (
#                 production_id,
#                 itemname,
#                 quantity,
#                 uom,
#                 rate,
#                 item_total
#             ))

#             # -------------------------
#             # CHECK STOCK EXISTS
#             # -------------------------

#             check_stock_sql = """
#             SELECT id, CurrentLevel
#             FROM stock_statement
#             WHERE ItemName = %s
#             AND OutletName = %s
#             AND GroupName = 'Finished Goods'
#             LIMIT 1
#             """

#             cursor.execute(check_stock_sql, (
#                 itemname,
#                 outlet
#             ))

#             stock_result = cursor.fetchone()

#             # -------------------------
#             # UPDATE EXISTING STOCK
#             # -------------------------

#             if stock_result:

#                 stock_id = stock_result["id"]
#                 current_level = float(stock_result["CurrentLevel"] or 0)

#                 new_level = current_level + quantity
#                 new_total = new_level * rate

#                 update_stock_sql = """
#                 UPDATE stock_statement
#                 SET
#                     CurrentLevel = %s,
#                     Rate = %s,
#                     Total = %s
#                 WHERE id = %s
#                 """

#                 cursor.execute(update_stock_sql, (
#                     new_level,
#                     rate,
#                     new_total,
#                     stock_id
#                 ))

#             # -------------------------
#             # INSERT NEW STOCK
#             # -------------------------

#             else:

#                 insert_stock_sql = """
#                 INSERT INTO stock_statement
#                 (
#                     GroupName,
#                     ItemName,
#                     BrandName,
#                     UOM,
#                     CurrentLevel,
#                     Rate,
#                     Total,
#                     OutletName,
#                     Type
#                 )
#                 VALUES
#                 (
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s
#                 )
#                 """

#                 cursor.execute(insert_stock_sql, (
#                     group_name,
#                     itemname,
#                     brand_name,
#                     uom,
#                     quantity,
#                     rate,
#                     item_total,
#                     outlet,
#                     "Production"
#                 ))

#         # =========================
#         # COMMIT
#         # =========================

#         mydb.commit()

#         return jsonify({
#             "message": "Central kitchen production posted successfully",
#             "production_id": production_id
#         }), 200

#     except mysql.connector.Error as db_error:

#         if mydb:
#             mydb.rollback()

#         return jsonify({
#             "error": f"Database error: {str(db_error)}"
#         }), 500

#     except Exception as e:

#         if mydb:
#             mydb.rollback()

#         return jsonify({
#             "error": f"Unexpected error: {str(e)}"
#         }), 500

#     finally:

#         if cursor:
#             cursor.close()

#         if mydb:
#             mydb.close()


@app_file231.route("/postcentralkitchenproduction", methods=["POST"])
@cross_origin()
def post_central_kitchen_production():
    mydb = None
    cursor = None

    try:
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password')
        )

        cursor = mydb.cursor(buffered=True, dictionary=True)

        # Select DB
        cursor.execute(f"USE {os.getenv('database')}")

        data = request.get_json()

        # =========================
        # VALIDATIONS
        # =========================

        if not data:
            return jsonify({"error": "No data provided"}), 400

        production_date = data.get("date")
        outlet = data.get("outlet")
        total = data.get("total", 0)
        items = data.get("items", [])

        if not production_date:
            return jsonify({"error": "date is required"}), 400

        if not outlet:
            return jsonify({"error": "outlet is required"}), 400

        if not items or len(items) == 0:
            return jsonify({"error": "items are required"}), 400

        # =========================
        # GET CURRENT TIME AS STRING
        # =========================
        from datetime import datetime
        # current_time = datetime.now().strftime("%H:%M:%S")  # Format: HH:MM:SS
        # Alternative formats:
        current_time = datetime.now().strftime("%I:%M:%S %p")  # Format: 02:30:45 PM
        # current_time = datetime.now().strftime("%H:%M:%S")  # 24-hour format

        # =========================
        # INSERT MASTER TABLE
        # =========================

        master_sql = """
        INSERT INTO centralkitchen_production
        (
            production_date,
            outlet,
            total,
            time
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s
        )
        """

        cursor.execute(master_sql, (
            production_date,
            outlet,
            total,
            current_time
        ))

        production_id = cursor.lastrowid

        # =========================
        # INSERT ITEMS
        # =========================

        item_sql = """
        INSERT INTO centralkitchen_productionitems
        (
            production_id,
            itemname,
            quantity,
            uom,
            rate,
            total
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        """

        # =========================
        # STOCK UPDATE
        # =========================

        for item in items:

            itemname = item.get("ItemName")
            quantity = float(item.get("Quantity", 0))
            uom = item.get("UOM")
            rate = float(item.get("Rate", 0))
            item_total = float(item.get("Total", 0))
            group_name = "Finished Goods"
            # brand_name = item.get("BrandName")

            # -------------------------
            # INSERT ITEM
            # -------------------------

            cursor.execute(item_sql, (
                production_id,
                itemname,
                quantity,
                uom,
                rate,
                item_total
            ))

            # -------------------------
            # CHECK STOCK EXISTS
            # -------------------------

            check_stock_sql = """
            SELECT id, CurrentLevel
            FROM stock_statement
            WHERE ItemName = %s
            AND OutletName = %s
            AND GroupName = 'Finished Goods'
            LIMIT 1
            """

            cursor.execute(check_stock_sql, (
                itemname,
                outlet
            ))

            stock_result = cursor.fetchone()

            # -------------------------
            # UPDATE EXISTING STOCK
            # -------------------------

            if stock_result:

                stock_id = stock_result["id"]
                current_level = float(stock_result["CurrentLevel"] or 0)

                new_level = current_level + quantity
                new_total = new_level * rate

                update_stock_sql = """
                UPDATE stock_statement
                SET
                    CurrentLevel = %s,
                    Rate = %s,
                    Total = %s
                WHERE id = %s
                """

                cursor.execute(update_stock_sql, (
                    new_level,
                    rate,
                    new_total,
                    stock_id
                ))

            # -------------------------
            # INSERT NEW STOCK
            # -------------------------

            else:

                insert_stock_sql = """
                INSERT INTO stock_statement
                (
                    GroupName,
                    ItemName,
                    UOM,
                    CurrentLevel,
                    Rate,
                    Total,
                    OutletName,
                    Type
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                """

                cursor.execute(insert_stock_sql, (
                    group_name,
                    itemname,
                    uom,
                    quantity,
                    rate,
                    item_total,
                    outlet,
                    "Production"
                ))

        # =========================
        # COMMIT
        # =========================

        mydb.commit()

        return jsonify({
            "message": "Central kitchen production posted successfully",
            "production_id": production_id,
            "production_time": current_time
        }), 200

    except mysql.connector.Error as db_error:

        if mydb:
            mydb.rollback()

        return jsonify({
            "error": f"Database error: {str(db_error)}"
        }), 500

    except Exception as e:

        if mydb:
            mydb.rollback()

        return jsonify({
            "error": f"Unexpected error: {str(e)}"
        }), 500

    finally:

        if cursor:
            cursor.close()

        if mydb:
            mydb.close()



@app_file231.route("/deletecentralkitchenproduction/<int:production_id>", methods=["DELETE"])
@cross_origin()
def delete_central_kitchen_production(production_id):
    mydb = None
    cursor = None

    try:
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password')
        )

        cursor = mydb.cursor(buffered=True, dictionary=True)
        cursor.execute(f"USE {os.getenv('database')}")

        # =========================
        # GET PRODUCTION DETAILS
        # =========================
        
        # Get master record
        master_query = """
        SELECT production_date, outlet, total 
        FROM centralkitchen_production 
        WHERE id = %s
        """
        cursor.execute(master_query, (production_id,))
        production = cursor.fetchone()
        
        if not production:
            return jsonify({"error": "Production record not found"}), 404
        
        outlet = production['outlet']
        
        # Get all production items
        items_query = """
        SELECT id, itemname, quantity, uom, rate, total 
        FROM centralkitchen_productionitems 
        WHERE production_id = %s
        """
        cursor.execute(items_query, (production_id,))
        production_items = cursor.fetchall()
        
        if not production_items:
            return jsonify({"error": "No items found for this production"}), 404
        
        # =========================
        # REVERSE STOCK UPDATES
        # =========================
        
        for item in production_items:
            itemname = item['itemname']
            quantity = float(item['quantity'])
            rate = float(item['rate'])
            
            # Check current stock
            check_stock_sql = """
            SELECT id, CurrentLevel, Total
            FROM stock_statement
            WHERE ItemName = %s
            AND OutletName = %s
            AND GroupName = 'Finished Goods'
            LIMIT 1
            """
            
            cursor.execute(check_stock_sql, (itemname, outlet))
            stock_result = cursor.fetchone()
            
            if stock_result:
                stock_id = stock_result["id"]
                current_level = float(stock_result["CurrentLevel"] or 0)
                
                # Reverse: subtract the quantity that was added
                new_level = current_level - quantity
                new_total = new_level * rate
                
                if new_level <= 0:
                    # Delete stock record if level becomes zero or negative
                    delete_stock_sql = "DELETE FROM stock_statement WHERE id = %s"
                    cursor.execute(delete_stock_sql, (stock_id,))
                else:
                    # Update stock with reversed values
                    update_stock_sql = """
                    UPDATE stock_statement
                    SET
                        CurrentLevel = %s,
                        Total = %s
                    WHERE id = %s
                    """
                    cursor.execute(update_stock_sql, (
                        new_level,
                        new_total,
                        stock_id
                    ))
            else:
                # This shouldn't happen if production was properly created
                print(f"Warning: Stock not found for {itemname} at {outlet}")
        
        # =========================
        # DELETE PRODUCTION ITEMS
        # =========================
        
        delete_items_sql = "DELETE FROM centralkitchen_productionitems WHERE production_id = %s"
        cursor.execute(delete_items_sql, (production_id,))
        
        # =========================
        # DELETE PRODUCTION MASTER
        # =========================
        
        delete_master_sql = "DELETE FROM centralkitchen_production WHERE id = %s"
        cursor.execute(delete_master_sql, (production_id,))
        
        # =========================
        # COMMIT TRANSACTION
        # =========================
        
        mydb.commit()
        
        return jsonify({
            "message": "Production deleted successfully",
            "production_id": production_id,
            "reversed_items": len(production_items),
            "outlet": outlet
        }), 200
        
    except mysql.connector.Error as db_error:
        if mydb:
            mydb.rollback()
        return jsonify({
            "error": f"Database error: {str(db_error)}"
        }), 500
        
    except Exception as e:
        if mydb:
            mydb.rollback()
        return jsonify({
            "error": f"Unexpected error: {str(e)}"
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if mydb:
            mydb.close()


@app_file231.route("/getcentralkitchenproduction", methods=["GET"])
@cross_origin()
def get_central_kitchen_production():
    mydb = None
    cursor = None

    try:
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password')
        )

        cursor = mydb.cursor(buffered=True, dictionary=True)
        cursor.execute(f"USE {os.getenv('database')}")

        # Get query parameters for filtering
        production_id = request.args.get('id')
        outlet = request.args.get('outlet')
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        include_items = True
        # Base query
        query = """
        SELECT 
            p.id,
            p.production_date,
            p.outlet,
            p.total,
            p.remarks,
            COUNT(pi.id) as item_count,
            SUM(pi.quantity) as total_quantity
            p.time
        FROM centralkitchen_production p
        LEFT JOIN centralkitchen_productionitems pi ON p.id = pi.production_id
        WHERE 1=1
        """
        params = []
        
        # Apply filters
        if production_id:
            query += " AND p.id = %s"
            params.append(production_id)
        
        if outlet:
            query += " AND p.outlet = %s"
            params.append(outlet)
        
        if from_date:
            query += " AND p.production_date >= %s"
            params.append(from_date)
        
        if to_date:
            query += " AND p.production_date <= %s"
            params.append(to_date)
        
        query += " GROUP BY p.id ORDER BY p.production_date DESC, p.id DESC"
        
        cursor.execute(query, params)
        productions = cursor.fetchall()
        
        # If specific ID requested OR include_items=true, get items
        if production_id and productions:
            # Get items for single production
            items_query = """
            SELECT 
                id,
                itemname,
                quantity,
                uom,
                rate,
                total,
                remarks
            FROM centralkitchen_productionitems
            WHERE production_id = %s
            ORDER BY id
            """
            cursor.execute(items_query, (production_id,))
            items = cursor.fetchall()
            
            productions[0]['items'] = items
            
            return jsonify({
                "success": True,
                "production": productions[0]
            }), 200
        
        # If include_items=true, get items for all productions
        elif include_items and productions:
            for production in productions:
                items_query = """
                SELECT 
                    id,
                    itemname,
                    quantity,
                    uom,
                    rate,
                    total,
                    remarks
                FROM centralkitchen_productionitems
                WHERE production_id = %s
                ORDER BY id
                """
                cursor.execute(items_query, (production['id'],))
                items = cursor.fetchall()
                production['items'] = items
            
            return jsonify({
                "success": True,
                "productions": productions,
                "count": len(productions)
            }), 200
        
        return jsonify({
            "success": True,
            "productions": productions,
            "count": len(productions)
        }), 200
        
    except mysql.connector.Error as db_error:
        return jsonify({
            "error": f"Database error: {str(db_error)}"
        }), 500
        
    except Exception as e:
        return jsonify({
            "error": f"Unexpected error: {str(e)}"
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if mydb:
            mydb.close()


@app_file231.route("/getcentralkitchenproduction/<int:production_id>", methods=["GET"])
@cross_origin()
def get_single_central_kitchen_production(production_id):
    mydb = None
    cursor = None

    try:
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password')
        )

        cursor = mydb.cursor(buffered=True, dictionary=True)
        cursor.execute(f"USE {os.getenv('database')}")
        
        # Get production master
        master_query = """
        SELECT 
            id,
            production_date,
            outlet,
            total,
            remarks
        FROM centralkitchen_production
        WHERE id = %s
        """
        cursor.execute(master_query, (production_id,))
        production = cursor.fetchone()
        
        if not production:
            return jsonify({"error": "Production record not found"}), 404
        
        # Get production items
        items_query = """
        SELECT 
            id,
            production_id,
            itemname,
            quantity,
            uom,
            rate,
            total,
            remarks
        FROM centralkitchen_productionitems
        WHERE production_id = %s
        ORDER BY id
        """
        cursor.execute(items_query, (production_id,))
        items = cursor.fetchall()
        
        production['items'] = items
        
        return jsonify({
            "success": True,
            "production": production
        }), 200
        
    except mysql.connector.Error as db_error:
        return jsonify({
            "error": f"Database error: {str(db_error)}"
        }), 500
        
    except Exception as e:
        return jsonify({
            "error": f"Unexpected error: {str(e)}"
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if mydb:
            mydb.close()


@app_file231.route("/updatecentralkitchenproduction/<int:production_id>", methods=["PUT"])
@cross_origin()
def update_central_kitchen_production(production_id):
    mydb = None
    cursor = None

    try:
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password')
        )

        cursor = mydb.cursor(buffered=True, dictionary=True)
        cursor.execute(f"USE {os.getenv('database')}")

        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Check if production exists
        check_query = "SELECT id, outlet FROM centralkitchen_production WHERE id = %s"
        cursor.execute(check_query, (production_id,))
        existing_production = cursor.fetchone()
        
        if not existing_production:
            return jsonify({"error": "Production record not found"}), 404
        
        # REMOVED: mydb.start_transaction() - Transaction is automatic
        
        # =========================
        # UPDATE MASTER TABLE
        # =========================
        
        update_fields = []
        params = []
        
        if 'date' in data:
            update_fields.append("production_date = %s")
            params.append(data['date'])
        
        if 'outlet' in data:
            update_fields.append("outlet = %s")
            params.append(data['outlet'])
        
        if 'total' in data:
            update_fields.append("total = %s")
            params.append(data['total'])
        
        if 'remarks' in data:
            update_fields.append("remarks = %s")
            params.append(data['remarks'])
        
        if update_fields:
            update_sql = f"UPDATE centralkitchen_production SET {', '.join(update_fields)} WHERE id = %s"
            params.append(production_id)
            cursor.execute(update_sql, params)
        
        # =========================
        # UPDATE ITEMS (if provided)
        # =========================
        
        if 'items' in data and data['items'] is not None:
            # Get existing items
            cursor.execute("SELECT id, itemname, quantity, rate FROM centralkitchen_productionitems WHERE production_id = %s", (production_id,))
            existing_items = {item['id']: item for item in cursor.fetchall()}
            
            outlet = data.get('outlet', existing_production['outlet'])
            
            for item in data['items']:
                item_id = item.get('id')
                itemname = item.get('ItemName')
                quantity = float(item.get('Quantity', 0))
                uom = item.get('UOM')
                rate = float(item.get('Rate', 0))
                item_total = float(item.get('Total', 0))
                brand_name = item.get('BrandName', '')
                
                if item_id and item_id in existing_items:
                    # UPDATE existing item
                    old_item = existing_items[item_id]
                    old_quantity = float(old_item['quantity'])
                    old_rate = float(old_item['rate'])
                    
                    # Calculate difference
                    quantity_diff = quantity - old_quantity
                    
                    if quantity_diff != 0:
                        # Update stock with the difference
                        update_stock_for_item(cursor, itemname, outlet, quantity_diff, rate)
                    elif rate != old_rate:
                        # If only rate changed, update stock total
                        update_stock_rate(cursor, itemname, outlet, old_quantity, old_rate, rate)
                    
                    # Update item
                    update_item_sql = """
                    UPDATE centralkitchen_productionitems
                    SET itemname = %s, quantity = %s, uom = %s, rate = %s, total = %s
                    WHERE id = %s AND production_id = %s
                    """
                    cursor.execute(update_item_sql, (itemname, quantity, uom, rate, item_total, item_id, production_id))
                    
                    # Remove from existing_items dict to track deletion
                    del existing_items[item_id]
                    
                else:
                    # INSERT new item
                    insert_item_sql = """
                    INSERT INTO centralkitchen_productionitems
                    (production_id, itemname, quantity, uom, rate, total)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_item_sql, (production_id, itemname, quantity, uom, rate, item_total))
                    
                    # Add to stock
                    add_to_stock(cursor, itemname, outlet, quantity, rate, item_total, brand_name, uom)
            
            # DELETE items not in the update list
            for item_id, item_data in existing_items.items():
                # Reverse stock before deletion
                reverse_stock_for_item(cursor, item_data['itemname'], outlet, float(item_data['quantity']))
                
                # Delete item
                cursor.execute("DELETE FROM centralkitchen_productionitems WHERE id = %s", (item_id,))
        
        # =========================
        # RECALCULATE TOTAL IF NEEDED
        # =========================
        
        if 'items' in data and data['items'] is not None:
            cursor.execute("SELECT SUM(total) as total FROM centralkitchen_productionitems WHERE production_id = %s", (production_id,))
            total_result = cursor.fetchone()
            new_total = float(total_result['total'] or 0)
            
            cursor.execute("UPDATE centralkitchen_production SET total = %s WHERE id = %s", (new_total, production_id))
        
        # Commit transaction
        mydb.commit()
        
        return jsonify({
            "message": "Production updated successfully",
            "production_id": production_id
        }), 200
        
    except mysql.connector.Error as db_error:
        if mydb:
            mydb.rollback()
        return jsonify({
            "error": f"Database error: {str(db_error)}"
        }), 500
        
    except Exception as e:
        if mydb:
            mydb.rollback()
        return jsonify({
            "error": f"Unexpected error: {str(e)}"
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if mydb:
            mydb.close()


# Updated Helper functions
def update_stock_for_item(cursor, itemname, outlet, quantity_diff, rate):
    """Update stock with quantity difference"""
    check_stock_sql = """
    SELECT id, CurrentLevel, Rate
    FROM stock_statement
    WHERE ItemName = %s AND OutletName = %s AND GroupName = 'Finished Goods'
    LIMIT 1
    """
    cursor.execute(check_stock_sql, (itemname, outlet))
    stock_result = cursor.fetchone()
    
    if stock_result:
        stock_id = stock_result["id"]
        current_level = float(stock_result["CurrentLevel"] or 0)
        current_rate = float(stock_result["Rate"] or rate)
        
        new_level = current_level + quantity_diff
        
        # Use the new rate if quantity changed, otherwise keep current rate
        final_rate = rate if quantity_diff != 0 else current_rate
        new_total = new_level * final_rate
        
        if new_level <= 0:
            cursor.execute("DELETE FROM stock_statement WHERE id = %s", (stock_id,))
        else:
            update_stock_sql = """
            UPDATE stock_statement
            SET CurrentLevel = %s, Rate = %s, Total = %s
            WHERE id = %s
            """
            cursor.execute(update_stock_sql, (new_level, final_rate, new_total, stock_id))


def update_stock_rate(cursor, itemname, outlet, quantity, old_rate, new_rate):
    """Update stock when only rate changes"""
    check_stock_sql = """
    SELECT id, CurrentLevel
    FROM stock_statement
    WHERE ItemName = %s AND OutletName = %s AND GroupName = 'Finished Goods'
    LIMIT 1
    """
    cursor.execute(check_stock_sql, (itemname, outlet))
    stock_result = cursor.fetchone()
    
    if stock_result:
        stock_id = stock_result["id"]
        current_level = float(stock_result["CurrentLevel"] or 0)
        
        # Calculate new total with new rate
        new_total = current_level * new_rate
        
        update_stock_sql = """
        UPDATE stock_statement
        SET Rate = %s, Total = %s
        WHERE id = %s
        """
        cursor.execute(update_stock_sql, (new_rate, new_total, stock_id))


def add_to_stock(cursor, itemname, outlet, quantity, rate, total, brand_name, uom):
    """Add new item to stock"""
    check_stock_sql = """
    SELECT id, CurrentLevel
    FROM stock_statement
    WHERE ItemName = %s AND OutletName = %s AND GroupName = 'Finished Goods'
    LIMIT 1
    """
    cursor.execute(check_stock_sql, (itemname, outlet))
    stock_result = cursor.fetchone()
    
    if stock_result:
        stock_id = stock_result["id"]
        current_level = float(stock_result["CurrentLevel"] or 0)
        new_level = current_level + quantity
        new_total = new_level * rate
        
        update_stock_sql = """
        UPDATE stock_statement
        SET CurrentLevel = %s, Rate = %s, Total = %s
        WHERE id = %s
        """
        cursor.execute(update_stock_sql, (new_level, rate, new_total, stock_id))
    else:
        insert_stock_sql = """
        INSERT INTO stock_statement
        (GroupName, ItemName, BrandName, UOM, CurrentLevel, Rate, Total, OutletName, Type)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_stock_sql, ("Finished Goods", itemname, brand_name, uom, quantity, rate, total, outlet, "Production"))


def reverse_stock_for_item(cursor, itemname, outlet, quantity):
    """Reverse stock for deleted item"""
    check_stock_sql = """
    SELECT id, CurrentLevel, Rate
    FROM stock_statement
    WHERE ItemName = %s AND OutletName = %s AND GroupName = 'Finished Goods'
    LIMIT 1
    """
    cursor.execute(check_stock_sql, (itemname, outlet))
    stock_result = cursor.fetchone()
    
    if stock_result:
        stock_id = stock_result["id"]
        current_level = float(stock_result["CurrentLevel"] or 0)
        rate = float(stock_result["Rate"] or 0)
        new_level = current_level - quantity
        new_total = new_level * rate
        
        if new_level <= 0:
            cursor.execute("DELETE FROM stock_statement WHERE id = %s", (stock_id,))
        else:
            update_stock_sql = """
            UPDATE stock_statement
            SET CurrentLevel = %s, Total = %s
            WHERE id = %s
            """
            cursor.execute(update_stock_sql, (new_level, new_total, stock_id))


@app_file231.route("/getcentralkitchenproduction-itemlists", methods=["GET"])
@cross_origin()
def get_central_kitchen_production_itemlists():
    mydb = None
    cursor = None

    try:
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password')
        )

        cursor = mydb.cursor(buffered=True, dictionary=True)
        cursor.execute(f"USE {os.getenv('database')}")

        # Get query parameters for filtering
        production_id = request.args.get('id')
        outlet = request.args.get('outlet')
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        
        # Base query for productions (summary)
        query = """
        SELECT 
            p.id,
            p.production_date,
            p.outlet,
            p.total,
            p.remarks,
            COUNT(pi.id) as item_count,
            SUM(pi.quantity) as total_quantity
        FROM centralkitchen_production p
        LEFT JOIN centralkitchen_productionitems pi ON p.id = pi.production_id
        WHERE 1=1
        """
        params = []
        
        # Apply filters
        if production_id:
            query += " AND p.id = %s"
            params.append(production_id)
        
        if outlet:
            query += " AND p.outlet = %s"
            params.append(outlet)
        
        if from_date:
            query += " AND p.production_date >= %s"
            params.append(from_date)
        
        if to_date:
            query += " AND p.production_date <= %s"
            params.append(to_date)
        
        query += " GROUP BY p.id ORDER BY p.production_date DESC, p.id DESC"
        
        cursor.execute(query, params)
        productions = cursor.fetchall()
        
        # Query to get items grouped by itemname and outlet
        items_grouped_query = """
        SELECT 
            pi.itemname,
            p.outlet,
            SUM(pi.quantity) as total_quantity,
            pi.uom,
            AVG(pi.rate) as avg_rate,
            SUM(pi.total) as total_amount,
            GROUP_CONCAT(DISTINCT p.production_date ORDER BY p.production_date SEPARATOR ', ') as production_dates,
            COUNT(DISTINCT p.id) as production_count
        FROM centralkitchen_productionitems pi
        INNER JOIN centralkitchen_production p ON pi.production_id = p.id
        WHERE 1=1
        """
        
        items_params = []
        
        # Apply same filters to items query
        if production_id:
            items_grouped_query += " AND p.id = %s"
            items_params.append(production_id)
        
        if outlet:
            items_grouped_query += " AND p.outlet = %s"
            items_params.append(outlet)
        
        if from_date:
            items_grouped_query += " AND p.production_date >= %s"
            items_params.append(from_date)
        
        if to_date:
            items_grouped_query += " AND p.production_date <= %s"
            items_params.append(to_date)
        
        items_grouped_query += " GROUP BY pi.itemname, p.outlet, pi.uom ORDER BY p.outlet, pi.itemname"
        
        cursor.execute(items_grouped_query, items_params)
        grouped_items = cursor.fetchall()
        
        # Calculate grand totals
        grand_total_quantity = sum(item['total_quantity'] for item in grouped_items) if grouped_items else 0
        grand_total_amount = sum(item['total_amount'] for item in grouped_items) if grouped_items else 0
        
        # If specific ID requested, also return detailed items for that production
        if production_id and productions:
            # Get detailed items for single production
            items_query = """
            SELECT 
                id,
                itemname,
                quantity,
                uom,
                rate,
                total,
                remarks
            FROM centralkitchen_productionitems
            WHERE production_id = %s
            ORDER BY id
            """
            cursor.execute(items_query, (production_id,))
            detailed_items = cursor.fetchall()
            
            productions[0]['detailed_items'] = detailed_items
            productions[0]['grouped_items'] = grouped_items
            
            return jsonify({
                "success": True,
                "production": productions[0],
                "grouped_items_summary": grouped_items,
                "summary_totals": {
                    "total_quantity": grand_total_quantity,
                    "total_amount": grand_total_amount,
                    "unique_items": len(grouped_items)
                }
            }), 200
        
        # Return all productions with grouped items summary
        return jsonify({
            "success": True,
            "productions": productions,
            "productions_count": len(productions),
            "grouped_items_by_outlet_item": grouped_items,
            "summary_totals": {
                "total_quantity": grand_total_quantity,
                "total_amount": grand_total_amount,
                "unique_item_outlet_combinations": len(grouped_items)
            }
        }), 200
        
    except mysql.connector.Error as db_error:
        return jsonify({
            "error": f"Database error: {str(db_error)}"
        }), 500
        
    except Exception as e:
        return jsonify({
            "error": f"Unexpected error: {str(e)}"
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if mydb:
            mydb.close()