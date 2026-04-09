from flask import Flask, Blueprint, request, jsonify
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv
from root.auth.check import token_auth
from datetime import datetime
from root.utils.getoutletwisedailymonthforecast import getmonthlysaleForecastdatewise
load_dotenv()

app_file86 = Blueprint('appfile_86', __name__)

@app_file86.route('/getmonthlytrackforecast', methods=["POST"])
@cross_origin()
def getmonthlytrackprediction():

    json = request.get_json()
    if "token" not in json  or not any([json["token"]])  or json["token"]=="":
        data = {"error":"No token provided."}
        return data,400

    token = json["token"]



    if not token_auth(token):
        data = {"error":"Invalid token."}
        return data,400
    try:
        results = getmonthlysaleForecastdatewise()

        return jsonify(results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

