from flask import jsonify
def get_costcenterwisestockissue(item_name, startDate, endDate, cursor, outlet):

    # Query to get the stock requisition data filtered by date range and outlet
    query_storerequisition = """
        SELECT `idintblStoreRequisition`, `Date`, `CostCenter`, `Outlet`, `OutletREQID`
        FROM `intblstorerequisition`
         WHERE `Date` BETWEEN %s AND %s AND `Outlet` = %s
    """
    cursor.execute(query_storerequisition, (startDate, endDate, outlet))
    store_requisitions = cursor.fetchall()

    if not store_requisitions:
        return []

    all_requisitions = {}

    # Iterate over all store requisitions
    for store_requisition in store_requisitions:
        store_req_id = store_requisition[0]
        cost_center = store_requisition[2]

        # Fetch item details for each store requisition
        query_storereqdetails = """
            SELECT `ItemName`, `GroupName`, `BrandName`, `Amount`, `UOM`, `Rate`
            FROM `intblstorereqdetails`
            WHERE `StoreReqID` = %s  and `ItemName` = %s order by GroupName
        """
        cursor.execute(query_storereqdetails, (store_req_id, item_name))
        store_itemdetails = cursor.fetchall()

        # If the cost center does not exist in the dictionary, create it
        if cost_center not in all_requisitions:
            # all_requisitions[cost_center] = []
            all_requisitions[cost_center] = {"item_details": [], "grand_total": 0}
        # grand_total = 0
        # Iterate over the item details and group by ItemName and Rate
        for item in store_itemdetails:
            item_name = item[0]
            rate = item[5]
            amount = item[3]
            # Check if the item with the same name and rate already exists in the list for this cost center
            found = False
            for entry in all_requisitions[cost_center]["item_details"]:
                if entry["ItemName"] == item_name and entry["Rate"] == rate:
                    # If found, sum the amounts
                    entry["Amount"] += amount
                    entry["Amount"] = round(entry["Amount"], 2)
                    entry["Total"] =  round(entry["Rate"] * entry["Amount"], 2)
                    # all_requisitions[cost_center]["grand_total"] += entry["Total"]
                    found = True
                    break

            # If not found, add a new entry for this item
            if not found:
                all_requisitions[cost_center]["item_details"].append({
                    "ItemName": item_name,
                    "Rate": rate,
                    "Amount": round(amount, 2),
                    "UOM": item[4],
                    "GroupName": item[1],
                    "BrandName": item[2],
                    "Total": round(rate * amount, 2)
                })
                # all_requisitions[cost_center]["grand_total"] += round(rate * amount, 2)
    # Format the data as a list of cost centers with their items grouped and summed
    final_response = []
    for cost_center, items in all_requisitions.items():
        grand_total = sum(data["Total"] for data in items["item_details"])  # Calculate grand total
        sorted_item_details = sorted(items["item_details"], key=lambda x: x["GroupName"])
        final_response.append({
            "CostCenter": cost_center,
            "ItemDetailsList": sorted_item_details,
            "grand_total": grand_total,
        })

    return final_response