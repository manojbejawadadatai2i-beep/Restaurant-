# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from typing import List
# pyrefly: ignore [missing-import]
from pydantic import BaseModel
from typing import Optional
# pyrefly: ignore [missing-import]
from fastapi import HTTPException
from app.models import models
from app.core import database
from app.api import auth as router_auth
from app.core import permissions

router = APIRouter(prefix="/stores", tags=["stores"])


class StoreOut(BaseModel):
    id: int
    store_id: str
    district_id: Optional[int] = None
    store_name: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    manager_name: Optional[str] = None
    status: Optional[str] = None
    total_revenue: float = 0.0
    today_revenue: float = 0.0

    class Config:
        from_attributes = True


class StoreCreate(BaseModel):
    store_name: str
    district_id: int
    city: Optional[str] = None
    address: Optional[str] = None
    manager_name: Optional[str] = None
    status: Optional[str] = "ACTIVE"


@router.post("", response_model=StoreOut)
def create_store(
    store_in: StoreCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(router_auth.get_current_active_user),
):
    permissions.require_role(current_user, [permissions.ROLE_ADMIN, permissions.ROLE_USERADD])
    # Auto-generate store_code like STR019
    from sqlalchemy import func
    
    # Calculate explicit id to avoid NotNullViolation (DB sequence might be missing)
    max_id = db.query(func.max(models.Store.id)).scalar() or 0
    new_id = max_id + 1

    count = db.query(func.count(models.Store.id)).scalar() or 0
    store_code = f"STR{str(count + 1).zfill(3)}"
    # Make sure it's unique
    while db.query(models.Store).filter(models.Store.store_id == store_code).first():
        count += 1
        store_code = f"STR{str(count).zfill(3)}"

    db_store = models.Store(
        id=new_id,
        store_id=store_code,
        store_name=store_in.store_name,
        district_id=store_in.district_id,
        city=store_in.city,
        address=store_in.address,
        manager_name=store_in.manager_name,
        status=store_in.status,
    )
    db.add(db_store)
    db.commit()
    db.refresh(db_store)
    return db_store


@router.get("", response_model=List[StoreOut])
def read_stores(
    skip: int = 0,
    limit: int = 100,
    date: Optional[str] = None,
    district_id: Optional[int] = None,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(router_auth.get_current_active_user),
):
    from sqlalchemy import func, and_
    from datetime import date as dt_date, timedelta, datetime
    
    sale_join_cond = models.Store.store_id == models.Sale.store_id
    
    if date and date != 'all':
        today = dt_date.today()
        if date == 'today':
            sale_join_cond = and_(sale_join_cond, models.Sale.sale_date == today)
        elif date == 'last7days':
            sale_join_cond = and_(sale_join_cond, models.Sale.sale_date >= today - timedelta(days=7))
        elif date == 'lastmonth':
            sale_join_cond = and_(sale_join_cond, models.Sale.sale_date >= today - timedelta(days=30))
        else:
            try:
                specific_date = datetime.strptime(date, "%Y-%m-%d").date()
                sale_join_cond = and_(sale_join_cond, models.Sale.sale_date == specific_date)
            except ValueError:
                pass

    query = db.query(
        models.Store,
        func.sum(models.Sale.revenue).label("total_revenue")
    ).outerjoin(
        models.Sale, sale_join_cond
    )
    
    if district_id:
        query = query.filter(models.Store.district_id == district_id)
        
    query = permissions.scope_filter(current_user, query, models.Store)
    query = query.group_by(models.Store.id)
    
    results = query.offset(skip).limit(limit).all()
    
    # Fetch today's revenue for all stores
    today_date = dt_date.today()
    today_sales_query = db.query(
        models.Sale.store_id, 
        func.sum(models.Sale.revenue).label("today_revenue")
    ).filter(models.Sale.sale_date == today_date).group_by(models.Sale.store_id).all()
    
    today_revenue_map = {row.store_id: float(row.today_revenue or 0.0) for row in today_sales_query}
    
    stores = []
    for store, total_revenue in results:
        s_dict = {
            "id": store.id,
            "store_id": store.store_id,
            "district_id": store.district_id,
            "store_name": store.store_name,
            "city": store.city,
            "address": store.address,
            "manager_name": store.manager_name,
            "status": store.status,
            "total_revenue": float(total_revenue or 0.0),
            "today_revenue": today_revenue_map.get(store.store_id, 0.0)
        }
        stores.append(s_dict)
    return stores



@router.get("/{store_id}", response_model=StoreOut)
def read_store(
    store_id: str,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(router_auth.get_current_active_user),
):
    
    store = db.query(models.Store).filter(models.Store.store_id == store_id).first()
    if store is None:
        raise HTTPException(status_code=404, detail="Store not found")
    return store


class StoreManagerOut(BaseModel):
    assigned: bool
    manager_name: Optional[str] = None
    employee_id: Optional[str] = None

@router.get("/{id}/manager", response_model=StoreManagerOut)
def get_store_manager(
    id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(router_auth.get_current_active_user),
):
    manager = db.query(models.User).filter(
        models.User.store_id == id,
        models.User.role_id == permissions.ROLE_STORE_MGR,
        models.User.is_active == True
    ).first()
    
    if manager:
        return {"assigned": True, "manager_name": manager.full_name, "employee_id": manager.employee_id}
    return {"assigned": False}
