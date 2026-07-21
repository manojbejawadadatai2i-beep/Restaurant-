import urllib.request
import urllib.parse
import json

try:
    url = 'http://localhost:8000/auth/register'
    data = json.dumps({"email":"newuser123@example.com", "password":"password123", "full_name":"New User", "role_id":4}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as response:
        print("REGISTER:", response.read().decode())
except Exception as e:
    print("REGISTER ERROR:", e)
    try:
        print("ERROR BODY:", e.read().decode())
    except:
        pass
