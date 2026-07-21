import sys
import os

backend_dir = os.path.join(os.getcwd(), "backend")
sys.path.append(backend_dir)

from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

print("--- SALES ---")
sales = db.execute(text('SELECT * FROM sales LIMIT 5;')).fetchall()
for r in sales:
    print(r)

print("\n--- TABLES IN DB ---")
tables = db.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")).fetchall()
for t in tables:
    print(t[0])

db.close()
