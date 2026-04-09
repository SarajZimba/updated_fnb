
from flask import Blueprint, jsonify, request
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime

app_file79 = Blueprint('app_file79', __name__)

@app_file79.route("/getspecialevents", methods=["POST"])
@cross_origin()
def get_stocks_by_group():
    try:
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password')
        )
        cursor = mydb.cursor(buffered=True)
        database_sql = "USE {};".format(os.getenv('database'))
        cursor.execute(database_sql)

        data = request.get_json()
        outlet_name = data.get("outlet", "")
        
        today_date_str = datetime.today().strftime('%Y-%m-%d')
        # Fetch special dates from database
        special_dates_query = """SELECT * FROM tblevents where `thisyeardate` > %s and outlet = %s order by `thisyeardate` limit 10"""
        cursor.execute(special_dates_query, (today_date_str,outlet_name,))

        # data = request.get_json()
        # Process special dates into a dictionary list
        results = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        special_date_data = [dict(zip(column_names, row)) for row in results]

        data = {"events": special_date_data}
        return jsonify(data), 200

    except mysql.connector.Error as db_error:
        return jsonify({"error": f"Database error: {str(db_error)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
    finally:
        if mydb:
            mydb.close()


