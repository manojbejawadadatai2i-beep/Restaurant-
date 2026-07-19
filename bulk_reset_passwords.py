"""
Bulk reset passwords for ALL users that have the placeholder hash.
Sets a default password based on their employee_id (e.g. EMP001 -> password is "EMP001")
so each user has a unique, predictable default password they can change later.
"""
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import User
from app.auth import get_password_hash

PLACEHOLDER = "$2b$12$PLACEHOLDER"  # prefix that identifies fake hashes

def bulk_reset():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print(f"📋 Total users found: {len(users)}\n")

        fixed = 0
        skipped = 0

        for user in users:
            pw = user.hashed_password or ""
            if pw.startswith(PLACEHOLDER) or pw == "" or "PLACEHOLDER" in pw:
                # Default password = their employee_id (e.g. "EMP001")
                # If no employee_id, fall back to "Password@123"
                default_pw = user.employee_id if user.employee_id else "Password@123"
                user.hashed_password = get_password_hash(default_pw)
                print(f"  ✅ {user.email:<40}  password → {default_pw}")
                fixed += 1
            else:
                print(f"  ⏭️  {user.email:<40}  already has a real password (skipped)")
                skipped += 1

        db.commit()
        print(f"\n🎉 Done! {fixed} passwords reset, {skipped} skipped.")
        print("\n📌 Each user's default password is their Employee ID (e.g. EMP001, EMP002...)")
        print("   They should change it after first login.")

    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    bulk_reset()
