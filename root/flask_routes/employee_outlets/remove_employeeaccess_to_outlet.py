from flask import Blueprint, request
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv
load_dotenv()

app_file221 = Blueprint('app_file221', __name__)
from root.auth.check import token_auth

@app_file221.route("/toggle_employee_outlet", methods=["POST"])
@cross_origin()
def toggle_employee_outlet():
    try:
        json_data = request.get_json()

        # Validate token
        if "token" not in json_data or not json_data["token"].strip():
            return {"error": "No token provided."}, 400
        token = json_data["token"]
        if not token_auth(token):
            return {"error": "Invalid token."}, 400

        # Validate employee_outlet_id
        if "employee_outlet_id" not in json_data or not json_data["employee_outlet_id"]:
            return {"error": "No employee_outlet_id provided."}, 400
        employee_outlet_id = json_data["employee_outlet_id"]

        # Connect to DB
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password')
        )
        cursor = mydb.cursor(buffered=True)
        cursor.execute(f"USE {os.getenv('database')}")

        # Toggle status using NOT operator
        cursor.execute("""
            UPDATE employeeoutlets
            SET status = NOT status
            WHERE id = %s
        """, (employee_outlet_id,))
        mydb.commit()

        # Optional: return the new status
        cursor.execute("SELECT status FROM employeeoutlets WHERE id = %s", (employee_outlet_id,))
        new_status = cursor.fetchone()[0]
        mydb.close()

        return {"message": "Employee outlet access toggled successfully", "new_status": bool(new_status)}, 200

    except Exception as e:
        return {"error": str(e)}, 400