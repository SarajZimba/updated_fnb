from flask import Blueprint, jsonify, request
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv

load_dotenv()

app_file122 = Blueprint('app_file122', __name__)

@app_file122.route("/updatestocks", methods=["POST"])
@cross_origin()
def update_stocks():
    try:
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password')
        )
        cursor = mydb.cursor(buffered=True)

        cursor.execute(f"USE {os.getenv('database')}")

        data = request.get_json()

        if not data or "outlet_name" not in data or "stocks" not in data:
            return jsonify({"error": "Please provide 'outlet_name' and 'stocks' list"}), 400

        outlet_name = data["outlet_name"]
        stocks = data["stocks"]

        updated_count = 0
        for stock in stocks:
            item_name = stock.get("ItemName")
            current_level = stock.get("CurrentLevel")
            rate = stock.get("Rate")
            total = stock.get("Total")

            if not item_name:
                continue

            update_fields = []
            update_values = []

            if current_level is not None:
                update_fields.append("CurrentLevel = %s")
                update_values.append(current_level)
            if rate is not None:
                update_fields.append("Rate = %s")
                update_values.append(rate)
            if total is not None:
                update_fields.append("Total = %s")
                update_values.append(total)

            if update_fields:
                update_sql = f"""
                UPDATE stock_statement 
                SET {', '.join(update_fields)} 
                WHERE ItemName = %s AND OutletName = %s
                """
                update_values.extend([item_name, outlet_name])
                cursor.execute(update_sql, update_values)
                updated_count += cursor.rowcount

                if rate is not None:
                    cursor.execute("UPDATE recipe_items SET rate = %s WHERE name = %s", (rate, item_name))
                    cursor.execute("UPDATE sub_recipe_items SET rate = %s WHERE name = %s", (rate, item_name))

                    cursor.execute("""
                        UPDATE recipe_items 
                        SET cost = rate * quantity 
                        WHERE name = %s
                    """, (item_name,))

                    cursor.execute("""
                        UPDATE sub_recipe_items 
                        SET cost = rate * quantity 
                        WHERE name = %s
                    """, (item_name,))

        mydb.commit()

        return jsonify({"message": f"{updated_count} stock records updated and recipe rates/costs synced."}), 200

    except mysql.connector.Error as db_error:
        return jsonify({"error": f"Database error: {str(db_error)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
    finally:
        if 'mydb' in locals():
            mydb.close()