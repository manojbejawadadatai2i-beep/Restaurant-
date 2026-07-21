import sys
import os
import random
from datetime import date, timedelta, datetime

backend_dir = os.path.join(os.getcwd(), "backend")
sys.path.append(backend_dir)

from app.core.database import SessionLocal, engine, Base
from app.models.models import HourlyMetric, Store
from sqlalchemy import text

# Create table if not exists
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Check if data exists
existing = db.query(HourlyMetric).first()
if not existing:
    print("Generating mock hourly metrics for the last 30 days...")
    stores = db.query(Store).all()
    today = date.today()
    
    metrics_to_add = []
    
    for store in stores:
        for i in range(30):
            record_date = today - timedelta(days=i)
            # Generate 24 hours of data
            for hour in range(24):
                # Simulate peak around 12pm and 7pm
                is_peak = (11 <= hour <= 13) or (18 <= hour <= 20)
                
                base_orders = random.randint(5, 20) if not is_peak else random.randint(30, 60)
                actual_orders = base_orders + random.randint(-5, 5)
                actual_orders = max(0, actual_orders)
                expected_orders = base_orders
                
                customer_count = int(actual_orders * random.uniform(1.1, 1.5))
                revenue = actual_orders * random.uniform(15.0, 25.0)
                
                hm = HourlyMetric(
                    store_id=store.store_id,
                    record_date=record_date,
                    hour_of_day=hour,
                    expected_orders=expected_orders,
                    actual_orders=actual_orders,
                    customer_count=customer_count,
                    revenue=revenue,
                    created_at=datetime.utcnow()
                )
                metrics_to_add.append(hm)
    
    db.bulk_save_objects(metrics_to_add)
    db.commit()
    print(f"Generated {len(metrics_to_add)} hourly metric records.")
else:
    print("Hourly metrics already exist.")

db.close()
