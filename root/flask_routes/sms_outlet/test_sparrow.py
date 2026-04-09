from flask import Blueprint, request, jsonify
import mysql.connector
from flask_cors import cross_origin
import os, requests
from dotenv import load_dotenv
load_dotenv()
def send_sparrow_sms(numbers, message):
    to_numbers = ", ".join(str(num) for num in numbers)

    url = "https://api.sparrowsms.com/v2/sms/"
    payload = {
        "token": os.getenv("SPARROW_TOKEN"),
        "from": os.getenv("SPARROW_SENDER"),
        "to": to_numbers,
        "text": message
    }

    print("payload", payload)

    response = requests.post(url, data=payload)


    print("response", response)
    # Try parsing JSON, otherwise return raw body
    try:
        return response.json()
    except:
        return {
            "response_code": 500,
            "response": "Non-JSON returned",
            "raw_response": response.text
        }
    
result = send_sparrow_sms(["9849597735"], "test")
print("Result:", result)
