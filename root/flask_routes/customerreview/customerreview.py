from flask import Blueprint, jsonify, request
import mysql.connector
import os
from dotenv import load_dotenv
from flask_cors import cross_origin
from root.auth.check import token_auth

load_dotenv()

app_file106 = Blueprint('app_file106', __name__)

@app_file106.route('/submit-review', methods=['POST'])
def submit_review():
    data = request.json
    try:
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password')
        )
        cursor = mydb.cursor(buffered=True)
        cursor.execute(f"USE {os.getenv('database')}")

        insert_query = """
        INSERT INTO customerreviews (
            customer_name, customer_email, phonenumber,
            service, staff_friendliness, food_quality,
            atmosphere, cleanliness,
            experience, comments, post_review_consent, outlet_name,
            experience_today, most_enjoyed, improvement_suggestions,
            would_recommend, visit_type, type
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            data.get('customer_name', None),
            data.get('customer_email', None),
            data.get('phonenumber', None),
            data.get('service', None),
            data.get('staff_friendliness', None),
            data.get('food_quality', None),
            data.get('atmosphere', None),
            data.get('cleanliness', None),
            data.get('experience', None),
            data.get('comments', None),
            data.get('post_review_consent', None),
            data.get('outlet_name', None),

            data.get('experience_today', None),
            data.get('most_enjoyed', None),
            data.get('improvement_suggestions', None),
            data.get('would_recommend', None),
            data.get('visit_type', None),
            data.get('type', None),
        )

        cursor.execute(insert_query, values)
        mydb.commit()

        from root.app import send_review_email
        send_review_email(data)

        return jsonify({'message': 'Review submitted and email sent.'}), 201

    except Exception as e:
        print(e)
        return jsonify({'error': 'Submission failed', 'details': str(e)}), 500

    finally:
        cursor.close()
        mydb.close()

@app_file106.route('/get-reviews', methods=['POST'])
@cross_origin()
def get_reviews():
    try:
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password')
        )
        cursor = mydb.cursor(dictionary=True)
        cursor.execute(f"USE {os.getenv('database')}")

        json = request.get_json()
        if "token" not in json or not json["token"]:
            return {"error": "No token provided."}, 400

        cursor.execute("""
            SELECT id, customer_name, customer_email, phonenumber,
                   service, staff_friendliness, food_quality,
                   atmosphere, cleanliness, experience, comments,
                   post_review_consent, outlet_name,
                   experience_today, most_enjoyed, improvement_suggestions,
                   would_recommend, visit_type
            FROM customerreviews
            ORDER BY id DESC
        """)

        reviews = cursor.fetchall()
        return jsonify(reviews), 200

    except Exception as e:
        print(e)
        return jsonify({'error': 'Failed to fetch reviews', 'details': str(e)}), 500

    finally:
        cursor.close()
        mydb.close()
