from flask import Blueprint, jsonify, request
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv

load_dotenv()

app_file238 = Blueprint('app_file238', __name__)

@app_file238.route("/getcentralkitchenitems", methods=["GET"])
@cross_origin()
def get_central_kitchen_items():
    cursor = None
    mydb = None
    
    try:
        # Database connection
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password')
        )
        
        cursor = mydb.cursor(buffered=True, dictionary=True)
        
        # Select database
        cursor.execute(f"USE {os.getenv('database')}")
        
        # Query to get distinct items issued to Central Kitchen
        query = """
            SELECT DISTINCT 
                d.ItemName as item_name,
                d.UOM as uom
            FROM intblstorereqdetails d
            JOIN intblstorerequisition r ON d.StoreReqID = r.idintblStoreRequisition
            WHERE r.CostCenter = 'Central Kitchen'
            ORDER BY d.ItemName ASC
        """
        
        cursor.execute(query)
        items = cursor.fetchall()
        
        # Check if any items found
        if not items:
            return jsonify({
                "message": "No items found for Central Kitchen",
                "items": []
            }), 200
        
        # Format response
        response_items = []
        for item in items:
            response_items.append({
                "item_name": item['item_name'],
                "uom": item['uom']
            })
        
        return jsonify({
            "success": True,
            "count": len(response_items),
            "items": response_items
        }), 200
        
    except mysql.connector.Error as db_error:
        return jsonify({
            "success": False,
            "error": f"Database error: {str(db_error)}"
        }), 500
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if mydb:
            mydb.close()


# # Alternative version with optional outlet filter
# @app_file238.route("/getcentralkitchenitems/filter", methods=["GET"])
# @cross_origin()
# def get_central_kitchen_items_with_filter():
#     cursor = None
#     mydb = None
    
#     try:
#         # Get optional outlet parameter from query string
#         outlet = request.args.get('outlet', None)
        
#         # Database connection
#         mydb = mysql.connector.connect(
#             host=os.getenv('host'),
#             user=os.getenv('user'),
#             password=os.getenv('password')
#         )
        
#         cursor = mydb.cursor(buffered=True, dictionary=True)
        
#         # Select database
#         cursor.execute(f"USE {os.getenv('database')}")
        
#         # Build query with optional outlet filter
#         if outlet:
#             query = """
#                 SELECT DISTINCT 
#                     d.ItemName as item_name,
#                     d.UOM as uom,
#                     d.Rate
#                 FROM intblstorereqdetails d
#                 JOIN intblstorerequisition r ON d.StoreReqID = r.idintblStoreRequisition
#                 WHERE r.CostCenter = 'Central Kitchen'
#                     AND r.Outlet = %s
#                 ORDER BY d.ItemName ASC
#             """
#             cursor.execute(query, (outlet,))
#         else:
#             query = """
#                 SELECT DISTINCT 
#                     d.ItemName as item_name,
#                     d.UOM as uom, 
#                     d.Rate
#                 FROM intblstorereqdetails d
#                 JOIN intblstorerequisition r ON d.StoreReqID = r.idintblStoreRequisition
#                 WHERE r.CostCenter = 'Central Kitchen'
#                 ORDER BY d.ItemName ASC
#             """
#             cursor.execute(query)
        
#         items = cursor.fetchall()
        
#         # Check if any items found
#         if not items:
#             return jsonify({
#                 "success": True,
#                 "message": "No items found for Central Kitchen",
#                 "items": []
#             }), 200
        
#         # Format response
#         response_items = []
#         for item in items:
#             response_items.append({
#                 "item_name": item['item_name'],
#                 "uom": item['uom']
#             })
        
#         return jsonify({
#             "success": True,
#             "count": len(response_items),
#             "items": response_items
#         }), 200
        
#     except mysql.connector.Error as db_error:
#         return jsonify({
#             "success": False,
#             "error": f"Database error: {str(db_error)}"
#         }), 500
        
#     except Exception as e:
#         return jsonify({
#             "success": False,
#             "error": f"Unexpected error: {str(e)}"
#         }), 500
        
#     finally:
#         if cursor:
#             cursor.close()
#         if mydb:
#             mydb.close()


# Alternative version with optional outlet filter
@app_file238.route("/getcentralkitchenitems/filter", methods=["GET"])
@cross_origin()
def get_central_kitchen_items_with_filter():
    cursor = None
    mydb = None
    
    try:
        # Get optional outlet parameter from query string
        outlet = request.args.get('outlet', None)
        
        # Database connection
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password')
        )
        
        cursor = mydb.cursor(buffered=True, dictionary=True)
        
        # Select database
        cursor.execute(f"USE {os.getenv('database')}")
        
        # Build query with optional outlet filter and unit definition
        if outlet:
            query = """
                SELECT DISTINCT 
                    d.ItemName as item_name,
                    d.UOM as uom,
                    d.Rate as rate,
                    ud.id as unit_definition_id,
                    ud.name as unit_name,
                    ud.unit as unit_value,
                    ud.uom as unit_uom,
                    ud.rate as unit_rate,
                    ud.outlet as unit_outlet
                FROM intblstorereqdetails d
                JOIN intblstorerequisition r ON d.StoreReqID = r.idintblStoreRequisition
                LEFT JOIN tblunitdefinition ud ON d.ItemName = ud.name AND r.Outlet = ud.outlet
                WHERE r.CostCenter = 'Central Kitchen'
                    AND r.Outlet = %s
                ORDER BY d.ItemName ASC
            """
            cursor.execute(query, (outlet,))
        else:
            query = """
                SELECT DISTINCT 
                    d.ItemName as item_name,
                    d.UOM as uom,
                    d.Rate as rate,
                    ud.id as unit_definition_id,
                    ud.name as unit_name,
                    ud.unit as unit_value,
                    ud.uom as unit_uom,
                    ud.rate as unit_rate,
                    ud.outlet as unit_outlet
                FROM intblstorereqdetails d
                JOIN intblstorerequisition r ON d.StoreReqID = r.idintblStoreRequisition
                LEFT JOIN tblunitdefinition ud ON d.ItemName = ud.name AND r.Outlet = ud.outlet
                WHERE r.CostCenter = 'Central Kitchen'
                ORDER BY d.ItemName ASC
            """
            cursor.execute(query)
        
        items = cursor.fetchall()
        
        # Check if any items found
        if not items:
            return jsonify({
                "success": True,
                "message": "No items found for Central Kitchen",
                "items": []
            }), 200
        
        # Format response with unit definition
        response_items = []
        for item in items:
            # Create unit definition object if exists
            unit_definition = None
            if item.get('unit_definition_id'):
                unit_definition = {
                    "id": item['unit_definition_id'],
                    "name": item['unit_name'],
                    "unit_value": float(item['unit_value']) if item.get('unit_value') else None,
                    "uom": item['unit_uom'],
                    "rate": float(item['unit_rate']) if item.get('unit_rate') else None,
                    "outlet": item['unit_outlet']
                }
            
            response_items.append({
                "item_name": item['item_name'],
                "uom": item['uom'],
                "rate": float(item['rate']) if item.get('rate') else None,
                "unit_definition": unit_definition
            })
        
        return jsonify({
            "success": True,
            "count": len(response_items),
            "items": response_items
        }), 200
        
    except mysql.connector.Error as db_error:
        return jsonify({
            "success": False,
            "error": f"Database error: {str(db_error)}"
        }), 500
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if mydb:
            mydb.close()