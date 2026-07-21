import os
import shutil
import glob
import re

ROOT_DIR = os.getcwd()
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")

# 1. Create Backend Structure
BACKEND_APP_DIR = os.path.join(BACKEND_DIR, "app")
BACKEND_FOLDERS = [
    "api", "core", "models", "schemas", "services", "repositories",
    "middleware", "utils", "chatbot", "prompts", "dependencies", "static", "templates"
]
os.makedirs(BACKEND_DIR, exist_ok=True)
os.makedirs(BACKEND_APP_DIR, exist_ok=True)
for f in BACKEND_FOLDERS:
    os.makedirs(os.path.join(BACKEND_APP_DIR, f), exist_ok=True)
os.makedirs(os.path.join(BACKEND_DIR, "tests"), exist_ok=True)

# Create standard empty __init__.py files
with open(os.path.join(BACKEND_APP_DIR, "__init__.py"), "w") as f: f.write("")
for folder in BACKEND_FOLDERS:
    with open(os.path.join(BACKEND_APP_DIR, folder, "__init__.py"), "w") as f: f.write("")

# 2. Move existing app/ to backend/app/
OLD_APP_DIR = os.path.join(ROOT_DIR, "app")
if os.path.exists(OLD_APP_DIR):
    # Move api (routers -> api)
    if os.path.exists(os.path.join(OLD_APP_DIR, "routers")):
        for item in os.listdir(os.path.join(OLD_APP_DIR, "routers")):
            shutil.move(os.path.join(OLD_APP_DIR, "routers", item), os.path.join(BACKEND_APP_DIR, "api", item))
    
    # Move core
    if os.path.exists(os.path.join(OLD_APP_DIR, "core")):
        for item in os.listdir(os.path.join(OLD_APP_DIR, "core")):
            shutil.move(os.path.join(OLD_APP_DIR, "core", item), os.path.join(BACKEND_APP_DIR, "core", item))
            
    # Move db/models.py and db/database.py
    if os.path.exists(os.path.join(OLD_APP_DIR, "db")):
        if os.path.exists(os.path.join(OLD_APP_DIR, "db", "models.py")):
            shutil.move(os.path.join(OLD_APP_DIR, "db", "models.py"), os.path.join(BACKEND_APP_DIR, "models", "models.py"))
        if os.path.exists(os.path.join(OLD_APP_DIR, "db", "database.py")):
            shutil.move(os.path.join(OLD_APP_DIR, "db", "database.py"), os.path.join(BACKEND_APP_DIR, "core", "database.py"))
            
    # Move services
    if os.path.exists(os.path.join(OLD_APP_DIR, "services")):
        for item in os.listdir(os.path.join(OLD_APP_DIR, "services")):
            if item != "__pycache__":
                shutil.move(os.path.join(OLD_APP_DIR, "services", item), os.path.join(BACKEND_APP_DIR, "services", item))
                
    # Move main.py
    if os.path.exists(os.path.join(OLD_APP_DIR, "main.py")):
        shutil.move(os.path.join(OLD_APP_DIR, "main.py"), os.path.join(BACKEND_APP_DIR, "main.py"))
        
    shutil.rmtree(OLD_APP_DIR, ignore_errors=True)

# 3. Move Root Python scripts & files
for py_file in glob.glob("*.py"):
    if py_file.startswith("test_"):
        shutil.move(py_file, os.path.join(BACKEND_DIR, "tests", py_file))
    elif py_file not in ["refactor_app.py", "fix_imports.py"]:
        # Put other root scripts into backend root
        shutil.move(py_file, os.path.join(BACKEND_DIR, py_file))

if os.path.exists(".env"):
    shutil.copy(".env", os.path.join(BACKEND_DIR, ".env"))

if os.path.exists("requirements.txt") and not os.path.isdir("requirements.txt"):
    shutil.move("requirements.txt", os.path.join(BACKEND_DIR, "requirements.txt"))
elif os.path.isdir("requirements.txt"):
    # Delete accidental dir
    shutil.rmtree("requirements.txt")
    with open(os.path.join(BACKEND_DIR, "requirements.txt"), "w") as f: f.write("fastapi\nuvicorn\nsqlalchemy\npydantic\n")
else:
    with open(os.path.join(BACKEND_DIR, "requirements.txt"), "w") as f: f.write("fastapi\nuvicorn\nsqlalchemy\npydantic\n")

if not os.path.exists(os.path.join(BACKEND_DIR, "Dockerfile")):
    with open(os.path.join(BACKEND_DIR, "Dockerfile"), "w") as f: f.write("FROM python:3.11\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install -r requirements.txt\nCOPY . .\nCMD [\"uvicorn\", \"app.main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]")

if not os.path.exists(os.path.join(BACKEND_DIR, "docker-compose.yml")):
    with open(os.path.join(BACKEND_DIR, "docker-compose.yml"), "w") as f: f.write("version: '3.8'\nservices:\n  backend:\n    build: .\n    ports:\n      - \"8000:8000\"")


# 4. Create Frontend Structure
FRONTEND_SRC_DIR = os.path.join(FRONTEND_DIR, "src")
FRONTEND_FOLDERS = ["app", "components", "layouts", "features", "hooks", "services", "api", "context", "utils", "types", "styles", "assets"]
for f in FRONTEND_FOLDERS:
    os.makedirs(os.path.join(FRONTEND_SRC_DIR, f), exist_ok=True)

if os.path.exists(os.path.join(FRONTEND_SRC_DIR, "app", "globals.css")):
    shutil.move(os.path.join(FRONTEND_SRC_DIR, "app", "globals.css"), os.path.join(FRONTEND_SRC_DIR, "styles", "globals.css"))

if os.path.exists(os.path.join(FRONTEND_SRC_DIR, "config.ts")):
    shutil.move(os.path.join(FRONTEND_SRC_DIR, "config.ts"), os.path.join(FRONTEND_SRC_DIR, "utils", "config.ts"))

if os.path.exists(".env"):
    shutil.copy(".env", os.path.join(FRONTEND_DIR, ".env"))

# 5. Fix Python Imports
def fix_python_imports(content):
    content = content.replace("from app.api import", "from app.api import")
    content = content.replace("from app.models import models", "from app.models import models")
    content = content.replace("from app.core import database", "from app.core import database")
    content = content.replace("from app.models import models", "from app.models import models")
    return content

for root, _, files in os.walk(BACKEND_DIR):
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            new_content = fix_python_imports(content)
            if new_content != content:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new_content)

# 6. Fix Frontend Imports
def fix_tsx_imports(content):
    content = content.replace('import "./globals.css"', 'import "@/styles/globals.css"')
    content = content.replace('import "@/config"', 'import "@/utils/config"')
    return content

for root, _, files in os.walk(FRONTEND_DIR):
    for file in files:
        if file.endswith((".tsx", ".ts", ".js", ".jsx")):
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            new_content = fix_tsx_imports(content)
            if new_content != content:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new_content)

print("Restructure complete!")
