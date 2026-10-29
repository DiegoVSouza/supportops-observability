import json
from urllib.request import urlopen

with urlopen("http://127.0.0.1:29090/api/v1/alerts", timeout=5) as response:
    data = json.load(response)
print(json.dumps([{ "name": item["labels"].get("alertname"), "state": item["state"]} for item in data["data"]["alerts"]]))
