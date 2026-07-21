import os
import sys
sys.path.append(os.getcwd())
import urllib.request
import json
from dotenv import load_dotenv
load_dotenv()

key = os.getenv("GROQ_API_KEY")
req = urllib.request.Request("https://api.groq.com/openai/v1/models", headers={"Authorization": f"Bearer {key}", "User-Agent": "Mozilla/5.0"})
try:
    res = urllib.request.urlopen(req)
    models = json.loads(res.read()).get("data", [])
    for m in models:
        print(m["id"])
except Exception as e:
    print(e)
