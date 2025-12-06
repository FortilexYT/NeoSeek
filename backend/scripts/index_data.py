import requests
import json

url = "http://127.0.0.1:7700/indexes/docs/documents"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer rVR_Z3zs5Ah3zwbrJhj1HL7SgxoCssmdBiQd6A1Coj4"
}

with open("../../data/sample.json", "r", encoding="utf-8") as f:
    data = json.load(f)

response = requests.post(url, headers=headers, json=data)
print(response.status_code, response.text)
