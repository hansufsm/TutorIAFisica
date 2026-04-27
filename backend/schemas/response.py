from pydantic import BaseModel
from typing import Optional

class AgentOutput(BaseModel):
    agent_name: str
    color: str
    dimension: str
    content: str
    source_tag: Optional[str] = None

class TutorResponse(BaseModel):
    agents: list[AgentOutput]
    used_model: str
    fallback_occurred: bool
    visualization_code: Optional[str] = None
    formative_challenge: Optional[str] = None
    due_for_review: list[dict] = []
    session_id: Optional[str] = None
