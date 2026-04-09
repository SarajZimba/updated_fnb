# from flask import Blueprint, jsonify, request
# import mysql.connector
# import os
# from flask_cors import cross_origin
# from dotenv import load_dotenv
# from root.auth.check import token_auth
# from datetime import datetime, timedelta
# app_file89 = Blueprint('app_file89',__name__)

# @app_file89.route('/debtors-summary', methods=['POST'])

# @cross_origin()
# def debtorssummary():
#     try:
#         mydb = mysql.connector.connect(host=os.getenv('host'), user=os.getenv('user'), password=os.getenv('password'))
#         cursor = mydb.cursor(buffered=True)
#         database_sql = "USE {};".format(os.getenv('database'))
#         cursor.execute(database_sql)
#         json = request.get_json()
#         if "token" not in json  or not any([json["token"]])  or json["token"]=="":
#             data = {"error":"No token provided."}
#             return data,400

#         token = json["token"]
#         if not token_auth(token):
#             data = {"error":"Invalid token."}
#         if "outlet" not in json  or not any([json["outlet"]])  or json["outlet"]=="":
#             data = {"error":"No outlet provided."}
#             return data,400

#         outlet = json["outlet"]

#         # Define time ranges
#         today = datetime.today()
#         ranges = {
#             "0-30 days": (today - timedelta(days=30), today),
#             "31-60 days": (today - timedelta(days=60), today - timedelta(days=31)),
#             "61-90 days": (today - timedelta(days=90), today - timedelta(days=61)),
#             "91-180 days": (today - timedelta(days=180), today - timedelta(days=91)),
#             "181-365 days": (today - timedelta(days=365), today - timedelta(days=181)),
#             "366+ days": (None, today - timedelta(days=366))
#         }

#         # Query template
#         query_template = """
#         SELECT a.customerName,a.guestID,SUM(CASE WHEN a.creditState = 'InitialEntry' THEN a.Amount ELSE 0 END) AS InitialTotal,SUM(CASE WHEN a.creditState = 'Payment' THEN a.Amount ELSE 0 END) AS PaymentTotal 
#         FROM CreditHistory a WHERE a.outetName = %s AND a.Date BETWEEN %s AND %s 
#         GROUP BY a.guestID, a.customerName;
#         """

#         results = {}

#         for label, (start_date, end_date) in ranges.items():
#             print(start_date)
#             if start_date:
#                 cursor.execute(query_template, (outlet, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'),))
#             else:
#                 cursor.execute(query_template, (outlet, '1900-01-01', end_date.strftime('%Y-%m-%d')),)  # Handle 366+ days

#             data = cursor.fetchall()
#             results[label] = data

#         cursor.close()
#         mydb.close()


#         return results,200
#     except Exception as error:
#         data ={'error':str(error)}
#         return data,400

# from flask import Blueprint, jsonify, request
# import mysql.connector
# import os
# from flask_cors import cross_origin
# from dotenv import load_dotenv
# from root.auth.check import token_auth
# from datetime import datetime, timedelta

# app_file90 = Blueprint('app_file90', __name__)

# @app_file90.route('/debtors-summary', methods=['POST'])
# @cross_origin()
# def debtorssummary():
#     try:
#         mydb = mysql.connector.connect(
#             host=os.getenv('host'),
#             user=os.getenv('user'),
#             password=os.getenv('password'),
#             database=os.getenv('database')
#         )
#         cursor = mydb.cursor(dictionary=True)  # Fetch as dict

#         json_data = request.get_json()

#         # Validate token
#         if "token" not in json_data or not json_data["token"]:
#             return jsonify({"error": "No token provided."}), 400

#         if not token_auth(json_data["token"]):
#             return jsonify({"error": "Invalid token."}), 400

#         # Validate outlet
#         if "outlet" not in json_data or not json_data["outlet"]:
#             return jsonify({"error": "No outlet provided."}), 400

#         outlet = json_data["outlet"]

#         # Define time ranges
#         today = datetime.today()
#         ranges = {
#             "0-30": (today - timedelta(days=30), today),
#             "31-60": (today - timedelta(days=60), today - timedelta(days=31)),
#             "61-90": (today - timedelta(days=90), today - timedelta(days=61)),
#             "91-180": (today - timedelta(days=180), today - timedelta(days=91)),
#             "181-365": (today - timedelta(days=365), today - timedelta(days=181)),
#             "366+": (None, today - timedelta(days=366))
#         }

#         # Query template
#         query_template = """
#         SELECT 
#             a.customerName,
#             a.guestID,  
#             SUM(CASE WHEN a.creditState = 'InitialEntry' THEN a.Amount ELSE 0 END) AS InitialTotal,
#             SUM(CASE WHEN a.creditState = 'Payment' THEN a.Amount ELSE 0 END) AS PaymentTotal
#         FROM CreditHistory a 
#         WHERE a.outetName = %s 
#         AND a.Date BETWEEN %s AND %s 
#         GROUP BY a.guestID, a.customerName;
#         """

#         results = {}

#         for label, (start_date, end_date) in ranges.items():
#             if start_date:
#                 cursor.execute(query_template, (outlet, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
#             else:
#                 cursor.execute(query_template, (outlet, '1900-01-01', end_date.strftime('%Y-%m-%d')))

#             data = cursor.fetchall()

#             # Process data into dictionary format
#             total_initial = 0
#             total_payment = 0
#             formatted_data = []

#             for row in data:
#                 total_initial += float(row["InitialTotal"]) if row["InitialTotal"] else 0.0
#                 total_payment += float(row["PaymentTotal"]) if row["PaymentTotal"] else 0.0
#                 formatted_data.append({
#                     "customerName": row["customerName"],
#                     "guestID": row["guestID"],
#                     "InitialTotal": float(row["InitialTotal"]) if row["InitialTotal"] else 0.0,
#                     "PaymentTotal": float(row["PaymentTotal"]) if row["PaymentTotal"] else 0.0
#                 })

#             results[label] = {
#                 "data": formatted_data,
#                 "totalInitial": total_initial,
#                 "totalPayment": total_payment,
#                 "remainingTotal" : total_initial  -total_payment  
#             }

#         cursor.close()
#         mydb.close()

#         return jsonify(results), 200

#     except Exception as error:
#         return jsonify({"error": str(error)}), 400

from flask import Blueprint, jsonify, request
import mysql.connector
import os
from flask_cors import cross_origin
from dotenv import load_dotenv
from root.auth.check import token_auth
from datetime import datetime, timedelta

app_file90 = Blueprint('app_file90', __name__)

@app_file90.route('/debtors-summary', methods=['POST'])
@cross_origin()
def debtorssummary():
    try:
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password'),
            database=os.getenv('database')
        )
        cursor = mydb.cursor(dictionary=True)  # Fetch as dict

        json_data = request.get_json()

        # Validate token
        if "token" not in json_data or not json_data["token"]:
            return jsonify({"error": "No token provided."}), 400

        if not token_auth(json_data["token"]):
            return jsonify({"error": "Invalid token."}), 400

        # Validate outlet
        if "outlet" not in json_data or not json_data["outlet"]:
            return jsonify({"error": "No outlet provided."}), 400

        outlet = json_data["outlet"]

        # Define time ranges
        today = datetime.today()
        ranges = {
            "0-30": (today - timedelta(days=30), today),
            "31-60": (today - timedelta(days=60), today - timedelta(days=31)),
            "61-90": (today - timedelta(days=90), today - timedelta(days=61)),
            "91-180": (today - timedelta(days=180), today - timedelta(days=91)),
            "181-365": (today - timedelta(days=365), today - timedelta(days=181)),
            "366+": (None, today - timedelta(days=366))
        }

        # Query template
        query_template = """
        SELECT 
            a.customerName,
            a.guestID,  
            SUM(CASE WHEN a.creditState = 'InitialEntry' THEN a.Amount ELSE 0 END) AS InitialTotal,
            SUM(CASE WHEN a.creditState = 'Payment' THEN a.Amount ELSE 0 END) AS PaymentTotal
        FROM CreditHistory a 
        WHERE a.outetName = %s 
        AND a.Date BETWEEN %s AND %s 
        GROUP BY a.guestID, a.customerName;
        """

        results = {}
        net_total_initial = 0
        net_total_payment = 0

        for label, (start_date, end_date) in ranges.items():
            if start_date:
                cursor.execute(query_template, (outlet, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
            else:
                cursor.execute(query_template, (outlet, '1900-01-01', end_date.strftime('%Y-%m-%d')))

            data = cursor.fetchall()

            total_initial = 0
            total_payment = 0
            formatted_data = []

            for row in data:
                initial_total = float(row["InitialTotal"]) if row["InitialTotal"] else 0.0
                payment_total = float(row["PaymentTotal"]) if row["PaymentTotal"] else 0.0
                
                total_initial += initial_total
                total_payment += payment_total
                formatted_data.append({
                    "customerName": row["customerName"],
                    "guestID": row["guestID"],
                    "InitialTotal": initial_total,
                    "PaymentTotal": payment_total
                })

            remaining_total = total_initial - total_payment
            net_total_initial += total_initial
            net_total_payment += total_payment
            
            results[label] = {
                "data": formatted_data,
                "totalInitial": total_initial,
                "totalPayment": total_payment,
                "remainingTotal": remaining_total
            }

        net_total_remaining = net_total_initial - net_total_payment

        results["summary"] = {
            "netTotalInitial": net_total_initial,
            "netTotalPayment": net_total_payment,
            "netTotalRemaining": net_total_remaining
        }

        cursor.close()
        mydb.close()

        return jsonify(results), 200

    except Exception as error:
        return jsonify({"error": str(error)}), 400

