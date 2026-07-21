"""
AI Insights Router — role-scoped KPI analysis using Groq LLM.

Role scoping:
  1 (Corporate Admin)  → all stores
  2 (Regional Manager) → stores in their region (via district → store join)
  3 (District Manager) → stores in their district
  4 (Store Manager)    → their single store
  5 (User Admin)       → no access (403)
"""

import os
import json
from datetime import date
from typing import Optional

# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException, status
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel

from app.models import models
from app.core import database
from app.api import auth as router_auth
from app.core import permissions

router = APIRouter(prefix="/insights", tags=["insights"])

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")


def _get_groq_client():
    if not GROQ_API_KEY or GROQ_API_KEY.startswith("gsk_placeholder"):
        raise HTTPException(
            status_code=503,
            detail="GROQ_API_KEY is not configured. Please set it in the .env file."
        )
    try:
        from groq import Groq  # pyrefly: ignore [missing-import]
        return Groq(api_key=GROQ_API_KEY)
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="Groq package not installed. Run: pip install groq"
        )


def _build_prompt(kpi_text: str, role_label: str) -> str:
    return f"""
You are a highly experienced Business Intelligence Analyst and Data Analytics Expert.

You are generating insights for a {role_label}.

Your task is to analyze the restaurant KPI data provided below and generate concise, meaningful business insights, critical alerts, and actionable recommendations.

Restaurant KPI Data
---------------------
{kpi_text}

Analyze the KPI data and return ONLY a valid JSON object with EXACTLY this structure:

{{
  "summary": "2-3 sentence overview of overall business performance.",
  "insights": ["Insight 1", "Insight 2", "Insight 3", "Insight 4"],
  "alerts": ["Alert 1", "Alert 2"],
  "recommendations": ["Recommendation 1", "Recommendation 2", "Recommendation 3"]
}}

Guidelines:
- Summary: Brief professional overview suitable for a {role_label}.
- Insights: Patterns in revenue, orders, AOV, customers, cancellations, channel mix.
- Alerts: Only critical issues. Return [] if none.
- Recommendations: Actionable, specific to the data. Avoid generic suggestions.

IMPORTANT: Return ONLY valid JSON. No markdown, no backticks, no explanations.
"""


def _generate_insights(kpi_text: str, role_label: str) -> dict:
    client = _get_groq_client()
    prompt = _build_prompt(kpi_text, role_label)
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        content = response.choices[0].message.content.strip()
        # Strip markdown code fences if model wraps in them
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        return json.loads(content)
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Insights generation error: {e}", exc_info=True)
        if "429" in str(e) or "rate limit" in str(e).lower():
            raise HTTPException(status_code=503, detail="You have reached your daily Groq API usage limit for this model. Please try again tomorrow.")
        raise HTTPException(status_code=500, detail="The AI service encountered an error while generating insights. Please try again later.")


def _get_scoped_store_ids(current_user: models.User, db: Session) -> Optional[list]:
    """Return list of DB store integer IDs the user can see, or None for all."""
    role = current_user.role_id

    if role == permissions.ROLE_ADMIN:
        return None  # All stores

    if role == permissions.ROLE_STORE:
        if current_user.store_id is None:
            return []
        # store_id on User is the integer pk from stores table
        return [current_user.store_id]

    if role == permissions.ROLE_DISTRICT:
        if current_user.district_id is None:
            return []
        rows = db.execute(
            text("SELECT id FROM stores WHERE district_id = :did"),
            {"did": current_user.district_id}
        ).fetchall()
        return [r[0] for r in rows]

    if role == permissions.ROLE_REGIONAL:
        if current_user.region_id is None:
            return []
        rows = db.execute(
            text("""
                SELECT s.id FROM stores s
                JOIN districts d ON s.district_id = d.id
                WHERE d.region_id = :rid
            """),
            {"rid": current_user.region_id}
        ).fetchall()
        return [r[0] for r in rows]

    return []  # User Admin and unknown roles get nothing


class InsightRequest(BaseModel):
    kpi_date: date


@router.post("")
def generate_insights(
    req: InsightRequest,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(router_auth.get_current_active_user),
):
    # User Admin cannot access insights
    if current_user.role_id == permissions.ROLE_USERADD:
        raise HTTPException(status_code=403, detail="User Admins do not have access to insights.")

    role_label = permissions.ROLE_LABELS.get(current_user.role_id, "Manager")

    # Get scoped store IDs
    store_ids = _get_scoped_store_ids(current_user, db)

    # Query KPI table
    query = db.query(models.KPI).filter(models.KPI.kpi_date == req.kpi_date)
    if store_ids is not None:
        if len(store_ids) == 0:
            raise HTTPException(status_code=404, detail="No stores assigned to your account.")
        query = query.filter(models.KPI.store_id.in_(store_ids))

    kpi_records = query.all()

    if not kpi_records:
        raise HTTPException(
            status_code=404,
            detail=f"No KPI data found for {req.kpi_date}. Please try a different date."
        )

    # Build the KPI text block
    kpi_text = ""
    for row in kpi_records:
        kpi_text += f"""
Store ID: {row.store_id}
KPI Date: {row.kpi_date}
Total Revenue: ₹{row.total_revenue}
Total Orders: {row.total_orders}
Average Order Value: ₹{row.average_order_value}
Customer Count: {row.customer_count}
Cancelled Orders: {row.cancelled_orders}
Online Orders: {row.online_orders}
Takeaway Orders: {row.takeaway_orders}
Dine-in Orders: {row.dine_in_orders}
---------------------------------------
"""

    insights = _generate_insights(kpi_text, role_label)
    return {
        "status": "success",
        "date": str(req.kpi_date),
        "role": role_label,
        "store_count": len(kpi_records),
        "report": insights,
    }


@router.get("/check")
def check_kpi_dates(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(router_auth.get_current_active_user),
):
    """Return min/max available KPI dates for the user's scope (for date picker hints)."""
    store_ids = _get_scoped_store_ids(current_user, db)
    query = db.query(models.KPI)
    if store_ids is not None:
        if not store_ids:
            return {"min_date": None, "max_date": None}
        query = query.filter(models.KPI.store_id.in_(store_ids))

    from sqlalchemy import func
    result = db.query(
        func.min(models.KPI.kpi_date),
        func.max(models.KPI.kpi_date)
    )
    if store_ids is not None:
        result = result.filter(models.KPI.store_id.in_(store_ids))
    row = result.one()
    return {"min_date": str(row[0]) if row[0] else None, "max_date": str(row[1]) if row[1] else None}
