# from flask import Blueprint, jsonify, request
# import mysql.connector
# import os
# from dotenv import load_dotenv
# from flask_cors import cross_origin
# # Token validation — call your existing function
# from root.auth.check import token_auth
# load_dotenv()

# app_file205 = Blueprint("app_file205", __name__)

# def get_db():
#     return mysql.connector.connect(
#         host=os.getenv("host"),
#         user=os.getenv("user"),
#         password=os.getenv("password"),
#         database=os.getenv("database")
#     )

# @app_file205.route("/sms-history", methods=["POST"])
# @cross_origin()
# def sms_history():
#     try:
#         data = request.get_json()

#         if not data:
#             return jsonify({"error": "Missing JSON body"}), 400

#         token = data.get("token")

#         if not token:
#             return jsonify({"error": "token is required"}), 400

#         # Validate token
#         if not token_auth(token):
#             return jsonify({"error": "Invalid token"}), 403

#         db = get_db()
#         cursor = db.cursor(dictionary=True)

#         cursor.execute("""
#             SELECT 
#                 id,
#                 task_id,
#                 sender_name,
#                 message_text,
#                 total_numbers,
#                 numbers_sent,
#                 created_at
#             FROM sms_history
#             ORDER BY id DESC
#         """)

#         rows = cursor.fetchall()
#         cursor.close()
#         db.close()

#         return jsonify({
#             "success": True,
#             "count": len(rows),
#             "data": rows
#         }), 200

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


from flask import Blueprint, jsonify, request
import mysql.connector
import os
from dotenv import load_dotenv
from flask_cors import cross_origin
from root.auth.check import token_auth
from datetime import datetime
import pytz

load_dotenv()
app_file205 = Blueprint("app_file205", __name__)

def get_db():
    return mysql.connector.connect(
        host=os.getenv("host"),
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )

@app_file205.route("/sms-history", methods=["POST"])
@cross_origin()
def sms_history():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing JSON body"}), 400

        token = data.get("token")
        if not token:
            return jsonify({"error": "token is required"}), 400

        if not token_auth(token):
            return jsonify({"error": "Invalid token"}), 403

        # -----------------------------
        # Date range filter
        # -----------------------------
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        nepal_tz = pytz.timezone("Asia/Kathmandu")
        today = datetime.now(nepal_tz).date()

        date_filter = ""
        params = []

        if start_date and end_date:
            date_filter = "WHERE DATE(created_at) BETWEEN %s AND %s"
            params.extend([start_date, end_date])
        else:
            # default to today's SMS
            date_filter = "WHERE DATE(created_at) = %s"
            params.append(today)

        # -----------------------------
        # Fetch SMS history
        # -----------------------------
        db = get_db()
        cursor = db.cursor(dictionary=True)

        sql = f"SELECT * FROM sms_history {date_filter} ORDER BY created_at DESC"
        cursor.execute(sql, params)
        rows = cursor.fetchall()

        # -----------------------------
        # Separate system and other senders
        # -----------------------------
        system_entries = []
        other_senders = {}
        total_system_numbers = 0

        for row in rows:
            if row["sender_name"] == "System":
                system_entries.append(row)
                total_system_numbers += row["total_numbers"]
            else:
                sender = row["sender_name"]
                if sender not in other_senders:
                    other_senders[sender] = {
                        "entries": [],
                        "total_numbers": 0
                    }
                other_senders[sender]["entries"].append(row)
                other_senders[sender]["total_numbers"] += row["total_numbers"]

        cursor.close()
        db.close()

        # -----------------------------
        # Simplified response
        # -----------------------------
        response = {
            "success": True,
            "system_total_numbers": total_system_numbers,
            "system_entries": system_entries,
            "outlets": [
                {
                    "sender_name": sender,
                    "total_numbers": info["total_numbers"],
                    "entries": info["entries"]
                }
                for sender, info in other_senders.items()
            ]
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

