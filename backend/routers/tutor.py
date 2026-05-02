import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import json
import time
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from backend.schemas.request import TutorRequest, EvaluatorFeedback, BrokenLinkReport
from backend.db.student_model import (
    get_or_create_student, get_concepts_due_for_review,
    update_concept_after_answer, log_session, log_broken_link,
    get_similar_sessions,
)
from backend.db.embeddings import generate_embedding

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


def _build_state(req: TutorRequest) -> tuple[PhysicsState, str, str]:
    state = PhysicsState(raw_input=req.question)
    if req.image_base64 and req.image_media_type:
        state.image_input = {"data": req.image_base64, "media_type": req.image_media_type}
    model_info = Config.AVAILABLE_MODELS.get(req.model_name,
        list(Config.AVAILABLE_MODELS.values())[0])
    model_id = model_info["id"]
    key_name = Config.get_provider_key_name(req.model_name)
    api_key = os.getenv(key_name, "") if key_name else ""
    return state, model_id, api_key


@router.post("/ask/stream")
async def ask_tutor_stream(req: TutorRequest):
    """SSE streaming: emite tokens individuais durante geração e agent_complete ao finalizar cada agente."""
    student = get_or_create_student(req.student_email, req.student_name)
    state, model_id, api_key = _build_state(req)

    due_before = get_concepts_due_for_review(student["id"])
    state.due_concepts = due_before[:5]

    # Sprint 3: Long-term RAG — buscar sessões anteriores similares
    question_embedding = await generate_embedding(req.question)
    if question_embedding:
        similar = get_similar_sessions(student["id"], question_embedding, limit=3)
        if similar:
            lines = ["### [HISTÓRICO RELEVANTE DO ALUNO — sessões anteriores similares]"]
            for s in similar:
                date_str = (s.get("created_at") or "")[:10]
                lines.append(f"- **{s.get('topic') or 'Física'}** ({date_str}): \"{s.get('question', '')}\"")
                interp = (s.get("agents_output") or {}).get("Intérprete", "")
                if interp:
                    lines.append(f"  ↳ Abordagem anterior: {interp[:200]}...")
            state.prior_sessions_context = "\n".join(lines)

    async def generate():
        t0 = time.monotonic()
        orchestrator = PhysicsOrchestrator()
        agents_dict = {}

        for event in orchestrator.process_streaming(
            state, model_id=model_id, api_key=api_key, quick_mode=req.quick_mode
        ):
            event_type = event.get("type")
            agent_name = event.get("agent_name", "")
            meta = AGENT_META.get(agent_name, {"color": "#666", "dimension": ""})

            if event_type == "token":
                chunk = {
                    "type": "token",
                    "agent_name": agent_name,
                    "token": event.get("token", ""),
                    "color": meta["color"],
                    "dimension": meta["dimension"],
                }
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"

            elif event_type == "agent_complete":
                content = event.get("content", "")
                agents_dict[agent_name] = content
                chunk = {
                    "type": "agent_complete",
                    "agent_name": agent_name,
                    "color": meta["color"],
                    "dimension": meta["dimension"],
                    "content": content,
                    "is_final": False,
                }
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"

        response_time_ms = int((time.monotonic() - t0) * 1000)
        session_id = log_session(
            student_id=student["id"],
            question=req.question,
            topic=getattr(state, "domain", ""),
            model_used=state.used_model_display_name or req.model_name,
            fallback=state.fallback_occurred or False,
            agents_output=agents_dict,
            response_time_ms=response_time_ms,
            embedding=question_embedding,
        )
        yield f"data: {json.dumps({'is_final': True, 'due_for_review': due_before[:3], 'session_id': session_id, 'response_time_ms': response_time_ms})}\n\n"

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


@router.post("/report-link")
async def report_broken_link(report: BrokenLinkReport):
    """Registra um report de link quebrado/inexistente de uma referência."""
    student = get_or_create_student(report.student_email)
    log_broken_link(
        student_id=student["id"],
        session_id=report.session_id,
        agent_name=report.agent_name,
        url=report.url,
        note=report.note,
    )
    return {"received": True}


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
