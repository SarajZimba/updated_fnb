# from flask import Blueprint, request, jsonify
# import os
# import mysql.connector

# # Create a blueprint for customer-related routes
# customer_bp = Blueprint('customer_bp', __name__)

# @customer_bp.route("/add-customers", methods=["POST"])
# def add_customers():
#     """
#     Expects JSON body like:
#     [
#         {"name": "Sara", "email": "sara@example.com", "phone": "12345", "address": "Kathmandu"},
#         {"name": "John", "email": "john@example.com", "phone": "67890", "address": "Pokhara"}
#     ]
#     """
#     customers = request.get_json()
#     if not isinstance(customers, list):
#         return jsonify({"error": "Expected a list of customer objects"}), 400

#     values = []
#     for c in customers:
#         name = c.get("name")
#         email = c.get("email")
#         phone = c.get("phone")
#         address = c.get("address")
#         if not all([name, email, phone, address]):
#             return jsonify({"error": "All fields (name, email, phone, address) are required for each customer"}), 400
#         values.append((name, email, phone, address))

#     try:
#         mydb = mysql.connector.connect(
#             host=os.getenv('host'),
#             user=os.getenv('user'),
#             password=os.getenv('password'),
#             database=os.getenv('database')
#         )
#         cursor = mydb.cursor()
#         sql = "INSERT INTO customers (name, email, phone, address) VALUES (%s, %s, %s, %s)"
#         cursor.executemany(sql, values)  # Insert all at once
#         mydb.commit()
#         cursor.close()
#         mydb.close()
#         return jsonify({"message": f"{len(values)} customers added successfully!"}), 201
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


# from flask import Blueprint, request, jsonify
# import os
# import mysql.connector

# # Create a blueprint for customer-related routes
# customer_bp = Blueprint('customer_bp', __name__)

# @customer_bp.route("/add-customers", methods=["POST"])
# def add_customers():
#     """
#     Expects JSON body like:
#     [
#         {
#             "name": "Sara",
#             "email": "sara@example.com",
#             "phone": "12345",
#             "address": "Kathmandu",
#             "status": true,
#             "source": "Facebook"
#         }
#     ]
#     """
#     customers = request.get_json()

#     if not isinstance(customers, list):
#         return jsonify({"error": "Expected a list of customer objects"}), 400

#     values = []
#     for c in customers:
#         name = c.get("name")
#         email = c.get("email")
#         phone = c.get("phone")
#         address = c.get("address")
#         status = c.get("status", True)       # default True if not provided
#         source = c.get("source", "")         # default empty string

#         if not all([name, email, phone, address]):
#             return jsonify({"error": "Fields name, email, phone, address are required"}), 400

#         values.append((name, email, phone, address, status, source))

#     try:
#         mydb = mysql.connector.connect(
#             host=os.getenv('host'),
#             user=os.getenv('user'),
#             password=os.getenv('password'),
#             database=os.getenv('database')
#         )
#         cursor = mydb.cursor()

#         sql = """
#             INSERT INTO customers 
#             (name, email, phone, address, status, source)
#             VALUES (%s, %s, %s, %s, %s, %s)
#         """

#         cursor.executemany(sql, values)
#         mydb.commit()

#         cursor.close()
#         mydb.close()

#         return jsonify({"message": f"{len(values)} customers added successfully!"}), 201

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

from flask import Blueprint, request, jsonify
import os
import mysql.connector

customer_bp = Blueprint('customer_bp', __name__)

@customer_bp.route("/add-customers", methods=["POST"])
def add_customers():
    customers = request.get_json()

    if not isinstance(customers, list):
        return jsonify({"error": "Expected a list of customer objects"}), 400

    inserted_count = 0
    skipped = []   # log skipped entries

    try:
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password'),
            database=os.getenv('database')
        )
        cursor = mydb.cursor()

        # Check duplicates one-by-one
        for c in customers:
            name = c.get("name")
            email = c.get("email")
            phone = c.get("phone")
            address = c.get("address")
            status = c.get("status", True)
            source = c.get("source", "")

            # # Validate required fields
            # if not all([name, email, phone, address]):
            #     skipped.append(f"Skipped customer with phone {phone}: missing required fields.")
            #     continue

            # Check if phone already exists
            cursor.execute("SELECT COUNT(*) FROM customers WHERE phone = %s", (phone,))
            exists = cursor.fetchone()[0]

            if exists > 0:
                skipped.append(f"Skipped {phone}: already exists.")
                continue

            # Insert customer
            insert_sql = """
                INSERT INTO customers (name, email, phone, address, status, source)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_sql, (name, email, phone, address, status, source))
            inserted_count += 1

        mydb.commit()
        cursor.close()
        mydb.close()

        return jsonify({
            "message": "Import completed",
            "inserted": inserted_count,
            "skipped": skipped
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500




# @customer_bp.route("/get-customers", methods=["GET"])
# def get_customers():
#     """
#     Returns a list of all customers in the database.
#     """
#     try:
#         mydb = mysql.connector.connect(
#             host=os.getenv('host'),
#             user=os.getenv('user'),
#             password=os.getenv('password'),
#             database=os.getenv('database')
#         )
#         cursor = mydb.cursor(dictionary=True)  # dictionary=True returns rows as dicts
#         cursor.execute("SELECT id, name, email, phone, address FROM customers")
#         customers = cursor.fetchall()
#         cursor.close()
#         mydb.close()
#         return jsonify({"customers": customers}), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


@customer_bp.route("/get-customers", methods=["GET"])
def get_customers():
    """
    Returns a list of all customers in the database.
    """
    try:
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password'),
            database=os.getenv('database')
        )
        cursor = mydb.cursor(dictionary=True)  # dictionary=True returns rows as dicts

        cursor.execute("""
            SELECT 
                id, 
                name, 
                email, 
                phone, 
                address, 
                status, 
                source
            FROM customers order by id desc;
        """)

        customers = cursor.fetchall()

        cursor.close()
        mydb.close()

        return jsonify({"customers": customers}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@customer_bp.route("/get-customer-status-summary", methods=["GET"])
def get_customer_status_summary():
    try:
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password'),
            database=os.getenv('database')
        )
        cursor = mydb.cursor(dictionary=True)

        # Fetch active customers
        cursor.execute("SELECT * FROM customers WHERE status = 1")
        active_customers = cursor.fetchall()

        # Fetch inactive customers
        cursor.execute("SELECT * FROM customers WHERE status = 0")
        inactive_customers = cursor.fetchall()

        cursor.close()
        mydb.close()

        return jsonify({
            "active_count": len(active_customers),
            "inactive_count": len(inactive_customers),
            "active_customers": active_customers,
            "inactive_customers": inactive_customers
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@customer_bp.route("/customer/toggle-status", methods=["PUT"])
def toggle_customer_status():
    data = request.get_json()

    customer_id = data.get("customer_id")

    if customer_id is None:
        return jsonify({"error": "customer_id is required"}), 400

    try:
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password'),
            database=os.getenv('database')
        )
        cursor = mydb.cursor()

        # Fetch current status
        cursor.execute("SELECT status FROM customers WHERE id = %s", (customer_id,))
        result = cursor.fetchone()

        if not result:
            cursor.close()
            mydb.close()
            return jsonify({"error": "Customer not found"}), 404

        current_status = result[0]

        # Toggle status
        new_status = 1 if current_status == 0 else 0

        cursor.execute(
            "UPDATE customers SET status = %s WHERE id = %s",
            (new_status, customer_id)
        )
        mydb.commit()

        cursor.close()
        mydb.close()

        return jsonify({
            "message": "Customer status updated successfully",
            "customer_id": customer_id,
            "old_status": current_status,
            "new_status": new_status
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@customer_bp.route("/update-customer/<int:customer_id>", methods=["PUT"])
def update_customer(customer_id):
    data = request.get_json()

    if not data:
        return jsonify({"error": "No update data provided"}), 400

    # Allowed fields to update
    allowed_fields = ["name", "email", "phone", "address", "status", "source"]
    update_fields = {}
    
    # Filter only fields present in JSON request
    for field in allowed_fields:
        if field in data:
            update_fields[field] = data[field]

    if not update_fields:
        return jsonify({"error": "No valid fields to update"}), 400

    try:
        # DB connection
        mydb = mysql.connector.connect(
            host=os.getenv("host"),
            user=os.getenv("user"),
            password=os.getenv("password"),
            database=os.getenv("database")
        )
        cursor = mydb.cursor()

        # 1️⃣ Check if customer exists
        cursor.execute("SELECT id FROM customers WHERE id = %s", (customer_id,))
        exists = cursor.fetchone()

        if not exists:
            return jsonify({"error": f"Customer ID {customer_id} does not exist"}), 404

        # 2️⃣ Validate phone uniqueness (if phone being updated)
        if "phone" in update_fields and data["phone"] != "":
            cursor.execute(
                "SELECT COUNT(*) FROM customers WHERE phone = %s AND id != %s",
                (update_fields["phone"], customer_id)
            )
            if cursor.fetchone()[0] > 0:
                return jsonify({"error": "Phone number already used by another customer"}), 400

        # 3️⃣ Validate email uniqueness (optional)
        if "email" in update_fields and data["email"] != "":
            cursor.execute(
                "SELECT COUNT(*) FROM customers WHERE email = %s AND id != %s",
                (update_fields["email"], customer_id)
            )
            if cursor.fetchone()[0] > 0:
                return jsonify({"error": "Email already used by another customer"}), 400

        # 4️⃣ Build dynamic UPDATE query
        set_clause = ", ".join(f"{field} = %s" for field in update_fields.keys())
        values = list(update_fields.values())
        values.append(customer_id)

        sql = f"UPDATE customers SET {set_clause} WHERE id = %s"
        cursor.execute(sql, tuple(values))
        mydb.commit()

        cursor.close()
        mydb.close()

        return jsonify({
            "message": "Customer updated successfully",
            "updated_fields": list(update_fields.keys())
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



