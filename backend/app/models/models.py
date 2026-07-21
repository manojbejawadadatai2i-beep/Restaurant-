# pyrefly: ignore [missing-import]
from sqlalchemy import Column, Integer, String, Float, Numeric, Date, DateTime, Boolean, Text
from app.core.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String(50), nullable=True)
    full_name = Column(String(255), nullable=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column("password_hash", String(255), nullable=True)
    google_id = Column(String(255), nullable=True)
    role_id = Column(Integer, nullable=True)
    corporate_id = Column(Integer, nullable=True)
    region_id = Column(Integer, nullable=True)
    district_id = Column(Integer, nullable=True)
    store_id = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    must_change_password = Column(Boolean, default=True)
    password_changed_at = Column(DateTime, nullable=True)

class PasswordHistory(Base):
    __tablename__ = "password_history"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, index=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=True)

class Role(Base):
    __tablename__ = "roles"
    role_id = Column("id", Integer, primary_key=True, autoincrement=True)
    role_name = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)


class Region(Base):
    __tablename__ = "regions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    region_id = Column("region_code", String, unique=True, index=True)
    corporate_id = Column(Integer, nullable=True)
    region_name = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)


class District(Base):
    __tablename__ = "districts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    district_id = Column("district_code", String, unique=True, index=True)
    region_id = Column(Integer, nullable=True)
    district_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)


class Store(Base):
    __tablename__ = "stores"
    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column("store_code", String, unique=True, index=True)
    district_id = Column(Integer, nullable=True)
    store_name = Column(String, nullable=True)
    city = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    manager_name = Column(String, nullable=True)
    opened_on = Column(Date, nullable=True)
    status = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)


class Sale(Base):
    __tablename__ = "sales"
    sale_id = Column(String, primary_key=True)
    store_id = Column(String, nullable=True)
    revenue = Column(Numeric, nullable=True)
    order_count = Column(Integer, nullable=True)
    customer_count = Column(Integer, nullable=True)
    sale_date = Column(Date, nullable=True)
    created_at = Column(DateTime, nullable=True)


class Report(Base):
    __tablename__ = "reports"
    report_id = Column(String, primary_key=True)
    generated_by = Column(String, nullable=True)
    report_type = Column(String, nullable=True)
    file_path = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=True)


class KPI(Base):
    __tablename__ = "daily_store_kpis"
    kpi_id = Column(Integer, primary_key=True)
    store_id = Column(Integer, nullable=True)
    kpi_date = Column(Date, nullable=True)
    total_revenue = Column(Float, nullable=True)
    total_orders = Column(Integer, nullable=True)
    average_order_value = Column(Float, nullable=True)
    customer_count = Column(Integer, nullable=True)
    cancelled_orders = Column(Integer, nullable=True)
    online_orders = Column(Integer, nullable=True)
    takeaway_orders = Column(Integer, nullable=True)
    dine_in_orders = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)


class HourlyMetric(Base):
    __tablename__ = "hourly_metrics"
    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(String(50), nullable=True) # Reference to store_code
    record_date = Column(Date, nullable=True)
    hour_of_day = Column(Integer, nullable=True) # 0-23
    expected_orders = Column(Integer, nullable=True)
    actual_orders = Column(Integer, nullable=True)
    customer_count = Column(Integer, nullable=True)
    revenue = Column(Numeric, nullable=True)
    created_at = Column(DateTime, nullable=True)
