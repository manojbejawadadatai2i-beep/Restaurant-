import os

FRONTEND_DIR = os.path.join(os.getcwd(), "frontend")

for root, dirs, files in os.walk(FRONTEND_DIR):
    if "node_modules" in dirs:
        dirs.remove("node_modules")
    if ".next" in dirs:
        dirs.remove(".next")
        
    for f in files:
        if f.endswith((".tsx", ".ts", ".js", ".jsx")):
            path = os.path.join(root, f)
            with open(path, "r", encoding="utf-8") as file:
                content = file.read()
            
            new_content = content.replace('from "@/config"', 'from "@/utils/config"')
            
            if new_content != content:
                with open(path, "w", encoding="utf-8") as file:
                    file.write(new_content)
print("Done fixing config imports!")
