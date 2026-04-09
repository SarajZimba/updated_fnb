import requests
import datetime

def post_credit_note_to_ird(payload):
    """
    Posts a sales return / void bill to IRD CBMS
    """
    cbms_url = "https://cbapi.ird.gov.np/api/billreturn"
    headers = {"Content-Type": "application/json"}
    print(payload)
    try:
        r = requests.post(cbms_url, json=payload, headers=headers, timeout=10)
        if r.status_code == 200:
            print(f"Credit Note {payload['credit_note_number']} posted successfully: {r.text}")
            return True, r.text
        else:
            print(f"CBMS Credit Note API failed: {r.text}")
            return False, r.text
    except Exception as e:
        print(f"Error posting credit note to IRD: {str(e)}")
        return False, str(e)
