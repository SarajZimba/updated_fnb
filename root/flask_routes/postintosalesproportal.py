import os
import requests
def registeruserinsalesproportal(data):

    salespro_token = os.getenv('salesproportal_token')

    data["token"] = salespro_token

    salespropotal_url = os.getenv('salesproportal_url')

    if not salespro_token or not salespropotal_url:
        print("Environment variables not set correctly.")
        return False


    headers = {
            "Content-Type": "application/json"   # Optional, ensures JSON content
        }
    register_url = salespropotal_url + "/registerAccountingInfopwordersystem"
    response = requests.post(register_url, json=data, headers=headers)
    return True

    # if response.status_code == 201:
    #     print({"message": "User created successfully"})
    #     return register_url
    # else:
    #     # print(response.json())
    #     print({"error": str(response.json())})
    #     return False


def updateuserinsalesproportal(data):

    salespro_token = os.getenv('salesproportal_token')

    data["token"] = salespro_token


    salespropotal_url = os.getenv('salesproportal_url')

    headers = {
            "Content-Type": "application/json"   # Optional, ensures JSON content
        }
    register_url = salespropotal_url + "/updateAccountingordersystem"
    response = requests.post(register_url, json=data, headers=headers)


    if response.status_code == 201:
        print({"message": "User updated successfully"})
        return True
    else:
        # print(response.json())
        print({"error": str(response.json())})
        return False


def deleteuserinsalesproportal(data):

    salespro_token = os.getenv('salesproportal_token')

    data["token"] = salespro_token


    salespropotal_url = os.getenv('salesproportal_url')

    headers = {
            "Content-Type": "application/json"   # Optional, ensures JSON content
        }
    register_url = salespropotal_url + "/deleteAccountingordersystem"
    response = requests.post(register_url, json=data, headers=headers)


    if response.status_code == 201:
        print({"message": "User deleted successfully"})
        return True
    else:
        # print(response.json())
        print({"error": str(response.json())})
        return False
