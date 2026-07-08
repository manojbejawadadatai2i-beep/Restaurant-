# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException, status
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from typing import List, Optional
# pyrefly: ignore [missing-import]
from pydantic import BaseModel

from . import models, database, router_auth, permissions

router = APIRouter(prefix="/users", tags=["users"])

class UserCreate(BaseModel):
    user_id: str
    full_name: Optional[str] = None
    email: str
    password: str
    role_id: str
    store_id: Optional[str] = None
    district_id: Optional[str] = None
    region_id: Optional[str] = None
    is_active: Optional[bool] = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    role_id: Optional[str] = None
    store_id: Optional[str] = None
    district_id: Optional[str] = None
    region_id: Optional[str] = None
    is_active: Optional[bool] = None

class UserOut(BaseModel):
    user_id: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    role_id: Optional[str] = None
    store_id: Optional[str] = None
    district_id: Optional[str] = None
    region_id: Optional[str] = None
    is_active: Optional[bool] = None

    class Config:
        from_attributes = True

# List users – filtered by caller's scope
@router.get("/", response_model=List[UserOut])
def list_users(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(router_auth.get_current_active_user),
):
    query = db.query(models.User)
    query = permissions.scope_filter(current_user, query, models.User)
    return query.all()

# Create a new user – admin only
@router.post("/", response_model=UserOut)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(router_auth.get_current_active_user),
):
    permissions.require_role(current_user, [permissions.ROLE_ADMIN])
    # Check for duplicate email
    if db.query(models.User).filter(models.User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    # Hash password (reuse auth utilities)
    from .auth import get_password_hash
    hashed = get_password_hash(user_in.password)
    db_user = models.User(
        user_id=user_in.user_id,
        full_name=user_in.full_name,
        email=user_in.email,
        hashed_password=hashed,
        role_id=user_in.role_id,
        store_id=user_in.store_id,
        district_id=user_in.district_id,
        region_id=user_in.region_id,
        is_active=user_in.is_active,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Update user – admin can edit anyone, users can edit themselves
@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: str,
    user_in: UserUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(router_auth.get_current_active_user),
):
    target = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    # Permission check
    if current_user.user_id != user_id:
        permissions.require_role(current_user, [permissions.ROLE_ADMIN])
    # Apply updates
    if user_in.password:
        from .auth import get_password_hash
        target.hashed_password = get_password_hash(user_in.password)
    for attr, value in user_in.dict(exclude_unset=True).items():
        if attr != "password":
            setattr(target, attr, value)
    db.commit()
    db.refresh(target)
    return target

# Delete user – admin only
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(router_auth.get_current_active_user),
):
    permissions.require_role(current_user, [permissions.ROLE_ADMIN])
    target = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(target)
    db.commit()
    return None

# Assign store/district/region – admin only (individual endpoints)
@router.patch("/{user_id}/assign-store", response_model=UserOut)
def assign_store(user_id: str, store_id: str, db: Session = Depends(database.get_db), current_user: models.User = Depends(router_auth.get_current_active_user)):
    permissions.require_role(current_user, [permissions.ROLE_ADMIN])
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.store_id = store_id
    db.commit()
    db.refresh(user)
    return user

@router.patch("/{user_id}/assign-district", response_model=UserOut)
def assign_district(user_id: str, district_id: str, db: Session = Depends(database.get_db), current_user: models.User = Depends(router_auth.get_current_active_user)):
    permissions.require_role(current_user, [permissions.ROLE_ADMIN])
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.district_id = district_id
    db.commit()
    db.refresh(user)
    return user

@router.patch("/{user_id}/assign-region", response_model=UserOut)
def assign_region(user_id: str, region_id: str, db: Session = Depends(database.get_db), current_user: models.User = Depends(router_auth.get_current_active_user)):
    permissions.require_role(current_user, [permissions.ROLE_ADMIN])
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.region_id = region_id
    db.commit()
    db.refresh(user)
    return user
