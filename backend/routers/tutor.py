import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from backend.schemas.request import TutorRequest, EvaluatorFeedback
from backend.schemas.response import TutorResponse, AgentOutput
from backend.db.student_model import (
    get_or_create_student, get_concepts_due_for_review,
    update_concept_after_answer, log_session
)

# Importa lógica Python INTACTA
from core import PhysicsOrchestrator, PhysicsState
from config import Config

router = APIRouter(prefix="/tutor", tags=["tutor"])

AGENT_META = {
    "Intérprete":   {"color": "#3B82F6", "dimension": "Socrática"},
    "Solucionador": {"color": "#22C55E", "dimension": "Procedimental"},
    "Visualizador": {"color": "#F97316", "dimension": "Intuitiva"},
    "Curador":      {"color": "#A855F7", "dimension": "Contextual"},
    "Avaliador":    {"color": "#EF4444", "dimension": "Formativa"},
}

FIELD_MAP = [
    ("Intérprete",   "concepts"),
    ("Solucionador", "solution_steps"),
    ("Visualizador", "visualization_code"),
    ("Curador",      "academic_sources"),
    ("Avaliador",    "formative_challenge"),
]


def _build_state(req: TutorRequest) -> tuple[PhysicsState, str, str]:
    state = PhysicsState(question=req.question)
    if req.image_base64 and req.image_media_type:
        state.image = {"data": req.image_base64, "media_type": req.image_media_type}
    model_info = Config.AVAILABLE_MODELS.get(req.model_name,
        list(Config.AVAILABLE_MODELS.values())[0])
    model_id = model_info["id"]
    api_key = os.getenv(Config.get_provider_key_name(req.model_name), "")
    return state, model_id, api_key


@router.post("/ask", response_model=TutorResponse)
async def ask_tutor(req: TutorRequest):
    """Roda pipeline completo, retorna quando todos os agentes terminam."""
    student = get_or_create_student(req.student_email, req.student_name)
    state, model_id, api_key = _build_state(req)

    orchestrator = PhysicsOrchestrator()
    result = orchestrator.process(state, model_id=model_id, api_key=api_key)

    agents_out = []
    agents_dict = {}
    for name, field in FIELD_MAP:
        content = getattr(result, field, None)
        if content:
            meta = AGENT_META[name]
            agents_out.append(AgentOutput(
                agent_name=name, color=meta["color"],
                dimension=meta["dimension"], content=content
            ))
            agents_dict[name] = content

    # Salvar sessão no Supabase
    log_session(
        student_id=student["id"],
        question=req.question,
        topic=getattr(result, "domain", ""),
        model_used=result.used_model_display_name or req.model_name,
        fallback=result.fallback_occurred or False,
        agents_output=agents_dict,
    )

    due = get_concepts_due_for_review(student["id"])
    return TutorResponse(
        agents=agents_out,
        used_model=result.used_model_display_name or req.model_name,
        fallback_occurred=result.fallback_occurred or False,
        visualization_code=result.visualization_code,
        formative_challenge=result.formative_challenge,
        due_for_review=due[:3],  # máximo 3 sugestões
    )


@router.post("/ask/stream")
async def ask_tutor_stream(req: TutorRequest):
    """
    Streaming SSE: envia cada agente assim que termina.
    Requer process_streaming() em src/core.py (ver Etapa 3.2).
    """
    student = get_or_create_student(req.student_email, req.student_name)
    state, model_id, api_key = _build_state(req)

    async def generate():
        orchestrator = PhysicsOrchestrator()
        agents_dict = {}

        # Tentar usar process_streaming se disponível
        if hasattr(orchestrator, 'process_streaming'):
            for name, result_content in orchestrator.process_streaming(
                state, model_id=model_id, api_key=api_key
            ):
                meta = AGENT_META.get(name, {"color": "#666", "dimension": ""})
                chunk = {
                    "agent_name": name,
                    "color": meta["color"],
                    "dimension": meta["dimension"],
                    "content": result_content,
                    "is_final": False,
                }
                agents_dict[name] = result_content
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
        else:
            # Fallback: usar process() normal
            result = orchestrator.process(state, model_id=model_id, api_key=api_key)
            for name, field in FIELD_MAP:
                content = getattr(result, field, None)
                if content:
                    meta = AGENT_META.get(name, {"color": "#666", "dimension": ""})
                    chunk = {
                        "agent_name": name,
                        "color": meta["color"],
                        "dimension": meta["dimension"],
                        "content": content,
                        "is_final": False,
                    }
                    agents_dict[name] = content
                    yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"

        due = get_concepts_due_for_review(student["id"])
        yield f"data: {json.dumps({'is_final': True, 'due_for_review': due[:3]})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/feedback")
async def submit_feedback(fb: EvaluatorFeedback):
    """Recebe feedback do Avaliador e atualiza Student Model."""
    student = get_or_create_student(fb.student_email)
    updated = update_concept_after_answer(
        student_id=student["id"],
        concept_id=fb.concept_id,
        topic=fb.topic,
        correct=fb.correct,
        quality=fb.quality,
    )
    return {"updated": updated}


@router.post("/transcribe")
async def transcribe_audio(file: bytes):
    """Transcreve áudio via Whisper (OpenAI)."""
    import openai
    client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    transcript = await client.audio.transcriptions.create(
        model="whisper-1",
        file=("audio.webm", file, "audio/webm"),
    )
    return {"text": transcript.text}
