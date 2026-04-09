from flask import Blueprint, request, jsonify
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv
import uuid
from root.auth.check import token_auth
load_dotenv()
app_file101 = Blueprint('app_file101', __name__)

# DB Connection
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('host'),
        user=os.getenv('user'),
        password=os.getenv('password'),
        database=os.getenv('database')
    )

# ---------------- LOGIN ------------------
@app_file101.route("/counter-login", methods=["POST"])
@cross_origin()
def login():
    try:
        data = request.get_json()
        if "username" not in data or "password" not in data:
            return {"error": "Missing fields"}, 400

        username = data["username"]
        password = data["password"]

        if username == "" or password == "":
            return {"error": "Empty fields not allowed"}, 400

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "SELECT Token, type, outlet, userName FROM tblcounteruser WHERE userName = %s AND Password = %s",
            (username, password)
        )
        user = cursor.fetchone()
        cursor.close()
        db.close()

        if not user:
            return {"error": "Invalid credentials"}, 400

        return {"token": user["Token"], "type": user["type"], "outlet": user["outlet"], "username": user["userName"]}, 200


    except Exception as e:
        return {"error": str(e)}, 400

# ---------------- REGISTER ------------------
@app_file101.route("/counter-register", methods=["POST"])
@cross_origin()
def register():
    try:
        data = request.get_json()
        required_fields = ["username", "password", "type", "outlet"]
        if not all(field in data and data[field] for field in required_fields):
            return {"error": "Missing or empty required fields"}, 400

        username = data["username"]
        password = data["password"]
        token = "test"
        user_type = data["type"]
        outlet = data["outlet"]

        db = get_db_connection()
        cursor = db.cursor()

        # Check if username already exists
        cursor.execute("SELECT id FROM tblcounteruser WHERE userName = %s", (username,))
        if cursor.fetchone():
            cursor.close()
            db.close()
            return {"error": "Username already exists. Please choose a different username."}, 409

        # Insert new user
        cursor.execute(
            "INSERT INTO tblcounteruser (userName, Password, Token, type, outlet) VALUES (%s, %s, %s, %s, %s)",
            (username, password, token, user_type, outlet)
        )
        db.commit()
        cursor.close()
        db.close()

        return {"success": "User registered successfully"}, 201

    except Exception as e:
        return {"error": str(e)}, 400


# ---------------- UPDATE ------------------
@app_file101.route("/counter-update", methods=["PUT"])
@cross_origin()
def update():
    try:
        data = request.get_json()
        username = data.get("username")

        if not username:
            return {"error": "Current username required"}, 400

        updates = []
        values = []

        if "new_username" in data and data["new_username"]:
            updates.append("userName = %s")
            values.append(data["new_username"])
        if "new_password" in data and data["new_password"]:
            updates.append("Password = %s")
            values.append(data["new_password"])
        if "new_type" in data and data["new_type"]:
            updates.append("type = %s")
            values.append(data["new_type"])
        if "new_outlet" in data and data["new_outlet"]:
            updates.append("outlet = %s")
            values.append(data["new_outlet"])

        if not updates:
            return {"error": "No valid fields to update"}, 400

        values.append(username)

        db = get_db_connection()
        cursor = db.cursor()
        sql = f"UPDATE tblcounteruser SET {', '.join(updates)} WHERE userName = %s"
        cursor.execute(sql, tuple(values))
        db.commit()
        cursor.close()
        db.close()

        return {"success": "User updated successfully"}, 200

    except Exception as e:
        return {"error": str(e)}, 400

# ---------------- DELETE ------------------
@app_file101.route("/counter-delete", methods=["DELETE"])
@cross_origin()
def delete():
    try:
        data = request.get_json()
        username = data.get("username")
        if not username:
            return {"error": "Username is required"}, 400

        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("DELETE FROM tblcounteruser WHERE userName = %s", (username,))
        db.commit()
        cursor.close()
        db.close()

        if cursor.rowcount == 0:
            return {"error": "User not found"}, 404

        return {"success": "User deleted successfully"}, 200

    except Exception as e:
        return {"error": str(e)}, 400
    
# ---------------- GET all users ------------------
@app_file101.route("/counter-userlists", methods=["POST"])
@cross_origin()
def get():
    try:
        data = request.get_json()
        token = data.get("token")
        if not token:
            return {"error": "token is required"}, 400
        if not token or not token_auth(token):
            return jsonify({'error': 'Invalid or missing token'}), 400
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)  # Use dictionary cursor for better JSON response
        cursor.execute("SELECT userName, type, outlet, Password FROM tblcounteruser")

        users = cursor.fetchall()
        db.commit()
        cursor.close()
        db.close()

        if cursor.rowcount == 0:
            return {"error": "User not found"}, 404

        return {"data": users }, 200

    except Exception as e:
        return {"error": str(e)}, 400
