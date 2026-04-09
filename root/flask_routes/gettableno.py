# from flask import Blueprint, request, jsonify
# import mysql.connector
# from flask_cors import cross_origin
# import os
# from dotenv import load_dotenv
# from root.auth.check import token_auth

# load_dotenv()
# app_file210 = Blueprint('app_file210', __name__)

# def get_db_connection():
#     return mysql.connector.connect(
#         host=os.getenv('host'),
#         user=os.getenv('user'),
#         password=os.getenv('password'),
#         database=os.getenv('database')
#     )

# @app_file210.route("/get-tables-by-outlet", methods=["POST"])
# @cross_origin()
# def get_tables_by_outlet():
#     try:
#         data = request.get_json()

#         # --- Token Validation ---
#         if "token" not in data or not data["token"]:
#             return {"error": "No token provided."}, 400

#         if not token_auth(data["token"]):
#             return {"error": "Invalid token."}, 400

#         # --- Required Field ---
#         if "outlet_name" not in data or not data["outlet_name"]:
#             return {"error": "outlet_name is required."}, 400

#         outlet_name = data["outlet_name"]

#         mydb = get_db_connection()
#         cursor = mydb.cursor(dictionary=True)

#         # --- FETCH ONLY TABLES WITHOUT COORDINATES ---
#         sql = """
#             SELECT DISTINCT oh.Table_No
#             FROM tblorderhistory oh
#             LEFT JOIN tbl_table_coordinates tc
#                 ON tc.outlet_name = oh.Outlet_Name
#                AND tc.table_no = oh.Table_No
#             WHERE oh.Outlet_Name = %s and TRIM(oh.bill_no) != ''
#               AND tc.table_no IS NULL
#             ORDER BY oh.Table_No
#         """
#         cursor.execute(sql, (outlet_name,))
#         tables = cursor.fetchall()

#         cursor.close()
#         mydb.close()

#         return jsonify({
#             "outlet_name": outlet_name,
#             "tables": tables
#         }), 200

#     except Exception as error:
#         return {"error": str(error)}, 500

from flask import Blueprint, request, jsonify
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv
from root.auth.check import token_auth

load_dotenv()

app_file210 = Blueprint('app_file210', __name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('host'),
        user=os.getenv('user'),
        password=os.getenv('password'),
        database=os.getenv('database'),
        autocommit=True
    )

@app_file210.route("/get-tables-by-outlet", methods=["POST"])
@cross_origin()
def get_tables_by_outlet():
    cursor = None
    mydb = None

    try:
        # ---------- SAFE JSON ----------
        data = request.get_json(silent=True)
        if not data:
            return {"error": "Invalid JSON body"}, 400

        # ---------- TOKEN ----------
        token = data.get("token")
        if not token:
            return {"error": "No token provided."}, 400
        if not token_auth(token):
            return {"error": "Invalid token."}, 400

        # ---------- REQUIRED FIELD ----------
        outlet_name = data.get("outlet_name")
        if not outlet_name:
            return {"error": "outlet_name is required."}, 400

        # ---------- DB ----------
        mydb = get_db_connection()
        cursor = mydb.cursor(dictionary=True)

        # ---------- OPTIMIZED SQL ----------
        # Filters empty tables in DB itself (fast)
        sql = """
            SELECT DISTINCT oh.Table_No
            FROM tblorderhistory oh
            LEFT JOIN tbl_table_coordinates tc
                ON tc.outlet_name = oh.Outlet_Name
               AND tc.table_no = oh.Table_No
            WHERE oh.Outlet_Name = %s
              AND oh.bill_no IS NOT NULL
              AND TRIM(oh.bill_no) <> ''
              AND oh.Table_No IS NOT NULL
              AND TRIM(oh.Table_No) <> ''
              AND tc.table_no IS NULL
            ORDER BY CAST(oh.Table_No AS UNSIGNED), oh.Table_No
        """

        cursor.execute(sql, (outlet_name,))
        rows = cursor.fetchall()

        # ---------- PYTHON FINAL CLEAN ----------
        # Extra protection if DB contains strange values
        cleaned_tables = []
        seen = set()

        for r in rows:
            table = str(r.get("Table_No", "")).strip()

            # remove empty / weird values again
            if not table:
                continue

            # optional: remove non-visible characters
            table = table.replace('\u200b', '')

            # avoid duplicates
            if table in seen:
                continue
            seen.add(table)

            cleaned_tables.append({"Table_No": table})

        # ---------- RETURN ----------
        return jsonify({
            "outlet_name": outlet_name,
            "tables": cleaned_tables
        }), 200

    except mysql.connector.Error as db_error:
        return {"error": f"Database error: {str(db_error)}"}, 500

    except Exception as error:
        return {"error": str(error)}, 500

    finally:
        if cursor:
            cursor.close()
        if mydb:
            mydb.close()