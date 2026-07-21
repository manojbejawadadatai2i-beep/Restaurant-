from app.database import SessionLocal
from app.models import User
# pyrefly: ignore [missing-import]
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
db = SessionLocal()

email = 'manojbejawada143@gmail.com'
if not db.query(User).filter(User.email == email).first():
    user = User(
        id='U016', 
        email=email, 
        role_id='RL01',  # Giving Admin role
        full_name='Manoj Bejawada (Google)', 
        hashed_password=pwd_context.hash('google_auth_placeholder')
    )
    db.add(user)
    db.commit()
    print('✅ User added successfully!')
else:
    print('✅ User already exists.')
