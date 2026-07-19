import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import User

def activate_all_pending_users():
    db = SessionLocal()
    try:
        pending_users = db.query(User).filter(User.is_active == False).all()
        if not pending_users:
            print("✅ No pending users found.")
            return

        for user in pending_users:
            user.is_active = True
            print(f"✅ Activated user: {user.email}")
            
        db.commit()
        print("✅ All pending users have been approved and activated!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    activate_all_pending_users()
