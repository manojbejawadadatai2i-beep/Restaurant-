# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException, status
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from typing import List, Optional
# pyrefly: ignore [missing-import]
from pydantic import BaseModel
from datetime import date, datetime

import uuid
from app.models import models
from app.core import database
from app.api import auth as router_auth
from app.core import permissions

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

class SaleIn(BaseModel):
    revenue: float
    order_count: int
    customer_count: int

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

@router.post("/sales", response_model=SaleOut)
def create_sale(
    sale_in: SaleIn,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(router_auth.get_current_active_user),
):
    if not current_user.store_id:
        raise HTTPException(status_code=403, detail="Only store managers can submit sales")
        
    sale_id = f"SALE{uuid.uuid4().hex[:5].upper()}"
    db_sale = models.Sale(
        sale_id=sale_id,
        store_id=str(current_user.store_id),
        revenue=sale_in.revenue,
        order_count=sale_in.order_count,
        customer_count=sale_in.customer_count,
        sale_date=date.today()
    )
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    return db_sale

# Revenue analytics – aggregated metrics, also scope‑filtered
@router.get("/metrics", response_model=RevenueAnalytics)
def revenue_metrics(
    region: Optional[str] = None,
    district: Optional[str] = None,
    store: Optional[str] = None,
    date: Optional[str] = None,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(router_auth.get_current_active_user),
):
    query = db.query(models.Sale)
    query = permissions.scope_filter(current_user, query, models.Sale)
    
    if store and store != 'all':
        query = query.filter(models.Sale.store_id == store.upper())
    elif district and district != 'all':
        query = query.join(models.Store, models.Store.store_id == models.Sale.store_id)
        try:
            district_int = int(district)
            query = query.filter(models.Store.district_id == district_int)
        except ValueError:
            pass
    elif region and region != 'all':
        from sqlalchemy import func
        query = query.join(models.Store, models.Store.store_id == models.Sale.store_id)
        query = query.join(models.District, models.District.id == models.Store.district_id)
        query = query.join(models.Region, models.Region.id == models.District.region_id)
        query = query.filter(func.lower(models.Region.region_name).like(f"%{region.lower()}%"))

    if date and date != 'all':
        from datetime import date as dt_date, timedelta
        today = dt_date.today()
        if date == 'today':
            query = query.filter(models.Sale.sale_date == today)
        elif date == 'last7days':
            query = query.filter(models.Sale.sale_date >= today - timedelta(days=7))
        elif date == 'lastmonth':
            query = query.filter(models.Sale.sale_date >= today - timedelta(days=30))

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

class PeakTime(BaseModel):
    hour: str
    orders: int
    customers: int
    revenue: float
    status: str
    trend: int

class HourlyTraffic(BaseModel):
    hour: str
    orders: int
    customers: int
    revenue: float

class PeakHoursResponse(BaseModel):
    revenue: float
    customers: int
    peak_time: Optional[PeakTime]
    hourly_traffic: List[HourlyTraffic]

@router.get("/peak-hours", response_model=PeakHoursResponse)
def get_peak_hours(
    region: Optional[str] = None,
    district: Optional[str] = None,
    store: Optional[str] = None,
    date: Optional[str] = None,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(router_auth.get_current_active_user),
):
    from sqlalchemy import func, extract
    
    # Base query for HourlyMetric
    query = db.query(
        models.HourlyMetric.hour_of_day.label('hour'),
        func.sum(models.HourlyMetric.actual_orders).label('orders'),
        func.sum(models.HourlyMetric.customer_count).label('customers'),
        func.sum(models.HourlyMetric.revenue).label('revenue')
    )
    
    # Apply RBAC - using HourlyMetric store_id instead of Sale
    query = permissions.scope_filter(current_user, query, models.HourlyMetric)

    # Apply Location Filters
    if store and store != 'all':
        query = query.filter(models.HourlyMetric.store_id == store.upper())
    elif district and district != 'all':
        query = query.join(models.Store, models.Store.store_id == models.HourlyMetric.store_id)
        try:
            district_int = int(district)
            query = query.filter(models.Store.district_id == district_int)
        except ValueError:
            pass
    elif region and region != 'all':
        query = query.join(models.Store, models.Store.store_id == models.HourlyMetric.store_id)
        query = query.join(models.District, models.District.id == models.Store.district_id)
        query = query.join(models.Region, models.Region.id == models.District.region_id)
        query = query.filter(func.lower(models.Region.region_name).like(f"%{region.lower()}%"))

    # Apply Date Filter
    if date and date != 'all':
        from datetime import date as dt_date, timedelta
        today = dt_date.today()
        if date == 'today':
            query = query.filter(models.HourlyMetric.record_date == today)
        elif date == 'yesterday':
            query = query.filter(models.HourlyMetric.record_date == today - timedelta(days=1))
        elif date == 'last7days':
            query = query.filter(models.HourlyMetric.record_date >= today - timedelta(days=7))
        elif date == 'lastmonth':
            query = query.filter(models.HourlyMetric.record_date >= today - timedelta(days=30))

    query = query.group_by('hour').order_by('hour')
    results = query.all()

    hourly_traffic = []
    total_revenue = 0.0
    total_customers = 0
    peak_row = None
    
    for row in results:
        hr = int(row.hour) if row.hour is not None else 0
        hr_str = f"{hr:02d}:00"
        
        traffic = HourlyTraffic(
            hour=hr_str,
            orders=row.orders or 0,
            customers=int(row.customers or 0),
            revenue=float(row.revenue or 0)
        )
        hourly_traffic.append(traffic)
        
        total_revenue += traffic.revenue
        total_customers += traffic.customers
        
        if not peak_row or traffic.orders > peak_row.orders:
            peak_row = traffic

    peak_time = None
    if peak_row:
        # Determine status
        status = "Normal"
        if peak_row.orders > 50:
            status = "Busy"
        if peak_row.orders > 100:
            status = "Very Busy"
            
        peak_time = PeakTime(
            hour=f"{peak_row.hour} - {(int(peak_row.hour.split(':')[0]) + 1) % 24:02d}:00",
            orders=peak_row.orders,
            customers=peak_row.customers,
            revenue=peak_row.revenue,
            status=status,
            trend=12  # Dummy trend for now, as calculating yesterday's exact hour is complex and out of scope
        )

    return PeakHoursResponse(
        revenue=total_revenue,
        customers=total_customers,
        peak_time=peak_time,
        hourly_traffic=hourly_traffic
    )
