# services/wolfram_service.py
import xml.etree.ElementTree as ET
import requests

def WA_response(input_message):
    """
    Queries the WolframAlpha API with the input message and returns the result.
    """
    url = "http://api.wolframalpha.com/v2/query"
    params = {
        "appid": "QEKE9P-9R44U336AX",
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
