from fastapi import APIRouter
from backend.db.student_model import get_or_create_student, get_student_progress

router = APIRouter(prefix="/student", tags=["student"])

@router.get("/{email}/progress")
async def get_progress(email: str):
    student = get_or_create_student(email)
    return get_student_progress(student["id"])
