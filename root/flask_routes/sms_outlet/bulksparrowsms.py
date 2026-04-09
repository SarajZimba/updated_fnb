from flask import Blueprint, request, jsonify
import mysql.connector
from flask_cors import cross_origin
import os, requests
from dotenv import load_dotenv
load_dotenv()

app_file204 = Blueprint('app_file204', __name__)
from root.auth.check import token_auth     # Your existing token auth


# def send_sparrow_sms(numbers, message):
#     """Send SMS to multiple numbers using Sparrow SMS."""
#     to_numbers = ", ".join(str(num) for num in numbers)

#     url = "https://api.sparrowsms.com/v1/sms/"
#     payload = {
#         "token": os.getenv("SPARROW_TOKEN"),
#         "from": os.getenv("SPARROW_SENDER"),
#         "to": to_numbers,
#         "text": message
#     }

#     response = requests.post(url, data=payload)
#     return response.json()

def send_sparrow_sms(numbers, message):
    to_numbers = ", ".join(str(num) for num in numbers)

    url = "https://api.sparrowsms.com/v2/sms/"
    payload = {
        "token": os.getenv("SPARROW_TOKEN"),
        "from": os.getenv("SPARROW_SENDER"),
        "to": to_numbers,
        "text": message
    }

    print("payload", payload)

    response = requests.post(url, data=payload)

    # Try parsing JSON, otherwise return raw body
    try:
        return response.json()
    except:
        return {
            "response_code": 500,
            "response": "Non-JSON returned",
            "raw_response": response.text
        }



# @app_file204.route("/send-bulk-sms", methods=["POST"])
# @cross_origin()
# def send_bulk_sms():
#     try:
#         data = request.get_json()

#         # Validate JSON
#         if not data:
#             return jsonify({"error": "Missing JSON body"}), 400

#         # Token validation
#         if "token" not in data or not data["token"]:
#             return jsonify({"error": "No token provided."}), 400

#         token = data["token"]
#         if not token_auth(token):
#             return jsonify({"error": "Invalid token."}), 400

#         # Required Fields
#         sms_text = data.get("text")

        
#         if not sms_text:
#             return jsonify({"error": "'text' (SMS message) is required"}), 400

#         # Connect DB
#         mydb = mysql.connector.connect(
#             host=os.getenv("host"),
#             user=os.getenv("user"),
#             password=os.getenv("password"),
#         )
#         cursor = mydb.cursor(buffered=True)
#         cursor.execute("USE {}".format(os.getenv("database")))

#         # Get customers & phone numbers
#         cursor.execute("SELECT name, phone FROM customers")
#         rows = cursor.fetchall()

#         mydb.close()

#         if not rows:
#             return jsonify({"error": "No customers found"}), 404

#         # Extract all mobile numbers
#         phone_numbers = [row[1] for row in rows if row[1]]

#         if not phone_numbers:
#             return jsonify({"error": "No phone numbers available"}), 400

#         # Send SMS
#         sms_response = send_sparrow_sms(
#             numbers=phone_numbers,
#             message=sms_text
#         )

#         return jsonify({
#             "success": True,
#             "total_customers": len(phone_numbers),
#             "result": sms_response
#         }), 200

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @app_file204.route("/send-bulk-sms", methods=["POST"])
# @cross_origin()
# def send_bulk_sms():
#     try:
#         data = request.get_json()

#         # Validate JSON
#         if not data:
#             return jsonify({"error": "Missing JSON body"}), 400

#         # Token validation
#         if "token" not in data or not data["token"]:
#             return jsonify({"error": "No token provided."}), 400

#         token = data["token"]
#         if not token_auth(token):
#             return jsonify({"error": "Invalid token."}), 400

#         # Required Fields
#         sms_text = data.get("text")
#         extra_numbers = data.get("extra_numbers", [])   # <-- NEW FIELD

#         if not sms_text:
#             return jsonify({"error": "'text' (SMS message) is required"}), 400

#         # Connect DB
#         mydb = mysql.connector.connect(
#             host=os.getenv("host"),
#             user=os.getenv("user"),
#             password=os.getenv("password"),
#         )
#         cursor = mydb.cursor(buffered=True)
#         cursor.execute("USE {}".format(os.getenv("database")))

#         # Get customers & phone numbers
#         cursor.execute("SELECT name, phone FROM customers")
#         rows = cursor.fetchall()
#         mydb.close()

#         if not rows and not extra_numbers:
#             return jsonify({"error": "No recipients found"}), 404

#         # Extract customer numbers
#         customer_numbers = [row[1] for row in rows if row[1]]

#         # Merge with extra numbers
#         all_numbers = customer_numbers + extra_numbers

#         # Remove duplicates, empty, invalid, etc.
#         all_numbers = list({num.strip() for num in all_numbers if num})

#         if not all_numbers:
#             return jsonify({"error": "No valid phone numbers available"}), 400

#         # Send SMS
#         sms_response = send_sparrow_sms(
#             numbers=all_numbers,
#             message=sms_text
#         )

#         return jsonify({
#             "success": True,
#             "total_customers": len(customer_numbers),
#             "extra_numbers": len(extra_numbers),
#             "total_sent": len(all_numbers),
#             "result": sms_response
#         }), 200

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


# @app_file204.route("/send-bulk-sms", methods=["POST"])
# @cross_origin()
# def send_bulk_sms():
#     try:
#         data = request.get_json()

#         # Validate JSON
#         if not data:
#             return jsonify({"error": "Missing JSON body"}), 400

#         # Token validation
#         if "token" not in data or not data["token"]:
#             return jsonify({"error": "No token provided."}), 400

#         token = data["token"]
#         if not token_auth(token):
#             return jsonify({"error": "Invalid token."}), 400

#         # Required Fields
#         sms_text = data.get("text")
#         extra_numbers = data.get("extra_numbers", [])
#         send_to_all = bool(data.get("send_to_all", False))

#         if not sms_text:
#             return jsonify({"error": "'text' (SMS message) is required"}), 400

#         # Connect DB
#         mydb = mysql.connector.connect(
#             host=os.getenv("host"),
#             user=os.getenv("user"),
#             password=os.getenv("password"),
#         )
#         cursor = mydb.cursor(buffered=True)
#         cursor.execute("USE {}".format(os.getenv("database")))

#         # Default: only extra numbers
#         all_numbers = list(extra_numbers)

#         customer_numbers = []

#         # If we need to send to all customers
#         if send_to_all:
#             cursor.execute("SELECT phone FROM customers")
#             rows = cursor.fetchall()
#             mydb.close()

#             customer_numbers = [row[0] for row in rows if row[0]]

#             # Merge extra + customers
#             all_numbers = customer_numbers + extra_numbers

#         else:
#             # Close DB if it wasn't already closed
#             mydb.close()

#         # Remove duplicates & empty values
#         all_numbers = list({num.strip() for num in all_numbers if num})

#         if not all_numbers:
#             return jsonify({"error": "No valid phone numbers available"}), 400

#         # Send SMS
#         sms_response = send_sparrow_sms(
#             numbers=all_numbers,
#             message=sms_text
#         )

#         return jsonify({
#             "success": True,
#             "sent_to_all_customers": send_to_all,
#             "customer_count": len(customer_numbers),
#             "extra_number_count": len(extra_numbers),
#             "total_sent": len(all_numbers),
#             "result": sms_response
#         }), 200

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# import random

# @app_file204.route("/send-bulk-sms", methods=["POST"])
# @cross_origin()
# def send_bulk_sms():
#     try:
#         data = request.get_json()

#         # Validate JSON
#         if not data:
#             return jsonify({"error": "Missing JSON body"}), 400

#         # Token validation
#         if "token" not in data or not data["token"]:
#             return jsonify({"error": "No token provided."}), 400

#         token = data["token"]
#         if not token_auth(token):
#             return jsonify({"error": "Invalid token."}), 400

#         # Required Fields
#         sms_text = data.get("text")
#         extra_numbers = data.get("extra_numbers", [])
#         sample_size = data.get("sample_size")   # <-- NEW FIELD

#         if not sms_text:
#             return jsonify({"error": "'text' (SMS message) is required"}), 400

#         if not sample_size or type(sample_size) != int:
#             return jsonify({"error": "'sample_size' integer is required"}), 400

#         # Connect DB
#         mydb = mysql.connector.connect(
#             host=os.getenv("host"),
#             user=os.getenv("user"),
#             password=os.getenv("password"),
#         )
#         cursor = mydb.cursor(buffered=True)
#         cursor.execute("USE {}".format(os.getenv("database")))

#         cursor.execute("SELECT phone FROM customers")
#         rows = cursor.fetchall()
#         mydb.close()

#         # Extract phones from DB
#         customer_numbers = [row[0] for row in rows if row[0]]

#         # Remove duplicates + strip spaces from extra
#         extra_numbers = list({num.strip() for num in extra_numbers if num})

#         # Total required from DB
#         needed_from_db = sample_size - len(extra_numbers)

#         if needed_from_db < 0:
#             return jsonify({"error": "sample_size is smaller than extra_numbers count"}), 400

#         # Random sample from DB
#         if needed_from_db > len(customer_numbers):
#             return jsonify({"error": "Not enough customers in database"}), 400

#         sampled_customer_numbers = (
#             random.sample(customer_numbers, needed_from_db)
#             if needed_from_db > 0
#             else []
#         )

#         # Final combined list
#         all_numbers = list(set(sampled_customer_numbers + extra_numbers))

#         if not all_numbers:
#             return jsonify({"error": "No valid phone numbers available"}), 400

#         # Send SMS
#         sms_response = send_sparrow_sms(
#             numbers=all_numbers,
#             message=sms_text
#         )

#         return jsonify({
#             "success": True,
#             "total_customers_available": len(customer_numbers),
#             "using_from_customer_db": len(sampled_customer_numbers),
#             "extra_numbers": len(extra_numbers),
#             "total_sent": len(all_numbers),
#             "result": sms_response
#         }), 200

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

import random
from tasks import send_bulk_sms_task


# @app_file204.route("/send-bulk-sms", methods=["POST"])
# @cross_origin()
# def send_bulk_sms():
#     try:
#         data = request.get_json()

#         if not data:
#             return jsonify({"error": "Missing JSON body"}), 400

#         if "token" not in data or not data["token"]:
#             return jsonify({"error": "No token provided."}), 400

#         token = data["token"]
#         if not token_auth(token):
#             return jsonify({"error": "Invalid token."}), 400

#         sms_text = data.get("text")
#         extra_numbers = data.get("extra_numbers", [])
#         sample_size = data.get("sample_size")

#         if not sms_text:
#             return jsonify({"error": "'text' is required"}), 400

#         if not sample_size or type(sample_size) != int:
#             return jsonify({"error": "'sample_size' integer is required"}), 400

#         # Connect to DB
#         mydb = mysql.connector.connect(
#             host=os.getenv("host"),
#             user=os.getenv("user"),
#             password=os.getenv("password")
#         )
#         cursor = mydb.cursor(buffered=True)
#         cursor.execute("USE {}".format(os.getenv("database")))
#         cursor.execute("SELECT phone FROM customers WHERE status = 1")
#         # cursor.execute("SELECT guestPhone FROM guest")
#         rows = cursor.fetchall()

#         customer_numbers = [row[0] for row in rows if row[0]]

#         # dedupe + strip extra numbers
#         extra_numbers = list({num.strip() for num in extra_numbers if num})

#         needed_from_db = sample_size - len(extra_numbers)

#         if needed_from_db < 0:
#             return jsonify({"error": "sample_size smaller than extra_numbers"}), 400

#         if needed_from_db > len(customer_numbers):
#             return jsonify({"error": "Not enough customers in DB"}), 400

#         sampled_from_db = random.sample(customer_numbers, needed_from_db) if needed_from_db > 0 else []

#         final_numbers = list(set(sampled_from_db + extra_numbers))

#         if not final_numbers:
#             return jsonify({"error": "No valid phone numbers"}), 400

#         # START CELERY TASK
#         task = send_bulk_sms_task.delay(
#             message=sms_text,
#             numbers=final_numbers
#         )

#         sql = """
#         INSERT INTO sms_history (task_id, sender_name, message_text, total_numbers, numbers_sent)
#         VALUES (%s, %s, %s, %s, %s)
#         """

#         cursor.execute(sql, (
#             task.id,
#             data.get("sender", "System"),   # or logged-in username
#             sms_text,
#             len(final_numbers),
#             ",".join(final_numbers)
#         ))

#         mydb.commit()
#         mydb.close()

#         return jsonify({
#             "success": True,
#             "message": "Bulk SMS sending started",
#             "task_id": task.id,
#             "scheduled_numbers": len(final_numbers)
#         }), 200

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @app_file204.route("/send-bulk-sms", methods=["POST"])
# @cross_origin()
# def send_bulk_sms():
#     try:
#         data = request.get_json()

#         if not data:
#             return jsonify({"error": "Missing JSON body"}), 400

#         if "token" not in data or not data["token"]:
#             return jsonify({"error": "No token provided."}), 400

#         token = data["token"]
#         if not token_auth(token):
#             return jsonify({"error": "Invalid token."}), 400

#         sms_text = data.get("text")
#         extra_numbers = data.get("extra_numbers", [])
#         sample_size = data.get("sample_size")

#         if not sms_text:
#             return jsonify({"error": "'text' is required"}), 400

#         if not sample_size or type(sample_size) != int:
#             return jsonify({"error": "'sample_size' integer is required"}), 400

#         # Connect to DB
#         mydb = mysql.connector.connect(
#             host=os.getenv("host"),
#             user=os.getenv("user"),
#             password=os.getenv("password")
#         )
#         cursor = mydb.cursor(dictionary=True)
#         cursor.execute("USE {}".format(os.getenv("database")))

#         # Fetch name + phone
#         cursor.execute("SELECT name, phone FROM customers WHERE status = 1")
#         rows = cursor.fetchall()

#         # Extract DB numbers
#         customer_numbers = [r for r in rows if r["phone"]]

#         # Clean extra numbers
#         extra_numbers = list({num.strip() for num in extra_numbers if num})

#         needed_from_db = sample_size - len(extra_numbers)

#         if needed_from_db < 0:
#             return jsonify({"error": "sample_size smaller than extra_numbers"}), 400

#         if needed_from_db > len(customer_numbers):
#             return jsonify({"error": "Not enough customers in DB"}), 400

#         # Random sample DB customers
#         sampled_from_db = random.sample(customer_numbers, needed_from_db) if needed_from_db > 0 else []

#         # Convert extra_numbers → name/phone pairs (name unknown)
#         extra_number_objects = [{"name": "Unknown", "phone": num} for num in extra_numbers]

#         # Final combined list
#         final_customers = sampled_from_db + extra_number_objects

#         # Remove duplicates based on phone
#         unique = {}
#         for c in final_customers:
#             unique[c["phone"]] = c
#         final_customers = list(unique.values())

#         if not final_customers:
#             return jsonify({"error": "No valid phone numbers"}), 400

#         # Extract just numbers for sending
#         final_numbers = [c["phone"] for c in final_customers]

#         # START CELERY TASK
#         task = send_bulk_sms_task.delay(
#             message=sms_text,
#             numbers=final_numbers
#         )

#         # Insert into SMS history
#         sql = """
#         INSERT INTO sms_history (task_id, sender_name, message_text, total_numbers, numbers_sent)
#         VALUES (%s, %s, %s, %s, %s)
#         """

#         cursor.execute(sql, (
#             task.id,
#             data.get("sender", "System"),
#             sms_text,
#             len(final_numbers),
#             ",".join(final_numbers)
#         ))

#         mydb.commit()
#         mydb.close()

#         # Sort customers alphabetically by name
#         final_customers_sorted = sorted(final_customers, key=lambda x: x["name"].lower())

#         return jsonify({
#             "success": True,
#             "message": "Bulk SMS sending started",
#             "task_id": task.id,
#             "scheduled_numbers": len(final_numbers),
#             "recipients": final_customers_sorted     # <── HERE!
#         }), 200

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


@app_file204.route("/send-bulk-sms", methods=["POST"])
@cross_origin()
def send_bulk_sms():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Missing JSON body"}), 400

        if "token" not in data or not data["token"]:
            return jsonify({"error": "No token provided."}), 400

        token = data["token"]
        if not token_auth(token):
            return jsonify({"error": "Invalid token."}), 400

        sms_text = data.get("text")
        extra_numbers = data.get("extra_numbers", [])
        sample_size = data.get("sample_size")

        if not sms_text:
            return jsonify({"error": "'text' is required"}), 400

        if not sample_size or type(sample_size) != int:
            return jsonify({"error": "'sample_size' integer is required"}), 400

        # Connect to DB
        mydb = mysql.connector.connect(
            host=os.getenv("host"),
            user=os.getenv("user"),
            password=os.getenv("password")
        )
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("USE {}".format(os.getenv("database")))

        # Fetch name + phone
        cursor.execute("SELECT name, phone FROM customers WHERE status = 1")
        rows = cursor.fetchall()

        # Extract DB numbers
        customer_numbers = [r for r in rows if r["phone"]]

        # Clean extra numbers
        extra_numbers = list({num.strip() for num in extra_numbers if num})

        needed_from_db = sample_size - len(extra_numbers)

        if needed_from_db < 0:
            return jsonify({"error": "sample_size smaller than extra_numbers"}), 400

        if needed_from_db > len(customer_numbers):
            return jsonify({"error": "Not enough customers in DB"}), 400

        # Random sample DB customers
        sampled_from_db = random.sample(customer_numbers, needed_from_db) if needed_from_db > 0 else []

        # ------------------------------------------------------------
        # FIX: Lookup each extra number in DB → return actual name
        # ------------------------------------------------------------
        extra_number_objects = []
        for num in extra_numbers:
            cursor.execute("SELECT name FROM customers WHERE phone = %s", (num,))
            result = cursor.fetchone()

            if result:
                extra_number_objects.append({
                    "name": result["name"],   # Found name
                    "phone": num
                })
            else:
                extra_number_objects.append({
                    "name": "Unknown",        # Not found
                    "phone": num
                })
        # ------------------------------------------------------------

        # Final combined list
        final_customers = sampled_from_db + extra_number_objects

        # Remove duplicates based on phone
        unique = {}
        for c in final_customers:
            unique[c["phone"]] = c
        final_customers = list(unique.values())

        if not final_customers:
            return jsonify({"error": "No valid phone numbers"}), 400

        # Extract just numbers for sending
        final_numbers = [c["phone"] for c in final_customers]

        # START CELERY TASK
        task = send_bulk_sms_task.delay(
            message=sms_text,
            numbers=final_numbers
        )

        # Insert into SMS history
        sql = """
        INSERT INTO sms_history (task_id, sender_name, message_text, total_numbers, numbers_sent)
        VALUES (%s, %s, %s, %s, %s)
        """

        cursor.execute(sql, (
            task.id,
            data.get("sender", "System"),
            sms_text,
            len(final_numbers),
            ",".join(final_numbers)
        ))

        mydb.commit()
        mydb.close()

        # Sort customers alphabetically by name
        final_customers_sorted = sorted(final_customers, key=lambda x: x["name"].lower())

        return jsonify({
            "success": True,
            "message": "Bulk SMS sending started",
            "task_id": task.id,
            "scheduled_numbers": len(final_numbers),
            "recipients": final_customers_sorted
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
