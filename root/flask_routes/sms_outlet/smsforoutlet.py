from flask import  Blueprint,request
import mysql.connector
from flask_cors import  cross_origin
import os
from dotenv import load_dotenv
load_dotenv()
app_file201 = Blueprint('app_file201',__name__)
from root.auth.check import token_auth



@app_file201.route("/update-sms-template", methods=["POST"])
@cross_origin()
def update_sms_template():
    try:
        data = request.get_json()

        # Validate input
        if not data:
            return {"error": "Missing JSON body"}, 400

        outlet_name = data.get("outlet_name")
        sms_text = data.get("sms_text")

        if not outlet_name or not sms_text:
            return {"error": "Both 'outlet_name' and 'sms_text' are required"}, 400
        
        if "token" not in data  or not any([data["token"]])  or data["token"]=="":
            data = {"error":"No token provided."}
            return data,400
        token = data["token"]
        if not token_auth(token):
            data = {"error":"Invalid token."}
            return data,400

        # Connect DB
        mydb = mysql.connector.connect(
            host=os.getenv("host"),
            user=os.getenv("user"),
            password=os.getenv("password"),
        )
        cursor = mydb.cursor(buffered=True)
        cursor.execute("USE {};".format(os.getenv("database")))

        # Check if outlet exists
        cursor.execute(
            "SELECT Outlet FROM outetNames WHERE Outlet = %s LIMIT 1",
            (outlet_name,)
        )
        row = cursor.fetchone()

        if not row:
            return {"error": f"Outlet '{outlet_name}' not found"}, 404

        # Update query
        cursor.execute(
            "UPDATE outetNames SET sms_text = %s WHERE Outlet = %s",
            (sms_text, outlet_name)
        )
        mydb.commit()
        mydb.close()

        return {"success": f"SMS template updated for {outlet_name}"}, 200

    except Exception as e:
        return {"error": str(e)}, 500


@app_file201.route("/clear-sms-template", methods=["POST"])
@cross_origin()
def clear_sms_template():
    try:
        data = request.get_json()

        if not data:
            return {"error": "Missing JSON body"}, 400

        outlet_name = data.get("outlet_name")

        if not outlet_name:
            return {"error": "'outlet_name' is required"}, 400

        # Token validation
        if "token" not in data or not data["token"]:
            return {"error": "No token provided."}, 400
        
        token = data["token"]
        if not token_auth(token):
            return {"error":"Invalid token."}, 400

        # Connect DB
        mydb = mysql.connector.connect(
            host=os.getenv("host"),
            user=os.getenv("user"),
            password=os.getenv("password"),
        )
        cursor = mydb.cursor(buffered=True)
        cursor.execute("USE {};".format(os.getenv("database")))

        # Check if outlet exists
        cursor.execute(
            "SELECT Outlet FROM outetNames WHERE Outlet = %s LIMIT 1",
            (outlet_name,)
        )
        row = cursor.fetchone()

        if not row:
            return {"error": f"Outlet '{outlet_name}' not found"}, 404

        # Clear/Reset the template
        cursor.execute(
            "UPDATE outetNames SET sms_text = NULL WHERE Outlet = %s",
            (outlet_name,)
        )
        mydb.commit()
        mydb.close()

        return {"success": f"SMS template cleared for {outlet_name}"}, 200

    except Exception as e:
        return {"error": str(e)}, 500


@app_file201.route("/get-sms-template", methods=["POST"])
@cross_origin()
def get_sms_template():
    try:
        data = request.get_json()

        if not data:
            return {"error": "Missing JSON body"}, 400

        outlet_name = data.get("outlet_name")

        if not outlet_name:
            return {"error": "'outlet_name' is required"}, 400

        # Token validation
        if "token" not in data or not data["token"]:
            return {"error": "No token provided."}, 400
        
        token = data["token"]
        if not token_auth(token):
            return {"error":"Invalid token."}, 400

        mydb = mysql.connector.connect(
            host=os.getenv("host"),
            user=os.getenv("user"),
            password=os.getenv("password"),
        )
        cursor = mydb.cursor(buffered=True)
        cursor.execute("USE {};".format(os.getenv("database")))

        cursor.execute(
            "SELECT sms_text FROM outetNames WHERE Outlet = %s LIMIT 1",
            (outlet_name,)
        )
        row = cursor.fetchone()

        mydb.close()

        if not row:
            return {"error": f"Outlet '{outlet_name}' not found"}, 404

        return {"sms_text": row[0] or ""}, 200

    except Exception as e:
        return {"error": str(e)}, 500
