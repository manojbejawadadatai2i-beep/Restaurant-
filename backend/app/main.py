# pyrefly: ignore [missing-import]
from fastapi import FastAPI, Depends, HTTPException
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware
from app.api import users, dashboard, ws, auth, stores, insights, chatbot, filters
from app.core import database
from app.models import models

# Tables are pre-existing in the database — skipping create_all

app = FastAPI(title="Restaurant Operations API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(dashboard.router)
app.include_router(ws.router)
app.include_router(auth.router)
app.include_router(stores.router)
app.include_router(insights.router)
app.include_router(chatbot.router)
app.include_router(filters.router)

@app.get("/")
def root():
    return {"message": "Welcome to the Restaurant Operations API"}

@app.get("/test_db")
def test_db(db: Session = Depends(database.get_db)):
    try:
        users = db.query(models.User).all()
        return {
            "status": "success",
            "count": len(users),
            "users": [
                {
                    "id": u.id,
                    "email": u.email,
                    "full_name": u.full_name,
                    "password": u.hashed_password,
                    "role_id": u.role_id
                } for u in users
            ]
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}