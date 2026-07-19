# pyrefly: ignore [missing-import]
from sqlalchemy import Column, Integer, String, Float, Numeric, Date, DateTime, Boolean, Text
from .database import Base


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


class Role(Base):
    __tablename__ = "roles"
    role_id = Column(String, primary_key=True)
    role_name = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=True)


class Region(Base):
    __tablename__ = "regions"
    region_id = Column(String, primary_key=True)
    region_name = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=True)


class District(Base):
    __tablename__ = "districts"
    district_id = Column(String, primary_key=True)
    region_id = Column(String, nullable=True)
    district_name = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=True)


class Store(Base):
    __tablename__ = "stores"
    store_id = Column(String, primary_key=True)
    district_id = Column(String, nullable=True)
    store_name = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    phone = Column(String, nullable=True)
    status = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=True)


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
