from app.database import SessionLocal, engine
from sqlalchemy import text

def upgrade():
    with engine.connect() as conn:
        print("Adding must_change_password column...")
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN must_change_password BOOLEAN DEFAULT TRUE;"))
            conn.commit()
            print("must_change_password added successfully.")
        except Exception as e:
            print(f"Column might already exist: {e}")
            conn.rollback()

        print("Adding password_changed_at column...")
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN password_changed_at TIMESTAMP;"))
            conn.commit()
            print("password_changed_at added successfully.")
        except Exception as e:
            print(f"Column might already exist: {e}")
            conn.rollback()

        print("Creating password_history table...")
        try:
            conn.execute(text("""
                CREATE TABLE password_history (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    hashed_password VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            conn.commit()
            print("password_history created successfully.")
        except Exception as e:
            print(f"Table might already exist: {e}")
            conn.rollback()

if __name__ == "__main__":
    upgrade()
