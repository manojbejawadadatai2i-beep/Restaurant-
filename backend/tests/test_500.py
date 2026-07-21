import requests

try:
    res = requests.get("http://127.0.0.1:8000/filters/regions?region_id=crash")
except Exception:
    pass
