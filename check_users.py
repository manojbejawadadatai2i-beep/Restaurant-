import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import User
# pyrefly: ignore [missing-import]
from sqlalchemy import text

def check_db():
    db = SessionLocal()
    try:
        print("--- Testing Database Connection ---")
        result = db.execute(text("SELECT 1")).scalar()
        print("Connection Successful! Result:", result)
        
        print("\n--- Querying Users Table ---")
        users = db.query(User).all()
        print(f"Found {len(users)} users in the database.")
        for u in users:
            print(f"ID: {u.id}, Email: {u.email}, Name: {u.full_name}, PW Hash: {u.hashed_password}, Role ID: {u.role_id}")
            
    except Exception as e:
        print("\n!!! ERROR connecting to DB or querying users !!!")
        print(str(e))
    finally:
        db.close()

if __name__ == "__main__":
    check_db()
