from flask import Flask, request, jsonify, Blueprint
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()

app_file47 = Blueprint('app_file47', __name__)

@app_file47.route("/getlatestsyncdate", methods=["POST"])
@cross_origin()
def get_latest_sync_date():
    try:
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password'),
        )
        cursor = mydb.cursor(buffered=True)
        database_sql = "USE {};".format(os.getenv('database'))
        cursor.execute(database_sql)

        # Check if the organization table has rows
        # sql_check = "SELECT last_synced FROM organization LIMIT 1"
        # cursor.execute(sql_check)
        # result = cursor.fetchone()
        data = request.get_json()

        if "outlet_name" not in data or data["outlet_name"] == "":
            return jsonify({"error": "please provide the outlet_name"}), 400
        outlet_name = data["outlet_name"]

        # Check if the organization table has rows
        sql_check = "SELECT last_synced FROM organization where outlet_name = %s LIMIT 1"
        cursor.execute(sql_check, (outlet_name,))
        result = cursor.fetchone()

        if result is None:
            # No rows in the organization table
            return jsonify({"last_synced": None}), 200
        else:
            # Return the datetime of the first row
            return jsonify({"last_synced": datetime.strftime(result[0], "%Y-%m-%d %I:%M:%S %p")}), 200

    except mysql.connector.Error as db_error:
        return jsonify({"error": f"Database error: {str(db_error)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
    finally:
        if mydb:
            mydb.close()
