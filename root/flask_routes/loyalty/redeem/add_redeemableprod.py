# from flask import Blueprint, request, jsonify
# import os
# from werkzeug.utils import secure_filename
# import mysql.connector
# from dotenv import load_dotenv
# from flask_cors import cross_origin
# from root.auth.check import token_auth

# load_dotenv()

# UPLOAD_FOLDER = 'root/static/uploads'
# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# app_file97 = Blueprint('app_file97', __name__)

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# @app_file97.route('/add-redeemable-product', methods=['POST'])
# @cross_origin()
# def add_redeemable_product():
#     try:
#         token = request.form.get('token')
#         if not token or not token_auth(token):
#             return jsonify({'error': 'Invalid or missing token'}), 400

#         product = request.form.get('product')
#         points = request.form.get('points')
#         valid_until = request.form.get('valid_until', None)
#         is_menu_item_flag = 1 if request.form.get('is_menu_item_flag') == 'true' else 0
#         description = request.form.get('description', None)
#         outlet = request.form.get('outlet', None)  # Get outlet field
#         image = request.files.get('image')

#         if not product or not points or not outlet:
#             return jsonify({"error": "Missing required fields: product, points, or outlet"}), 400

#         image_db_path = None
#         if image and allowed_file(image.filename):
#             filename = secure_filename(image.filename)
#             physical_path = os.path.join(UPLOAD_FOLDER, filename)
#             image.save(physical_path)
#             image_db_path = f"static/uploads/{filename}"

#         mydb = mysql.connector.connect(
#             host=os.getenv('host'),
#             user=os.getenv('user'),
#             password=os.getenv('password'),
#             database=os.getenv('database')
#         )
#         cursor = mydb.cursor()

#         sql = """
#             INSERT INTO redeemable_products 
#             (product, points, valid_until, is_menu_item_flag, image, description, outlet)
#             VALUES (%s, %s, %s, %s, %s, %s, %s)
#         """
#         cursor.execute(sql, (
#             product, points, valid_until, is_menu_item_flag, image_db_path, description, outlet
#         ))
#         mydb.commit()

#         return jsonify({'message': 'Product added successfully'}), 201

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

    

# from werkzeug.utils import secure_filename

# UPLOAD_FOLDER = 'root/static/uploads'
# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# @app_file97.route('/update-redeemable-product/<int:id>', methods=['PUT'])
# @cross_origin()
# def update_redeemable_product(id):
#     try:
#         token = request.form.get('token')
#         if not token or not token_auth(token):
#             return jsonify({'error': 'Invalid or missing token'}), 400

#         fields = ['product', 'description', 'points', 'valid_until', 'is_menu_item_flag', 'status']
#         values = []
#         updates = []

#         for field in fields:
#             value = request.form.get(field)
#             if value is not None:
#                 updates.append(f"{field} = %s")
#                 values.append(value)

#         image = request.files.get('image')
#         image_path = None
#         if image and allowed_file(image.filename):
#             filename = secure_filename(image.filename)
#             image_path = os.path.join(UPLOAD_FOLDER, filename)
#             image.save(image_path)
#             updates.append("image = %s")
#             values.append(image_path)

#         if not updates:
#             return jsonify({'error': 'No fields provided for update'}), 400

#         mydb = mysql.connector.connect(
#             host=os.getenv('host'),
#             user=os.getenv('user'),
#             password=os.getenv('password'),
#             database=os.getenv('database')
#         )
#         cursor = mydb.cursor()
#         sql = f"UPDATE redeemable_products SET {', '.join(updates)} WHERE id = %s"
#         values.append(id)
#         cursor.execute(sql, values)
#         mydb.commit()

#         return jsonify({'message': 'Product updated successfully'}), 200

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500



# @app_file97.route('/delete-redeemable-product/<int:id>', methods=['DELETE'])
# @cross_origin()
# def delete_redeemable_product(id):
#     try:
#         token = request.args.get('token')
#         if not token or not token_auth(token):
#             return jsonify({'error': 'Invalid or missing token'}), 400

#         mydb = mysql.connector.connect(
#             host=os.getenv('host'),
#             user=os.getenv('user'),
#             password=os.getenv('password'),
#             database=os.getenv('database')
#         )
#         cursor = mydb.cursor()
#         cursor.execute("DELETE FROM redeemable_products WHERE id = %s", (id,))
#         mydb.commit()

#         return jsonify({'message': 'Product deleted successfully'}), 200

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

from flask import Blueprint, request, jsonify
import os
from werkzeug.utils import secure_filename
import mysql.connector
from dotenv import load_dotenv
from flask_cors import cross_origin
from root.auth.check import token_auth

load_dotenv()

UPLOAD_FOLDER = 'root/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app_file97 = Blueprint('app_file97', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app_file97.route('/add-redeemable-product', methods=['POST'])
@cross_origin()
def add_redeemable_product():
    try:
        token = request.form.get('token')
        if not token or not token_auth(token):
            return jsonify({'error': 'Invalid or missing token'}), 400

        product = request.form.get('product')
        points = request.form.get('points')
        valid_until = request.form.get('valid_until', None)
        is_menu_item_flag = 1 if request.form.get('is_menu_item_flag') == 'true' else 0
        description = request.form.get('description', None)
        outlet = request.form.get('outlet', None)  # Get outlet field
        image = request.files.get('image')

        if not product or not points or not outlet:
            return jsonify({"error": "Missing required fields: product, points, or outlet"}), 400

        image_db_path = None
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            physical_path = os.path.join(UPLOAD_FOLDER, filename)
            image.save(physical_path)
            image_db_path = f"static/uploads/{filename}"

        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password'),
            database=os.getenv('database')
        )
        cursor = mydb.cursor()

        sql = """
            INSERT INTO redeemable_products 
            (product, points, valid_until, is_menu_item_flag, image, description, outlet)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            product, points, valid_until, is_menu_item_flag, image_db_path, description, outlet
        ))
        mydb.commit()

        return jsonify({'message': 'Product added successfully'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    

from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'root/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app_file97.route('/update-redeemable-product/<int:id>', methods=['PUT'])
@cross_origin()
def update_redeemable_product(id):
    try:
        token = request.form.get('token')
        if not token or not token_auth(token):
            return jsonify({'error': 'Invalid or missing token'}), 400

        fields = ['product', 'description', 'points', 'valid_until', 'is_menu_item_flag', 'status']
        values = []
        updates = []

        for field in fields:
            value = request.form.get(field)
            if value is not None:
                updates.append(f"{field} = %s")
                values.append(value)

        image = request.files.get('image')
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            physical_path = os.path.join(UPLOAD_FOLDER, filename)
            image.save(physical_path)
            image_db_path = f"static/uploads/{filename}"  # Save only relative path in DB
            updates.append("image = %s")
            values.append(image_db_path)

        if not updates:
            return jsonify({'error': 'No fields provided for update'}), 400

        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password'),
            database=os.getenv('database')
        )
        cursor = mydb.cursor()
        sql = f"UPDATE redeemable_products SET {', '.join(updates)} WHERE id = %s"
        values.append(id)
        cursor.execute(sql, values)
        mydb.commit()

        return jsonify({'message': 'Product updated successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app_file97.route('/delete-redeemable-product/<int:id>', methods=['DELETE'])
@cross_origin()
def delete_redeemable_product(id):
    try:
        data = request.get_json()
        token = data.get('token') if data else None
        
        if not token or not token_auth(token):
            return jsonify({'error': 'Invalid or missing token'}), 400

        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password'),
            database=os.getenv('database')
        )
        cursor = mydb.cursor()
        cursor.execute("DELETE FROM redeemable_products WHERE id = %s", (id,))
        mydb.commit()

        return jsonify({'message': 'Product deleted successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


