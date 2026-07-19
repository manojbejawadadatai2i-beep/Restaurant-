# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException, status
# pyrefly: ignore [missing-import]
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from datetime import timedelta
# pyrefly: ignore [missing-import]
from pydantic import BaseModel

from . import models, database, auth, utils_jwt, config

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
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
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
            "region_id": user.region_id
        }, 
        expires_delta=access_token_expires
    )
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
            detail=f"User with email '{email}' is not registered in the system database."
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
            "region_id": user.region_id
        }, 
        expires_delta=access_token_expires
    )
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

