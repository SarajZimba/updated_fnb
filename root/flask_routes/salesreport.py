# from flask import Blueprint, request
# import mysql.connector
# from flask_cors import cross_origin
# import os
# from dotenv import load_dotenv
# from root.auth.check import token_auth

# load_dotenv()
# app_file7 = Blueprint('app_file7', __name__)

# @app_file7.route("/saleshistory", methods=["POST"])
# @cross_origin()
# def stats():
#     try:
#         mydb = mysql.connector.connect(
#             host=os.getenv('host'),
#             user=os.getenv('user'),
#             password=os.getenv('password'),
#             database=os.getenv('database')
#         )
#         cursor = mydb.cursor()
#         json = request.get_json()

#         if "token" not in json or not json["token"]:
#             return {"error": "No token provided."}, 400

#         token = json["token"]
#         if not token_auth(token):
#             return {"error": "Invalid token."}, 400

#         if not all(k in json for k in ("outlet", "dateStart", "dateEnd")):
#             return {"error": "Some fields are missing"}, 400

#         outlet = json["outlet"]
#         startDate = json["dateStart"]
#         endDate = json["dateEnd"]

#         # Order summary
#         cursor.execute("""
#             SELECT Date, bill_no, (Total - serviceCharge - VAT) as Subtotal,
#                    Outlet_OrderID as id, serviceCharge, VAT, Total,
#                    DiscountAmt, PaymentMode, GuestName
#             FROM tblorderhistory
#             WHERE Date BETWEEN %s AND %s AND Outlet_Name = %s AND bill_no != ''
#             ORDER BY CAST(bill_no AS UNSIGNED)
#         """, (startDate, endDate, outlet))

#         row_headers = [x[0] for x in cursor.description]
#         json_data = [dict(zip(row_headers, row)) for row in cursor.fetchall()]

#         # Overall stats
#         cursor.execute("""
#             SELECT SUM(DiscountAmt) AS DiscountAmountSum,
#                    SUM(Total - serviceCharge - VAT) AS SubtotalAmountSum,
#                    SUM(Total) AS TotalSum, SUM(VAT) AS VatSum,
#                    SUM(serviceCharge) AS ServiceChargeSum,
#                    SUM(NoOfGuests) AS TotalGuestsServed,
#                    COUNT(idtblorderHistory) AS TotalOrders,
#                    COUNT(DISTINCT Date) AS DaysOperated
#             FROM tblorderhistory
#             WHERE Date BETWEEN %s AND %s AND Outlet_Name = %s AND bill_no != ''
#         """, (startDate, endDate, outlet))

#         row_headers = [x[0] for x in cursor.description]
#         stats_data = [dict(zip(row_headers, row)) for row in cursor.fetchall()]
#         stats_data[0]["orderDetails"] = json_data

#         # Typewise item queries
#         def fetch_items(item_type):
#             cursor.execute(f"""
#                 SELECT a.Description, a.itemName, a.itemRate as itemrate, a.ItemType,
#                        SUM(a.count) AS quantity, SUM(a.Total) AS total
#                 FROM tblorder_detailshistory a
#                 JOIN tblorderhistory b ON a.order_ID = b.idtblorderHistory
#                 WHERE a.ItemType = %s AND b.Outlet_Name = %s AND b.Date BETWEEN %s AND %s AND b.bill_no != ''
#                 GROUP BY a.Description, a.itemName, a.itemRate, a.ItemType
#                 ORDER BY a.Description, quantity DESC
#             """, (item_type, outlet, startDate, endDate))
#             return [dict(zip([x[0] for x in cursor.description], row)) for row in cursor.fetchall()]

#         def fetch_group_totals(item_type):
#             cursor.execute("""
#                 SELECT SUM(a.Total) AS groupTotal, a.Description AS groupName
#                 FROM tblorder_detailshistory a
#                 JOIN tblorderhistory b ON a.order_ID = b.idtblorderHistory
#                 WHERE a.ItemType = %s AND b.Outlet_Name = %s AND b.Date BETWEEN %s AND %s AND b.bill_no != ''
#                 GROUP BY a.Description
#                 ORDER BY groupTotal DESC
#             """, (item_type, outlet, startDate, endDate))
#             return [dict(zip([x[0] for x in cursor.description], row)) for row in cursor.fetchall()]

#         # Fetch and combine
#         food_items = fetch_items("Food")
#         beverage_items = fetch_items("Beverage")
#         other_items = fetch_items("Other")

#         food_group = fetch_group_totals("Food")
#         beverage_group = fetch_group_totals("Beverage")
#         other_group = fetch_group_totals("Other")

#         # Summarized totals
#         cursor.execute("""
#             SELECT 
#                 (SELECT SUM(a.Total) FROM tblorder_detailshistory a JOIN tblorderhistory b ON a.order_ID = b.idtblorderHistory WHERE a.ItemType='Food' AND b.Outlet_Name = %s AND b.Date BETWEEN %s AND %s AND b.bill_no != '') AS foodtotal,
#                 (SELECT SUM(a.count) FROM tblorder_detailshistory a JOIN tblorderhistory b ON a.order_ID = b.idtblorderHistory WHERE a.ItemType='Food' AND b.Outlet_Name = %s AND b.Date BETWEEN %s AND %s AND b.bill_no != '') AS foodquantity,
#                 (SELECT SUM(a.Total) FROM tblorder_detailshistory a JOIN tblorderhistory b ON a.order_ID = b.idtblorderHistory WHERE a.ItemType='Beverage' AND b.Outlet_Name = %s AND b.Date BETWEEN %s AND %s AND b.bill_no != '') AS beveragetotal,
#                 (SELECT SUM(a.count) FROM tblorder_detailshistory a JOIN tblorderhistory b ON a.order_ID = b.idtblorderHistory WHERE a.ItemType='Beverage' AND b.Outlet_Name = %s AND b.Date BETWEEN %s AND %s AND b.bill_no != '') AS beveragequantity,
#                 (SELECT SUM(a.Total) FROM tblorder_detailshistory a JOIN tblorderhistory b ON a.order_ID = b.idtblorderHistory WHERE a.ItemType='Other' AND b.Outlet_Name = %s AND b.Date BETWEEN %s AND %s AND b.bill_no != '') AS Othertotal,
#                 (SELECT SUM(a.count) FROM tblorder_detailshistory a JOIN tblorderhistory b ON a.order_ID = b.idtblorderHistory WHERE a.ItemType='Other' AND b.Outlet_Name = %s AND b.Date BETWEEN %s AND %s AND b.bill_no != '') AS Otherquantity
#         """, (outlet, startDate, endDate, outlet, startDate, endDate,
#               outlet, startDate, endDate, outlet, startDate, endDate,
#               outlet, startDate, endDate, outlet, startDate, endDate))

#         row_headers = [x[0] for x in cursor.description]
#         item_sum = [dict(zip(row_headers, row)) for row in cursor.fetchall()]

#         stats_data[0]["itemDetails"] = {
#             "itemSum": item_sum,
#             "food": food_items,
#             "foodGroup": food_group,
#             "beverage": beverage_items,
#             "beverageGroup": beverage_group,
#             "other": other_items,
#             "otherGroup": other_group
#         }

#         mydb.close()
#         return stats_data[0]

#     except Exception as error:
#         return {"error": str(error)}, 400


# from flask import Blueprint, request
# import mysql.connector
# from flask_cors import cross_origin
# import os
# from dotenv import load_dotenv
# load_dotenv()
# app_file7 = Blueprint('app_file7', __name__)
# from root.auth.check import token_auth

# @app_file7.route("/saleshistory", methods=["POST"])
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

#         data = request.get_json()
#         token = data.get("token")
#         if not token or not token_auth(token):
#             return {"error": "Invalid or missing token."}, 400

#         outlet = data.get("outlet")
#         startDate = data.get("dateStart")
#         endDate = data.get("dateEnd")

#         if not outlet or not startDate or not endDate:
#             return {"error": "Missing required fields."}, 400
        
#         # ----------------- Get bill_prefix for the outlet -----------------
#         cursor.execute("SELECT bill_prefix FROM outetNames WHERE Outlet=%s LIMIT 1", (outlet,))
#         bill_prefix_result = cursor.fetchone()
#         if not bill_prefix_result:
#             bill_prefix = "GEN"  # default if not found
#         else:
#             bill_prefix = bill_prefix_result[0]

#         # ----------------- ORDER DETAILS -----------------
#         order_sql = """
#         SELECT
#             o.Date, o.bill_no,o.fiscal_year,
#             (o.Total - o.serviceCharge - o.VAT) AS Subtotal,
#             o.Outlet_OrderID AS id, o.serviceCharge, o.VAT, o.Total,
#             o.DiscountAmt, o.PaymentMode, o.GuestName, o.idtblorderhistory,
#             p.paymentMode AS paymentModeHistory,
#             p.paymentAmount AS paymentAmountHistory,
#             o.guestID
#         FROM tblorderhistory o
#         LEFT JOIN payment_history p
#             ON o.idtblorderhistory = p.orderHistoryid AND o.PaymentMode = 'Split'
#         WHERE o.Date BETWEEN %s AND %s
#           AND o.Outlet_Name = %s
#         ORDER BY CAST(o.bill_no AS UNSIGNED);
#         """
#         cursor.execute(order_sql, (startDate, endDate, outlet))
#         orders = cursor.fetchall()
#         if not orders:
#             return {"error": "No data available."}, 400

#         row_headers = [x[0] for x in cursor.description]
#         json_orders = [dict(zip(row_headers, row)) for row in orders]

#         # ----------------- Add formatted_bill_no -----------------
#         for order in json_orders:
#             bill_no = str(order.get("bill_no", ""))
#             fiscal_year = str(order.get("fiscal_year", ""))

#             if bill_no == "":
#                 order["formatted_bill_no"] = ""
#             else:                
#                 order["formatted_bill_no"] = f"{bill_prefix}/{bill_no}/{fiscal_year}"

#         # ----------------- SUMMARY STATS -----------------
#         stats_sql = """
#         SELECT
#             SUM(DiscountAmt) AS DiscountAmountSum,
#             SUM(Total - serviceCharge - VAT) AS SubtotalAmountSum,
#             SUM(Total) AS TotalSum,
#             SUM(VAT) AS VatSum,
#             SUM(serviceCharge) AS ServiceChargeSum,
#             SUM(NoOfGuests) AS TotalGuestsServed,
#             COUNT(idtblorderHistory) AS TotalOrders,
#             COUNT(DISTINCT Date) AS DaysOperated
#         FROM tblorderhistory
#         WHERE Date BETWEEN %s AND %s
#           AND Outlet_Name = %s;
#         """
#         cursor.execute(stats_sql, (startDate, endDate, outlet))
#         stats = cursor.fetchall()
#         row_headers = [x[0] for x in cursor.description]
#         stats_json = [dict(zip(row_headers, stats[0]))]

#         # ----------------- FOOD ITEMS -----------------
#         items_food_sql = """
#         SELECT
#             a.Description, a.itemName,
#             SUM(a.count) AS quantity,
#             MAX(a.itemRate) AS itemrate,
#             SUM(a.Total) AS total,
#             MAX(a.ItemType) AS ItemType
#         FROM tblorder_detailshistory a
#         JOIN tblorderhistory b ON a.order_ID = b.idtblorderHistory
#         WHERE a.ItemType = 'Food'
#           AND b.Outlet_Name = %s
#           AND b.Date BETWEEN %s AND %s
#         GROUP BY a.Description, a.itemName
#         ORDER BY a.Description;
#         """
#         cursor.execute(items_food_sql, (outlet, startDate, endDate))
#         items_food = [dict(zip([x[0] for x in cursor.description], row)) for row in cursor.fetchall()]
#         if not items_food:
#             items_food = [{"Data": {"error": "No food data available."}}]

#         # ----------------- BEVERAGE ITEMS -----------------
#         items_beverage_sql = """
#         SELECT
#             a.Description, a.itemName,
#             SUM(a.count) AS quantity,
#             MAX(a.itemRate) AS itemrate,
#             SUM(a.Total) AS total,
#             MAX(a.ItemType) AS ItemType
#         FROM tblorder_detailshistory a
#         JOIN tblorderhistory b ON a.order_ID = b.idtblorderHistory
#         WHERE a.ItemType != 'Food' 
#           AND b.Outlet_Name = %s
#           AND b.Date BETWEEN %s AND %s
#         GROUP BY a.Description, a.itemName
#         ORDER BY a.Description;
#         """
#         cursor.execute(items_beverage_sql, (outlet, startDate, endDate))
#         items_beverage = [dict(zip([x[0] for x in cursor.description], row)) for row in cursor.fetchall()]
#         if not items_beverage:
#             items_beverage = [{"Data": {"error": "No beverage data available."}}]

#         # ----------------- FOOD & BEVERAGE SUMS -----------------
#         items_sum_sql = """
#         SELECT
#             (SELECT SUM(a.total) FROM tblorder_detailshistory a
#              JOIN tblorderhistory b ON a.order_ID = b.idtblorderHistory
#              WHERE a.ItemType != 'Food' AND b.Outlet_Name=%s AND b.Date BETWEEN %s AND %s) AS beveragetotal,
#             (SELECT SUM(a.count) FROM tblorder_detailshistory a
#              JOIN tblorderhistory b ON a.order_ID = b.idtblorderHistory
#              WHERE a.ItemType != 'Food' AND b.Outlet_Name=%s AND b.Date BETWEEN %s AND %s) AS beveragequantity,
#             (SELECT SUM(a.total) FROM tblorder_detailshistory a
#              JOIN tblorderhistory b ON a.order_ID = b.idtblorderHistory
#              WHERE a.ItemType = 'Food' AND b.Outlet_Name=%s AND b.Date BETWEEN %s AND %s) AS foodtotal,
#             (SELECT SUM(a.count) FROM tblorder_detailshistory a
#              JOIN tblorderhistory b ON a.order_ID = b.idtblorderHistory
#              WHERE a.ItemType = 'Food' AND b.Outlet_Name=%s AND b.Date BETWEEN %s AND %s) AS foodquantity;
#         """
#         cursor.execute(items_sum_sql, (outlet, startDate, endDate, outlet, startDate, endDate, outlet, startDate, endDate, outlet, startDate, endDate))
#         items_sum = [dict(zip([x[0] for x in cursor.description], cursor.fetchone()))]

#         # ----------------- GROUP TOTALS -----------------
#         def get_group_totals_food(item_type):
#             sql = f"""
#             SELECT
#                 SUM(a.Total) AS groupTotal,
#                 a.Description AS groupName
#             FROM tblorder_detailshistory a
#             JOIN tblorderhistory b ON a.order_ID = b.idtblorderHistory
#             WHERE b.Outlet_Name=%s AND b.Date BETWEEN %s AND %s
#               AND a.ItemType = %s
#             GROUP BY a.Description
#             ORDER BY SUM(a.Total) DESC;
#             """
#             cursor.execute(sql, (outlet, startDate, endDate, item_type))
#             return [dict(zip([x[0] for x in cursor.description], row)) for row in cursor.fetchall()] or [{"error": f"No {item_type.lower()} group data available."}]
        
#         def get_group_totals_beverage():
#             sql = f"""
#             SELECT
#                 SUM(a.Total) AS groupTotal,
#                 a.Description AS groupName
#             FROM tblorder_detailshistory a
#             JOIN tblorderhistory b ON a.order_ID = b.idtblorderHistory
#             WHERE b.Outlet_Name=%s AND b.Date BETWEEN %s AND %s
#               AND a.ItemType != 'Food'
#             GROUP BY a.Description
#             ORDER BY SUM(a.Total) DESC;
#             """
#             cursor.execute(sql, (outlet, startDate, endDate))
#             return [dict(zip([x[0] for x in cursor.description], row)) for row in cursor.fetchall()] or [{"error": f"No Beverage group data available."}]

#         food_group = get_group_totals_food("Food")
#         beverage_group = get_group_totals_beverage()

#         itemsumDetailsJson = {
#             "itemSum": items_sum,
#             "food": items_food,
#             "foodGroup": food_group,
#             "beverage": items_beverage,
#             "beverageGroup": beverage_group
#         }

#         # ----------------- SPLIT PAYMENTS -----------------
#         split_order_details = {}
#         for order in json_orders:
#             order_id = order["idtblorderhistory"]
#             if order_id not in split_order_details:
#                 split_order_details[order_id] = order
#                 split_order_details[order_id]["SplitPayments"] = []

#         for row in orders:
#             order_id = row[10]
#             payment_mode = row[8] or "Unknown"
#             if payment_mode == "Split" and order_id in split_order_details:
#                 split_order_details[order_id]["SplitPayments"].append({
#                     "PaymentMode": row[11] or "Unknown",
#                     "PaymentAmount": float(row[12] or 0.0)
#                 })

#         final_order_details = list(split_order_details.values())

#         for order_detail in final_order_details:
#             order_detail.pop("paymentAmountHistory", None)
#             order_detail.pop("paymentModeHistory", None)

#         stats_json[0]["itemDetails"] = itemsumDetailsJson
#         stats_json[0]["orderDetails"] = final_order_details

#         mydb.close()
#         return stats_json[0]

#     except Exception as error:
#         return {'error': str(error)}, 400



from flask import Blueprint, request
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv
load_dotenv()
app_file7 = Blueprint('app_file7', __name__)
from root.auth.check import token_auth

@app_file7.route("/saleshistory", methods=["POST"])
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

        data = request.get_json()
        token = data.get("token")
        if not token or not token_auth(token):
            return {"error": "Invalid or missing token."}, 400

        outlet = data.get("outlet")
        startDate = data.get("dateStart")
        endDate = data.get("dateEnd")

        if not outlet or not startDate or not endDate:
            return {"error": "Missing required fields."}, 400
        
        # ----------------- Get bill_prefix for the outlet -----------------
        cursor.execute("SELECT bill_prefix FROM outetNames WHERE Outlet=%s LIMIT 1", (outlet,))
        bill_prefix_result = cursor.fetchone()
        if not bill_prefix_result:
            bill_prefix = "GEN"  # default if not found
        else:
            bill_prefix = bill_prefix_result[0]

        # ----------------- ORDER DETAILS -----------------
        order_sql = """
        SELECT
            o.Date, o.bill_no,o.fiscal_year,
            (o.Total - o.serviceCharge - o.VAT) AS Subtotal,
            o.Outlet_OrderID AS id, o.serviceCharge, o.VAT, o.Total,
            o.DiscountAmt, o.PaymentMode, o.GuestName, o.idtblorderhistory,
            p.paymentMode AS paymentModeHistory,
            p.paymentAmount AS paymentAmountHistory,
            o.guestID
        FROM tblorderhistory o
        LEFT JOIN payment_history p
            ON o.idtblorderhistory = p.orderHistoryid AND o.PaymentMode = 'Split'
        WHERE o.Date BETWEEN %s AND %s
          AND o.Outlet_Name = %s
        ORDER BY CAST(o.bill_no AS UNSIGNED);
        """
        cursor.execute(order_sql, (startDate, endDate, outlet))
        orders = cursor.fetchall()
        if not orders:
            return {"error": "No data available."}, 400

        row_headers = [x[0] for x in cursor.description]
        json_orders = [dict(zip(row_headers, row)) for row in orders]

        # ----------------- Add formatted_bill_no -----------------
        for order in json_orders:
            bill_no = str(order.get("bill_no", ""))
            fiscal_year = str(order.get("fiscal_year", ""))

            if bill_no == "":
                order["formatted_bill_no"] = ""
            else:                
                order["formatted_bill_no"] = f"{bill_prefix}/{bill_no}/{fiscal_year}"

        # ----------------- SUMMARY STATS -----------------
        stats_sql = """
        SELECT
            SUM(DiscountAmt) AS DiscountAmountSum,
            SUM(Total - serviceCharge - VAT) AS SubtotalAmountSum,
            SUM(Total) AS TotalSum,
            SUM(VAT) AS VatSum,
            SUM(serviceCharge) AS ServiceChargeSum,
            SUM(NoOfGuests) AS TotalGuestsServed,
            COUNT(idtblorderHistory) AS TotalOrders,
            COUNT(DISTINCT Date) AS DaysOperated
        FROM tblorderhistory
        WHERE Date BETWEEN %s AND %s
          AND Outlet_Name = %s;
        """
        cursor.execute(stats_sql, (startDate, endDate, outlet))
        stats = cursor.fetchall()
        row_headers = [x[0] for x in cursor.description]
        stats_json = [dict(zip(row_headers, stats[0]))]

        # ----------------- REGULAR FOOD ITEMS (non-complementary) -----------------
        items_food_sql = """
        SELECT
            a.Description, a.itemName,
            SUM(a.count) AS quantity,
            MAX(a.itemRate) AS itemrate,
            SUM(a.Total) AS total,
            MAX(a.ItemType) AS ItemType
        FROM tblorder_detailshistory a
        JOIN tblorderhistory b ON a.order_ID = b.idtblorderHistory
        WHERE a.ItemType = 'Food'
          AND b.PaymentMode NOT IN ('Complimentary', 'Non Chargeable')
          AND b.Outlet_Name = %s
          AND b.Date BETWEEN %s AND %s
        GROUP BY a.Description, a.itemName
        ORDER BY a.Description;
        """
        cursor.execute(items_food_sql, (outlet, startDate, endDate))
        items_food = [dict(zip([x[0] for x in cursor.description], row)) for row in cursor.fetchall()]
        if not items_food:
            items_food = []

        # ----------------- REGULAR BEVERAGE ITEMS (non-complementary) -----------------
        items_beverage_sql = """
        SELECT
            a.Description, a.itemName,
            SUM(a.count) AS quantity,
            MAX(a.itemRate) AS itemrate,
            SUM(a.Total) AS total,
            MAX(a.ItemType) AS ItemType
        FROM tblorder_detailshistory a
        JOIN tblorderhistory b ON a.order_ID = b.idtblorderHistory
        WHERE a.ItemType != 'Food' 
          AND b.PaymentMode NOT IN ('Complimentary', 'Non Chargeable')
          AND b.Outlet_Name = %s
          AND b.Date BETWEEN %s AND %s
        GROUP BY a.Description, a.itemName
        ORDER BY a.Description;
        """
        cursor.execute(items_beverage_sql, (outlet, startDate, endDate))
        items_beverage = [dict(zip([x[0] for x in cursor.description], row)) for row in cursor.fetchall()]
        if not items_beverage:
            items_beverage = []

        # ----------------- COMPLEMENTARY BEVERAGE ITEMS -----------------
        complementary_beverage_sql = """
        SELECT
            a.Description, a.itemName,
            SUM(a.count) AS quantity,
            MAX(a.itemRate) AS itemrate,
            SUM(a.Total) AS total,
            MAX(a.ItemType) AS ItemType
        FROM tblorder_detailshistory a
        JOIN tblorderhistory b ON a.order_ID = b.idtblorderHistory
        WHERE a.ItemType != 'Food' 
          AND b.PaymentMode IN ('Complimentary', 'Non Chargeable')
          AND b.Outlet_Name = %s
          AND b.Date BETWEEN %s AND %s
        GROUP BY a.Description, a.itemName
        ORDER BY a.Description;
        """
        cursor.execute(complementary_beverage_sql, (outlet, startDate, endDate))
        complementary_beverage = [dict(zip([x[0] for x in cursor.description], row)) for row in cursor.fetchall()]
        if not complementary_beverage:
            complementary_beverage = []

        # ----------------- COMPLEMENTARY FOOD ITEMS -----------------
        complementary_food_sql = """
        SELECT
            a.Description, a.itemName,
            SUM(a.count) AS quantity,
            MAX(a.itemRate) AS itemrate,
            SUM(a.Total) AS total,
            MAX(a.ItemType) AS ItemType
        FROM tblorder_detailshistory a
        JOIN tblorderhistory b ON a.order_ID = b.idtblorderHistory
        WHERE a.ItemType = 'Food' 
          AND b.PaymentMode IN ('Complimentary', 'Non Chargeable')
          AND b.Outlet_Name = %s
          AND b.Date BETWEEN %s AND %s
        GROUP BY a.Description, a.itemName
        ORDER BY a.Description;
        """
        cursor.execute(complementary_food_sql, (outlet, startDate, endDate))
        complementary_food = [dict(zip([x[0] for x in cursor.description], row)) for row in cursor.fetchall()]
        if not complementary_food:
            complementary_food = []

        # ----------------- REGULAR FOOD & BEVERAGE SUMS -----------------
        items_sum_sql = """
        SELECT
            (SELECT SUM(a.total) FROM tblorder_detailshistory a
             JOIN tblorderhistory b ON a.order_ID = b.idtblorderHistory
             WHERE a.ItemType != 'Food' AND b.PaymentMode NOT IN ('Complimentary', 'Non Chargeable')
               AND b.Outlet_Name=%s AND b.Date BETWEEN %s AND %s) AS beveragetotal,
            (SELECT SUM(a.count) FROM tblorder_detailshistory a
             JOIN tblorderhistory b ON a.order_ID = b.idtblorderHistory
             WHERE a.ItemType != 'Food' AND b.PaymentMode NOT IN ('Complimentary', 'Non Chargeable')
               AND b.Outlet_Name=%s AND b.Date BETWEEN %s AND %s) AS beveragequantity,
            (SELECT SUM(a.total) FROM tblorder_detailshistory a
             JOIN tblorderhistory b ON a.order_ID = b.idtblorderHistory
             WHERE a.ItemType = 'Food' AND b.PaymentMode NOT IN ('Complimentary', 'Non Chargeable')
               AND b.Outlet_Name=%s AND b.Date BETWEEN %s AND %s) AS foodtotal,
            (SELECT SUM(a.count) FROM tblorder_detailshistory a
             JOIN tblorderhistory b ON a.order_ID = b.idtblorderHistory
             WHERE a.ItemType = 'Food' AND b.PaymentMode NOT IN ('Complimentary', 'Non Chargeable')
               AND b.Outlet_Name=%s AND b.Date BETWEEN %s AND %s) AS foodquantity;
        """
        cursor.execute(items_sum_sql, (outlet, startDate, endDate, outlet, startDate, endDate, outlet, startDate, endDate, outlet, startDate, endDate))
        items_sum = [dict(zip([x[0] for x in cursor.description], cursor.fetchone()))]
        
        # Handle NULL values
        for key in items_sum[0]:
            if items_sum[0][key] is None:
                items_sum[0][key] = 0

        # ----------------- COMPLEMENTARY ITEMS SUMS -----------------
        complementary_sum_sql = """
        SELECT
            (SELECT SUM(a.total) FROM tblorder_detailshistory a
             JOIN tblorderhistory b ON a.order_ID = b.idtblorderHistory
             WHERE a.ItemType != 'Food' AND b.PaymentMode IN ('Complimentary', 'Non Chargeable')
               AND b.Outlet_Name=%s AND b.Date BETWEEN %s AND %s) AS complementary_beverage_total,
            (SELECT SUM(a.count) FROM tblorder_detailshistory a
             JOIN tblorderhistory b ON a.order_ID = b.idtblorderHistory
             WHERE a.ItemType != 'Food' AND b.PaymentMode IN ('Complimentary', 'Non Chargeable')
               AND b.Outlet_Name=%s AND b.Date BETWEEN %s AND %s) AS complementary_beverage_quantity,
            (SELECT SUM(a.total) FROM tblorder_detailshistory a
             JOIN tblorderhistory b ON a.order_ID = b.idtblorderHistory
             WHERE a.ItemType = 'Food' AND b.PaymentMode IN ('Complimentary', 'Non Chargeable')
               AND b.Outlet_Name=%s AND b.Date BETWEEN %s AND %s) AS complementary_food_total,
            (SELECT SUM(a.count) FROM tblorder_detailshistory a
             JOIN tblorderhistory b ON a.order_ID = b.idtblorderHistory
             WHERE a.ItemType = 'Food' AND b.PaymentMode IN ('Complimentary', 'Non Chargeable')
               AND b.Outlet_Name=%s AND b.Date BETWEEN %s AND %s) AS complementary_food_quantity;
        """
        cursor.execute(complementary_sum_sql, (outlet, startDate, endDate, outlet, startDate, endDate, outlet, startDate, endDate, outlet, startDate, endDate))
        complementary_sum = [dict(zip([x[0] for x in cursor.description], cursor.fetchone()))]
        
        # Handle NULL values for complementary sums
        for key in complementary_sum[0]:
            if complementary_sum[0][key] is None:
                complementary_sum[0][key] = 0

        # ----------------- GROUP TOTALS - REGULAR FOOD -----------------
        def get_group_totals_food(is_complementary=False):
            payment_filter = "IN ('Complimentary', 'Non Chargeable')" if is_complementary else "NOT IN ('Complimentary', 'Non Chargeable')"
            sql = f"""
            SELECT
                SUM(a.Total) AS groupTotal,
                a.Description AS groupName
            FROM tblorder_detailshistory a
            JOIN tblorderhistory b ON a.order_ID = b.idtblorderHistory
            WHERE b.Outlet_Name=%s AND b.Date BETWEEN %s AND %s
              AND a.ItemType = 'Food'
              AND b.PaymentMode {payment_filter}
            GROUP BY a.Description
            ORDER BY SUM(a.Total) DESC;
            """
            cursor.execute(sql, (outlet, startDate, endDate))
            result = [dict(zip([x[0] for x in cursor.description], row)) for row in cursor.fetchall()]
            return result if result else []

        # ----------------- GROUP TOTALS - REGULAR BEVERAGE -----------------
        def get_group_totals_beverage(is_complementary=False):
            payment_filter = "IN ('Complimentary', 'Non Chargeable')" if is_complementary else "NOT IN ('Complimentary', 'Non Chargeable')"
            sql = f"""
            SELECT
                SUM(a.Total) AS groupTotal,
                a.Description AS groupName
            FROM tblorder_detailshistory a
            JOIN tblorderhistory b ON a.order_ID = b.idtblorderHistory
            WHERE b.Outlet_Name=%s AND b.Date BETWEEN %s AND %s
              AND a.ItemType != 'Food'
              AND b.PaymentMode {payment_filter}
            GROUP BY a.Description
            ORDER BY SUM(a.Total) DESC;
            """
            cursor.execute(sql, (outlet, startDate, endDate))
            result = [dict(zip([x[0] for x in cursor.description], row)) for row in cursor.fetchall()]
            return result if result else []

        # Get group totals for all categories
        food_group = get_group_totals_food(is_complementary=False)
        beverage_group = get_group_totals_beverage(is_complementary=False)
        complementary_food_group = get_group_totals_food(is_complementary=True)
        complementary_beverage_group = get_group_totals_beverage(is_complementary=True)

        # ----------------- Build itemsumDetailsJson with all sections -----------------
        itemsumDetailsJson = {
            # Regular items (non-complementary)
            "itemSum": items_sum,
            "food": items_food,
            "foodGroup": food_group,
            "beverage": items_beverage,
            "beverageGroup": beverage_group,
            
            # Complementary items
            "complementary_itemSum": complementary_sum,
            "complementary_food": complementary_food,
            "complementary_foodGroup": complementary_food_group,
            "complementary_beverage": complementary_beverage,
            "complementary_beverageGroup": complementary_beverage_group
        }

        # ----------------- SPLIT PAYMENTS -----------------
        split_order_details = {}
        for order in json_orders:
            order_id = order["idtblorderhistory"]
            if order_id not in split_order_details:
                split_order_details[order_id] = order
                split_order_details[order_id]["SplitPayments"] = []

        for row in orders:
            order_id = row[10]
            payment_mode = row[8] or "Unknown"
            if payment_mode == "Split" and order_id in split_order_details:
                split_order_details[order_id]["SplitPayments"].append({
                    "PaymentMode": row[11] or "Unknown",
                    "PaymentAmount": float(row[12] or 0.0)
                })

        final_order_details = list(split_order_details.values())

        for order_detail in final_order_details:
            order_detail.pop("paymentAmountHistory", None)
            order_detail.pop("paymentModeHistory", None)

        stats_json[0]["itemDetails"] = itemsumDetailsJson
        stats_json[0]["orderDetails"] = final_order_details

        mydb.close()
        return stats_json[0]

    except Exception as error:
        return {'error': str(error)}, 400