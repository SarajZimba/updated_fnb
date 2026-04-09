# from flask import Blueprint, request, jsonify
# import mysql.connector
# from flask_cors import cross_origin
# import os
# from dotenv import load_dotenv
# load_dotenv()
# app_file70 = Blueprint('app_file70', __name__)
# from root.auth.check import token_auth
# import re

# def valid_date(datestring):
#     try:
#         regex = re.compile(r"^(\d{4})-(0[1-9]|1[0-2]|[1-9])-([1-9]|0[1-9]|[1-2]\d|3[0-1])$")
#         match = re.match(regex, datestring)
#         return match is not None
#     except ValueError:
#         return False
    
# def normalize_department(dept):
#     if not dept:
#         return "Unknown"
#     return dept.strip().title()



# @app_file70.route("/vendorwise-purchaseitem-lists", methods=["POST"])
# @cross_origin()
# def stats():
#     try:
#         mydb = mysql.connector.connect(
#             host=os.getenv('host'),
#             user=os.getenv('user'),
#             password=os.getenv('password'),
#             database=os.getenv('database')
#         )
#         cursor = mydb.cursor(buffered=True)

#         json = request.get_json()
#         # ------------------------
#         # Validate payload
#         # ------------------------
#         required_fields = ["token", "outlet", "dateStart", "dateEnd", "aggregated", "departmentwise"]
#         for field in required_fields:
#             if field not in json or not json[field]:
#                 return {"error": f"No {field} provided."}, 400

#         token = json["token"]
#         outlet = json["outlet"]
#         dateStart = json["dateStart"]
#         dateEnd = json["dateEnd"]
#         aggregated = json["aggregated"]
#         departmentwise = json["departmentwise"]  # New flag

#         if not valid_date(dateStart) or not valid_date(dateEnd):
#             return {"error": "Invalid date supplied."}, 400

#         if not token_auth(token):
#             return {"error": "Invalid token."}, 400

#         # ------------------------
#         # Queries
#         # ------------------------
#         if aggregated == "False":
#             base_query = """
#                 SELECT 
#                     a.Name,
#                     a.BrandName,
#                     a.Department,
#                     a.UnitsOrdered as ItemCount,
#                     a.UOM,
#                     a.Rate as ItemRate,
#                     (a.Rate*a.UnitsOrdered) as Total,
#                     b.Outlet_PurchaseReqID,
#                     b.Company_Name,
#                     b.purchaseBillNumber
#                 FROM intbl_purchaserequisition_contract a
#                 JOIN intbl_purchaserequisition b
#                     ON a.PurchaseReqID = b.IDIntbl_PurchaseRequisition
#                 WHERE b.ReceivedDate BETWEEN %s AND %s
#                   AND b.Outlet_Name = %s
#             """
#         elif aggregated == "True":
#             if departmentwise == "True":
#                 # Department first, then vendor, then item
#                 base_query = """
#                     SELECT 
#                         a.Department,
#                         b.Company_Name,
#                         a.Name,
#                         a.BrandName,
#                         SUM(a.UnitsOrdered) as ItemCount,
#                         a.UOM,
#                         AVG(a.Rate) as ItemRate,
#                         SUM(a.Rate*a.UnitsOrdered) as Total
#                     FROM intbl_purchaserequisition_contract a
#                     JOIN intbl_purchaserequisition b
#                         ON a.PurchaseReqID = b.IDIntbl_PurchaseRequisition
#                     WHERE b.ReceivedDate BETWEEN %s AND %s
#                       AND b.Outlet_Name = %s
#                     GROUP BY a.Department, b.Company_Name, a.Name, a.BrandName, a.UOM
#                     ORDER BY a.Department, b.Company_Name
#                 """
#             else:
#                 # Vendor + Item aggregation
#                 base_query = """
#                     SELECT 
#                         a.Name,
#                         a.BrandName,
#                         a.Department,
#                         SUM(a.UnitsOrdered) as ItemCount,
#                         a.UOM,
#                         AVG(a.Rate) as ItemRate,
#                         SUM(a.Rate*a.UnitsOrdered) as Total,
#                         b.Company_Name
#                     FROM intbl_purchaserequisition_contract a
#                     JOIN intbl_purchaserequisition b
#                         ON a.PurchaseReqID = b.IDIntbl_PurchaseRequisition
#                     WHERE b.ReceivedDate BETWEEN %s AND %s
#                       AND b.Outlet_Name = %s
#                     GROUP BY a.Name, a.BrandName, a.Department, a.UOM, b.Company_Name
#                 """
#         else:
#             return {"error": "Invalid aggregated value provided."}, 400

#         cursor.execute(base_query, (dateStart, dateEnd, outlet))
#         columns = [desc[0] for desc in cursor.description]
#         results = [dict(zip(columns, row)) for row in cursor.fetchall()]

#         # ------------------------
#         # Build response
#         # ------------------------
#         if departmentwise == "True":
#             # Group by Department → Vendor → Items
#             response_data = {}
#             department_totals = {}
#             for r in results:
#                 dept_ = r.get("Department", "Other").title()
#                 dept = normalize_department(dept_)

#                 vendor = r["Company_Name"]
#                 total = float(r["Total"])

#                 if dept not in response_data:
#                     response_data[dept] = {}

#                 if vendor not in response_data[dept]:
#                     response_data[dept][vendor] = {
#                         "items": [],
#                         "total": 0.0
#                     }

#                 r["ItemRate"] = round(r["ItemRate"], 2)
#                 r["Total"] = round(r["Total"], 2)
#                 response_data[dept][vendor]["items"].append(r)
#                 response_data[dept][vendor]["total"] += total

#                 # Track department totals
#                 if dept not in department_totals:
#                     department_totals[dept] = 0.0
#                 department_totals[dept] += total

#             # Build final response
#             final_response = []
#             for dept, vendors in response_data.items():
#                 dept_entry = {
#                     "department": dept,
#                     "vendors": []
#                 }
#                 for vendor, vdata in vendors.items():
#                     dept_entry["vendors"].append({
#                         "vendor": vendor,
#                         "items": vdata["items"],
#                         "total": round(vdata["total"], 2)
#                     })
#                 final_response.append(dept_entry)

#             dept_summary = {
#                 "department_totals": {k: round(v, 2) for k, v in department_totals.items()},
#                 "overall_total_purchase": round(sum(department_totals.values()), 2)
#             }

#             return {"departments": final_response, "summary": dept_summary}, 200

#         else:
#             # Normal vendor-wise response (dynamic department totals)
#             response_data = {}
#             department_totals = {}

#             for result in results:
#                 vendor = result["Company_Name"]
#                 dept = normalize_department(result.get("Department"))
#                 total = float(result["Total"])

#                 # Dynamic department totals
#                 if dept not in department_totals:
#                     department_totals[dept] = 0.0
#                 department_totals[dept] += total

#                 if vendor not in response_data:
#                     response_data[vendor] = {
#                         "items": [],
#                         "total": 0.0
#                     }

#                 result["ItemRate"] = round(result["ItemRate"], 2)
#                 result["Total"] = round(result["Total"], 2)

#                 response_data[vendor]["items"].append(result)
#                 response_data[vendor]["total"] += total

#             response = []
#             for vendor, value in response_data.items():
#                 response.append({
#                     "vendor": vendor,
#                     "items": value["items"],
#                     "total": round(value["total"], 2)
#                 })

#             dept_summary = {
#                 "department_totals": {k: round(v, 2) for k, v in department_totals.items()},
#                 "overall_total_purchase": round(sum(department_totals.values()), 2)
#             }

#             return {"vendors": response, "summary": dept_summary}, 200

#     except mysql.connector.Error as db_error:
#         return jsonify({"error": f"Database error: {str(db_error)}"}), 500
#     except Exception as error:
#         return jsonify({"error": f"Internal server error: {str(error)}"}), 500
#     finally:
#         if cursor:
#             cursor.close()
#         if mydb:
#             mydb.close()





from flask import Blueprint, request, jsonify
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv
load_dotenv()
app_file70 = Blueprint('app_file70', __name__)
from root.auth.check import token_auth
import re

def valid_date(datestring):
    try:
        regex = re.compile(r"^(\d{4})-(0[1-9]|1[0-2]|[1-9])-([1-9]|0[1-9]|[1-2]\d|3[0-1])$")
        match = re.match(regex, datestring)
        return match is not None
    except ValueError:
        return False
    
def normalize_department(dept):
    if not dept or dept == "None" or dept == "NULL":
        return "Other"
    return dept.strip().title()

@app_file70.route("/vendorwise-purchaseitem-lists", methods=["POST"])
@cross_origin()
def stats():
    try:
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password'),
            database=os.getenv('database')
        )
        cursor = mydb.cursor(buffered=True)

        json_data = request.get_json()
        # ------------------------
        # Validate payload
        # ------------------------
        required_fields = ["token", "outlet", "dateStart", "dateEnd", "aggregated", "departmentwise"]
        for field in required_fields:
            if field not in json_data or not json_data[field]:
                return {"error": f"No {field} provided."}, 400

        token = json_data["token"]
        outlet = json_data["outlet"]
        dateStart = json_data["dateStart"]
        dateEnd = json_data["dateEnd"]
        aggregated = json_data["aggregated"]
        departmentwise = json_data["departmentwise"]
        
        # Optional: include debit notes flag
        include_debitnotes = json_data.get("include_debitnotes", True)

        if not valid_date(dateStart) or not valid_date(dateEnd):
            return {"error": "Invalid date supplied."}, 400

        if not token_auth(token):
            return {"error": "Invalid token."}, 400

        # ------------------------
        # Query 1: Purchase Requisitions
        # ------------------------
        if aggregated == "False":
            purchase_query = """
                SELECT 
                    a.Name,
                    a.BrandName,
                    a.Department,
                    a.UnitsOrdered as ItemCount,
                    a.UOM,
                    a.Rate as ItemRate,
                    (a.Rate * a.UnitsOrdered) as Total,
                    b.Outlet_PurchaseReqID,
                    b.Company_Name as Vendor,
                    b.purchaseBillNumber,
                    'purchase' as source_type,
                    NULL as debitnote_id,
                    NULL as debitnote_number,
                    b.ReceivedDate as transaction_date,
                    a.ItemID
                FROM intbl_purchaserequisition_contract a
                INNER JOIN intbl_purchaserequisition b
                    ON a.PurchaseReqID = b.IDIntbl_PurchaseRequisition
                WHERE b.ReceivedDate BETWEEN %s AND %s
                  AND b.Outlet_Name = %s
            """
            cursor.execute(purchase_query, (dateStart, dateEnd, outlet))
        elif aggregated == "True":
            if departmentwise == "True":
                purchase_query = """
                    SELECT 
                        COALESCE(a.Department, 'Other') as Department,
                        b.Company_Name as Vendor,
                        a.Name,
                        COALESCE(a.BrandName, 'N/A') as BrandName,
                        SUM(a.UnitsOrdered) as ItemCount,
                        COALESCE(a.UOM, 'Units') as UOM,
                        ROUND(AVG(a.Rate), 2) as ItemRate,
                        ROUND(SUM(a.Rate * a.UnitsOrdered), 2) as Total,
                        'purchase' as source_type
                    FROM intbl_purchaserequisition_contract a
                    INNER JOIN intbl_purchaserequisition b
                        ON a.PurchaseReqID = b.IDIntbl_PurchaseRequisition
                    WHERE b.ReceivedDate BETWEEN %s AND %s
                      AND b.Outlet_Name = %s
                    GROUP BY a.Department, b.Company_Name, a.Name, a.BrandName, a.UOM
                """
            else:
                purchase_query = """
                    SELECT 
                        a.Name,
                        COALESCE(a.BrandName, 'N/A') as BrandName,
                        COALESCE(a.Department, 'Other') as Department,
                        SUM(a.UnitsOrdered) as ItemCount,
                        COALESCE(a.UOM, 'Units') as UOM,
                        ROUND(AVG(a.Rate), 2) as ItemRate,
                        ROUND(SUM(a.Rate * a.UnitsOrdered), 2) as Total,
                        b.Company_Name as Vendor,
                        'purchase' as source_type
                    FROM intbl_purchaserequisition_contract a
                    INNER JOIN intbl_purchaserequisition b
                        ON a.PurchaseReqID = b.IDIntbl_PurchaseRequisition
                    WHERE b.ReceivedDate BETWEEN %s AND %s
                      AND b.Outlet_Name = %s
                    GROUP BY a.Name, a.BrandName, a.Department, a.UOM, b.Company_Name
                """
            cursor.execute(purchase_query, (dateStart, dateEnd, outlet))
        else:
            return {"error": "Invalid aggregated value provided."}, 400

        columns = [desc[0] for desc in cursor.description]
        purchase_results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # ------------------------
        # Query 2: Debit Notes (if requested)
        # ------------------------
        debit_results = []
        if include_debitnotes:
            if aggregated == "False":
                debit_query = """
                    SELECT 
                        dn_details.ItemID,
                        dn_details.ItemName as Name,
                        COALESCE(pc.BrandName, 'N/A') as BrandName,
                        COALESCE(pc.Department, 'Other') as Department,
                        dn_details.Quantity as ItemCount,
                        COALESCE(pc.UOM, 'Units') as UOM,
                        ROUND(dn_details.unit_price, 2) as ItemRate,
                        ROUND(dn_details.total_amount, 2) as Total,
                        dm.Outlet_PurchaseReqID,
                        COALESCE(pr.Company_Name, 'Unknown Vendor') as Vendor,
                        dm.purchaseBillNumber,
                        'debitnote' as source_type,
                        dm.id as debitnote_id,
                        COALESCE(dm.debitnote_number, CONCAT('DN-', dm.id)) as debitnote_number,
                        dm.debit_date as transaction_date
                    FROM debitnote_details dn_details
                    INNER JOIN debitnote_master dm 
                        ON dn_details.debitnote_id = dm.id
                    LEFT JOIN intbl_purchaserequisition pr
                        ON dm.GRN = pr.GRN 
                        AND dm.Outlet_Name = pr.Outlet_Name
                    LEFT JOIN intbl_purchaserequisition_contract pc
                        ON pr.IDIntbl_PurchaseRequisition = pc.PurchaseReqID
                        AND dn_details.ItemID = pc.ItemID
                    WHERE dm.debit_date BETWEEN %s AND %s
                      AND dm.Outlet_Name = %s
                """
                cursor.execute(debit_query, (dateStart, dateEnd, outlet))
            elif aggregated == "True":
                if departmentwise == "True":
                    debit_query = """
                        SELECT 
                            COALESCE(pc.Department, 'Other') as Department,
                            COALESCE(pr.Company_Name, 'Unknown Vendor') as Vendor,
                            dn_details.ItemName as Name,
                            COALESCE(pc.BrandName, 'N/A') as BrandName,
                            SUM(dn_details.Quantity) as ItemCount,
                            COALESCE(pc.UOM, 'Units') as UOM,
                            ROUND(AVG(dn_details.unit_price), 2) as ItemRate,
                            ROUND(SUM(dn_details.total_amount), 2) as Total,
                            'debitnote' as source_type
                        FROM debitnote_details dn_details
                        INNER JOIN debitnote_master dm 
                            ON dn_details.debitnote_id = dm.id
                        LEFT JOIN intbl_purchaserequisition pr
                            ON dm.GRN = pr.GRN 
                            AND dm.Outlet_Name = pr.Outlet_Name
                        LEFT JOIN intbl_purchaserequisition_contract pc
                            ON pr.IDIntbl_PurchaseRequisition = pc.PurchaseReqID
                            AND dn_details.ItemID = pc.ItemID
                        WHERE dm.debit_date BETWEEN %s AND %s
                          AND dm.Outlet_Name = %s
                        GROUP BY pc.Department, pr.Company_Name, dn_details.ItemName, pc.BrandName, pc.UOM
                    """
                else:
                    debit_query = """
                        SELECT 
                            dn_details.ItemName as Name,
                            COALESCE(pc.BrandName, 'N/A') as BrandName,
                            COALESCE(pc.Department, 'Other') as Department,
                            SUM(dn_details.Quantity) as ItemCount,
                            COALESCE(pc.UOM, 'Units') as UOM,
                            ROUND(AVG(dn_details.unit_price), 2) as ItemRate,
                            ROUND(SUM(dn_details.total_amount), 2) as Total,
                            COALESCE(pr.Company_Name, 'Unknown Vendor') as Vendor,
                            'debitnote' as source_type
                        FROM debitnote_details dn_details
                        INNER JOIN debitnote_master dm 
                            ON dn_details.debitnote_id = dm.id
                        LEFT JOIN intbl_purchaserequisition pr
                            ON dm.GRN = pr.GRN 
                            AND dm.Outlet_Name = pr.Outlet_Name
                        LEFT JOIN intbl_purchaserequisition_contract pc
                            ON pr.IDIntbl_PurchaseRequisition = pc.PurchaseReqID
                            AND dn_details.ItemID = pc.ItemID
                        WHERE dm.debit_date BETWEEN %s AND %s
                          AND dm.Outlet_Name = %s
                        GROUP BY dn_details.ItemName, pc.BrandName, pc.Department, pc.UOM, pr.Company_Name
                    """
                cursor.execute(debit_query, (dateStart, dateEnd, outlet))
            
            debit_columns = [desc[0] for desc in cursor.description]
            debit_results = [dict(zip(debit_columns, row)) for row in cursor.fetchall()]

        # ------------------------
        # Combine Results
        # ------------------------
        all_results = purchase_results + debit_results

        # ------------------------
        # Build response based on departmentwise flag
        # ------------------------
        if departmentwise == "True":
            # Group by Department → Vendor → Items
            response_data = {}
            department_totals = {}
            
            for r in all_results:
                dept = normalize_department(r.get("Department", "Other"))
                vendor = r["Vendor"]
                total = float(r["Total"])
                
                # Initialize department
                if dept not in response_data:
                    response_data[dept] = {}
                
                # Initialize vendor within department
                if vendor not in response_data[dept]:
                    response_data[dept][vendor] = {
                        "items": [],
                        "total": 0.0
                    }
                
                # Format numeric values
                if r.get("ItemRate"):
                    r["ItemRate"] = round(float(r["ItemRate"]), 2)
                r["Total"] = round(total, 2)
                if r.get("ItemCount"):
                    r["ItemCount"] = float(r["ItemCount"])
                
                # Add item to vendor's list (ALWAYS add regardless of type)
                response_data[dept][vendor]["items"].append(r)
                
                # ONLY add to totals for purchases (exclude debit notes)
                if r['source_type'] != 'debitnote':
                    response_data[dept][vendor]["total"] += total
                    
                    # Track department totals only for purchases
                    if dept not in department_totals:
                        department_totals[dept] = 0.0
                    department_totals[dept] += total
            
            # Build final response
            final_response = []
            for dept, vendors in response_data.items():
                dept_entry = {
                    "department": dept,
                    "vendors": []
                }
                for vendor, vdata in vendors.items():
                    dept_entry["vendors"].append({
                        "vendor": vendor,
                        "items": vdata["items"],
                        "total": round(vdata["total"], 2)
                    })
                final_response.append(dept_entry)
            
            # Sort departments alphabetically
            final_response.sort(key=lambda x: x["department"])
            
            dept_summary = {
                "department_totals": {k: round(v, 2) for k, v in department_totals.items()},
                "overall_total_purchase": round(sum(department_totals.values()), 2)
            }
            
            return {
                "departments": final_response, 
                "summary": dept_summary,
                "includes_debitnotes": include_debitnotes
            }, 200
        
        else:
            # Normal vendor-wise response (non-departmentwise)
            response_data = {}
            department_totals = {}
            
            for r in all_results:
                vendor = r["Vendor"]
                dept = normalize_department(r.get("Department", "Other"))
                total = float(r["Total"])
                
                # Initialize vendor if not exists
                if vendor not in response_data:
                    response_data[vendor] = {
                        "items": [],
                        "total": 0.0
                    }
                
                # Format numeric values
                if r.get("ItemRate"):
                    r["ItemRate"] = round(float(r["ItemRate"]), 2)
                r["Total"] = round(total, 2)
                if r.get("ItemCount"):
                    r["ItemCount"] = float(r["ItemCount"])
                
                # Add item to vendor's list (ALWAYS add regardless of type)
                response_data[vendor]["items"].append(r)
                
                # ONLY add to totals for purchases (exclude debit notes)
                if r['source_type'] != 'debitnote':
                    response_data[vendor]["total"] += total
                    
                    # Also add to department totals only for purchases
                    if dept not in department_totals:
                        department_totals[dept] = 0.0
                    department_totals[dept] += total
            
            # Build response
            response = []
            for vendor, value in response_data.items():
                response.append({
                    "vendor": vendor,
                    "items": value["items"],
                    "total": round(value["total"], 2)
                })
            
            # Sort vendors alphabetically
            response.sort(key=lambda x: x["vendor"])
            
            dept_summary = {
                "department_totals": {k: round(v, 2) for k, v in department_totals.items()},
                "overall_total_purchase": round(sum(department_totals.values()), 2)
            }
            
            return {
                "vendors": response, 
                "summary": dept_summary,
                "includes_debitnotes": include_debitnotes
            }, 200
    
    except mysql.connector.Error as db_error:
        return jsonify({"error": f"Database error: {str(db_error)}"}), 500
    except Exception as error:
        return jsonify({"error": f"Internal server error: {str(error)}"}), 500
    finally:
        if cursor:
            cursor.close()
        if mydb:
            mydb.close()