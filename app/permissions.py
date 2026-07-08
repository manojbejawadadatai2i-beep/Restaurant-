# pyrefly: ignore [missing-import]
from fastapi import HTTPException, status
# pyrefly: ignore [missing-import]
from sqlalchemy import text
from typing import List

# Role constants (must match DB values)
ROLE_ADMIN = "RL01"
ROLE_REGIONAL = "RL02"
ROLE_DISTRICT = "RL03"
ROLE_STORE = "RL04"

# Mapping of role to human‑readable name
ROLE_LABELS = {
    ROLE_ADMIN: "Corporate Administrator",
    ROLE_REGIONAL: "Regional Manager",
    ROLE_DISTRICT: "District Manager",
    ROLE_STORE: "Store Manager",
}


def require_role(user, allowed_roles: List[str]):
    """Raise 403 if user.role_id not in allowed_roles."""
    if user.role_id not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )


def scope_filter(user, query, model):
    """Apply SQLAlchemy filter based on the caller's role.
    Uses plain column comparisons – no ORM relationships required.
    """
    # Admin sees everything
    if user.role_id == ROLE_ADMIN:
        return query

    # Store manager – only their own store's records
    if user.role_id == ROLE_STORE:
        if hasattr(model, "store_id"):
            return query.filter(model.store_id == user.store_id)
        # If model has no store_id (e.g. querying users), show only self
        if hasattr(model, "user_id"):
            return query.filter(model.user_id == user.user_id)
        return query.filter(False)

    # District manager – all stores in their district
    if user.role_id == ROLE_DISTRICT:
        if hasattr(model, "store_id"):
            # Subquery: get store_ids in this district
            from . import database
            db = query.session
            store_ids = [
                row[0] for row in db.execute(
                    text("SELECT store_id FROM stores WHERE district_id = :did"),
                    {"did": user.district_id}
                ).fetchall()
            ]
            return query.filter(model.store_id.in_(store_ids))
        if hasattr(model, "district_id"):
            return query.filter(model.district_id == user.district_id)
        return query.filter(False)

    # Regional manager – all stores in districts of their region
    if user.role_id == ROLE_REGIONAL:
        if hasattr(model, "store_id"):
            from . import database
            db = query.session
            store_ids = [
                row[0] for row in db.execute(
                    text("""
                        SELECT s.store_id FROM stores s
                        JOIN districts d ON s.district_id = d.district_id
                        WHERE d.region_id = :rid
                    """),
                    {"rid": user.region_id}
                ).fetchall()
            ]
            return query.filter(model.store_id.in_(store_ids))
        if hasattr(model, "region_id"):
            return query.filter(model.region_id == user.region_id)
        return query.filter(False)

    # Default – no records
    return query.filter(False)


def get_role_label(role_id: str) -> str:
    return ROLE_LABELS.get(role_id, role_id)
