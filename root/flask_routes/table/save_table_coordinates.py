from flask import Blueprint, request, jsonify
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv
from root.auth.check import token_auth

load_dotenv()
app_file211 = Blueprint('app_file211', __name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('host'),
        user=os.getenv('user'),
        password=os.getenv('password'),
        database=os.getenv('database')
    )

@app_file211.route("/save-table-coordinates", methods=["POST"])
@cross_origin()
def save_table_coordinates():
    try:
        data = request.get_json()

        # --- Token Validation ---
        if "token" not in data or not data["token"]:
            return {"error": "No token provided."}, 400

        if not token_auth(data["token"]):
            return {"error": "Invalid token."}, 400

        # --- Required Fields ---
        if "outlet_name" not in data:
            return {"error": "outlet_name is required."}, 400

        if "tables" not in data or not isinstance(data["tables"], list):
            return {"error": "tables array is required."}, 400

        outlet_name = data["outlet_name"]
        tables = data["tables"]

        if len(tables) == 0:
            return {"error": "tables array cannot be empty."}, 400

        # --- Prepare Insert Values ---
        values = []
        for table in tables:
            if not all(k in table for k in ("table_no", "x_coordinate", "y_coordinate")):
                return {"error": "Each table must have table_no, x_coordinate, y_coordinate."}, 400

            values.append((
                outlet_name,
                table["table_no"],
                table["x_coordinate"],
                table["y_coordinate"]
            ))

        mydb = get_db_connection()
        cursor = mydb.cursor()

        # --- TRANSACTION START ---
        mydb.start_transaction()

        # --- DELETE OLD LAYOUT ---
        delete_sql = """
            DELETE FROM tbl_table_coordinates
            WHERE outlet_name = %s
        """
        cursor.execute(delete_sql, (outlet_name,))

        # --- INSERT NEW LAYOUT ---
        insert_sql = """
            INSERT INTO tbl_table_coordinates
                (outlet_name, table_no, x_coordinate, y_coordinate)
            VALUES (%s, %s, %s, %s)
        """
        cursor.executemany(insert_sql, values)

        # --- COMMIT ---
        mydb.commit()

        cursor.close()
        mydb.close()

        return jsonify({
            "message": "Table layout replaced successfully",
            "outlet_name": outlet_name,
            "tables_saved": len(values)
        }), 200

    except Exception as error:
        try:
            mydb.rollback()
        except:
            pass
        return {"error": str(error)}, 500
