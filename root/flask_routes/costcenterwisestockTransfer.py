# from flask import Flask, Blueprint,request, jsonify
# import mysql.connector
# from flask_cors import cross_origin
# import os
# from dotenv import load_dotenv
# load_dotenv()
# app_file60= Blueprint('app_file60',__name__)
# from root.auth.check import token_auth

# @app_file60.route('/costcenterwiseAllStockTransfers', methods=["POST"])
# @cross_origin()
# def getAllStockTransfers():
#     try:
#         # Connect to the database
#         mydb = mysql.connector.connect(user=os.getenv('user'), password=os.getenv('password'), host=os.getenv('host'))
#         cursor = mydb.cursor(buffered=True)

#         # Use the correct database
#         database_sql = "USE {};".format(os.getenv('database'))
#         cursor.execute(database_sql)

#         # Get JSON data from the request
#         json = request.get_json()

#         startDate = json["startDate"]
#         endDate = json["endDate"]
#         outlet = json["outlet"]

#         # Query to get the stock requisition data filtered by date range and outlet
#         query_storerequisition = """
#             SELECT `idintblStoreRequisition`, `Date`, `CostCenter`, `Outlet`, `OutletREQID`
#             FROM `intblstorerequisition`
#             WHERE `Date` BETWEEN %s AND %s AND `Outlet` = %s
#         """
#         cursor.execute(query_storerequisition, (startDate, endDate, outlet))
#         store_requisitions = cursor.fetchall()

#         if not store_requisitions:
#             return jsonify({"error": "No stock requisitions found!"}), 404

#         all_requisitions = {}

#         # Iterate over all store requisitions
#         for store_requisition in store_requisitions:
#             store_req_id = store_requisition[0]
#             cost_center = store_requisition[2]

#             # Fetch item details for each store requisition
#             query_storereqdetails = """
#                 SELECT `ItemName`, `GroupName`, `BrandName`, `Amount`, `UOM`, `Rate`
#                 FROM `intblstorereqdetails`
#                 WHERE `StoreReqID` = %s order by GroupName
#             """
#             cursor.execute(query_storereqdetails, (store_req_id,))
#             store_itemdetails = cursor.fetchall()

#             # If the cost center does not exist in the dictionary, create it
#             if cost_center not in all_requisitions:
#                 # all_requisitions[cost_center] = []
#                 all_requisitions[cost_center] = {"item_details": [], "grand_total": 0}
#             # grand_total = 0
#             # Iterate over the item details and group by ItemName and Rate
#             for item in store_itemdetails:
#                 item_name = item[0]
#                 rate = item[5]
#                 amount = item[3]
#                 # Check if the item with the same name and rate already exists in the list for this cost center
#                 found = False
#                 for entry in all_requisitions[cost_center]["item_details"]:
#                     if entry["ItemName"] == item_name and entry["Rate"] == rate:
#                         # If found, sum the amounts
#                         entry["Amount"] += amount
#                         entry["Amount"] = round(entry["Amount"], 2)
#                         entry["Total"] =  round(entry["Rate"] * entry["Amount"], 2)
#                         # all_requisitions[cost_center]["grand_total"] += entry["Total"]
#                         found = True
#                         break

#                 # If not found, add a new entry for this item
#                 if not found:
#                     all_requisitions[cost_center]["item_details"].append({
#                         "ItemName": item_name,
#                         "Rate": rate,
#                         "Amount": round(amount, 2),
#                         "UOM": item[4],
#                         "GroupName": item[1],
#                         "BrandName": item[2],
#                         "Total": round(rate * amount, 2)
#                     })
#                     # all_requisitions[cost_center]["grand_total"] += round(rate * amount, 2)
#         # Format the data as a list of cost centers with their items grouped and summed
#         final_response = []
#         for cost_center, items in all_requisitions.items():
#             grand_total = sum(data["Total"] for data in items["item_details"])  # Calculate grand total
#             sorted_item_details = sorted(items["item_details"], key=lambda x: x["GroupName"])
#             final_response.append({
#                 "CostCenter": cost_center,
#                 "ItemDetailsList": sorted_item_details,
#                 "grand_total": grand_total,
#             })

#         return jsonify(final_response)

#     except Exception as e:
#         data = {"error": str(e)}
#         return data, 400

#     finally:
#         mydb.close()


from flask import Blueprint, request, jsonify
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv
load_dotenv()

app_file60 = Blueprint('app_file60', __name__)
from root.auth.check import token_auth


@app_file60.route('/costcenterwiseAllStockTransfers', methods=["POST"])
@cross_origin()
def getAllStockTransfers():
    try:
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password')
        )
        cursor = mydb.cursor(buffered=True)

        cursor.execute(f"USE {os.getenv('database')}")

        json = request.get_json()

        startDate = json["startDate"]
        endDate = json["endDate"]
        outlet = json["outlet"]

        # Fetch store requisitions
        query_storerequisition = """
            SELECT idintblStoreRequisition, Date, CostCenter
            FROM intblstorerequisition
            WHERE Date BETWEEN %s AND %s AND Outlet = %s
        """
        cursor.execute(query_storerequisition, (startDate, endDate, outlet))
        store_requisitions = cursor.fetchall()

        if not store_requisitions:
            return jsonify({"error": "No stock requisitions found"}), 404

        all_requisitions = {}

        for store_req in store_requisitions:
            store_req_id = store_req[0]
            cost_center = store_req[2]

            query_storereqdetails = """
                SELECT ItemName, GroupName, BrandName, Amount, UOM, Rate
                FROM intblstorereqdetails
                WHERE StoreReqID = %s
            """
            cursor.execute(query_storereqdetails, (store_req_id,))
            items = cursor.fetchall()

            if cost_center not in all_requisitions:
                all_requisitions[cost_center] = {"groups": {}}

            for item in items:
                item_name = item[0]
                group_raw = item[1]
                brand = item[2]
                amount = item[3]
                uom = item[4]
                rate = item[5]

                # Normalize group name
                group_key = group_raw.strip().lower()

                groups = all_requisitions[cost_center]["groups"]

                if group_key not in groups:
                    groups[group_key] = {
                        "GroupName": group_raw.title(),
                        "group_total": 0,
                        "items": []
                    }

                group_items = groups[group_key]["items"]

                found = False
                for entry in group_items:
                    if entry["ItemName"] == item_name and entry["Rate"] == rate:
                        entry["Amount"] += amount
                        entry["Amount"] = round(entry["Amount"], 2)
                        entry["Total"] = round(entry["Rate"] * entry["Amount"], 2)
                        found = True
                        break

                if not found:
                    group_items.append({
                        "ItemName": item_name,
                        "Rate": rate,
                        "Amount": round(amount, 2),
                        "UOM": uom,
                        "BrandName": brand,
                        "Total": round(rate * amount, 2)
                    })

        # Build final response
        final_response = []

        for cost_center, data in all_requisitions.items():
            group_list = []
            grand_total = 0

            # Sort groups alphabetically
            for group in sorted(data["groups"].values(), key=lambda x: x["GroupName"]):
                group_total = sum(item["Total"] for item in group["items"])
                group["group_total"] = round(group_total, 2)
                grand_total += group_total

                # Sort items inside group
                group["items"] = sorted(group["items"], key=lambda x: x["ItemName"])

                group_list.append(group)

            final_response.append({
                "CostCenter": cost_center,
                "GroupWiseItemDetails": group_list,
                "grand_total": round(grand_total, 2)
            })

        return jsonify(final_response), 200

    except Exception as e:
        return {"error": str(e)}, 400

    finally:
        if mydb:
            mydb.close()