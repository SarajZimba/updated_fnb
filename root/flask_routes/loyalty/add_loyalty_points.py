# from flask import Blueprint, jsonify, request
# import mysql.connector
# import os
# from dotenv import load_dotenv
# from flask_cors import cross_origin
# from root.auth.check import token_auth
# import datetime

# load_dotenv()

# app_file94 = Blueprint('app_file94', __name__)

# @app_file94.route("/add-loyalty-points", methods=["POST"])
# @cross_origin()
# def add_loyalty_points():
#     try:
#         data = request.get_json()

#         # Connect to DB
#         mydb = mysql.connector.connect(
#             host=os.getenv('host'),
#             user=os.getenv('user'),
#             password=os.getenv('password'),
#             database=os.getenv('database')
#         )
        
#         cursor = mydb.cursor(dictionary=True,buffered=True)

#         # Validate token
#         token = data.get("token")
#         if not token or not token_auth(token):
#             return jsonify({"error": "Invalid or missing token"}), 400

#         # Get hash_code
#         hash_code = data.get("hash_code")
#         if not hash_code:
#             return jsonify({"error": "Missing hash_code"}), 400
#         # Get phone_no
#         guest_phone = data.get("phone_no")
#         if not guest_phone:
#             return jsonify({"error": "Missing phone_no"}), 400

#         # Step 1: Get order_id from loyaltyqueue
#         cursor.execute("SELECT * FROM loyaltyqueue WHERE hash_code = %s AND status != 'received'", (hash_code,))
#         order = cursor.fetchone()
#         if not order:
#             return jsonify({"error": "Order not found"}), 404
#         outlet = order["outlet"]
#         sub_total = float(order["sub_total"])
#         date = order["date"]

#         # Get customer
#         customer = data.get("customer", None)

#         print(customer)

#         if customer:
#             guest_email = customer["guest_email"] 
#             guest_phone = customer["guest_phone"] 
#             guest_address = customer["guest_address"] 
#             guest_name = customer["guest_name"]

#             # Check if guest already exists
#             cursor.execute("SELECT * FROM guest WHERE guestPhone = %s", (guest_phone,))
#             guest = cursor.fetchone()

#             if guest:
#                 # Existing guest, retrieve points
#                 prev_points = float(guest["loyalty_points"] or 0)
#             else:
#                 # New guest, insert
#                 cursor.execute("""
#                     INSERT INTO guest (guestEmail, guestPhone, guestAddress, Outlet_Name, GuestName, loyalty_points)
#                     VALUES (%s, %s, %s, %s, %s, %s)
#                 """, (guest_email, guest_phone, guest_address, outlet, guest_name, 0.0))
#                 mydb.commit()
#                 prev_points = 0.0
#         else:
#             query = """SELECT * from guest where guestPhone = %s"""
#             cursor.execute(query, (guest_phone,))
#             guest = cursor.fetchone()
#             print(guest)
#             guest_email = guest["guestEmail"] 
#             guest_phone = guest["guestPhone"] 
#             guest_address = guest["guestAddress"] 
#             guest_name = guest["GuestName"]
#             prev_points = float(guest["loyalty_points"] or 0)

#         # Step 3: Get loyalty percentage
#         cursor.execute("SELECT loyalty_percent FROM outetNames WHERE Outlet = %s", (outlet,))
#         loyalty_result = cursor.fetchone()
#         loyalty_percent = float(loyalty_result["loyalty_percent"]) if loyalty_result else 0.0

#         if loyalty_percent > 0:
#             earned_points = round((sub_total * loyalty_percent) / 100, 2)

#             new_points = round(prev_points + earned_points, 2)

#             # Step 5: Update guest's loyalty points
#             cursor.execute("""
#                 UPDATE guest SET loyalty_points = %s 
#                 WHERE guestPhone = %s
#             """, (new_points,  guest_phone, ))
#             mydb.commit()

#             # Step 6: Insert into GuestLoyaltyHistory
#             cursor.execute("""
#                 INSERT INTO GuestLoyaltyHistory (
#                     GuestName, Outlet_Name, Date, PreviousPoints, EarnedPoints, TotalPoints, phone_no
#                 ) VALUES (%s, %s, %s, %s, %s, %s, %s)
#             """, (guest_name, outlet, date, prev_points, earned_points, new_points, guest_phone, ))
#             mydb.commit()

#             # Step 7: Update loyaltyqueue status and verified_at
#             verified_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             cursor.execute("""
#                 UPDATE loyaltyqueue 
#                 SET status = 'received', verified_at = %s 
#                 WHERE hash_code = %s
#             """, (verified_at, hash_code))
#             mydb.commit()

#             return jsonify({
#                 "success": True,
#                 "earnedPoints": earned_points,
#                 "totalPoints": new_points,
#                 "guest_phone":guest_phone,

#             }), 200

#         return jsonify({"message": "Loyalty percent is 0. No points awarded."}), 200

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


from flask import Blueprint, jsonify, request
import mysql.connector
import os
from dotenv import load_dotenv
from flask_cors import cross_origin
from root.auth.check import token_auth
import datetime

load_dotenv()

app_file94 = Blueprint('app_file94', __name__)

@app_file94.route("/add-loyalty-points", methods=["POST"])
@cross_origin()
def add_loyalty_points():
    try:
        data = request.get_json()

        # Connect to DB
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password'),
            database=os.getenv('database')
        )
        
        cursor = mydb.cursor(dictionary=True,buffered=True)

        # Validate token
        token = data.get("token")
        if not token or not token_auth(token):
            return jsonify({"error": "Invalid or missing token"}), 400

        # Get hash_code
        hash_code = data.get("hash_code")
        if not hash_code:
            return jsonify({"error": "Missing hash_code"}), 400
        # Get phone_no
        guest_phone = data.get("phone_no")
        if not guest_phone:
            return jsonify({"error": "Missing phone_no"}), 400

        # Step 1: Get order_id from loyaltyqueue
        cursor.execute("SELECT * FROM loyaltyqueue WHERE hash_code = %s AND status != 'received'", (hash_code,))
        order = cursor.fetchone()
        if not order:
            return jsonify({"error": "Order not found"}), 404
        outlet = order["outlet"]
        sub_total = float(order["sub_total"])
        date = order["date"]

        # Get customer
        customer = data.get("customer", None)

        print(customer)

        if customer:
            guest_email = customer["guest_email"] 
            guest_phone = customer["guest_phone"] 
            guest_address = customer["guest_address"] 
            guest_name = customer["guest_name"]

            # Check if guest already exists
            cursor.execute("SELECT * FROM guest WHERE guestPhone = %s and Outlet_Name=%s", (guest_phone,outlet,))
            guest = cursor.fetchone()

            if guest:
                # Existing guest, retrieve points
                prev_points = float(guest["loyalty_points"] or 0)
            else:
                # New guest, insert
                cursor.execute("""
                    INSERT INTO guest (guestEmail, guestPhone, guestAddress, Outlet_Name, GuestName, loyalty_points)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (guest_email, guest_phone, guest_address, outlet, guest_name, 0.0))
                mydb.commit()
                prev_points = 0.0
        else:
            query = """SELECT * from guest where guestPhone = %s and Outlet_Name=%s"""
            cursor.execute(query, (guest_phone,outlet,))
            guest = cursor.fetchone()
            print(guest)
            guest_email = guest["guestEmail"] 
            guest_phone = guest["guestPhone"] 
            guest_address = guest["guestAddress"] 
            guest_name = guest["GuestName"]
            prev_points = float(guest["loyalty_points"] or 0)

        # Step 3: Get loyalty percentage
        cursor.execute("SELECT loyalty_percent FROM outetNames WHERE Outlet = %s", (outlet,))
        loyalty_result = cursor.fetchone()
        loyalty_percent = float(loyalty_result["loyalty_percent"]) if loyalty_result else 0.0

        if loyalty_percent > 0:
            earned_points = round((sub_total * loyalty_percent) / 100, 2)

            new_points = round(prev_points + earned_points, 2)

            # Step 5: Update guest's loyalty points
            cursor.execute("""
                UPDATE guest SET loyalty_points = %s 
                WHERE guestPhone = %s and Outlet_Name=%s
            """, (new_points,  guest_phone, outlet,))
            mydb.commit()

            # Step 6: Insert into GuestLoyaltyHistory
            cursor.execute("""
                INSERT INTO GuestLoyaltyHistory (
                    GuestName, Outlet_Name, Date, PreviousPoints, EarnedPoints, TotalPoints, phone_no
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (guest_name, outlet, date, prev_points, earned_points, new_points, guest_phone, ))
            mydb.commit()

            # Step 7: Update loyaltyqueue status and verified_at
            verified_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                UPDATE loyaltyqueue 
                SET status = 'received', verified_at = %s 
                WHERE hash_code = %s
            """, (verified_at, hash_code))
            mydb.commit()

            return jsonify({
                "success": True,
                "earnedPoints": earned_points,
                "totalPoints": new_points,
                "guest_phone":guest_phone,

            }), 200

        return jsonify({"message": "Loyalty percent is 0. No points awarded."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# from flask import Blueprint, jsonify, request
# import mysql.connector
# import os
# from dotenv import load_dotenv
# from flask_cors import cross_origin
# from root.auth.check import token_auth
# import datetime

# load_dotenv()

# app_file94 = Blueprint('app_file94', __name__)

# @app_file94.route("/add-loyalty-points", methods=["POST"])
# @cross_origin()
# def add_loyalty_points():
#     try:
#         data = request.get_json()

#         # Connect to DB
#         mydb = mysql.connector.connect(
#             host=os.getenv('host'),
#             user=os.getenv('user'),
#             password=os.getenv('password'),
#             database=os.getenv('database')
#         )
#         cursor = mydb.cursor(dictionary=True,buffered=True)

#         # Validate token
#         token = data.get("token")
#         if not token or not token_auth(token):
#             return jsonify({"error": "Invalid or missing token"}), 400

#         # Get hash_code
#         hash_code = data.get("hash_code")
#         if not hash_code:
#             return jsonify({"error": "Missing hash_code"}), 400
#         # Get phone_no
#         guest_phone = data.get("phone_no")
#         if not guest_phone:
#             return jsonify({"error": "Missing phone_no"}), 400

#         # Step 1: Get order_id from loyaltyqueue
#         cursor.execute("SELECT * FROM loyaltyqueue WHERE hash_code = %s AND status != 'received'", (hash_code,))
#         order = cursor.fetchone()
#         if not order:
#             return jsonify({"error": "Order not found"}), 404
#         outlet = order["outlet"]
#         sub_total = float(order["sub_total"])
#         date = order["date"]

#         # Get customer
#         customer = data.get("customer", None)

#         print(customer)

#         if customer:
#             guest_email = customer["guest_email"] 
#             guest_phone = customer["guest_phone"] 
#             guest_address = customer["guest_address"] 
#             guest_name = customer["guest_name"]

#             # Check if guest already exists
#             cursor.execute("SELECT * FROM guest WHERE guestPhone = %s and Outlet_Name=%s", (guest_phone,outlet,))
#             guest = cursor.fetchone()

#             if guest:
#                 # Existing guest, retrieve guest_id and points
#                 guest_id = guest["id"]
#                 # Existing guest, retrieve points
#                 prev_points = float(guest["loyalty_points"] or 0)
#             else:
#                 # New guest, insert
#                 cursor.execute("""
#                     INSERT INTO guest (guestEmail, guestPhone, guestAddress, Outlet_Name, GuestName, loyalty_points)
#                     VALUES (%s, %s, %s, %s, %s, %s)
#                 """, (guest_email, guest_phone, guest_address, outlet, guest_name, 0.0))
#                 mydb.commit()
#                 guest_id = cursor.lastrowid  # Get the newly inserted guest_id
#                 prev_points = 0.0
#         else:
#             query = """SELECT * from guest where guestPhone = %s and Outlet_Name= %s"""
#             cursor.execute(query, (guest_phone,outlet,))
#             guest = cursor.fetchone()
#             print(guest)
#             guest_id = guest["id"]
#             guest_email = guest["guestEmail"] 
#             guest_phone = guest["guestPhone"] 
#             guest_address = guest["guestAddress"] 
#             guest_name = guest["GuestName"]
#             prev_points = float(guest["loyalty_points"] or 0)

#         # Step 3: Get loyalty percentage
#         cursor.execute("SELECT loyalty_percent FROM outetnames WHERE Outlet = %s", (outlet,))
#         loyalty_result = cursor.fetchone()
#         loyalty_percent = float(loyalty_result["loyalty_percent"]) if loyalty_result else 0.0

#         if loyalty_percent > 0:
#             earned_points = round((sub_total * loyalty_percent) / 100, 2)

#             new_points = round(prev_points + earned_points, 2)

#             # Step 5: Update guest's loyalty points
#             cursor.execute("""
#                 UPDATE guest SET loyalty_points = %s 
#                 WHERE guestPhone = %s AND id = %s
#             """, (new_points,  guest_phone, guest_id ))
#             mydb.commit()

#             # Step 6: Insert into GuestLoyaltyHistory
#             cursor.execute("""
#                 INSERT INTO GuestLoyaltyHistory (
#                     guestID, GuestName, Outlet_Name, Date, PreviousPoints, EarnedPoints, TotalPoints, phone_no
#                 ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
#             """, (guest_id, guest_name, outlet, date, prev_points, earned_points, new_points, guest_phone, ))
#             mydb.commit()

#             # Step 7: Update loyaltyqueue status and verified_at
#             verified_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             cursor.execute("""
#                 UPDATE loyaltyqueue 
#                 SET status = 'received', verified_at = %s 
#                 WHERE hash_code = %s
#             """, (verified_at, hash_code))
#             mydb.commit()

#             return jsonify({
#                 "success": True,
#                 "earnedPoints": earned_points,
#                 "totalPoints": new_points,
#                 "guest_phone":guest_phone,
#                 "guest_id": guest_id
#             }), 200

#         return jsonify({"message": "Loyalty percent is 0. No points awarded."}), 200

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
