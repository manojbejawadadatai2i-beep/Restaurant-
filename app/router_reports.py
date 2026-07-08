# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from typing import List, Optional
# pyrefly: ignore [missing-import]
from pydantic import BaseModel
from datetime import date, datetime

from . import models, database, router_auth

router = APIRouter(prefix="/reports", tags=["reports"])


class SaleOut(BaseModel):
    sale_id: str
    store_id: Optional[str] = None
    revenue: Optional[float] = None
    order_count: Optional[int] = None
    customer_count: Optional[int] = None
    sale_date: Optional[date] = None

    class Config:
        from_attributes = True


class ReportOut(BaseModel):
    report_id: str
    generated_by: Optional[str] = None
    report_type: Optional[str] = None
    file_path: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


@router.get("/sales", response_model=List[SaleOut])
def get_sales(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(router_auth.get_current_active_user),
):
    return db.query(models.Sale).offset(skip).limit(limit).all()


@router.get("/metrics")
def get_metrics(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(router_auth.get_current_active_user),
):
    sales = db.query(models.Sale).all()
    total_revenue = sum(float(s.revenue or 0) for s in sales)
    total_customers = sum(s.customer_count or 0 for s in sales)
    total_orders = sum(s.order_count or 0 for s in sales)
    return {
        "total_revenue": total_revenue,
        "total_customers": total_customers,
        "total_orders": total_orders,
        "records": len(sales),
    }


@router.get("/list", response_model=List[ReportOut])
def get_reports(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(router_auth.get_current_active_user),
):
    return db.query(models.Report).offset(skip).limit(limit).all()
