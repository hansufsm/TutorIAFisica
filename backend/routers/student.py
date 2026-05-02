from fastapi import APIRouter, Query
from backend.db.student_model import get_or_create_student, get_student_progress, get_student_portfolio

router = APIRouter(prefix="/student", tags=["student"])

@router.get("/{email}/progress")
async def get_progress(email: str):
    student = get_or_create_student(email)
    return get_student_progress(student["id"])

@router.get("/{email}/portfolio")
async def get_portfolio(email: str, limit: int = Query(default=30, le=100)):
    student = get_or_create_student(email)
    return get_student_portfolio(student["id"], limit=limit)
