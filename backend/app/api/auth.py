# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException, status
# pyrefly: ignore [missing-import]
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from datetime import timedelta
# pyrefly: ignore [missing-import]
from pydantic import BaseModel

from app.models import models
from app.core import database
from app.core import auth
from app.core import utils_jwt
from app.core import config

router = APIRouter(prefix="/auth", tags=["auth"])


class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str = ""
    role_id: int = 4


class Token(BaseModel):
    access_token: str
    token_type: str


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = auth.jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except auth.JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(current_user: models.User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account pending admin approval"
        )
    return current_user


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account not found or incorrect password. Please ask a User Admin to add your account.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account not found or incorrect password. Please ask a User Admin to add your account.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account pending admin approval"
        )
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = utils_jwt.create_access_token(
        data={
            "sub": user.email, 
            "role_id": user.role_id,
            "employee_id": user.employee_id,
            "store_id": user.store_id,
            "district_id": user.district_id,
            "region_id": user.region_id,
            "must_change_password": getattr(user, "must_change_password", False)
        }, 
        expires_delta=access_token_expires
    )

    role_name = "Unknown Role"
    if user.role_id:
        role = db.query(models.Role).filter(models.Role.role_id == user.role_id).first()
        if role:
            role_name = role.role_name

    store_name = "N/A"
    store_code = "N/A"
    if user.store_id:
        store = db.query(models.Store).filter(models.Store.id == user.store_id).first()
        if store:
            store_name = store.store_name
            store_code = store.store_id

    try:
        from app.services.email_service import send_welcome_email
        send_welcome_email(
            full_name=user.full_name or "User",
            email=user.email,
            role_name=role_name,
            store_name=store_name,
            store_id=store_code
        )
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Failed to call send_welcome_email: {e}")

    return {"access_token": access_token, "token_type": "bearer"}


class GoogleLoginRequest(BaseModel):
    id_token: str


@router.post("/google", response_model=Token)
def google_login(payload: GoogleLoginRequest, db: Session = Depends(database.get_db)):
    import urllib.request
    import urllib.parse
    import json

    try:
        url = f"https://oauth2.googleapis.com/tokeninfo?id_token={urllib.parse.quote(payload.id_token)}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            res_data = json.loads(response.read().decode())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to verify Google Token: {str(e)}"
        )

    email = res_data.get("email")
    email_verified = res_data.get("email_verified")

    if not email or (email_verified not in [True, "true"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google account email is not verified or could not be retrieved"
        )

    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Account with email '{email}' is not registered. Please ask a User Admin to add your account."
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account pending admin approval"
        )

    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = utils_jwt.create_access_token(
        data={
            "sub": user.email, 
            "role_id": user.role_id,
            "employee_id": user.employee_id,
            "store_id": user.store_id,
            "district_id": user.district_id,
            "region_id": user.region_id,
            "must_change_password": getattr(user, "must_change_password", False)
        }, 
        expires_delta=access_token_expires
    )

    role_name = "Unknown Role"
    if user.role_id:
        role = db.query(models.Role).filter(models.Role.role_id == user.role_id).first()
        if role:
            role_name = role.role_name

    store_name = "N/A"
    store_code = "N/A"
    if user.store_id:
        store = db.query(models.Store).filter(models.Store.id == user.store_id).first()
        if store:
            store_name = store.store_name
            store_code = store.store_id

    try:
        from app.services.email_service import send_welcome_email
        send_welcome_email(
            full_name=user.full_name or "User",
            email=user.email,
            role_name=role_name,
            store_name=store_name,
            store_id=store_code
        )
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Failed to call send_welcome_email: {e}")

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register")
def register(user_in: UserCreate, db: Session = Depends(database.get_db)):
    import uuid
    import traceback
    import bcrypt as _bc

    # Check if user already exists
    if db.query(models.User).filter(models.User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password directly using bcrypt
    try:
        salt = _bc.gensalt()
        hashed_bytes = _bc.hashpw(user_in.password.encode("utf-8"), salt)
        hashed = hashed_bytes.decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Password hashing failed: {e}\n{traceback.format_exc()}")

    # Generate employee_id: "EMP" + 5 random hex chars
    try:
        emp_id = f"EMP{uuid.uuid4().hex[:5].upper()}"
        db_user = models.User(
            employee_id=emp_id,
            full_name=user_in.full_name,
            email=user_in.email,
            hashed_password=hashed,
            role_id=user_in.role_id,
            corporate_id=1,
            is_active=False  # pending admin approval
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Database error: {e}\n{traceback.format_exc()}")

    return {
        "message": "Registration successful! Your account is pending admin approval.",
        "employee_id": db_user.employee_id,
        "email": db_user.email,
    }


class ChangePasswordRequest(BaseModel):
    new_password: str

@router.post("/change-password")
def change_password(
    req: ChangePasswordRequest, 
    db: Session = Depends(database.get_db), 
    current_user: models.User = Depends(get_current_active_user)
):
    import re
    pwd = req.new_password
    if len(pwd) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long.")
    if not re.search(r"[A-Z]", pwd):
        raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter.")
    if not re.search(r"[a-z]", pwd):
        raise HTTPException(status_code=400, detail="Password must contain at least one lowercase letter.")
    if not re.search(r"[0-9]", pwd):
        raise HTTPException(status_code=400, detail="Password must contain at least one number.")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", pwd):
        raise HTTPException(status_code=400, detail="Password must contain at least one special character.")
        
    if auth.verify_password(req.new_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="New password cannot be the same as the old password.")
        
    histories = db.query(models.PasswordHistory).filter(models.PasswordHistory.user_id == current_user.id).order_by(models.PasswordHistory.created_at.desc()).limit(5).all()
    for h in histories:
        if auth.verify_password(req.new_password, h.hashed_password):
            raise HTTPException(status_code=400, detail="Cannot reuse any of your last 5 passwords.")
            
    new_hash = auth.get_password_hash(req.new_password)
    current_user.hashed_password = new_hash
    current_user.must_change_password = False
    from datetime import datetime
    current_user.password_changed_at = datetime.utcnow()
    
    new_history = models.PasswordHistory(
        user_id=current_user.id,
        hashed_password=new_hash
    )
    db.add(new_history)
    db.commit()
    db.refresh(current_user)
    
    # Generate fresh token so they don't have to log in again
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = utils_jwt.create_access_token(
        data={
            "sub": current_user.email, 
            "role_id": current_user.role_id,
            "employee_id": current_user.employee_id,
            "store_id": current_user.store_id,
            "district_id": current_user.district_id,
            "region_id": current_user.region_id,
            "must_change_password": False
        }, 
        expires_delta=access_token_expires
    )
    
    return {"message": "Password changed successfully", "access_token": access_token, "token_type": "bearer"}
