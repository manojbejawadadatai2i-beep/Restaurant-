from app.database import SessionLocal
from app.models import Store, Sale
import uuid
import random
from datetime import date, timedelta, datetime

db = SessionLocal()

# Delete existing sales if any
db.query(Sale).delete()
db.commit()

stores = db.query(Store).all()
if not stores:
    print("No stores found to seed sales data.")
    exit(1)

print(f"Found {len(stores)} stores. Generating sales data...")

today = date.today()
sales_to_insert = []

for store in stores:
    # Generate 10-20 random days of sales for each store in the past month
    num_days = random.randint(10, 20)
    for _ in range(num_days):
        days_ago = random.randint(0, 30)
        sale_date = today - timedelta(days=days_ago)
        
        # Random metrics
        order_count = random.randint(10, 100)
        customer_count = int(order_count * random.uniform(1.1, 1.5))
        revenue = order_count * random.uniform(15.0, 45.0)
        
        sale = Sale(
            sale_id=f"SALE{uuid.uuid4().hex[:8].upper()}",
            store_id=store.store_id, # store_code
            revenue=round(revenue, 2),
            order_count=order_count,
            customer_count=customer_count,
            sale_date=sale_date,
            created_at=datetime.utcnow()
        )
        sales_to_insert.append(sale)

db.bulk_save_objects(sales_to_insert)
db.commit()

print(f"Successfully inserted {len(sales_to_insert)} sales records!")
