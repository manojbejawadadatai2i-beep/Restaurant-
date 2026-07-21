import os
import sys

# Setup environment for testing
sys.path.append(os.getcwd())

from dotenv import load_dotenv
load_dotenv()

from app.models import models, database, permissions
from app.services.llm_service import ask_chatbot

def run_test():
    db = next(database.get_db())
    # Find a user (Corporate Administrator role_id=1)
    admin_user = db.query(models.User).filter(models.User.role_id == 1).first()
    if not admin_user:
        print("No admin user found")
        return

    try:
        print(f"Testing chatbot as user: {admin_user.email}...")
        response = ask_chatbot(admin_user, "how many districts are there", db)
        print("\n\nRESPONSE:")
        print(response)
    except Exception as e:
        print("\n\nUNCAUGHT EXCEPTION:")
        print(e)

if __name__ == "__main__":
    run_test()
