# pyrefly: ignore [missing-import]
from fastapi import HTTPException, status
# pyrefly: ignore [missing-import]
from sqlalchemy import text
from typing import List

# Role constants (must match DB integer values)
ROLE_ADMIN = 1        # Corporate Administrator — sees everything
ROLE_REGIONAL = 2     # Regional Manager
ROLE_DISTRICT = 3     # District Manager
ROLE_STORE = 4        # Store Manager
ROLE_USERADD = 5      # User Admin — can only add/manage users

# Mapping of role to human-readable name
ROLE_LABELS = {
    ROLE_ADMIN: "Corporate Administrator",
    ROLE_REGIONAL: "Regional Manager",
    ROLE_DISTRICT: "District Manager",
    ROLE_STORE: "Store Manager",
    ROLE_USERADD: "User Admin",
}


def require_role(user, allowed_roles: List[int]):
    """Raise 403 if user.role_id not in allowed_roles."""
    if user.role_id not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )


def scope_filter(user, query, model):
    """Apply SQLAlchemy filter based on the caller's role."""
    # Admin and User Admin see all users
    if user.role_id in (ROLE_ADMIN, ROLE_USERADD):
        return query

    # Store manager – only their own store's records
    if user.role_id == ROLE_STORE:
        if hasattr(model, "store_id"):
            db = query.session
            store_code_row = db.execute(
                text("SELECT store_code FROM stores WHERE id = :sid"),
                {"sid": user.store_id}
            ).fetchone()
            if store_code_row:
                return query.filter(model.store_id == store_code_row[0])
            return query.filter(False)
        if hasattr(model, "id"):
            return query.filter(model.id == user.id)
        return query.filter(False)

    # District manager – all stores in their district
    if user.role_id == ROLE_DISTRICT:
        if hasattr(model, "store_id"):
            from . import database
            db = query.session
            store_ids = [
                row[0] for row in db.execute(
                    text("SELECT store_code FROM stores WHERE district_id = :did"),
                    {"did": str(user.district_id)}
                ).fetchall()
            ]
            return query.filter(model.store_id.in_(store_ids))
        if hasattr(model, "district_id"):
            return query.filter(model.district_id == str(user.district_id))
        return query.filter(False)

    # Regional manager – all stores in districts of their region
    if user.role_id == ROLE_REGIONAL:
        if hasattr(model, "store_id"):
            from . import database
            db = query.session
            store_ids = [
                row[0] for row in db.execute(
                    text("""
                        SELECT s.store_code FROM stores s
                        JOIN districts d ON s.district_id = d.district_id
                        WHERE d.region_id = :rid
                    """),
                    {"rid": str(user.region_id)}
                ).fetchall()
            ]
            return query.filter(model.store_id.in_(store_ids))
        if hasattr(model, "region_id"):
            return query.filter(model.region_id == str(user.region_id))
        return query.filter(False)

    # Default – no records
    return query.filter(False)


def get_role_label(role_id: int) -> str:
    return ROLE_LABELS.get(role_id, str(role_id))
