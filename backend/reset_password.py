"""Reset password for an existing user."""
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import User
from app.auth import get_password_hash

def reset_password(email: str, new_password: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"❌ User with email '{email}' not found.")
            return

        user.hashed_password = get_password_hash(new_password)
        db.commit()
        print(f"✅ Password reset successfully for {email}!")
        print(f"   You can now log in with password: {new_password}")

    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reset_password("manoj@gmail.com", "admin123")
