from pydantic import BaseModel
from typing import Optional

class TutorRequest(BaseModel):
    question: str
    student_email: str = "anonimo@ufsm.br"
    student_name: str = "Aluno"
    model_name: str = "Gemini 3.0 Preview"
    image_base64: Optional[str] = None
    image_media_type: Optional[str] = None

class EvaluatorFeedback(BaseModel):
    student_email: str
    concept_id: str
    topic: str
    correct: bool
    quality: int = 3    # 0-5
