from flask import Blueprint, jsonify, request
import mysql.connector
import os
from dotenv import load_dotenv
from flask_cors import cross_origin
from decimal import Decimal
from root.auth.check import token_auth

load_dotenv()

app_file113 = Blueprint('app_file113', __name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("host"),
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )

@app_file113.route("/get-menu-item", methods=["POST"])
@cross_origin()
def get_menu_item():
    try:
        data = request.get_json()
        token = data.get("token")
        menu_name = data.get("name")
        restaurant = data.get("restaurant")
        
        # Token validation
        if not token or not token_auth(token):
            return jsonify({"error": "Invalid or missing token."}), 400
            
        if not menu_name:
            return jsonify({"error": "Menu name is required."}), 400

        if not restaurant:
            return jsonify({"error": "Restaurant is required."}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT 
                idtblMenu,
                Name,
                Description,
                Type,
                Price,
                Restaurant,
                state,
                discountExempt,
                serviceChargeExempt
            FROM tblmenu
            WHERE Name = %s AND Restaurant = %s
        """
        cursor.execute(query, (menu_name, restaurant))

        menu_item = cursor.fetchone()
        
        cursor.close()
        conn.close()

        if not menu_item:
            return jsonify({
                "error": "Menu item not found for the specified restaurant.",
                "details": f"No item named '{menu_name}' found in '{restaurant}'"
            }), 404

        # Convert Decimal to float for JSON serialization
        if 'Price' in menu_item and isinstance(menu_item['Price'], Decimal):
            menu_item['Price'] = float(menu_item['Price'])

        return jsonify(menu_item), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500