import sys
import os

backend_dir = os.path.join(os.getcwd(), "backend")
sys.path.append(backend_dir)
os.chdir(backend_dir)

try:
    import app.main
    print("Backend import successful!")
except Exception as e:
    import traceback
    traceback.print_exc()
