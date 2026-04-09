from flask import Blueprint, request
import mysql.connector
from flask_cors import cross_origin
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()

app_file208 = Blueprint('app_file208', __name__)

# Import your token_auth function
from root.auth.check import token_auth

# Allowed image extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Set upload folder to be inside 'root/uploads'
basedir = os.path.abspath(os.path.dirname(__file__))  # points to 'root/api' or wherever this file is
# Go up one level to 'root' folder
root_dir = os.path.abspath(os.path.join(basedir, '..'))
UPLOAD_FOLDER = os.path.join(root_dir, 'uploads')

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app_file208.route("/upload_outlet_logo", methods=["POST"])
@cross_origin()
def upload_outlet_logo():
    try:
        outlet = request.form.get("outlet")
        token = request.form.get("token")
        file = request.files.get("logo")

        if not token or not token_auth(token):
            return {"error": "Invalid or missing token"}, 400

        if not outlet:
            return {"error": "Missing outlet name"}, 400

        if not file or not allowed_file(file.filename):
            return {"error": "Invalid or missing logo file"}, 400

        # Secure filename
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        # Save file
        file.save(filepath)

        # Save filename to database
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password'),
            database=os.getenv('database')
        )
        cursor = mydb.cursor()

        update_sql = """
            UPDATE outetNames 
            SET logo = %s 
            WHERE Outlet = %s
        """
        cursor.execute(update_sql, (filename, outlet))
        mydb.commit()
        mydb.close()

        return {"message": "Logo uploaded successfully", "filename": filename}, 200

    except Exception as e:
        return {"error": str(e)}, 500
