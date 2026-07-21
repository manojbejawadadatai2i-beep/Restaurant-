import urllib.request
import urllib.error

try:
    req = urllib.request.Request("http://127.0.0.1:8000/docs")
    res = urllib.request.urlopen(req)
    print("Docs status:", res.getcode())
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code, e.read().decode())
except Exception as e:
    print(e)
    
try:
    req = urllib.request.Request("http://127.0.0.1:8000/filters/regions")
    res = urllib.request.urlopen(req)
    print("/filters/regions:", res.getcode(), res.read().decode()[:100])
except urllib.error.HTTPError as e:
    print("/filters/regions HTTP Error:", e.code, e.read().decode()[:200])
except Exception as e:
    print(e)
