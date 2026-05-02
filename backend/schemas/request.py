from pydantic import BaseModel
from typing import Optional

class TutorRequest(BaseModel):
    question: str
    student_email: str = "anonimo@ufsm.br"
    student_name: str = "Aluno"
    model_name: str = "Gemini 3.0 Preview"
    image_base64: Optional[str] = None
    image_media_type: Optional[str] = None
    quick_mode: bool = False

class EvaluatorFeedback(BaseModel):
    student_email: str
    concept_id: str
    topic: str
    correct: bool
    quality: int = 3    # 0-5

class BrokenLinkReport(BaseModel):
    student_email: str
    session_id: Optional[str] = None
    agent_name: str
    url: str
    note: Optional[str] = None
