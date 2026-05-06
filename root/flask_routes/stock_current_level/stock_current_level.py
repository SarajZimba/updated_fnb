# from flask import Flask, Blueprint, request, jsonify
# import mysql.connector
# from flask_cors import cross_origin
# import os
# from dotenv import load_dotenv
# from datetime import datetime

# load_dotenv()

# app_file226 = Blueprint('appfile_226', __name__)

# @app_file226.route('/getstocklevels', methods=["GET"])
# @cross_origin()
# def get_stock_levels():
#     mydb = None
#     try:
#         mydb = mysql.connector.connect(
#             user=os.getenv('user'), 
#             password=os.getenv('password'), 
#             host=os.getenv('host')
#         )
#         cursor = mydb.cursor(dictionary=True, buffered=True)
#         database_sql = "USE {};".format(os.getenv('database'))
#         cursor.execute(database_sql)
        
#         # Get query parameters for filtering
#         outlet = request.args.get('outlet', None)
#         name = request.args.get('name', None)
#         show_expired = request.args.get('show_expired', 'false').lower() == 'true'
#         min_qty = request.args.get('min_qty', None)
        
#         # Base query
#         query = """
#             SELECT 
#                 id,
#                 name,
#                 outlet,
#                 units,
#                 qty,
#                 expiry_date,
#                 rate,
#                 total,
#                 CASE 
#                     WHEN expiry_date IS NULL THEN 'No Expiry'
#                     WHEN expiry_date < CURDATE() THEN 'Expired'
#                     WHEN expiry_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY) THEN 'Expiring Soon'
#                     ELSE 'Valid'
#                 END as stock_status,
#                 DATEDIFF(expiry_date, CURDATE()) as days_until_expiry
#             FROM stock_current_level
#             WHERE 1=1
#         """
        
#         params = []
        
#         # Apply filters
#         if outlet:
#             query += " AND outlet = %s"
#             params.append(outlet)
        
#         if name:
#             query += " AND name LIKE %s"
#             params.append(f"%{name}%")
        
#         if not show_expired:
#             query += " AND (expiry_date IS NULL OR expiry_date >= CURDATE())"
        
#         if min_qty:
#             query += " AND qty >= %s"
#             params.append(min_qty)
        
#         # Order by name and expiry date
#         query += " ORDER BY name ASC, expiry_date ASC NULLS LAST"
        
#         cursor.execute(query, params)
#         results = cursor.fetchall()
        
#         # Get summary statistics
#         summary_query = """
#             SELECT 
#                 COUNT(DISTINCT name) as unique_items,
#                 SUM(qty) as total_quantity,
#                 SUM(total) as total_value,
#                 COUNT(CASE WHEN qty = 0 THEN 1 END) as out_of_stock,
#                 COUNT(CASE WHEN expiry_date < CURDATE() AND expiry_date IS NOT NULL THEN 1 END) as expired_items,
#                 COUNT(CASE WHEN expiry_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY) AND expiry_date IS NOT NULL THEN 1 END) as expiring_soon
#             FROM stock_current_level
#             WHERE 1=1
#         """
        
#         summary_params = []
        
#         if outlet:
#             summary_query += " AND outlet = %s"
#             summary_params.append(outlet)
        
#         cursor.execute(summary_query, summary_params)
#         summary = cursor.fetchone()
        
#         return jsonify({
#             "success": True,
#             "data": results,
#             "summary": summary,
#             "filters_applied": {
#                 "outlet": outlet,
#                 "name": name,
#                 "show_expired": show_expired,
#                 "min_qty": min_qty
#             },
#             "total_records": len(results)
#         }), 200
        
#     except Exception as e:
#         return jsonify({"error": str(e)}), 400
#     finally:
#         if mydb and mydb.is_connected():
#             mydb.close()


from flask import Flask, Blueprint, request, jsonify
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app_file226 = Blueprint('appfile_226', __name__)

@app_file226.route('/getstocklevels', methods=["GET"])
@cross_origin()
def get_stock_levels():
    mydb = None
    try:
        mydb = mysql.connector.connect(
            user=os.getenv('user'), 
            password=os.getenv('password'), 
            host=os.getenv('host')
        )
        cursor = mydb.cursor(dictionary=True, buffered=True)
        database_sql = "USE {};".format(os.getenv('database'))
        cursor.execute(database_sql)
        
        # Get query parameters for filtering
        outlet = request.args.get('outlet', None)
        name = request.args.get('name', None)
        show_expired = request.args.get('show_expired', 'false').lower() == 'true'
        min_qty = request.args.get('min_qty', None)
        
        # Base query
        query = """
            SELECT 
                id,
                name,
                outlet,
                units,
                qty,
                expiry_date,
                rate,
                total,
                CASE 
                    WHEN expiry_date IS NULL THEN 'No Expiry'
                    WHEN expiry_date < CURDATE() THEN 'Expired'
                    WHEN expiry_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY) THEN 'Expiring Soon'
                    ELSE 'Valid'
                END as stock_status,
                DATEDIFF(expiry_date, CURDATE()) as days_until_expiry
            FROM stock_current_level
            WHERE 1=1 and qty > 0 and expiry_date is not NULL
        """
        
        params = []
        
        # Apply filters
        if outlet:
            query += " AND outlet = %s"
            params.append(outlet)
        
        if name:
            query += " AND name LIKE %s"
            params.append(f"%{name}%")
        
        # if not show_expired:
        #     query += " AND (expiry_date IS NULL OR expiry_date >= CURDATE())"
        
        if min_qty:
            query += " AND qty >= %s"
            params.append(min_qty)
        
        # Order by name and expiry date (NULLs will automatically be last in ASC order)
        query += " ORDER BY name ASC, expiry_date ASC"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        # Get summary statistics
        summary_query = """
            SELECT 
                COUNT(DISTINCT name) as unique_items,
                SUM(qty) as total_quantity,
                SUM(total) as total_value,
                COUNT(CASE WHEN qty = 0 THEN 1 END) as out_of_stock,
                COUNT(CASE WHEN expiry_date < CURDATE() AND expiry_date IS NOT NULL THEN 1 END) as expired_items,
                COUNT(CASE WHEN expiry_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY) AND expiry_date IS NOT NULL THEN 1 END) as expiring_soon
            FROM stock_current_level
            WHERE 1=1
        """
        
        summary_params = []
        
        if outlet:
            summary_query += " AND outlet = %s"
            summary_params.append(outlet)
        
        cursor.execute(summary_query, summary_params)
        summary = cursor.fetchone()
        
        return jsonify({
            "success": True,
            "data": results,
            "summary": summary,
            "filters_applied": {
                "outlet": outlet,
                "name": name,
                "show_expired": show_expired,
                "min_qty": min_qty
            },
            "total_records": len(results)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        if mydb and mydb.is_connected():
            mydb.close()


@app_file226.route('/getstocklevels/<int:stock_id>', methods=["GET"])
@cross_origin()
def get_stock_level_by_id(stock_id):
    mydb = None
    try:
        mydb = mysql.connector.connect(
            user=os.getenv('user'), 
            password=os.getenv('password'), 
            host=os.getenv('host')
        )
        cursor = mydb.cursor(dictionary=True, buffered=True)
        database_sql = "USE {};".format(os.getenv('database'))
        cursor.execute(database_sql)
        
        query = """
            SELECT 
                id,
                name,
                outlet,
                units,
                qty,
                expiry_date,
                rate,
                total,
                CASE 
                    WHEN expiry_date IS NULL THEN 'No Expiry'
                    WHEN expiry_date < CURDATE() THEN 'Expired'
                    WHEN expiry_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY) THEN 'Expiring Soon'
                    ELSE 'Valid'
                END as stock_status
            FROM stock_current_level
            WHERE id = %s
        """
        
        cursor.execute(query, (stock_id,))
        result = cursor.fetchone()
        
        if result:
            return jsonify({"success": True, "data": result}), 200
        else:
            return jsonify({"error": "Stock record not found"}), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        if mydb and mydb.is_connected():
            mydb.close()


@app_file226.route('/getstocklevels/outlet/<outlet_name>', methods=["GET"])
@cross_origin()
def get_stock_levels_by_outlet(outlet_name):
    mydb = None
    try:
        mydb = mysql.connector.connect(
            user=os.getenv('user'), 
            password=os.getenv('password'), 
            host=os.getenv('host')
        )
        cursor = mydb.cursor(dictionary=True, buffered=True)
        database_sql = "USE {};".format(os.getenv('database'))
        cursor.execute(database_sql)
        
        query = """
            SELECT 
                name,
                units,
                SUM(qty) as total_qty,
                AVG(rate) as avg_rate,
                SUM(total) as total_value,
                COUNT(*) as batch_count,
                MIN(expiry_date) as earliest_expiry,
                MAX(expiry_date) as latest_expiry
            FROM stock_current_level
            WHERE outlet = %s AND qty > 0
            GROUP BY name, units
            ORDER BY name ASC
        """
        
        cursor.execute(query, (outlet_name,))
        results = cursor.fetchall()
        
        return jsonify({
            "success": True,
            "outlet": outlet_name,
            "data": results,
            "total_items": len(results)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        if mydb and mydb.is_connected():
            mydb.close()