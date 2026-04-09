# from flask import Blueprint, jsonify, request
# import mysql.connector
# import os
# from dotenv import load_dotenv

# load_dotenv()

# email_history_bp = Blueprint("email_history", __name__)

# def get_db():
#     """Create and return a new DB connection."""
#     return mysql.connector.connect(
#         host=os.getenv("host"),
#         user=os.getenv("user"),
#         password=os.getenv("password"),
#         database=os.getenv("database")
#     )

# @email_history_bp.route("/email-history", methods=["GET"])
# def get_email_history():
#     """
#     Fetch all email history records (with optional pagination)
#     GET /email-history?page=1&limit=20
#     """
#     try:
#         page = int(request.args.get("page", 1))
#         limit = int(request.args.get("limit", 50))
#         offset = (page - 1) * limit

#         db = get_db()
#         cursor = db.cursor(dictionary=True)

#         cursor.execute("""
#             SELECT 
#                 id,
#                 org,
#                 subject,
#                 html,
#                 from_name,
#                 sample_size,
#                 total_sent,
#                 sent_at
#             FROM email_history
#             ORDER BY sent_at DESC
#             LIMIT %s OFFSET %s
#         """, (limit, offset))

#         rows = cursor.fetchall()

#         cursor.execute("SELECT COUNT(*) AS total FROM email_history")
#         total_records = cursor.fetchone()["total"]

#         cursor.close()
#         db.close()

#         return jsonify({
#             "success": True,
#             "page": page,
#             "limit": limit,
#             "total_records": total_records,
#             "data": rows
#         }), 200

#     except Exception as e:
#         return jsonify({"success": False, "error": str(e)}), 500


from flask import Blueprint, jsonify
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

email_history_bp = Blueprint("email_history", __name__)

def get_db():
    """Create and return a new DB connection."""
    return mysql.connector.connect(
        host=os.getenv("host"),
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )

@email_history_bp.route("/email-history", methods=["GET"])
def get_email_history():
    """
    Fetch ALL email history records (no limit).
    GET /email-history
    """
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                id,
                org,
                subject,
                html,
                from_name,
                sample_size,
                total_sent,
                sent_at
            FROM email_history
            ORDER BY sent_at DESC
        """)

        rows = cursor.fetchall()

        cursor.close()
        db.close()

        return jsonify({
            "success": True,
            "count": len(rows),
            "data": rows
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
