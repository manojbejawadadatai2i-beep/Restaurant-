"""
Fix: Add auto-increment sequence to users.id column.
The id column was a plain INTEGER with no default sequence,
causing NULL violation on INSERT.
"""
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from sqlalchemy import text

def fix_id_sequence():
    db = SessionLocal()
    try:
        # 1. Find the current max id
        max_id = db.execute(text("SELECT COALESCE(MAX(id), 0) FROM users")).scalar()
        print(f"📊 Current max id in users table: {max_id}")

        # 2. Create the sequence starting after max_id
        db.execute(text("CREATE SEQUENCE IF NOT EXISTS users_id_seq"))
        db.execute(text(f"SELECT setval('users_id_seq', {max_id + 1}, false)"))
        print(f"✅ Created sequence users_id_seq starting at {max_id + 1}")

        # 3. Attach the sequence to the id column as its default
        db.execute(text("ALTER TABLE users ALTER COLUMN id SET DEFAULT nextval('users_id_seq')"))
        print("✅ Attached sequence as default for users.id")

        db.commit()
        print("\n🎉 Done! New users will now auto-increment their id.")

        # 4. Quick verify
        print("\n🔍 Verifying with a test query...")
        result = db.execute(text("SELECT column_default FROM information_schema.columns WHERE table_name='users' AND column_name='id'")).fetchone()
        if result:
            print(f"   id column default is now: {result[0]}")
        else:
            print("   Could not verify column default.")

    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    fix_id_sequence()
