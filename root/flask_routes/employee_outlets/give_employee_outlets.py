from flask import Blueprint, request
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv
load_dotenv()

app_file220 = Blueprint('app_file220', __name__)
from root.auth.check import token_auth

@app_file220.route("/employee_outlets", methods=["POST"])
@cross_origin()
def employee_outlets():
    try:
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password')
        )
        cursor = mydb.cursor(buffered=True)
        cursor.execute(f"USE {os.getenv('database')}")

        json_data = request.get_json()

        # Validate token
        if "token" not in json_data or not json_data["token"].strip():
            return {"error": "No token provided."}, 400
        token = json_data["token"]
        if not token_auth(token):
            return {"error": "Invalid token."}, 400

        # Validate employee_id
        if "employee_id" not in json_data or not json_data["employee_id"]:
            return {"error": "No employee_id provided."}, 400
        employee_id = json_data["employee_id"]

        # Get all outlets assigned to this employee including status
        cursor.execute("""
            SELECT eo.id AS employee_outlet_id, eo.status, 
                   o.id AS outlet_id, o.Outlet, o.Company_name, o.address, o.logo
            FROM employeeoutlets eo
            JOIN outetNames o ON eo.outlet_id = o.id
            WHERE eo.employee_id = %s
        """, (employee_id,))
        result = cursor.fetchall()

        if not result:
            return {"error": "No outlets assigned to this employee."}, 400

        # Build JSON response
        row_headers = [x[0] for x in cursor.description]
        response_json = []
        for row in result:
            outlet = dict(zip(row_headers, row))
            outlet_json = {
                "employee_outlet_id": outlet["employee_outlet_id"],
                "status": bool(outlet["status"]),  # convert 0/1 to boolean
                "id": outlet["outlet_id"],
                "name": outlet["Outlet"],
                "company": outlet["Company_name"],
                "address": outlet["address"],
                "logo": outlet["logo"],
            }
            response_json.append(outlet_json)

        mydb.close()
        return {"outlets": response_json}, 200

    except Exception as e:
        return {"error": str(e)}, 400