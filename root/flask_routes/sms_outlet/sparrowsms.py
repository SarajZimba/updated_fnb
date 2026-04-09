from flask import  Blueprint,request
import mysql.connector
from flask_cors import  cross_origin
import os
from dotenv import load_dotenv
load_dotenv()
app_file202 = Blueprint('app_file202',__name__)
from root.auth.check import token_auth
from root.flask_routes.send_message import get_credit_sparrow

@app_file202.route("/sparrow-credit", methods=["POST"])
@cross_origin()
def sparrow_credit():
    try:
        data = request.get_json()

        # Input validation
        if not data:
            return {"error": "Missing JSON body"}, 400

        if "token" not in data or not data["token"]:
            return {"error": "No token provided."}, 400

        # Validate token
        token = data["token"]
        if not token_auth(token):
            return {"error": "Invalid token."}, 400

        # Fetch sparrow credits
        result = get_credit_sparrow()

        return result, 200

    except Exception as e:
        return {"error": str(e)}, 500



