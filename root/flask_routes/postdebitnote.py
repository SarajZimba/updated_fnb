
# from flask import Blueprint, request, jsonify
# import mysql.connector
# from flask_cors import cross_origin
# import os
# from dotenv import load_dotenv
# load_dotenv()

# app_file224 = Blueprint('app_file224', __name__)
# from root.auth.check import token_auth

# @app_file224.route("/debitnote", methods=["POST"])
# @cross_origin()
# def create_debitnote():
#     try:
#         # -------- DATABASE CONNECTION --------
#         mydb = mysql.connector.connect(
#             host=os.getenv("host"),
#             user=os.getenv("user"),
#             password=os.getenv("password"),
#             database=os.getenv("database")
#         )
#         cursor = mydb.cursor(dictionary=True)

#         # -------- TOKEN AUTHENTICATION --------
#         auth_header = request.headers.get("Authorization")
#         if not auth_header:
#             return {"error": "No token provided."}, 400
#         try:
#             token = auth_header.split(" ")[1]
#         except:
#             return {"error": "Invalid Authorization header format."}, 400
#         if not token_auth(token):
#             return {"error": "Invalid token."}, 400

#         # -------- GET DATA FROM REQUEST BODY --------
#         data = request.get_json()
        
#         # Validate required fields
#         required_fields = ['GRN', 'Outlet_PurchaseReqID', 'Outlet_Name', 'ItemID', 'ItemName', 'Quantity']
#         for field in required_fields:
#             if field not in data:
#                 return {"error": f"Missing required field: {field}"}, 400
        
#         # Validate quantity is positive
#         if data['Quantity'] <= 0:
#             return {"error": "Quantity must be greater than 0"}, 400

#         # -------- INSERT INTO DEBITNOTE TABLE --------
#         insert_query = """
#             INSERT INTO debitnote (
#                 GRN, 
#                 Outlet_PurchaseReqID, 
#                 Outlet_Name, 
#                 ItemID, 
#                 ItemName, 
#                 Quantity,
#                 created_at,
#                 updated_at
#             ) VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
#         """
        
#         insert_values = (
#             data['GRN'],
#             data['Outlet_PurchaseReqID'],
#             data['Outlet_Name'],
#             data['ItemID'],
#             data['ItemName'],
#             data['Quantity']
#         )
        
#         cursor.execute(insert_query, insert_values)
#         mydb.commit()
        
#         # Get the inserted ID
#         new_id = cursor.lastrowid
        
#         # Fetch the newly created record
#         cursor.execute("SELECT * FROM debitnote WHERE id = %s", (new_id,))
#         new_debitnote = cursor.fetchone()
        
#         mydb.close()
        
#         return jsonify({
#             "message": "Debit note created successfully",
#             "debitnote": new_debitnote
#         }), 201
        
#     except mysql.connector.Error as e:
#         return {"error": f"Database error: {str(e)}"}, 500
#     except Exception as e:
#         return {"error": str(e)}, 500


from flask import Blueprint, request, jsonify
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv
load_dotenv()

app_file224 = Blueprint('app_file224', __name__)
from root.auth.check import token_auth

# @app_file224.route("/debitnote", methods=["POST"])
# @cross_origin()
# def create_debitnote():
#     try:
#         # -------- DATABASE CONNECTION --------
#         mydb = mysql.connector.connect(
#             host=os.getenv("host"),
#             user=os.getenv("user"),
#             password=os.getenv("password"),
#             database=os.getenv("database")
#         )
#         cursor = mydb.cursor(dictionary=True)

#         # -------- TOKEN AUTH --------
#         auth_header = request.headers.get("Authorization")
#         if not auth_header:
#             return {"error": "No token provided."}, 400

#         try:
#             token = auth_header.split(" ")[1]
#         except:
#             return {"error": "Invalid Authorization header format."}, 400

#         if not token_auth(token):
#             return {"error": "Invalid token."}, 400

#         # -------- REQUEST DATA --------
#         data = request.get_json()

#         required_fields = ['GRN', 'Outlet_PurchaseReqID', 'Outlet_Name', 'items']
#         for field in required_fields:
#             if field not in data:
#                 return {"error": f"Missing required field: {field}"}, 400

#         if not isinstance(data['items'], list) or len(data['items']) == 0:
#             return {"error": "Items must be a non-empty list"}, 400

#         # -------- OPTIONAL FIELDS --------
#         debit_date = data.get("date")  # format: YYYY-MM-DD
#         purchase_bill = str(data.get("purchaseBillNumber")) if data.get("purchaseBillNumber") else None
#         tax_amount = float(data.get("taxAmt", 0))


#         inserted_items = []

#         # -------- INSERT ITEMS --------
#         for item in data['items']:
#             # Validate item fields
#             item_required = ['ItemID', 'ItemName', 'Quantity']
#             for field in item_required:
#                 if field not in item:
#                     return {"error": f"Missing {field} in items"}, 400

#             if float(item['Quantity']) <= 0:
#                 return {"error": "Quantity must be greater than 0"}, 400

#             unit_price = float(item.get("unit_price", 0))
#             total_amt = float(item.get("totalAmt", item['Quantity'] * unit_price))

#             insert_query = """
#                 INSERT INTO debitnote (
#                     GRN,
#                     Outlet_PurchaseReqID,
#                     Outlet_Name,
#                     ItemID,
#                     ItemName,
#                     Quantity,
#                     unit_price,
#                     total_amount,
#                     purchaseBillNumber,
#                     tax_amount,
#                     debit_date,
#                     created_at,
#                     updated_at
#                 ) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
#             """

#             values = (
#                 data['GRN'],
#                 data['Outlet_PurchaseReqID'],
#                 data['Outlet_Name'],
#                 item['ItemID'],
#                 item['ItemName'],
#                 item['Quantity'],
#                 unit_price,
#                 total_amt,
#                 purchase_bill,
#                 tax_amount,
#                 debit_date
#             )

#             cursor.execute(insert_query, values)

#             inserted_items.append({
#                 "ItemID": item['ItemID'],
#                 "ItemName": item['ItemName'],
#                 "Quantity": item['Quantity'],
#                 "unit_price": unit_price,
#                 "total_amount": total_amt
#             })

#         mydb.commit()

#         mydb.close()

#         return jsonify({
#             "message": "Debit note created successfully",
#             "purchaseBillNumber": purchase_bill,
#             "tax_amount": tax_amount,
#             "items_inserted": inserted_items
#         }), 201

#     except mysql.connector.Error as e:
#         return {"error": f"Database error: {str(e)}"}, 500
#     except Exception as e:
#         return {"error": str(e)}, 500


@app_file224.route("/debitnote", methods=["POST"])
@cross_origin()
def create_debitnote():
    try:
        # -------- DATABASE CONNECTION --------
        mydb = mysql.connector.connect(
            host=os.getenv("host"),
            user=os.getenv("user"),
            password=os.getenv("password"),
            database=os.getenv("database")
        )
        cursor = mydb.cursor(dictionary=True)

        # -------- TOKEN AUTH --------
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return {"error": "No token provided."}, 400

        try:
            token = auth_header.split(" ")[1]
        except:
            return {"error": "Invalid Authorization header format."}, 400

        if not token_auth(token):
            return {"error": "Invalid token."}, 400

        # -------- REQUEST DATA --------
        data = request.get_json()

        required_fields = ['GRN', 'Outlet_PurchaseReqID', 'Outlet_Name', 'items', 'totalAmt']
        for field in required_fields:
            if field not in data:
                return {"error": f"Missing required field: {field}"}, 400

        if not isinstance(data['items'], list) or len(data['items']) == 0:
            return {"error": "Items must be a non-empty list"}, 400

        # -------- OPTIONAL FIELDS --------
        debit_date = data.get("date")
        purchase_bill = str(data.get("purchaseBillNumber")) if data.get("purchaseBillNumber") else None
        tax_amount = float(data.get("taxAmt", 0))

        # -------- CALCULATE TOTAL --------
        grand_total = 0
        prepared_items = []

        for item in data['items']:
            item_required = ['ItemID', 'ItemName', 'Quantity']
            for field in item_required:
                if field not in item:
                    return {"error": f"Missing {field} in items"}, 400

            qty = float(item['Quantity'])
            if qty <= 0:
                return {"error": "Quantity must be greater than 0"}, 400

            unit_price = float(item.get("unit_price", 0))
            total_amt = float(item.get("totalAmt", qty * unit_price))
            uom = item.get("uom", None)

            grand_total += total_amt

            prepared_items.append({
                "ItemID": item['ItemID'],
                "ItemName": item['ItemName'],
                "Quantity": qty,
                "unit_price": unit_price,
                "total_amount": total_amt,
                "uom": uom,
            })

        # -------- INSERT INTO MASTER --------
        master_query = """
            INSERT INTO debitnote_master (
                GRN,
                Outlet_PurchaseReqID,
                Outlet_Name,
                purchaseBillNumber,
                tax_amount,
                debit_date,
                total_amount,
                created_at,
                updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        """

        cursor.execute(master_query, (
            data['GRN'],
            data['Outlet_PurchaseReqID'],
            data['Outlet_Name'],
            purchase_bill,
            tax_amount,
            debit_date,
            data['totalAmt']
        ))

        debitnote_id = cursor.lastrowid

        # -------- INSERT INTO DETAILS --------
        detail_query = """
            INSERT INTO debitnote_details (
                debitnote_id,
                ItemID,
                ItemName,
                Quantity,
                unit_price,
                total_amount,
                uom
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        for item in prepared_items:
            cursor.execute(detail_query, (
                debitnote_id,
                item['ItemID'],
                item['ItemName'],
                item['Quantity'],
                item['unit_price'],
                item['total_amount'],
                item['uom'],
            ))

        mydb.commit()
        mydb.close()

        return jsonify({
            "message": "Debit note created successfully",
            "debitnote_id": debitnote_id,
            "grand_total": data['totalAmt'],
            "tax_amount": tax_amount,
            "items": prepared_items
        }), 201

    except mysql.connector.Error as e:
        return {"error": f"Database error: {str(e)}"}, 500
    except Exception as e:
        return {"error": str(e)}, 500