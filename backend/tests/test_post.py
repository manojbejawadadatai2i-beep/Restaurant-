import urllib.request
import urllib.error
import json
import sys

# Get a valid token first
try:
    # We need to simulate the login or just use the backend db directly to mint a token, 
    # but the simplest way to see if there's a 500 error is to send a request without a token.
    # It should return 401 JSON. If it returns 500 plain text, we found the bug!
    req = urllib.request.Request("http://127.0.0.1:8000/chatbot/ask", method="POST")
    req.add_header("Content-Type", "application/json")
    res = urllib.request.urlopen(req, data=json.dumps({"query": "hi"}).encode())
    print("Success:", res.read())
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print("HTTP Error:", e.code)
    print("BODY:", body)
except Exception as e:
    print(e)
