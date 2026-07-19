import os
# pyrefly: ignore [missing-import]
from sqlalchemy import create_engine
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import sessionmaker
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

from app.models import User, Sale
from app.permissions import scope_filter

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

db = SessionLocal()
user = db.query(User).filter(User.email == 'manoj@restaurant.com').first()
print(f"User: {user.email}, Role: {user.role_id}, Store: '{user.store_id}'")

query = db.query(Sale)
query = scope_filter(user, query, Sale)
print("Query SQL:", str(query.statement.compile(compile_kwargs={"literal_binds": True})))

sales = query.all()
print(f"Sales found: {len(sales)}")
for s in sales:
    print(f"  Sale ID: {s.sale_id}, Revenue: {s.revenue}, Store: {s.store_id}")
