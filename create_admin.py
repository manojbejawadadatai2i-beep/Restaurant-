import sys
import os

# Add the current directory to path so we can import app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import User, Role
from app.auth import get_password_hash

def create_admin():
    db = SessionLocal()
    
    try:
        # First check if the role exists, if not create it
        admin_role = db.query(Role).filter(Role.name == "Corporate Administrator").first()
        if not admin_role:
            admin_role = Role(name="Corporate Administrator")
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)
            print("Created 'Corporate Administrator' role.")

        # Check if admin user exists
        admin_email = "admin@restaurant.com"
        existing_user = db.query(User).filter(User.email == admin_email).first()
        if existing_user:
            print(f"User {admin_email} already exists!")
            return

        # Create admin user
        hashed_pw = get_password_hash("admin123")
        admin_user = User(
            email=admin_email,
            hashed_password=hashed_pw,
            role_id=admin_role.id
        )
        db.add(admin_user)
        db.commit()
        print(f"Successfully created admin user:\nEmail: {admin_email}\nPassword: admin123")
    except Exception as e:
        print(f"Error creating admin user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
