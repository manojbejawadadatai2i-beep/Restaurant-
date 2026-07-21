import sys
import os
sys.path.append(os.getcwd())

from app.database import SessionLocal
from app.models import models
from app.services.llm_service import execute_get_sales_summary, execute_get_store_performance, execute_get_user_stats

def test_executors():
    db = SessionLocal()
    try:
        # Test as Corporate Admin
        admin = db.query(models.User).filter(models.User.email == "manojbejawada143@gmail.com").first()
        if admin:
            print("--- ADMIN TEST ---")
            print("Sales Summary:", execute_get_sales_summary(admin, db, {}))
            print("Store Performance:", execute_get_store_performance(admin, db, {"limit": 3}))
            print("User Stats:", execute_get_user_stats(admin, db, {}))
            
        # Test as Store Manager
        manager = db.query(models.User).filter(models.User.email == "manojbejawada55@gmail.com").first()
        if manager:
            print("\n--- MANAGER TEST ---")
            print("Sales Summary:", execute_get_sales_summary(manager, db, {}))
            print("Store Performance:", execute_get_store_performance(manager, db, {"limit": 3}))
            print("User Stats:", execute_get_user_stats(manager, db, {}))
            
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_executors()
