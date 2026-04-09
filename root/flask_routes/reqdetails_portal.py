from flask import Blueprint, request
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv

load_dotenv()

# Blueprint initialization
app_file56 = Blueprint('app_file56', __name__)

# Function to add data to the dictionary, handling history and last purchase logic
def addDatatoDict(dicdata=0, data=0):
    _data = []
    for i in range(len(data)):
        if len(dicdata[i]) != 0:
            temp = data[i]
            temp1 = dicdata[i]
            key = temp1.keys()
            value = temp1.values()
            a = list(key)
            b = list(value)
            temp[a[0]] = float(b[0])
            _data.append(temp)  
        else:
            _data.append(data[i])
    return _data

@app_file56.route("/reqdetails_portal/<int:id>", methods=["GET"])
@cross_origin()
def reqdetails(id):
    try:
        # Establish database connection
        mydb = mysql.connector.connect(
            host=os.getenv('host'), 
            user=os.getenv('user'), 
            password=os.getenv('password')
        )
        cursor = mydb.cursor(buffered=True)
        
        # Select the database
        database_sql = "USE {};".format(os.getenv('database'))
        cursor.execute(database_sql)

        limit = request.args.get("limit", 10)  # Default limit to 5 if not provided        

        # Fetch main data with last purchase rate, using IFNULL to return 0 if last_purchase is NULL
        sql = f"""
        SELECT *, (
                    SELECT 
                        IFNULL(Rate, 0) AS last_purchase
                    FROM 
                        intbl_purchaserequisition_contract 
                    WHERE 
                        ItemID = a.ItemID 
                        AND PurchaseReqID != a.PurchaseReqID 
                    ORDER BY 
                        PurchaseReqID DESC 
                    LIMIT 1
                ) AS last_purchase , ROUND(UnitsOrdered * Rate, 2) as Total
        FROM 
            intbl_purchaserequisition_contract a 
        WHERE 
            a.PurchaseReqID=%s 
        ORDER BY ItemID DESC;
        """
        cursor.execute(sql, (id,))
        desc = cursor.description
        data = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]

        # Prepare to fetch history for each item
        for item in data:
            item_id = item['ItemID']

            # Fetch the history for each item, limit to the given number of records (default limit=5)
            sql = f"""
            SELECT a.rate, a.UnitsOrdered, b.ReceivedDate
            FROM intbl_purchaserequisition_contract a
            JOIN intbl_purchaserequisition b 
            ON a.PurchaseReqID = b.IDIntbl_PurchaseRequisition
            WHERE a.ItemID = %s
            ORDER BY a.PurchaseReqID DESC
            LIMIT %s;
            """
            cursor.execute(sql, (item_id, int(limit)))
            history_desc = cursor.description
            history_data = [
                dict(zip([col[0] for col in history_desc], row)) 
                for row in cursor.fetchall()
            ]
            item['history'] = history_data  # Add history data to the item block

        # Handle the logic for last_purchase: If history is empty or NULL, set it to 0
        for item in data:
            if not item['history']:  # No history entries
                item['last_purchase'] = 0.0
            elif item['last_purchase'] is None:  # If last_purchase is None
                item['last_purchase'] = 0.0

            item['last_purchase'] = float(item['last_purchase'])

        # Return the combined data including history
        response_data = {"intbl_purchaserequisition_contract": data}
        
        # Close the database connection
        mydb.close()
        
        return response_data, 200

    except Exception as error:
        # In case of error, return the error message
        data = {'error': str(error)}
        return data, 400


# from flask import Blueprint, request, jsonify
# import mysql.connector
# from flask_cors import cross_origin
# import os
# from dotenv import load_dotenv

# load_dotenv()

# app_file56 = Blueprint('app_file56', __name__)

# # Helper to merge last_purchase into main data
# def addDatatoDict(dicdata=0, data=0):
#     _data = []
#     for i in range(len(data)):
#         if len(dicdata[i]) != 0:
#             temp = data[i]
#             temp1 = dicdata[i]
#             key = list(temp1.keys())
#             value = list(temp1.values())
#             temp[key[0]] = float(value[0])
#             _data.append(temp)  
#         else:
#             _data.append(data[i])
#     return _data

# @app_file56.route("/reqdetails_portal/<int:id>", methods=["GET"])
# @cross_origin()
# def reqdetails_portal(id):
#     try:
#         # ------------------ DB Connection ------------------
#         mydb = mysql.connector.connect(
#             host=os.getenv('host'),
#             user=os.getenv('user'),
#             password=os.getenv('password'),
#             database=os.getenv('database')
#         )
#         cursor = mydb.cursor(dictionary=True, buffered=True)

#         limit = request.args.get("limit", 5)  # default history limit

#         # ------------------ 1️⃣ Get outlet name ------------------
#         cursor.execute("""
#             SELECT Outlet_Name
#             FROM intbl_purchaserequisition
#             WHERE IDIntbl_PurchaseRequisition = %s
#         """, (id,))
#         row = cursor.fetchone()
#         if not row:
#             return {"error": "Purchase requisition not found"}, 404

#         outlet_name = row["Outlet_Name"]

#         # ------------------ 2️⃣ Get current requisition items ------------------
#         cursor.execute("""
#             SELECT *, ROUND(UnitsOrdered * Rate, 2) AS Total
#             FROM intbl_purchaserequisition_contract
#             WHERE PurchaseReqID = %s
#             ORDER BY ItemID DESC
#         """, (id,))
#         data = cursor.fetchall()

#         # ------------------ 3️⃣ Get last purchase from same outlet ------------------
#         query = []
#         for item in data:
#             sql = """
#                 SELECT a.Rate AS last_purchase
#                 FROM intbl_purchaserequisition_contract a
#                 JOIN intbl_purchaserequisition b
#                     ON a.PurchaseReqID = b.IDIntbl_PurchaseRequisition
#                 WHERE a.ItemID = %s
#                 AND b.Outlet_Name = %s
#                 AND a.PurchaseReqID != %s
#                 ORDER BY a.PurchaseReqID DESC
#                 LIMIT 1
#             """
#             query.append((sql, (item["ItemID"], outlet_name, id)))

#         _list = []
#         for q, params in query:
#             cursor.execute(q, params)
#             result = cursor.fetchall()
#             _list.append(result)

#         _data = []
#         for i in range(len(_list)):
#             if len(_list[i]) == 0:
#                 _data.append({"last_purchase": 0})
#             else:
#                 _data.append(_list[i][0])

#         # ------------------ 4️⃣ Merge last_purchase into main items ------------------
#         data = addDatatoDict(_data, data)

#         # ------------------ 5️⃣ Optional: Add item history ------------------
#         for item in data:
#             item_id = item["ItemID"]
#             cursor.execute("""
#                 SELECT a.Rate, a.UnitsOrdered, b.ReceivedDate
#                 FROM intbl_purchaserequisition_contract a
#                 JOIN intbl_purchaserequisition b
#                     ON a.PurchaseReqID = b.IDIntbl_PurchaseRequisition
#                 WHERE a.ItemID = %s
#                 ORDER BY a.PurchaseReqID DESC
#                 LIMIT %s
#             """, (item_id, int(limit)))
#             history_desc = cursor.description
#             history_data = [
#                 dict(zip([col[0] for col in history_desc], row))
#                 for row in cursor.fetchall()
#             ]
#             item["history"] = history_data

#         response_data = {"intbl_purchaserequisition_contract": data}

#         cursor.close()
#         mydb.close()

#         return response_data, 200

#     except Exception as error:
#         return {"error": str(error)}, 400
