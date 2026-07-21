import os
import sys
sys.path.append(os.getcwd())
import urllib.request
import urllib.error
import json
from dotenv import load_dotenv
load_dotenv()
from app import database, models, auth

db = next(database.get_db())
admin_user = db.query(models.User).filter(models.User.role_id == 1).first()
token = auth.create_access_token(data={"sub": admin_user.email})

try:
    req = urllib.request.Request("http://127.0.0.1:8000/dashboard/metrics?date=today", method="GET")
    req.add_header("Authorization", f"Bearer {token}")
    res = urllib.request.urlopen(req)
    print("/dashboard/metrics:", res.read().decode()[:100])
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code, e.read().decode())
except Exception as e:
    print(e)
