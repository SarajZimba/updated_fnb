from flask import Blueprint, request, jsonify
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv
load_dotenv()
app_file228 = Blueprint('app_file228', __name__)

from datetime import datetime


@app_file228.route("/purchase_with_transfer", methods=["POST"])
@cross_origin()
def create_purchase_and_transfer():
    """
    Combined API to create purchase requisition and optionally handle multiple stock transfers
    Also deletes a previous order-state purchase if provided
    
    Expected payload structure:
    {
        // Purchase requisition data (same as original)
        "RequisitionType": "...",
        "Date": "...",
        "TotalAmount": "...",
        "TaxAmount": "...",
        "Company_Name": "...",
        "State": "...",
        "ReceivedDate": "...",
        "purchaseBillNumber": "...",
        "DiscountAmount": "...",
        "Outlet_Name": "...",
        "purchase_id_ocular": "...",
        "purchase_from": "web/c_app",
        "company_pan": "...",
        "payment_mode": "...",
        "RequisitionDetailsList": [...],
        
        // Optional: Previous order-state purchase to delete
        "purchase_id_to_delete": 123,  // Purchase ID to delete after successful creation
        
        // Optional: Multiple stock transfers (array)
        "stocktransfers": [  // Changed from "stocktransfer" to "stocktransfers" (plural)
            {
                "CostCenter": "...",
                "OutletName": "...",
                "Date": "...",
                "Outlet_Req_ID": "...",
                "ItemDetailsList": [...]
            },
            {
                "CostCenter": "...",
                "OutletName": "...",
                "Date": "...",
                "Outlet_Req_ID": "...",
                "ItemDetailsList": [...]
            }
            // ... can have multiple transfers
        ]
    }
    """
    
    mydb = None
    cursor = None
    
    try:
        # Get today's date
        today_str = datetime.today().strftime('%Y-%m-%d')
        
        # Connect to database
        mydb = mysql.connector.connect(
            host=os.getenv('host'), 
            user=os.getenv('user'), 
            password=os.getenv('password')
        )
        cursor = mydb.cursor(buffered=True)
        
        # Use the database
        database_sql = "USE {};".format(os.getenv('database'))
        cursor.execute(database_sql)
        
        # Parse request data
        data = request.get_json()
        
        # Extract stock transfers data (as array) and purchase_id_to_delete if present
        stock_transfers_data = data.pop("stocktransfers", None)  # Changed from "stocktransfer" to "stocktransfers"
        purchase_id_to_delete = data.pop("purchase_id_to_delete", None)
        
        # Handle backward compatibility: if "stocktransfer" is provided (singular), convert to array
        if stock_transfers_data is None and "stocktransfer" in data:
            single_transfer = data.pop("stocktransfer", None)
            if single_transfer:
                stock_transfers_data = [single_transfer]
        
        # ==================== VALIDATION: Check if purchase_id_to_delete exists and is in "Ordered" state ====================
        if purchase_id_to_delete:
            cursor.execute("""
                SELECT State, Outlet_PurchaseReqID 
                FROM ordered_purchase 
                WHERE IDOrdered_Purchase = %s
            """, (purchase_id_to_delete,))
            
            existing_purchase = cursor.fetchone()
            
            if not existing_purchase:
                raise Exception(f"Purchase with ID {purchase_id_to_delete} not found")
            
            if existing_purchase[0] != "Ordered":
                raise Exception(f"Purchase with ID {purchase_id_to_delete} is in '{existing_purchase[0]}' state, not 'Ordered'. Cannot delete.")
            
            print(f"Will delete purchase ID {purchase_id_to_delete} (State: {existing_purchase[0]}) after successful creation")
        
        # ==================== PART 1: CREATE PURCHASE REQUISITION ====================
        purchase_from = data.get("purchase_from", "c_app")
        
        # Handle automatic increment for web
        if purchase_from == "web":
            # Get the maximum Outlet_PurchaseReqID and increment
            cursor.execute("SELECT MAX(Outlet_PurchaseReqID) FROM intbl_purchaserequisition")
            max_purchase_id = cursor.fetchone()[0]
            if max_purchase_id is None:
                purchase_requisition_id = 1
            else:
                purchase_requisition_id = max_purchase_id + 1
            
            # Get the maximum GRN and increment
            cursor.execute("SELECT MAX(GRN) FROM intbl_purchaserequisition")
            max_grn = cursor.fetchone()[0]
            if max_grn is None:
                grn = 1
            else:
                grn = max_grn + 1
        else:
            # For c_app, use values from request
            purchase_requisition_id = data["PurchaseRequistionID"]
            grn = data["GRN"]
        
        # Insert into purchase requisition table
        sql = f"""INSERT INTO `intbl_purchaserequisition` 
        (Outlet_PurchaseReqID, RequisitionType, Date, TotalAmount, TaxAmount, Company_Name, 
         State, ReceivedDate, ServerReceivedDate, purchaseBillNumber, DiscountAmount, 
         Outlet_Name, GRN, purchase_id_ocular, purchase_from, company_pan, payment_mode)
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(
            sql,
            (
                purchase_requisition_id,
                data["RequisitionType"],
                data["Date"],
                data["TotalAmount"],
                data["TaxAmount"],
                data.get("Company_Name", None),
                data["State"],
                data["ReceivedDate"],
                today_str,
                data["purchaseBillNumber"],
                data["DiscountAmount"],
                data["Outlet_Name"],
                grn,
                data.get("purchase_id_ocular", None),
                purchase_from,
                data.get("company_pan", None),
                data.get("payment_mode", None)
            ),
        )
        
        purchase_req_id = cursor.lastrowid
        state = data.get("State", "")
        
        # Prepare for stock current level entries
        current_level_entries = []
        
        # Insert purchase requisition details
        sql2 = """
        INSERT INTO `intbl_purchaserequisition_contract`    
        (ItemID, UnitsOrdered, PurchaseReqID, Rate, Name, BrandName, Code, UOM, 
         StockType, Department, GroupName, ExpDate, Status, Taxable) 
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        for item in data["RequisitionDetailsList"]:
            listitem = (
                item["ItemID"],
                item["UnitsOrdered"],
                purchase_req_id,
                item["Rate"],
                item["Name"],
                item["BrandName"],
                item["Code"],
                item["UOM"],
                item["StockType"],
                item["Department"],
                item["GroupName"],
                item["ExpDate"],
                item["Status"],
                item["Taxable"],
            )
            cursor.execute(sql2, listitem)
            
            # Only add to stock if State is "Received"
            if state == "Received":
                item_total = float(item["UnitsOrdered"]) * float(item["Rate"])
                
                # Add to stock_current_level
                current_level_entries.append((
                    item["Name"],
                    data["Outlet_Name"],
                    item["UOM"],
                    item["UnitsOrdered"],
                    item.get("ExpDate") if item.get("ExpDate") else None,
                    item["Rate"],
                    item_total,
                    purchase_req_id
                ))
                
                # Update stock_statement
                cursor.execute("""
                    SELECT CurrentLevel 
                    FROM stock_statement 
                    WHERE ItemName = %s AND UOM = %s AND OutletName = %s
                """, (item["Name"], item["UOM"], data["Outlet_Name"]))
                
                existing = cursor.fetchone()
                
                if existing:
                    cursor.execute("""
                        UPDATE stock_statement
                        SET CurrentLevel = CurrentLevel + %s, Rate = %s
                        WHERE ItemName = %s AND UOM = %s AND OutletName = %s
                    """, (item["UnitsOrdered"], item["Rate"], item["Name"], item["UOM"], data["Outlet_Name"]))
                else:
                    cursor.execute("""
                        INSERT INTO stock_statement 
                        (GroupName, ItemName, BrandName, UOM, CurrentLevel, Rate, OutletName)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        item["GroupName"],
                        item["Name"],
                        item["BrandName"],
                        item["UOM"],
                        item["UnitsOrdered"],
                        item["Rate"],
                        data["Outlet_Name"]
                    ))
        
        # Insert batch stock entries
        if current_level_entries:
            sql3 = """
            INSERT INTO stock_current_level (name, outlet, units, qty, expiry_date, rate, total, purchase_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.executemany(sql3, current_level_entries)
        
        # ==================== PART 2: HANDLE MULTIPLE STOCK TRANSFERS ====================
        transfer_results = []
        
        # If stock transfers data exists (as array), validate everything first
        if stock_transfers_data and isinstance(stock_transfers_data, list):
            # FIRST VALIDATION PASS: Check stock availability for ALL items across ALL transfers
            validation_errors = []
            
            # Track cumulative deductions per item across all transfers
            cumulative_deductions = {}
            
            for transfer_index, transfer in enumerate(stock_transfers_data):
                for item in transfer["ItemDetailsList"]:
                    item_name = item["ItemName"]
                    requested_qty = float(item["Amount"])
                    
                    # Accumulate total requested quantity across all transfers
                    if item_name not in cumulative_deductions:
                        cumulative_deductions[item_name] = {
                            "total_requested": 0,
                            "transfer_indices": []
                        }
                    
                    cumulative_deductions[item_name]["total_requested"] += requested_qty
                    cumulative_deductions[item_name]["transfer_indices"].append(transfer_index)
            
            # Validate against stock_current_level
            for item_name, deduction_info in cumulative_deductions.items():
                total_requested = deduction_info["total_requested"]
                
                cursor.execute("""
                    SELECT SUM(qty) as total_available 
                    FROM stock_current_level 
                    WHERE name = %s 
                    AND qty > 0
                    AND (expiry_date IS NULL OR expiry_date > CURDATE())
                """, (item_name,))
                
                result = cursor.fetchone()
                total_available = result[0] if result[0] else 0
                
                if total_available < total_requested - 0.001:
                    validation_errors.append(
                        f"Insufficient stock for {item_name} in stock_current_level. "
                        f"Available: {total_available:.2f}, Requested across all transfers: {total_requested:.2f}"
                    )
                
                # Validate against stock_statement
                cursor.execute("""
                    SELECT CurrentLevel 
                    FROM stock_statement 
                    WHERE ItemName = %s AND OutletName = %s
                """, (item_name, data["Outlet_Name"]))
                
                existing = cursor.fetchone()
                if not existing:
                    validation_errors.append(f"Stock statement missing for {item_name}")
                elif float(existing[0]) < total_requested - 0.001:
                    validation_errors.append(
                        f"Insufficient stock in stock_statement for {item_name}. "
                        f"Available: {float(existing[0]):.2f}, Requested across all transfers: {total_requested:.2f}"
                    )
            
            # If any validation fails, raise exception before making any changes
            if validation_errors:
                raise Exception("Stock validation failed: " + "; ".join(validation_errors))
            
            # SECOND PASS: All validations passed, now process each transfer
            for transfer_idx, transfer in enumerate(stock_transfers_data):
                try:
                    transfer_result = process_single_transfer(
                        cursor, transfer, data, purchase_from, purchase_req_id
                    )
                    transfer_results.append(transfer_result)
                    
                except Exception as transfer_error:
                    # If any transfer fails, raise exception to trigger complete rollback
                    raise Exception(f"Stock transfer #{transfer_idx + 1} failed: {str(transfer_error)}")
        
        # ==================== PART 3: DELETE PREVIOUS ORDER-STATE PURCHASE ====================
        deleted_purchase_info = None
        
        if purchase_id_to_delete:
            try:
                # Get purchase details before deletion for response
                cursor.execute("""
                    SELECT Outlet_PurchaseReqID, Outlet_Name, State 
                    FROM ordered_purchase 
                    WHERE IDOrdered_Purchase = %s
                """, (purchase_id_to_delete,))
                
                purchase_to_delete = cursor.fetchone()
                
                # Delete purchase requisition details first (foreign key constraint)
                cursor.execute("""
                    DELETE FROM ordered_purchaseitems 
                    WHERE OrderedPurchaseID = %s
                """, (purchase_id_to_delete,))
                
                # Delete the purchase requisition
                cursor.execute("""
                    DELETE FROM ordered_purchase 
                    WHERE  IDOrdered_Purchase= %s AND State = 'Ordered'
                """, (purchase_id_to_delete,))
                
                if cursor.rowcount > 0:
                    deleted_purchase_info = {
                        "purchase_id": purchase_id_to_delete,
                        "outlet_purchase_req_id": purchase_to_delete[0] if purchase_to_delete else None,
                        "outlet_name": purchase_to_delete[1] if purchase_to_delete else None,
                        "state": "Ordered",
                        "status": "deleted"
                    }
                    print(f"Successfully deleted purchase ID {purchase_id_to_delete}")
                else:
                    # This shouldn't happen because we validated earlier, but just in case
                    raise Exception(f"Failed to delete purchase ID {purchase_id_to_delete}. It may have been modified.")
                    
            except Exception as delete_error:
                raise Exception(f"Failed to delete previous purchase: {str(delete_error)}")
        
        # ==================== COMMIT EVERYTHING ====================
        # Only commit if we reach here (purchase, all transfers, and deletion all succeeded)
        mydb.commit()
        
        # ==================== RETURN RESPONSE ====================
        response_data = {
            "success": True,
            "purchase": {
                "purchase_requisition_id": purchase_req_id,
                "grn": grn if purchase_from == "web" else None,
                "outlet_purchase_req_id": purchase_requisition_id,
                "items_added": len(data["RequisitionDetailsList"])
            }
        }
        
        if transfer_results:
            response_data["stock_transfers"] = transfer_results
        
        if deleted_purchase_info:
            response_data["deleted_purchase"] = deleted_purchase_info
        
        return jsonify(response_data), 200
        
    except Exception as error:
        # Rollback ALL changes (new purchase, all transfers, AND deletion)
        if mydb:
            mydb.rollback()
        error_response = {'error': str(error)}
        return jsonify(error_response), 400
        
    finally:
        if cursor:
            cursor.close()
        if mydb:
            mydb.close()


def process_single_transfer(cursor, transfer, parent_data, purchase_from, purchase_req_id):
    """
    Process a single stock transfer transaction
    
    Args:
        cursor: Database cursor
        transfer: Single transfer object
        parent_data: Parent purchase data
        purchase_from: Source of purchase ("web" or "c_app")
        purchase_req_id: ID of the created purchase requisition
    
    Returns:
        dict: Transfer result information
    """
    # Convert date format
    try:
        date_obj = datetime.strptime(transfer['Date'], '%Y-%m-%dT%H:%M:%S')
        formatted_date = date_obj.strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        raise Exception(f"Invalid date format in stocktransfer: {str(e)}")
    
    # Get outlet name from parent data
    outlet_name = parent_data["Outlet_Name"]
    
    # Generate OutletREQID if from web
    if purchase_from == "web":
        cursor.execute("""
            SELECT MAX(CAST(OutletREQID AS UNSIGNED)) 
            FROM intblstorerequisition
            WHERE Outlet = %s
        """, (outlet_name,))
        
        max_id = cursor.fetchone()[0]
        outlet_req_id = int(max_id) + 1 if max_id else 1
    else:
        outlet_req_id = transfer["Outlet_Req_ID"]
    
    # Insert stock requisition header
    insert_storerequisitionSql = """
    INSERT INTO intblstorerequisition 
    (`Date`, `CostCenter`, `Outlet`, `OutletREQID`, `purchase_from`, `purchase_id`) 
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    cursor.execute(insert_storerequisitionSql, (
        formatted_date,
        transfer["CostCenter"],
        outlet_name,
        outlet_req_id,
        purchase_from,
        purchase_req_id
    ))
    
    store_req_id = cursor.lastrowid
    costcenter = transfer["CostCenter"]
    
    # Determine item type
    if costcenter == "Kitchen":
        item_type = "Food"
    elif costcenter == "Bar":
        item_type = "Beverage"
    else:
        item_type = costcenter
    
    # Process each item in the transfer
    for item in transfer["ItemDetailsList"]:
        item_name = item["ItemName"]
        requested_qty = float(item["Amount"])
        
        # Get stock batches ordered by expiry
        cursor.execute("""
            SELECT id, qty, total, rate, expiry_date
            FROM stock_current_level 
            WHERE name = %s 
            AND qty > 0
            AND (expiry_date IS NULL OR expiry_date > CURDATE())
            ORDER BY expiry_date ASC, id ASC
        """, (item_name,))
        
        stock_batches = cursor.fetchall()
        remaining_to_deduct = requested_qty
        
        # Deduct from batches
        for batch in stock_batches:
            if remaining_to_deduct <= 0.001:
                break
            
            batch_id = batch[0]
            current_qty = float(batch[1])
            current_total = float(batch[2])
            current_rate = float(batch[3])
            
            if current_qty <= remaining_to_deduct + 0.001:
                new_qty = 0
                new_total = 0
                remaining_to_deduct -= current_qty
            else:
                new_qty = current_qty - remaining_to_deduct
                new_total = new_qty * current_rate
                remaining_to_deduct = 0
            
            # Update stock current level
            cursor.execute("""
                UPDATE stock_current_level 
                SET qty = %s, total = %s 
                WHERE id = %s AND qty >= %s
            """, (new_qty, new_total, batch_id, current_qty))
            
            if cursor.rowcount == 0:
                raise Exception(f"Concurrent update detected for batch {batch_id}")
        
        # Update stock_statement
        cursor.execute("""
            SELECT CurrentLevel, Total 
            FROM stock_statement 
            WHERE ItemName = %s AND UOM = %s AND OutletName = %s
        """, (item["ItemName"], item["UOM"], outlet_name))
        
        existing = cursor.fetchone()
        
        if existing:
            current_level = float(existing[0])
            current_total = float(existing[1]) if existing[1] else 0
            
            new_level = current_level - requested_qty
            deduction_total = requested_qty * float(item["Rate"])
            new_total = current_total - deduction_total
            
            if new_level < -0.001:
                raise Exception(f"Stock level would become negative for {item['ItemName']}")
            
            if abs(new_level) < 0.001:
                new_level = 0
                new_total = 0
            
            cursor.execute("""
                UPDATE stock_statement
                SET CurrentLevel = %s, Total = %s
                WHERE ItemName = %s AND UOM = %s AND OutletName = %s
                AND CurrentLevel >= %s
            """, (
                new_level,
                new_total,
                item["ItemName"],
                item["UOM"],
                outlet_name,
                requested_qty
            ))
            
            if cursor.rowcount == 0:
                raise Exception(f"Concurrent update detected for stock_statement of {item['ItemName']}")
        else:
            raise Exception(f"Stock statement missing for {item['ItemName']}")
        
        # Insert into stock requisition details
        insert_detailsSql = """
        INSERT INTO intblstorereqdetails 
        (`ItemName`, `GroupName`, `BrandName`, `Amount`, `UOM`, `Rate`, `StoreReqID`, `itemtype`) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(insert_detailsSql, (
            item["ItemName"],
            item["GroupName"],
            item["BrandName"],
            item["Amount"],
            item["UOM"],
            item["Rate"],
            store_req_id,
            item_type
        ))
        
        # Insert into item_current_level
        cursor.execute("""
            INSERT INTO item_current_level (itemname, quantity, rate, outlet, costcenter)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            item['ItemName'],
            float(item['Amount']),
            float(item['Rate']),
            outlet_name,
            costcenter
        ))
    
    return {
        "store_req_id": store_req_id,
        "outlet_req_id": outlet_req_id,
        "cost_center": costcenter,
        "items_transferred": len(transfer["ItemDetailsList"]),
        "status": "success"
    }