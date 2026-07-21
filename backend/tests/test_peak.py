import os
import sys

sys.path.append(os.getcwd())

from dotenv import load_dotenv
load_dotenv()

from app import database, models, router_dashboard
from fastapi import Depends

def run_test():
    db = next(database.get_db())
    admin_user = db.query(models.User).filter(models.User.role_id == 1).first()
    
    try:
        res = router_dashboard.get_peak_hours(
            region="all",
            district="all",
            store="all",
            date="all",
            db=db,
            current_user=admin_user
        )
        print("Success:", res)
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_test()
