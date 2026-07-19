import os
# pyrefly: ignore [missing-import]
import bcrypt as _bcrypt
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError

SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Expose JWTError so router_auth can catch it
JWTError = JWTError


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Handle missing or empty hash
    if not hashed_password:
        return False
    # Handle legacy plain text passwords stored directly in DB
    if not hashed_password.startswith("$2b$"):
        return plain_password == hashed_password
    # bcrypt hashes must be exactly 60 characters — reject malformed hashes
    # to prevent a Rust-level panic inside the pyo3 bcrypt binding
    if len(hashed_password) != 60:
        return False
    try:
        return _bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except BaseException:
        # Catches pyo3_runtime.PanicException which inherits from BaseException
        # not Exception, so a plain `except Exception` misses it
        return False


def get_password_hash(password: str) -> str:
    salt = _bcrypt.gensalt()
    hashed = _bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
