import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

def send_sms_sparrow(phone_no, message):
    try:
        url = "https://api.sparrowsms.com/v2/sms/"

        payload = {
            "token": os.getenv("SPARROW_TOKEN"),
            "from": os.getenv("SPARROW_SENDER"),   # Sender ID provided by Sparrow
            "to": phone_no,
            "text": message
        }

        response = requests.post(url, data=payload)
        return response.json()

    except Exception as e:
        return {"error": str(e)}
    
def get_credit_sparrow():
    try:
        url = "https://api.sparrowsms.com/v2/credit/"
        token = os.getenv("SPARROW_TOKEN")

        response = requests.get(url, params={"token": token})

        # Try parsing JSON even if error
        data = response.json()

        # If server returned 200 OK
        if response.status_code == 200:
            return data

        # Otherwise return API response as error
        return {"error": data}

    except Exception as e:
        return {"error": str(e)}

def send_sparrow_sms(token, sender_id, numbers, message):
    """
    Send SMS to multiple numbers using Sparrow SMS API.
    
    numbers must be a list, but will be converted to:
    "9841512345, 9801234567"
    """

    # Convert list → comma separated string with space after comma
    to_numbers = ", ".join(str(num) for num in numbers)

    url = "https://api.sparrowsms.com/v1/sms/"

    payload = {
        "token": token,
        "from": os.getenv("SPARROW_SENDER"),
        "to": to_numbers,
        "text": message
    }

    try:
        response = requests.post(url, data=payload)
        return response.json()
    except Exception as e:
        return {
            "response_code": 500,
            "response": f"Error: {e}"
        }


