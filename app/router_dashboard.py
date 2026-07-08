# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import date, datetime

from . import models, database, router_auth, permissions

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

class SaleOut(BaseModel):
    sale_id: str
    store_id: Optional[str] = None
    revenue: Optional[float] = None
    order_count: Optional[int] = None
    customer_count: Optional[int] = None
    sale_date: Optional[date] = None

    class Config:
        from_attributes = True

class RevenueAnalytics(BaseModel):
    total_revenue: float
    total_customers: int
    total_orders: int
    records: int

    class Config:
        from_attributes = True

# Sales list – filtered by user scope
@router.get("/sales", response_model=List[SaleOut])
def list_sales(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(router_auth.get_current_active_user),
):
    query = db.query(models.Sale)
    query = permissions.scope_filter(current_user, query, models.Sale)
    return query.offset(skip).limit(limit).all()

# Revenue analytics – aggregated metrics, also scope‑filtered
@router.get("/metrics", response_model=RevenueAnalytics)
def revenue_metrics(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(router_auth.get_current_active_user),
):
    query = db.query(models.Sale)
    query = permissions.scope_filter(current_user, query, models.Sale)
    sales = query.all()
    total_revenue = sum(float(s.revenue or 0) for s in sales)
    total_customers = sum(s.customer_count or 0 for s in sales)
    total_orders = sum(s.order_count or 0 for s in sales)
    return {
        "total_revenue": total_revenue,
        "total_customers": total_customers,
        "total_orders": total_orders,
        "records": len(sales),
    }

class SaleCreate(BaseModel):
    revenue: float
    order_count: int
    customer_count: int

@router.post("/sales", response_model=SaleOut)
def create_sale(
    sale_in: SaleCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(router_auth.get_current_active_user),
):
    if current_user.role_id != permissions.ROLE_STORE:
        raise HTTPException(status_code=403, detail="Only store managers can submit sales")
    
    if not current_user.store_id:
        raise HTTPException(status_code=400, detail="User is not assigned to a store")
    
    import uuid
    new_sale = models.Sale(
        sale_id=f"SA{uuid.uuid4().hex[:6].upper()}",
        store_id=current_user.store_id,
        revenue=sale_in.revenue,
        order_count=sale_in.order_count,
        customer_count=sale_in.customer_count,
        sale_date=date.today(),
        created_at=datetime.utcnow()
    )
    db.add(new_sale)
    db.commit()
    db.refresh(new_sale)
    return new_sale

# Store performance – aggregated per store (basic example)
@router.get("/store/{store_id}")
def store_performance(
    store_id: str,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(router_auth.get_current_active_user),
):
    # Ensure the user can view this store
    query = db.query(models.Sale).filter(models.Sale.store_id == store_id)
    query = permissions.scope_filter(current_user, query, models.Sale)
    sales = query.all()
    if not sales:
        raise HTTPException(status_code=404, detail="No sales for this store or access denied")
    total_rev = sum(float(s.revenue or 0) for s in sales)
    total_orders = sum(s.order_count or 0 for s in sales)
    total_customers = sum(s.customer_count or 0 for s in sales)
    return {
        "store_id": store_id,
        "total_revenue": total_rev,
        "total_orders": total_orders,
        "total_customers": total_customers,
        "records": len(sales),
    }
