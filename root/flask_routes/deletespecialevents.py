from flask import Blueprint, request, jsonify
import mysql.connector
from flask_cors import CORS, cross_origin
import os
from dotenv import load_dotenv

load_dotenv()

app_file83 = Blueprint('app_file83', __name__)

@app_file83.route("/deletespecialevents", methods=['POST'])
@cross_origin()
def delete_special_event():
    try:
        # Connect to the database
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password'),
            database=os.getenv('database')
        )
        cursor = mydb.cursor(buffered=True)

        # Get JSON data from request
        data = request.get_json()
        print(data)
        specialevent_id = data.get("specialevent_id")

        if specialevent_id is None:
            return jsonify({"error": "specialevent_id is required"}), 400

        # Check if the event exists
        check_sql = "SELECT COUNT(*) FROM tblevents WHERE id = %s"
        cursor.execute(check_sql, (specialevent_id,))
        event_count = cursor.fetchone()[0]

        if event_count == 0:
            return jsonify({"message": "No data found"}), 404

        # Delete the event
        delete_sql = "DELETE FROM tblevents WHERE id = %s"
        cursor.execute(delete_sql, (specialevent_id,))
        mydb.commit()

        return jsonify({"message": "Special event deleted successfully"}), 200

    except Exception as error:
        return jsonify({"error": str(error)}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'mydb' in locals():
            mydb.close()
