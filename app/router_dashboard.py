# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException, status
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from typing import List, Optional
# pyrefly: ignore [missing-import]
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
