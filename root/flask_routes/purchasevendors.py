from flask import Blueprint, request, jsonify
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv

load_dotenv()
app_file227 = Blueprint('app_file227', __name__)

@app_file227.route("/getCompanies", methods=["POST"])
@cross_origin()
def get_companies():
    try:
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password')
        )
        cursor = mydb.cursor(dictionary=True)
        
        database_sql = "USE {};".format(os.getenv('database'))
        cursor.execute(database_sql)


        data = request.get_json()
        
        # Get purchase_from from request data
        outlet_name = data.get("outlet_name", None)


        # Validation
        if not outlet_name:
            return jsonify({"error": "outlet_name is required"}), 400
        
        # Query to get distinct company names
        sql = """
        SELECT DISTINCT Company_Name 
        FROM intbl_purchaserequisition 
        WHERE Company_Name IS NOT NULL AND Company_Name != '' AND Outlet_Name = %s
        ORDER BY Company_Name ASC
        """
        cursor.execute(sql, (outlet_name,))
        
        companies = cursor.fetchall()
        
        # Extract just the company names into a list
        company_list = [company['Company_Name'] for company in companies]
        
        mydb.close()
        
        return jsonify({
            "success": True,
            "count": len(company_list),
            "companies": company_list
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400