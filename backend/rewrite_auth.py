import os

with open('app/router_auth.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update JWT payload in login
content = content.replace(
    '"region_id": user.region_id',
    '"region_id": user.region_id,\n            "must_change_password": getattr(user, "must_change_password", False)'
)

# 2. Add change_password endpoint at the end of the file
new_endpoint = """
class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

@router.post("/change-password")
def change_password(
    req: ChangePasswordRequest, 
    db: Session = Depends(database.get_db), 
    current_user: models.User = Depends(get_current_active_user)
):
    if not auth.verify_password(req.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect old password")
        
    import re
    pwd = req.new_password
    if len(pwd) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long.")
    if not re.search(r"[A-Z]", pwd):
        raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter.")
    if not re.search(r"[a-z]", pwd):
        raise HTTPException(status_code=400, detail="Password must contain at least one lowercase letter.")
    if not re.search(r"[0-9]", pwd):
        raise HTTPException(status_code=400, detail="Password must contain at least one number.")
    if not re.search(r"[!@#$%^&*(),.?\\\":{}|<>]", pwd):
        raise HTTPException(status_code=400, detail="Password must contain at least one special character.")
        
    if req.old_password == req.new_password:
        raise HTTPException(status_code=400, detail="New password cannot be the same as the old password.")
        
    histories = db.query(models.PasswordHistory).filter(models.PasswordHistory.user_id == current_user.id).order_by(models.PasswordHistory.created_at.desc()).limit(5).all()
    for h in histories:
        if auth.verify_password(req.new_password, h.hashed_password):
            raise HTTPException(status_code=400, detail="Cannot reuse any of your last 5 passwords.")
            
    new_hash = auth.get_password_hash(req.new_password)
    current_user.hashed_password = new_hash
    current_user.must_change_password = False
    from datetime import datetime
    current_user.password_changed_at = datetime.utcnow()
    
    new_history = models.PasswordHistory(
        user_id=current_user.id,
        hashed_password=new_hash
    )
    db.add(new_history)
    db.commit()
    
    return {"message": "Password changed successfully"}
"""

content += new_endpoint

with open('app/router_auth.py', 'w', encoding='utf-8') as f:
    f.write(content)
