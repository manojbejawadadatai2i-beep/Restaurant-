"""Seed an admin user into the restaurant_dashboard database.
Matches the actual DB schema: id (int PK), employee_id, role_id (int), etc.
"""
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import User
from app.auth import get_password_hash

def seed():
    db = SessionLocal()
    try:
        # Check if EMP001 (Corporate Admin) already exists
        existing = db.query(User).filter(User.employee_id == "EMP001").first()
        if existing:
            print(f"⚠️  Admin user EMP001 already exists (email={existing.email})")
            print(f"   You can log in with: {existing.email}")
        else:
            hashed = get_password_hash("admin123")
            admin = User(
                employee_id="EMP001",
                full_name="Corporate Admin",
                email="admin@restaurant.com",
                hashed_password=hashed,
                role_id=1,          # Corporate Administrator
                corporate_id=1,
                is_active=True,
            )
            db.add(admin)
            db.commit()
            print("✅ Admin user created!")
            print("   Employee ID: EMP001")
            print("   Email:       admin@restaurant.com")
            print("   Password:    admin123")
            print("   Role:        1 (Corporate Administrator)")

        # Show all users
        all_users = db.query(User).all()
        print(f"\n📋 Total users in database: {len(all_users)}")
        for u in all_users:
            print(f"   {u.employee_id} | {u.email} | role={u.role_id} | active={u.is_active}")

    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
