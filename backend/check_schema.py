"""Test the insights endpoint directly."""
from app.database import SessionLocal
from app.models import User, KPI
from app.router_insights import _get_scoped_store_ids, _generate_insights
from datetime import date

db = SessionLocal()

# Get the corporate admin user
admin = db.query(User).filter(User.role_id == 1).first()
print(f"Admin user: {admin.employee_id if admin else 'None'}")

if admin:
    store_ids = _get_scoped_store_ids(admin, db)
    print(f"Scoped store IDs: {store_ids}")

    kpi_records = db.query(KPI).filter(KPI.kpi_date == date(2026, 7, 10)).all()
    print(f"KPI records for 2026-07-10: {len(kpi_records)}")

    if kpi_records:
        # Build sample kpi text
        kpi_text = ""
        for row in kpi_records[:2]:
            kpi_text += f"Store ID: {row.store_id}, Revenue: {row.total_revenue}, Orders: {row.total_orders}\n"
        
        print("\nTesting Groq call...")
        try:
            result = _generate_insights(kpi_text, "Corporate Administrator")
            print("SUCCESS:", list(result.keys()))
        except Exception as e:
            print(f"ERROR: {e}")

db.close()
