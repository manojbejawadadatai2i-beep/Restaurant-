import sys
import os
sys.path.append(os.getcwd())
from app.database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
for col in inspector.get_columns("roles"):
    print(col["name"], col["type"])
