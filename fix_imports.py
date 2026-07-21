import os
import re

APP_DIR = os.path.join(os.getcwd(), "app")

for root, _, files in os.walk(APP_DIR):
    for f in files:
        if f.endswith(".py"):
            path = os.path.join(root, f)
            with open(path, "r", encoding="utf-8") as file:
                content = file.read()
            
            new_content = content.replace("from app.routers import router_auth", "from app.routers import auth as router_auth")
            
            if new_content != content:
                with open(path, "w", encoding="utf-8") as file:
                    file.write(new_content)
print("Done!")
