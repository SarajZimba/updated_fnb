from flask import Blueprint, request
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv

from nepali_datetime import date as nepali_date
import datetime
# from .send_message import send_sms_sparrow
# from .ird.postbillintoird import postbillintoird


load_dotenv()

app_file8 = Blueprint("app_file8", __name__)


from .menuengineering.currentleveladjustmentaftersale import adjust_item_current_level_after_sale

@app_file8.route("/postsales", methods=["POST"])
@cross_origin()
def stats():
    try:
        mydb = mysql.connector.connect(
            host=os.getenv("host"),
            user=os.getenv("user"),
            password=os.getenv("password"),
        )
        cursor = mydb.cursor(buffered=True)
        cursor.execute("USE {};".format(os.getenv("database")))

        data = request.get_json()

        if not data:
            return {"error": "Missing or invalid JSON body"}, 400
        
        # Check if the entry already exists based on the date and Outlet_Name
        cursor.execute(
                "SELECT * FROM tblorderhistory WHERE Date = %s AND bill_no = %s AND Outlet_Name=%s",
                (data["date"], data["bill_No"],data["Outlet_Name"],)
        )
        existing_entry = cursor.fetchone()

        # If an existing entry is found, skip the insertion for this record
        if existing_entry:
            # print(f"Skipping date {data['date']} for Outlet {data['Outlet_Name']} (already exists).")
            return({"data": f"Skipping date {data['date']} for Outlet {data['OrderID']} (already exists)."}, 200)

        # Insert into tblorderhistory
        insert_order_sql = """
            INSERT INTO tblorderhistory (
                Outlet_OrderID, Employee, Table_No, NoOfGuests, Start_Time, End_Time, State, Type,
                Discounts, Date, bill_no, Total, serviceCharge, VAT, DiscountAmt, PaymentMode,
                fiscal_year, GuestName, Outlet_Name, billPrintTime, guestID, guestEmail,
                guestPhone, guestAddress, order_id_ocular, guestPan
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        # Normalize noofGuest to integer, default 0 if empty or invalid
        no_of_guests = data.get("noofGuest")
        try:
            no_of_guests = int(no_of_guests) if str(no_of_guests).strip() != "" else 0
        except ValueError:
            no_of_guests = 0

        cursor.execute(
            insert_order_sql,
            (
                data["OrderID"],
                data["Employee"],
                data["TableNo"],
                no_of_guests,
                data["start_Time"],
                data["end_Time"],
                data["state"],
                data["type"],
                data["discounts"],
                data["date"],
                data["bill_No"],
                data["Total"],
                data["serviceCharge"],
                data["VAT"],
                data["discountAmt"],
                data["paymentMode"],
                data["fiscal_Year"],
                data["GuestName"],
                data["Outlet_Name"],
                data["billPrintTime"],
                data["guestID"],
                data["guestEmail"],
                data["guestPhone"],
                data["guestAddress"],
                data.get("order_id_ocular", None),
                data["guestPAN"]
            ),
        )
        mydb.commit()

        # Handle Credit Entry
        if data["paymentMode"] == "Credit":
            credit_sql = """
                INSERT INTO CreditHistory (outetName, Date, customerName, guestID, creditState, Outlet_OrderID, Amount, guestPan)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(
                credit_sql,
                (
                    data["Outlet_Name"],
                    data["date"],
                    data["GuestName"],
                    data["guestID"],
                    "InitialEntry",
                    data["OrderID"],
                    data["Total"],
                    data["guestPAN"]

                ),
            )
            mydb.commit()

        # Get order ID for item insertion
        cursor.execute(
            "SELECT idtblorderhistory FROM tblorderhistory ORDER BY idtblorderhistory DESC LIMIT 1"
        )
        order_id = cursor.fetchone()[0]

        # -------------------------------
        # SPLIT PAYMENTS
        # -------------------------------
        if data["paymentMode"] == "Split":
            payment_sql = """
                INSERT INTO payment_history
                (bill_No, paymentMode, paymentAmount, orderHistoryid, FiscalYear)
                VALUES (%s,%s,%s,%s,%s)
            """
            for payment in data.get("SplitPaymentDetailsList", []):
                cursor.execute(payment_sql, (
                    data["bill_No"],
                    payment["paymentMode"],
                    payment["paymentAmount"],
                    order_id,
                    data["fiscal_Year"],
                ))

        # Insert each item into tblorder_detailshistory
        insert_item_sql = """
            INSERT INTO tblorder_detailshistory (
                order_ID, ItemName, itemRate, Total, ItemType, Description, discountExempt, count
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        for item in data["ItemDetailsList"]:
            item_data = (
                order_id,
                item["itemName"],
                item["ItemRate"],
                item["total"],
                item["ItemType"],
                item["Description"],
                item["disExempt"],
                item["count"],
            )
            cursor.execute(insert_item_sql, item_data)
            mydb.commit()

            if item["count"] > 0:
                adjust_item_current_level_after_sale(item["itemName"], item["count"], data["Outlet_Name"], cursor, mydb, data["date"])

        # Fetch IRD credentials for the outlet
        # cursor.execute(
        #     "SELECT username, password, seller_pan FROM ird_credentials WHERE outlet_name = %s LIMIT 1",
        #     (data["Outlet_Name"],)
        # )
        cursor.execute(
            "SELECT username, password, seller_pan FROM ird_credentials LIMIT 1"
        )
        ird_creds = cursor.fetchone()

        if not ird_creds:
            return {"error": f"No IRD credentials found for outlet {data['Outlet_Name']}"}, 400

        ird_username, ird_password, ird_seller_pan = ird_creds

        # --- Convert AD date to BS string for IRD ---
        ad_date = datetime.datetime.strptime(data["date"], "%Y-%m-%d").date()
        bs_date = nepali_date.from_datetime_date(ad_date)
        bs_date_str = f"{bs_date.year}.{bs_date.month:02d}.{bs_date.day:02d}"

        # Fetch outlet info including bill_prefix
        cursor.execute(
            "SELECT Company_name, bill_prefix, postingToIRD FROM outetNames WHERE Outlet = %s LIMIT 1",
            (data["Outlet_Name"],)
        )
        outlet_info = cursor.fetchone()
        if not outlet_info:
            return {"error": f"Outlet for name {data['Outlet_Name']} not found"}, 400

        company_name, bill_prefix, postingToIRD = outlet_info

        # --- Prepare IRD API payload ---
        cbms_payload = {
            "username": ird_username,
            "password": ird_password,
            "seller_pan": ird_seller_pan,
            "buyer_pan": data.get("buyer_pan", ""),
            "fiscal_year": data["fiscal_Year"],
            "buyer_name": data.get("GuestName", ""),
            "invoice_number": f"{bill_prefix}/{data['bill_No']}/{data['fiscal_Year']}",
            "invoice_date": bs_date_str,
            "total_sales": float(data["Total"]),
            "taxable_sales_vat": float(data["Total"]) - float(data["VAT"]),
            "vat": float(data["VAT"]),
            "excisable_amount": 0,
            "excise": 0,
            "taxable_sales_hst": 0,
            "hst": 0,
            "amount_for_esf": 0,
            "esf": 0,
            "export_sales": 0,
            "tax_exempted_sales": 0,
            "isrealtime": True,
            "datetimeClient": datetime.datetime.now().isoformat()
        }
        

        print(cbms_payload)

        # if postingToIRD:
        #     postbillintoird(cbms_payload)

        if data["guestPhone"] != "":

            loyalty_received_check_query = """SELECT * FROM loyaltyqueue WHERE outlet = %s and bill_no = %s and date= %s"""
            cursor.execute(
                loyalty_received_check_query,
                (
                    data["Outlet_Name"],
                    data["bill_No"],
                    data["date"],
                ),
            )
            loyalty_received_record = cursor.fetchone()
            print(loyalty_received_record)
            if not loyalty_received_record or (loyalty_received_record[3] and loyalty_received_record[3].lower() == "pending"):
                # Check and Insert Guest if not exists
                guest_check_query = """
                    SELECT * FROM guest WHERE guestPhone = %s
                """
                cursor.execute(guest_check_query, (data["guestPhone"],))
                guest_record = cursor.fetchone()
                print("guest recrd", guest_record)
                if not guest_record:
                    insert_guest_query = """
                        INSERT INTO guest (guestID, guestEmail, guestPhone, guestAddress, Outlet_Name, GuestName, loyalty_points, guestPan)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(
                        insert_guest_query,
                        (
                            data["guestID"],
                            data["guestEmail"],
                            data["guestPhone"],
                            data["guestAddress"],
                            data["Outlet_Name"],
                            data["GuestName"],
                            0.00,
                            data["guestPAN"]

                        ),
                    )
                    mydb.commit()

                print("Outlet name is", data["Outlet_Name"])

                # Loyalty points logic
                cursor.execute(
                    "SELECT loyalty_percent FROM outetNames WHERE Outlet = %s",
                    (data["Outlet_Name"],),
                )

                loyalty_result = cursor.fetchone()
                loyalty_percent = (
                    loyalty_result[0] if loyalty_result and loyalty_result[0] else 0.0
                )

                if loyalty_percent > 0:
                    loyalty_earned = (
                        float(data["Total"] - data["VAT"]) * float(loyalty_percent)
                    ) / 100

                    # Get previous points
                    cursor.execute(
                        """
                        SELECT loyalty_points FROM guest 
                        WHERE guestID = %s AND GuestName = %s AND Outlet_Name = %s
                    """,
                        (data["guestID"], data["GuestName"], data["Outlet_Name"]),
                    )
                    prev_points_result = cursor.fetchone()
                    prev_points = (
                        float(prev_points_result[0]) if prev_points_result else 0.00
                    )

                    new_total_points = round(prev_points + loyalty_earned, 2)

                    # Update guest's total loyalty points
                    update_loyalty_query = """
                        UPDATE guest
                        SET loyalty_points = %s
                        WHERE guestID = %s AND GuestName = %s AND Outlet_Name = %s
                    """
                    cursor.execute(
                        update_loyalty_query,
                        (
                            new_total_points,
                            data["guestID"],
                            data["GuestName"],
                            data["Outlet_Name"],
                        ),
                    )
                    mydb.commit()

                    # Insert history
                    insert_loyalty_history = """
                        INSERT INTO GuestLoyaltyHistory (
                            guestID, GuestName, Outlet_Name, Date, PreviousPoints, EarnedPoints, TotalPoints, phone_no, guestPan
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(
                        insert_loyalty_history,
                        (
                            data["guestID"],
                            data["GuestName"],
                            data["Outlet_Name"],
                            data["date"],
                            round(prev_points, 2),
                            round(loyalty_earned, 2),
                            new_total_points,
                            data["guestPhone"],
                            data["guestPAN"]                            
                        ),
                    )
                    mydb.commit()

                    # LoyaltyQueue update or insert
                    loyaltyqueue_pending_check_query = """
                        SELECT id FROM loyaltyqueue 
                        WHERE outlet = %s AND bill_no = %s AND date = %s and status='pending'
                    """
                    cursor.execute(
                        loyaltyqueue_pending_check_query,
                        (data["Outlet_Name"], data["bill_No"], data["date"]),
                    )
                    loyalty_row = cursor.fetchone()

                    if loyalty_row:
                        # Update existing entry to received if it was pending
                        update_loyalty_status = """
                            UPDATE loyaltyqueue
                            SET status = 'received'
                            WHERE outlet = %s AND bill_no = %s AND date = %s AND status = 'pending'
                        """
                        cursor.execute(
                            update_loyalty_status,
                            (data["Outlet_Name"], data["bill_No"], data["date"]),
                        )
                        mydb.commit()
                    else:
                        # Insert new entry marked as received
                        insert_loyalty_entry = """
                            INSERT INTO loyaltyqueue (hash_code, status, outlet, bill_no, sub_total, date)
                            VALUES ( %s, 'received', %s, %s, %s, %s)
                        """
                        import hashlib

                        hash_input = (
                            f"{data['bill_No']}{data['Outlet_Name']}{data['date']}"
                        )
                        hash_code = hashlib.sha256(hash_input.encode()).hexdigest()

                        cursor.execute(
                            insert_loyalty_entry,
                            (
                                hash_code,
                                data["Outlet_Name"],
                                data["bill_No"],
                                data["Total"],  # Using total as sub_total here
                                data["date"],
                            ),
                        )
                        mydb.commit()
            # cursor.execute(
            #     """
            #     SELECT sms_text 
            #     FROM outetNames 
            #     WHERE Outlet = %s LIMIT 1
            #     """,
            #     (data["Outlet_Name"],)
            # )
            # row = cursor.fetchone()

            # if row and row[0]:
            #     sms_template = row[0]
            # else:
            #     sms_template = "Thank you {{name}} for visiting {{outlet}}!"
            # # sms_text = f"Dear {data['GuestName']}, thank you for visiting {data['Outlet_Name']}! Your bill number {data['bill_No']} has been recorded."
            # sms_message = (
            #     sms_template
            #         .replace("{{name}}", data.get("GuestName", "Customer"))
            #         .replace("{{bill_no}}", str(data.get("bill_No", "")))
            #         .replace("{{outlet}}", data.get("Outlet_Name", ""))
            #         .replace("{{total}}", str(data.get("Total", "")))
            # )            
            
            # sms_response = send_sms_sparrow(data["guestPhone"], sms_message)
            # print("SMS Response:", sms_response)
            
            # cursor.execute("""
            # INSERT INTO sms_history 
            # (task_id, sender_name, message_text, total_numbers, numbers_sent)
            # VALUES (%s, %s, %s, %s, %s)
            # """, (
            #     order_id,
            #     data.get("Outlet_Name", ""),
            #     sms_message,
            #     1,
            #     data["guestPhone"]
            # ))

            # mydb.commit()

            # Check and Insert Guest if not exists
            customer_check_query = """
                SELECT * FROM customers WHERE phone = %s
            """
            cursor.execute(customer_check_query, (data["guestPhone"],))
            customer_record = cursor.fetchone()
            print("customer recrd", customer_record)
            if not customer_record:
                insert_customer_query = """
                    INSERT INTO customers (email, phone, address, source, name, guestPan)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(
                    insert_customer_query,
                        (
                            data["guestEmail"],
                            data["guestPhone"],
                            data["guestAddress"],
                            data["Outlet_Name"],
                            data["GuestName"],
                            data["guestPan"]
                        ),
                )
                mydb.commit()

        mydb.close()
        return {"success": "Data posted successfully"}

    except Exception as error:
        return {"error": str(error)}, 400