import os
import sys

sys.path.append(os.getcwd())

import urllib.request
import urllib.error
import urllib.parse
import json

from dotenv import load_dotenv
load_dotenv()

from app import database, models, auth
from fastapi import Depends

db = next(database.get_db())
admin_user = db.query(models.User).filter(models.User.role_id == 1).first()

# mint token
token = auth.create_access_token(data={"sub": admin_user.email})

try:
    # Now try peak hours
    req2 = urllib.request.Request("http://127.0.0.1:8000/dashboard/peak-hours?date=today", method="GET")
    req2.add_header("Authorization", f"Bearer {token}")
    res2 = urllib.request.urlopen(req2)
    print("Peak hours success:", res2.read()[:100])
    
    # Try chatbot
    req3 = urllib.request.Request("http://127.0.0.1:8000/chatbot/ask", method="POST")
    req3.add_header("Authorization", f"Bearer {token}")
    req3.add_header("Content-Type", "application/json")
    res3 = urllib.request.urlopen(req3, data=json.dumps({"query": "hi"}).encode())
    print("Chatbot success:", res3.read()[:100])
    
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code)
    print("BODY:", e.read().decode())
except Exception as e:
    print(e)
