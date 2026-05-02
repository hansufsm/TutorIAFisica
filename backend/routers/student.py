from fastapi import APIRouter, Query
from backend.db.student_model import get_or_create_student, get_student_progress, get_student_portfolio
from backend.db.curriculum import get_current_week, get_current_topics
from backend.db.supabase_client import get_supabase

router = APIRouter(prefix="/student", tags=["student"])

@router.get("/{email}/progress")
async def get_progress(email: str):
    student = get_or_create_student(email)
    return get_student_progress(student["id"])

@router.get("/{email}/portfolio")
async def get_portfolio(email: str, limit: int = Query(default=30, le=100)):
    student = get_or_create_student(email)
    return get_student_portfolio(student["id"], limit=limit)

@router.get("/{email}/weekly-suggestion")
async def get_weekly_suggestion(email: str):
    """Retorna temas esperados na semana atual com o status do aluno em cada um."""
    student = get_or_create_student(email)
    week = get_current_week()
    topics = get_current_topics()

    if not topics:
        return {"week": week, "in_semester": False, "topics": []}

    sb = get_supabase()
    enriched = []
    for t in topics:
        tema = t["tema"]
        rows = sb.table("concept_status") \
            .select("status, mastery_level") \
            .eq("student_id", student["id"]) \
            .ilike("topic", f"%{tema}%") \
            .limit(1) \
            .execute().data
        status = rows[0]["status"] if rows else "not_started"
        mastery = rows[0]["mastery_level"] if rows else 0.0
        enriched.append({**t, "status": status, "mastery_level": mastery})

    return {"week": week, "in_semester": True, "topics": enriched}
