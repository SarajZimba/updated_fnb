import requests


def postbillintoird(cbms_payload):
        # 6️⃣ Post to IRD CBMS

        cbms_url = "https://cbapi.ird.gov.np/api/bill"
        headers = {"Content-Type": "application/json"}
        r = requests.post(cbms_url, json=cbms_payload, headers=headers, timeout=10)

        if r.status_code == 200:
            print( f"BIll {cbms_payload} posted successfully into ird {r.text}")
        else:
            print( "CBMS API failed",r.text)
            # return {"success": "", "cbms_error": r.text}, 400