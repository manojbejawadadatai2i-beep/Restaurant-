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
from . import models, database, router_auth

router = APIRouter(prefix="/stores", tags=["stores"])


class StoreOut(BaseModel):
    store_id: str
    district_id: Optional[str] = None
    store_name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None

    class Config:
        from_attributes = True


@router.get("/", response_model=List[StoreOut])
def read_stores(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(router_auth.get_current_active_user),
):
    return db.query(models.Store).offset(skip).limit(limit).all()


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
