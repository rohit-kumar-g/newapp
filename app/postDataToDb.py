import os
import json
import requests



def postSheet(data, id):
    print("posting "+ id)
    # print(data)
    # Google Apps Script URL
    try:
        reqUrl = f"{os.getenv('SCRIPT_URL', 'http://localhost')}?id={id}"
        

        # Headers for the POST request
        headersList = {
            "Accept": "*/*",
            "Content-Type": "application/json"
        }

        # Convert the data to JSON
        payload = json.dumps(data)

        # Make the POST request
        response = requests.request("POST", reqUrl, data=payload, headers=headersList)

        print(response.text)
    except Exception as e:
        # Handle the exception (e.g., log the error)
        print(f"An error occurred: {e}")
