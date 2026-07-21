import sys
import os
from sqlalchemy.orm import Session
sys.path.append(os.getcwd())
from app.database import SessionLocal
from app.models import models
from app import utils_jwt, config
from datetime import timedelta

def test_login_flow():
    db = SessionLocal()
    try:
        user = db.query(models.User).filter(models.User.email == "manojbejawada143@gmail.com").first()
        if not user:
            print("User not found!")
            return
        
        print("User:", user.email)
        
        access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = utils_jwt.create_access_token(
            data={
                "sub": user.email, 
                "role_id": user.role_id,
                "employee_id": user.employee_id,
                "store_id": user.store_id,
                "district_id": user.district_id,
                "region_id": user.region_id
            }, 
            expires_delta=access_token_expires
        )
        print("Token created:", access_token)
        
        role_name = "Unknown Role"
        if user.role_id:
            role = db.query(models.Role).filter(models.Role.role_id == str(user.role_id)).first()
            if role:
                role_name = role.role_name
        print("Role:", role_name)
        
        store_name = "N/A"
        store_code = "N/A"
        if user.store_id:
            store = db.query(models.Store).filter(models.Store.id == user.store_id).first()
            if store:
                store_name = store.store_name
                store_code = store.store_id
        print("Store:", store_name)
        
        try:
            from app.services.email_service import send_welcome_email
            print("Imported send_welcome_email successfully")
            send_welcome_email(
                full_name=user.full_name or "User",
                email=user.email,
                role_name=role_name,
                store_name=store_name,
                store_id=store_code
            )
            print("Email sent (or mocked)")
        except Exception as e:
            print(f"Failed to call send_welcome_email: {e}")
        
        print("Success!")
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        db.close()

test_login_flow()
