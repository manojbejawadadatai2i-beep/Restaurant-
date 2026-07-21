import urllib.request
import urllib.parse

try:
    url = 'http://localhost:8000/test_db'
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        print("TEST_DB:", response.read().decode())
except Exception as e:
    print("TEST_DB ERROR:", e)
    try:
        print("ERROR BODY:", e.read().decode())
    except:
        pass

try:
    url = 'http://localhost:8000/auth/login'
    data = urllib.parse.urlencode({'username':'admin@example.com', 'password':'password'}).encode('utf-8')
    req = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(req) as response:
        print("LOGIN:", response.read().decode())
except Exception as e:
    print("LOGIN ERROR:", e)
    try:
        print("ERROR BODY:", e.read().decode())
    except:
        pass
