"""Promote EMP032 to User Admin role (role_id=5)."""
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import User
from app.auth import get_password_hash

def promote_user_admin():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "manojbejawada555@gmail.com").first()
        if not user:
            print("❌ User manojbejawada555@gmail.com not found.")
            return

        user.role_id = 5          # User Admin
        user.is_active = True
        # Also set a working password so they can log in
        user.hashed_password = get_password_hash("useradmin123")
        db.commit()
        print("✅ EMP032 promoted to User Admin (role_id=5)!")
        print("   Email:    manojbejawada555@gmail.com")
        print("   Password: useradmin123")
        print("   Role:     5 (User Admin) — can add/manage users")

    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    promote_user_admin()
