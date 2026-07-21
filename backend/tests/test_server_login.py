import urllib.request
import urllib.parse

try:
    url = 'http://localhost:8000/auth/login'
    data = urllib.parse.urlencode({'username':'manojbejawada143@gmail.com', 'password':'password'}).encode('utf-8')
    req = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(req) as response:
        print("LOGIN:", response.read().decode())
except Exception as e:
    print("LOGIN ERROR:", e)
    try:
        print("ERROR BODY:", e.read().decode())
    except:
        pass
