from flask import Blueprint, request, jsonify
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv
from decimal import Decimal
load_dotenv()
app_file75 = Blueprint('app_file75', __name__)
from datetime import datetime

@app_file75.route("/posteventdata", methods=["POST"])
@cross_origin()

def stats():
    try:
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password'),
            database=os.getenv('database')
        )
        cursor = mydb.cursor(buffered=True)



        data = request.get_json()
        event = data.get("event")
        thisyeardate = data.get("thisyeardate")  # Expected format: 'YYYY-MM-DD'
        lastyeardate = data.get("lastyeardate")  # Expected format: 'YYYY-MM-DD'
        outlet = data.get("outlet")  
        # Get current year
        current_year = datetime.today().year
        previous_year = current_year - 1

        # Convert the dates to datetime objects
        try:
            thisyeardate_obj = datetime.strptime(thisyeardate, "%Y-%m-%d")
            lastyeardate_obj = datetime.strptime(lastyeardate, "%Y-%m-%d")
        except ValueError:
            return jsonify({"error": "Invalid date format. Please use 'YYYY-MM-DD'."}), 400

        # Check if lastyeardate is greater than thisyeardate
        if lastyeardate_obj > thisyeardate_obj:
            return jsonify({"error": "lastyeardate cannot be greater than thisyeardate."}), 400

        # Validate lastyeardate must be from the previous year
        if lastyeardate_obj.year != previous_year:
            return jsonify({"error": f"lastyeardate must be from the year {previous_year}."}), 400

        # Validate thisyeardate must be from the current year
        if thisyeardate_obj.year != current_year:
            return jsonify({"error": f"thisyeardate must be from the year {current_year}."}), 400



        sql = "INSERT INTO tblevents (event, thisyeardate, lastyeardate, outlet) VALUES (%s, %s, %s, %s)"
        values = (event, thisyeardate, lastyeardate, outlet)

        cursor.execute(sql, values)
        
        mydb.commit()
        cursor.close()
        mydb.close()
        return ({"message": "Event added successfully!"}), 201

    except Exception as e:
        return {"error": str(e)}, 500