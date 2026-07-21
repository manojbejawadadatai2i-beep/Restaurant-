# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from typing import List, Optional
# pyrefly: ignore [missing-import]
from pydantic import BaseModel

from app.models import models
from app.core import database
from app.api import auth as router_auth
from app.core import permissions

router = APIRouter(prefix="/users", tags=["users"])

class UserCreate(BaseModel):
    employee_id: Optional[str] = None
    full_name: Optional[str] = None
    email: str
    password: Optional[str] = None
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

class UserCreateOut(UserOut):
    generated_password: Optional[str] = None

class PasswordResetResponse(BaseModel):
    message: str
    temporary_password: str

# List users – accessible by Admin and User Admin
@router.get("", response_model=List[UserOut])
def list_users(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(router_auth.get_current_active_user),
):
    query = db.query(models.User)
    query = permissions.scope_filter(current_user, query, models.User)
    return query.all()

@router.get("/{employee_id}", response_model=UserOut)
def get_user(
    employee_id: str,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(router_auth.get_current_active_user),
):
    user = db.query(models.User).filter(models.User.employee_id == employee_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Create a new user – admin or user-admin
@router.post("", response_model=UserCreateOut)
def create_user(
    user_in: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(router_auth.get_current_active_user),
):
    permissions.require_role(current_user, [permissions.ROLE_ADMIN, permissions.ROLE_USERADD])
    
    # RBAC constraint: User Admin cannot create Corporate Admin
    if current_user.role_id == permissions.ROLE_USERADD and user_in.role_id == permissions.ROLE_ADMIN:
        raise HTTPException(status_code=403, detail="User Admin cannot create Corporate Admins.")

    # Auto populate district and region from store
    if user_in.store_id:
        store = db.query(models.Store).filter(models.Store.id == user_in.store_id).first()
        if not store:
            raise HTTPException(status_code=400, detail="Invalid store selected.")
        user_in.district_id = store.district_id
        if store.district_id:
            district = db.query(models.District).filter(models.District.id == store.district_id).first()
            if district:
                user_in.region_id = district.region_id

    # Store manager constraint
    if user_in.role_id == permissions.ROLE_STORE_MGR and user_in.store_id:
        existing_mgr = db.query(models.User).filter(
            models.User.store_id == user_in.store_id, 
            models.User.role_id == permissions.ROLE_STORE_MGR,
            models.User.is_active == True
        ).first()
        if existing_mgr:
            raise HTTPException(status_code=400, detail="Store already has an active Store Manager.")
            
    # Check for duplicate email
    if db.query(models.User).filter(models.User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Generate employee_id if not provided
    if not user_in.employee_id:
        import uuid
        user_in.employee_id = f"EMP{uuid.uuid4().hex[:5].upper()}"
    else:
        if db.query(models.User).filter(models.User.employee_id == user_in.employee_id).first():
            raise HTTPException(status_code=400, detail="Employee ID already exists.")

    # Generate password automatically
    import string, random
    gen_pass = "Temp@" + "".join(random.choices(string.ascii_letters + string.digits, k=6)) + "!"

    # Hash password (reuse auth utilities)
    from .auth import get_password_hash
    hashed = get_password_hash(gen_pass)
        
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
        must_change_password=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Insert initial password into history
    db_history = models.PasswordHistory(
        user_id=db_user.id,
        hashed_password=hashed
    )
    db.add(db_history)
    db.commit()
    
    # Get human readable names for email
    role_name = "N/A"
    if db_user.role_id:
        role = db.query(models.Role).filter(models.Role.role_id == db_user.role_id).first()
        if role: role_name = role.role_name

    region_name = "N/A"
    if db_user.region_id:
        region = db.query(models.Region).filter(models.Region.id == db_user.region_id).first()
        if region: region_name = region.region_name

    district_name = "N/A"
    if db_user.district_id:
        district = db.query(models.District).filter(models.District.id == db_user.district_id).first()
        if district: district_name = district.district_name

    store_name, store_code = "N/A", "N/A"
    if db_user.store_id:
        store = db.query(models.Store).filter(models.Store.id == db_user.store_id).first()
        if store:
            store_name = store.store_name
            store_code = store.store_id

    # Attach generated password for the response
    db_user.generated_password = gen_pass

    # Send account creation email
    from .services.email_service import send_account_creation_email
    background_tasks.add_task(
        send_account_creation_email,
        full_name=db_user.full_name or "User",
        email=db_user.email,
        role=role_name,
        region=region_name,
        district=district_name,
        store_name=store_name,
        store_id=store_code,
        emp_id=db_user.employee_id,
        temp_password=gen_pass
    )

    # Automatically generate (or append to) a CSV file containing credentials
    import csv, os
    csv_file = "new_users_credentials.csv"
    file_exists = os.path.isfile(csv_file)
    try:
        with open(csv_file, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Full Name", "Email", "Role", "Assignment", "Temporary Password"])
            
            assignment = "Unassigned"
            if store_name != "N/A":
                assignment = f"{store_name}"
            elif district_name != "N/A":
                assignment = f"{district_name}"
            elif region_name != "N/A":
                assignment = f"{region_name}"
                
            writer.writerow([
                db_user.full_name or "Unknown", 
                db_user.email, 
                role_name, 
                assignment, 
                gen_pass
            ])
    except Exception as e:
        print(f"Failed to write to CSV: {e}")

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

@router.post("/{employee_id}/reset-password", response_model=PasswordResetResponse)
def reset_password(
    employee_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(router_auth.get_current_active_user),
):
    permissions.require_role(current_user, [permissions.ROLE_ADMIN, permissions.ROLE_USERADD])
    user = db.query(models.User).filter(models.User.employee_id == employee_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    import string, random
    gen_pass = "Temp@" + "".join(random.choices(string.ascii_letters + string.digits, k=6)) + "!"
    
    from .auth import get_password_hash
    hashed = get_password_hash(gen_pass)
    
    user.hashed_password = hashed
    user.must_change_password = True
    
    db_history = models.PasswordHistory(
        user_id=user.id,
        hashed_password=hashed
    )
    db.add(db_history)
    db.commit()
    
    # Ideally send email here too, but simple return is enough for now.
    return {"message": "Password reset successfully", "temporary_password": gen_pass}
