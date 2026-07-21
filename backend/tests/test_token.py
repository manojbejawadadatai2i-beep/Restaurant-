import os
import sys
sys.path.append(os.getcwd())
import urllib.request
import json
from dotenv import load_dotenv
load_dotenv()

# We can just call the functions directly to see what token is generated
from app import database, models, auth, utils_jwt, config

db = next(database.get_db())
user = db.query(models.User).filter(models.User.email == "manojbejawada143@gmail.com").first()

print("Original role_id:", user.role_id)

access_token_expires = auth.timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
new_token = utils_jwt.create_access_token(
    data={
        "sub": user.email, 
        "role_id": user.role_id,
        "employee_id": user.employee_id,
        "store_id": user.store_id,
        "district_id": user.district_id,
        "region_id": user.region_id,
        "must_change_password": False
    }, 
    expires_delta=access_token_expires
)
print("New token generated:", new_token[:20] + "...")

# Now test decoding it with get_current_user logic
try:
    payload = auth.jwt.decode(new_token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
    print("Decoded sub:", payload.get("sub"))
except Exception as e:
    print("Failed to decode token!", e)

