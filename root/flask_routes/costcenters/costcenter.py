from flask import Blueprint, request, jsonify
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv
load_dotenv()
from root.auth.check import token_auth

app_file230 = Blueprint('app_file230', __name__)

# Helper function to validate outlet
def validate_outlet(cursor, outlet_id, outlet_name):
    """Validate if outlet exists in outetNames table"""
    cursor.execute(
        "SELECT id, Outlet FROM outetNames WHERE id = %s AND Outlet = %s",
        (outlet_id, outlet_name)
    )
    outlet = cursor.fetchone()
    
    if not outlet:
        # Try to check if outlet_id exists with different name
        cursor.execute(
            "SELECT id, Outlet FROM outetNames WHERE id = %s",
            (outlet_id,)
        )
        outlet_by_id = cursor.fetchone()
        
        if outlet_by_id:
            return False, f"Outlet name mismatch. Expected '{outlet_name}', found '{outlet_by_id['Outlet']}'"
        else:
            return False, f"Outlet with id {outlet_id} does not exist"
    
    return True, "Valid outlet"

# ------------------- CREATE Cost Center -------------------
@app_file230.route("/create_costcenter", methods=["POST"])
@cross_origin()
def create_costcenter():
    try:
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password')
        )
        cursor = mydb.cursor(dictionary=True)
        
        database_sql = "USE {};".format(os.getenv('database'))
        cursor.execute(database_sql)
        
        data = request.get_json()
        
        # Validate token
        token = data.get('token')
        if not token or not token_auth(token):
            return jsonify({"error": "Invalid or missing token."}), 400
        
        # Validate required fields
        costcenter_name = data.get('costcenter_name')
        outlet_id = data.get('outlet_id')
        outlet_name = data.get('outlet_name')
        
        if not costcenter_name:
            return jsonify({"error": "costcenter_name is required"}), 400
        
        if not outlet_id:
            return jsonify({"error": "outlet_id is required"}), 400
        
        if not outlet_name:
            return jsonify({"error": "outlet_name is required"}), 400
        
        # Validate outlet exists in outetNames table
        is_valid, message = validate_outlet(cursor, outlet_id, outlet_name)
        if not is_valid:
            return jsonify({"error": message}), 400
        
        # Check if cost center already exists for this outlet
        cursor.execute(
            "SELECT id FROM costcenter WHERE costcenter_name = %s AND outlet_id = %s",
            (costcenter_name, outlet_id)
        )
        existing = cursor.fetchone()
        
        if existing:
            return jsonify({"error": "Cost center already exists for this outlet"}), 400
        
        # Insert new cost center
        sql = """
        INSERT INTO costcenter (costcenter_name, outlet_id, outlet_name)
        VALUES (%s, %s, %s)
        """
        
        cursor.execute(sql, (costcenter_name, outlet_id, outlet_name))
        mydb.commit()
        
        new_id = cursor.lastrowid
        
        return jsonify({
            "success": True,
            "message": "Cost center created successfully",
            "data": {
                "id": new_id,
                "costcenter_name": costcenter_name,
                "outlet_id": outlet_id,
                "outlet_name": outlet_name
            }
        }), 201
        
    except mysql.connector.Error as db_error:
        return jsonify({"error": f"Database error: {str(db_error)}"}), 400
    except Exception as error:
        return jsonify({'error': str(error)}), 400
    finally:
        if mydb and mydb.is_connected():
            mydb.close()

# ------------------- GET Cost Centers by Outlet ID -------------------
@app_file230.route("/get_costcenters_by_outlet", methods=["POST"])
@cross_origin()
def get_costcenters_by_outlet():
    try:
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password')
        )
        cursor = mydb.cursor(dictionary=True)
        
        database_sql = "USE {};".format(os.getenv('database'))
        cursor.execute(database_sql)
        
        data = request.get_json()
        
        # Validate token
        token = data.get('token')
        if not token or not token_auth(token):
            return jsonify({"error": "Invalid or missing token."}), 400
        
        outlet_name = data.get('outlet_name')
        
        if not outlet_name:
            return jsonify({"error": "outlet_id is required"}), 400
        
        # Optional: Validate outlet exists
        cursor.execute("SELECT id FROM outetNames WHERE Outlet = %s", (outlet_name,))
        outlet_exists = cursor.fetchone()
        
        if not outlet_exists:
            return jsonify({"error": f"Outlet with name {outlet_name} does not exist"}), 400
        
        # Get all cost centers for the outlet
        sql = """
        SELECT id, costcenter_name, outlet_id, outlet_name 
        FROM costcenter 
        WHERE outlet_name = %s
        ORDER BY costcenter_name
        """
        
        cursor.execute(sql, (outlet_name,))
        costcenters = cursor.fetchall()
        
        if not costcenters:
            return jsonify({
                "success": True,
                "message": "No cost centers found for this outlet",
                "data": [],
                "count": 0
            }), 200
        
        # Convert datetime to string if needed
        for costcenter in costcenters:
            if 'created_at' in costcenter and costcenter['created_at']:
                costcenter['created_at'] = costcenter['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({
            "success": True,
            "data": costcenters,
            "count": len(costcenters)
        }), 200
        
    except mysql.connector.Error as db_error:
        return jsonify({"error": f"Database error: {str(db_error)}"}), 400
    except Exception as error:
        return jsonify({'error': str(error)}), 400
    finally:
        if mydb and mydb.is_connected():
            mydb.close()

# ------------------- GET Cost Center by ID -------------------
@app_file230.route("/get_costcenter_by_id", methods=["POST"])
@cross_origin()
def get_costcenter_by_id():
    try:
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password')
        )
        cursor = mydb.cursor(dictionary=True)
        
        database_sql = "USE {};".format(os.getenv('database'))
        cursor.execute(database_sql)
        
        data = request.get_json()
        
        # Validate token
        token = data.get('token')
        if not token or not token_auth(token):
            return jsonify({"error": "Invalid or missing token."}), 400
        
        costcenter_id = data.get('id')
        
        if not costcenter_id:
            return jsonify({"error": "id is required"}), 400
        
        # Get cost center by ID
        sql = "SELECT id, costcenter_name, outlet_id, outlet_name FROM costcenter WHERE id = %s"
        cursor.execute(sql, (costcenter_id,))
        costcenter = cursor.fetchone()
        
        if not costcenter:
            return jsonify({"error": "Cost center not found"}), 404
        
        # Validate that the outlet still exists (optional)
        cursor.execute("SELECT id FROM outetNames WHERE id = %s", (costcenter['outlet_id'],))
        outlet_exists = cursor.fetchone()
        costcenter['outlet_exists'] = outlet_exists is not None
        
        return jsonify({
            "success": True,
            "data": costcenter
        }), 200
        
    except mysql.connector.Error as db_error:
        return jsonify({"error": f"Database error: {str(db_error)}"}), 400
    except Exception as error:
        return jsonify({'error': str(error)}), 400
    finally:
        if mydb and mydb.is_connected():
            mydb.close()

# ------------------- UPDATE Cost Center -------------------
@app_file230.route("/update_costcenter", methods=["PUT"])
@cross_origin()
def update_costcenter():
    try:
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password')
        )
        cursor = mydb.cursor(dictionary=True)
        
        database_sql = "USE {};".format(os.getenv('database'))
        cursor.execute(database_sql)
        
        data = request.get_json()
        
        # Validate token
        token = data.get('token')
        if not token or not token_auth(token):
            return jsonify({"error": "Invalid or missing token."}), 400
        
        costcenter_id = data.get('id')
        
        if not costcenter_id:
            return jsonify({"error": "id is required"}), 400
        
        # Check if cost center exists
        cursor.execute("SELECT id, outlet_id, outlet_name FROM costcenter WHERE id = %s", (costcenter_id,))
        existing = cursor.fetchone()
        
        if not existing:
            return jsonify({"error": "Cost center not found"}), 404
        
        # Build update query dynamically
        update_fields = []
        params = []
        
        if 'costcenter_name' in data:
            update_fields.append("costcenter_name = %s")
            params.append(data['costcenter_name'])
        
        if 'outlet_id' in data or 'outlet_name' in data:
            # If updating outlet, validate both together
            new_outlet_id = data.get('outlet_id', existing['outlet_id'])
            new_outlet_name = data.get('outlet_name', existing['outlet_name'])
            
            # Validate the new outlet combination
            is_valid, message = validate_outlet(cursor, new_outlet_id, new_outlet_name)
            if not is_valid:
                return jsonify({"error": message}), 400
            
            if 'outlet_id' in data:
                update_fields.append("outlet_id = %s")
                params.append(new_outlet_id)
            
            if 'outlet_name' in data:
                update_fields.append("outlet_name = %s")
                params.append(new_outlet_name)
        
        if not update_fields:
            return jsonify({"error": "No fields to update"}), 400
        
        params.append(costcenter_id)
        sql = f"UPDATE costcenter SET {', '.join(update_fields)} WHERE id = %s"
        
        cursor.execute(sql, params)
        mydb.commit()
        
        # Get updated cost center
        cursor.execute("SELECT id, costcenter_name, outlet_id, outlet_name FROM costcenter WHERE id = %s", (costcenter_id,))
        updated_costcenter = cursor.fetchone()
        
        return jsonify({
            "success": True,
            "message": "Cost center updated successfully",
            "data": updated_costcenter
        }), 200
        
    except mysql.connector.Error as db_error:
        if mydb:
            mydb.rollback()
        return jsonify({"error": f"Database error: {str(db_error)}"}), 400
    except Exception as error:
        if mydb:
            mydb.rollback()
        return jsonify({'error': str(error)}), 400
    finally:
        if mydb and mydb.is_connected():
            mydb.close()

# ------------------- DELETE Cost Center -------------------
@app_file230.route("/delete_costcenter", methods=["POST"])
@cross_origin()
def delete_costcenter():
    try:
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password')
        )
        cursor = mydb.cursor(dictionary=True)
        
        database_sql = "USE {};".format(os.getenv('database'))
        cursor.execute(database_sql)
        
        data = request.get_json()
        
        # Validate token
        token = data.get('token')
        if not token or not token_auth(token):
            return jsonify({"error": "Invalid or missing token."}), 400
        
        costcenter_id = data.get('id')
        
        if not costcenter_id:
            return jsonify({"error": "id is required"}), 400
        
        # Check if cost center exists and get its details
        cursor.execute("SELECT id, costcenter_name, outlet_id FROM costcenter WHERE id = %s", (costcenter_id,))
        existing = cursor.fetchone()
        
        if not existing:
            return jsonify({"error": "Cost center not found"}), 404
        
        # Optional: Check if cost center is being used elsewhere before deleting
        # Add any dependency checks here if needed
        
        # Delete the cost center
        cursor.execute("DELETE FROM costcenter WHERE id = %s", (costcenter_id,))
        mydb.commit()
        
        return jsonify({
            "success": True,
            "message": f"Cost center '{existing['costcenter_name']}' deleted successfully",
            "deleted_id": costcenter_id,
            "outlet_id": existing['outlet_id']
        }), 200
        
    except mysql.connector.Error as db_error:
        if mydb:
            mydb.rollback()
        return jsonify({"error": f"Database error: {str(db_error)}"}), 400
    except Exception as error:
        if mydb:
            mydb.rollback()
        return jsonify({'error': str(error)}), 400
    finally:
        if mydb and mydb.is_connected():
            mydb.close()

# ------------------- GET ALL Cost Centers with Outlet Validation -------------------
@app_file230.route("/get_all_costcenters", methods=["POST"])
@cross_origin()
def get_all_costcenters():
    try:
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password')
        )
        cursor = mydb.cursor(dictionary=True)
        
        database_sql = "USE {};".format(os.getenv('database'))
        cursor.execute(database_sql)
        
        data = request.get_json()
        
        # Validate token
        token = data.get('token')
        if not token or not token_auth(token):
            return jsonify({"error": "Invalid or missing token."}), 400
        
        # Optional pagination
        page = data.get('page', 1)
        limit = data.get('limit', 100)
        offset = (int(page) - 1) * int(limit)
        
        # Only include valid outlets (join with outetNames)
        sql = """
        SELECT 
            c.id, 
            c.costcenter_name, 
            c.outlet_id, 
            c.outlet_name,
            c.created_at,
            CASE WHEN o.id IS NOT NULL THEN 'Active' ELSE 'Inactive' END as outlet_status
        FROM costcenter c
        LEFT JOIN outetNames o ON c.outlet_id = o.id AND c.outlet_name = o.Outlet
        ORDER BY c.outlet_name, c.costcenter_name
        LIMIT %s OFFSET %s
        """
        
        cursor.execute(sql, (int(limit), offset))
        costcenters = cursor.fetchall()
        
        # Get total count
        cursor.execute("SELECT COUNT(*) as total FROM costcenter")
        total_count = cursor.fetchone()['total']
        
        # Convert datetime to string
        for costcenter in costcenters:
            if 'created_at' in costcenter and costcenter['created_at']:
                costcenter['created_at'] = costcenter['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({
            "success": True,
            "data": costcenters,
            "pagination": {
                "current_page": int(page),
                "limit": int(limit),
                "total_count": total_count,
                "total_pages": (total_count + int(limit) - 1) // int(limit) if total_count > 0 else 0
            },
            "count": len(costcenters)
        }), 200
        
    except mysql.connector.Error as db_error:
        return jsonify({"error": f"Database error: {str(db_error)}"}), 400
    except Exception as error:
        return jsonify({'error': str(error)}), 400
    finally:
        if mydb and mydb.is_connected():
            mydb.close()