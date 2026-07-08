# pyrefly: ignore [missing-import]
import asyncio
# pyrefly: ignore [missing-import]
from fastapi import APIRouter, WebSocket, Depends, HTTPException, status

from . import router_auth, permissions, models, database

router = APIRouter()

@router.websocket("/ws/metrics")
async def metrics_ws(websocket: WebSocket, token: str):
    # Authenticate token
    try:
        # Create a short-lived DB session for authentication
        auth_db = database.SessionLocal()
        user = router_auth.get_current_user(token, db=auth_db)
        auth_db.close()
    except HTTPException:
        await websocket.close(code=1008)
        return
    await websocket.accept()
    while True:
        # Open a new DB session each iteration (or reuse if you prefer)
        db = database.SessionLocal()
        query = db.query(models.Sale)
        query = permissions.scope_filter(user, query, models.Sale)
        latest = query.order_by(models.Sale.created_at.desc()).limit(5).all()
        data = [
            {
                "sale_id": s.sale_id,
                "store_id": s.store_id,
                "revenue": float(s.revenue or 0),
                "order_count": s.order_count,
                "customer_count": s.customer_count,
                "sale_date": str(s.sale_date),
            }
            for s in latest
        ]
        await websocket.send_json(data)
        db.close()
        await asyncio.sleep(3)
