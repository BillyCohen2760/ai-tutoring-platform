# services/wolfram_service.py
# This code was developed with the help of WolframAlpha documentation (https://products.wolframalpha.com/api/documentation). 
import xml.etree.ElementTree as ET
import requests
import os

def WA_response(input_message):
    """
    Queries the WolframAlpha API with the input message and returns the result.
    """
    url = "http://api.wolframalpha.com/v2/query"
    params = {
        "appid": os.getenv('WA_KEY'),
        "input": input_message,
        "format": "plaintext"
    }
    response = requests.get(url, params=params)

    if response.status_code != 200:
        return f"Error: API request failed with status code {response.status_code}"

    tree = ET.fromstring(response.text)
    results = tree.findall(".//pod[@id='Result']/subpod/plaintext")
    answers = [result.text for result in results if result is not None and result.text]

    return answers if answers else ["No results found."]
