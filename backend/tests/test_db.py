import os

# pyrefly: ignore [missing-import]
from sqlalchemy import text
from app.database import engine

def test_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("Database connected successfully! Result:", result.scalar())
    except Exception as e:
        print("Database connection failed:", str(e))

if __name__ == "__main__":
    test_connection()
