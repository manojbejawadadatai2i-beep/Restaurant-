import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    print("--- USERS ---")
    users = conn.execute(text("SELECT email, role_id, full_name FROM users")).fetchall()
    for u in users:
        print(f"User: {u.email}, Role: {u.role_id}, Name: {u.full_name}")
