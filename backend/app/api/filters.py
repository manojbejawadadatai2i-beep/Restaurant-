from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.models import models
from app.core import database
from app.api import auth as router_auth
from app.core import permissions

router = APIRouter(prefix="/filters", tags=["filters"])

class RegionOut(BaseModel):
    id: int
    region_id: str
    region_name: str

    class Config:
        from_attributes = True

class DistrictOut(BaseModel):
    id: int
    district_id: str
    region_id: Optional[int] = None
    district_name: str

    class Config:
        from_attributes = True

@router.get("/regions", response_model=List[RegionOut])
def read_regions(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(router_auth.get_current_active_user),
):
    query = db.query(models.Region)
    # Apply RBAC manually
    if current_user.role_id == permissions.ROLE_REGIONAL:
        query = query.filter(models.Region.id == current_user.region_id)
    elif current_user.role_id == permissions.ROLE_DISTRICT:
        # Get district's region
        district = db.query(models.District).filter(models.District.id == current_user.district_id).first()
        if district:
            query = query.filter(models.Region.id == district.region_id)
        else:
            query = query.filter(False)
    elif current_user.role_id == permissions.ROLE_STORE:
        # Get store -> district -> region
        store = db.query(models.Store).filter(models.Store.id == current_user.store_id).first()
        if store:
            district = db.query(models.District).filter(models.District.id == store.district_id).first()
            if district:
                query = query.filter(models.Region.id == district.region_id)
            else:
                query = query.filter(False)
        else:
            query = query.filter(False)
            
    return query.all()

@router.get("/districts", response_model=List[DistrictOut])
def read_districts(
    region_id: Optional[int] = None,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(router_auth.get_current_active_user),
):
    query = db.query(models.District)
    if region_id:
        query = query.filter(models.District.region_id == region_id)
        
    # Apply RBAC manually
    if current_user.role_id == permissions.ROLE_REGIONAL:
        query = query.filter(models.District.region_id == current_user.region_id)
    elif current_user.role_id == permissions.ROLE_DISTRICT:
        query = query.filter(models.District.id == current_user.district_id)
    elif current_user.role_id == permissions.ROLE_STORE:
        store = db.query(models.Store).filter(models.Store.id == current_user.store_id).first()
        if store:
            query = query.filter(models.District.id == store.district_id)
        else:
            query = query.filter(False)

    return query.all()
