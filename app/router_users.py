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
    employee_id: Optional[str] = None
    full_name: Optional[str] = None
    email: str
    password: str
    role_id: int
    corporate_id: Optional[int] = 1
    store_id: Optional[int] = None
    district_id: Optional[int] = None
    region_id: Optional[int] = None
    is_active: Optional[bool] = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    role_id: Optional[int] = None
    corporate_id: Optional[int] = None
    store_id: Optional[int] = None
    district_id: Optional[int] = None
    region_id: Optional[int] = None
    is_active: Optional[bool] = None

class UserOut(BaseModel):
    id: int
    employee_id: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    role_id: Optional[int] = None
    corporate_id: Optional[int] = None
    store_id: Optional[int] = None
    district_id: Optional[int] = None
    region_id: Optional[int] = None
    is_active: Optional[bool] = None

    class Config:
        from_attributes = True

# List users – accessible by Admin and User Admin
@router.get("/", response_model=List[UserOut])
def list_users(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(router_auth.get_current_active_user),
):
    query = db.query(models.User)
    query = permissions.scope_filter(current_user, query, models.User)
    return query.all()

# Create a new user – admin or user-admin
@router.post("/", response_model=UserOut)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(router_auth.get_current_active_user),
):
    permissions.require_role(current_user, [permissions.ROLE_ADMIN, permissions.ROLE_USERADD])
    # Check for duplicate email
    if db.query(models.User).filter(models.User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    # Hash password (reuse auth utilities)
    from .auth import get_password_hash
    hashed = get_password_hash(user_in.password)
    # Generate employee_id if not provided
    if not user_in.employee_id:
        import uuid
        user_in.employee_id = f"EMP{uuid.uuid4().hex[:5].upper()}"
        
    db_user = models.User(
        employee_id=user_in.employee_id,
        full_name=user_in.full_name,
        email=user_in.email,
        hashed_password=hashed,
        role_id=user_in.role_id,
        corporate_id=user_in.corporate_id,
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
@router.put("/{employee_id}", response_model=UserOut)
def update_user(
    employee_id: str,
    user_in: UserUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(router_auth.get_current_active_user),
):
    target = db.query(models.User).filter(models.User.employee_id == employee_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    # Permission check – admins and user-admins can edit anyone, others edit only themselves
    if current_user.employee_id != employee_id:
        permissions.require_role(current_user, [permissions.ROLE_ADMIN, permissions.ROLE_USERADD])
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
@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    employee_id: str,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(router_auth.get_current_active_user),
):
    permissions.require_role(current_user, [permissions.ROLE_ADMIN, permissions.ROLE_USERADD])
    target = db.query(models.User).filter(models.User.employee_id == employee_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(target)
    db.commit()
    return None

# Assign store/district/region – admin only (individual endpoints)
@router.patch("/{employee_id}/assign-store", response_model=UserOut)
def assign_store(employee_id: str, store_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(router_auth.get_current_active_user)):
    permissions.require_role(current_user, [permissions.ROLE_ADMIN])
    user = db.query(models.User).filter(models.User.employee_id == employee_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.store_id = store_id
    db.commit()
    db.refresh(user)
    return user

@router.patch("/{employee_id}/assign-district", response_model=UserOut)
def assign_district(employee_id: str, district_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(router_auth.get_current_active_user)):
    permissions.require_role(current_user, [permissions.ROLE_ADMIN])
    user = db.query(models.User).filter(models.User.employee_id == employee_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.district_id = district_id
    db.commit()
    db.refresh(user)
    return user

@router.patch("/{employee_id}/assign-region", response_model=UserOut)
def assign_region(employee_id: str, region_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(router_auth.get_current_active_user)):
    permissions.require_role(current_user, [permissions.ROLE_ADMIN])
    user = db.query(models.User).filter(models.User.employee_id == employee_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.region_id = region_id
    db.commit()
    db.refresh(user)
    return user
