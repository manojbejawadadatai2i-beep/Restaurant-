import os
import shutil
import re

APP_DIR = os.path.join(os.getcwd(), "app")

NEW_DIRS = ["routers", "core", "db", "services"]
for d in NEW_DIRS:
    os.makedirs(os.path.join(APP_DIR, d), exist_ok=True)

FILE_MAP = {
    "router_auth.py": "routers/auth.py",
    "router_chatbot.py": "routers/chatbot.py",
    "router_dashboard.py": "routers/dashboard.py",
    "router_filters.py": "routers/filters.py",
    "router_insights.py": "routers/insights.py",
    "router_reports.py": "routers/reports.py",
    "router_stores.py": "routers/stores.py",
    "router_users.py": "routers/users.py",
    "router_ws.py": "routers/ws.py",
    
    "auth.py": "core/auth.py",
    "config.py": "core/config.py",
    "permissions.py": "core/permissions.py",
    "utils_jwt.py": "core/utils_jwt.py",
    
    "database.py": "db/database.py",
    "models.py": "db/models.py",
}

MODULE_LOCATIONS = {
    "models": "app.db.models",
    "database": "app.db.database",
    "auth": "app.core.auth",
    "config": "app.core.config",
    "permissions": "app.core.permissions",
    "utils_jwt": "app.core.utils_jwt",
    
    "router_auth": "app.routers.auth",
    "router_chatbot": "app.routers.chatbot",
    "router_dashboard": "app.routers.dashboard",
    "router_filters": "app.routers.filters",
    "router_insights": "app.routers.insights",
    "router_reports": "app.routers.reports",
    "router_stores": "app.routers.stores",
    "router_users": "app.routers.users",
    "router_ws": "app.routers.ws",
}

def replace_imports(content, is_main=False):
    if is_main:
        # In main.py, replace 'from . import router_users, router_dashboard...'
        content = re.sub(r"^from \. import (.*router_.*)$", lambda m: "from app.routers import " + m.group(1).replace("router_", ""), content, flags=re.MULTILINE)
        content = re.sub(r"router_([a-z]+)\.router", r"\1.router", content)
    else:
        # Standard replacements
        def replacer(match):
            imports = [i.strip() for i in match.group(1).split(",")]
            res = []
            for imp in imports:
                if imp in MODULE_LOCATIONS:
                    parent = MODULE_LOCATIONS[imp].rsplit('.', 1)[0]
                    res.append(f"from {parent} import {imp}")
                else:
                    res.append(f"from . import {imp}")
            return "\n".join(res)
        
        content = re.sub(r"^from \. import (.*?)$", replacer, content, flags=re.MULTILINE)
        
        # Absolute imports from app
        for mod, loc in MODULE_LOCATIONS.items():
            content = re.sub(rf"^from app import {mod}$", f"from {loc.rsplit('.', 1)[0]} import {mod}", content, flags=re.MULTILINE)
            content = re.sub(rf"^from app import (.*?, ){mod}(, .*?)?$", lambda m: m.group(0).replace(f" {mod}", "").replace(", ,", ",") + f"\nfrom {loc.rsplit('.', 1)[0]} import {mod}", content, flags=re.MULTILINE)

    return content

for root, _, files in os.walk(APP_DIR):
    for f in files:
        if f.endswith(".py"):
            path = os.path.join(root, f)
            with open(path, "r", encoding="utf-8") as file:
                content = file.read()
            
            new_content = replace_imports(content, is_main=(f == "main.py"))
            
            if new_content != content:
                with open(path, "w", encoding="utf-8") as file:
                    file.write(new_content)

for old_name, new_rel_path in FILE_MAP.items():
    old_path = os.path.join(APP_DIR, old_name)
    new_path = os.path.join(APP_DIR, new_rel_path)
    if os.path.exists(old_path):
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        shutil.move(old_path, new_path)
        print(f"Moved {old_name} -> {new_rel_path}")

print("Done!")
