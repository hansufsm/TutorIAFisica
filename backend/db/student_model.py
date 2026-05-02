"""
CRUD do Student Model no Supabase.
Implementa algoritmo SM-2 para repetição espaçada.
"""
import math
from datetime import datetime, timedelta, timezone
from backend.db.supabase_client import get_supabase


def get_or_create_student(email: str, name: str = "") -> dict:
    """Retorna aluno existente ou cria novo."""
    sb = get_supabase()
    result = sb.table("students").select("*").eq("email", email).execute()
    if result.data:
        # atualizar last_seen
        sb.table("students").update(
            {"last_seen": datetime.now(timezone.utc).isoformat()}
        ).eq("email", email).execute()
        return result.data[0]
    # criar novo aluno
    new = sb.table("students").insert(
        {"email": email, "name": name}
    ).execute()
    return new.data[0]


def get_concepts_due_for_review(student_id: str) -> list[dict]:
    """Retorna conceitos com next_review <= agora (prontos para revisar)."""
    sb = get_supabase()
    now = datetime.now(timezone.utc).isoformat()
    result = sb.table("concept_status") \
        .select("*") \
        .eq("student_id", student_id) \
        .lte("next_review", now) \
        .order("next_review") \
        .execute()
    return result.data or []


def update_concept_after_answer(
    student_id: str,
    concept_id: str,
    topic: str,
    correct: bool,
    quality: int = 3   # 0-5: 0=blackout, 5=perfeito
) -> dict:
    """
    Atualiza conceito aplicando SM-2.
    quality: 0-5 (0=esqueceu tudo, 5=perfeito sem hesitar)
    """
    sb = get_supabase()
    now = datetime.now(timezone.utc)

    # buscar estado atual
    existing = sb.table("concept_status") \
        .select("*") \
        .eq("student_id", student_id) \
        .eq("concept_id", concept_id) \
        .execute()

    if existing.data:
        row = existing.data[0]
        interval = row["review_interval_days"]
        ef = row["ease_factor"]
    else:
        interval = 1
        ef = 2.5

    # SM-2: calcular próximo intervalo
    if not correct or quality < 3:
        new_interval = 1
        new_ef = max(1.3, ef - 0.2)
    elif interval == 1:
        new_interval = 6
        new_ef = ef + (0.1 - (5 - quality) * 0.08)
    else:
        new_interval = round(interval * ef)
        new_ef = ef + (0.1 - (5 - quality) * 0.08)

    new_ef = max(1.3, new_ef)
    next_review = (now + timedelta(days=new_interval)).isoformat()

    # calcular mastery_level (retenção estimada por Ebbinghaus)
    days_since = 0 if not existing.data else (
        (now - datetime.fromisoformat(
            existing.data[0].get("last_reviewed") or now.isoformat()
        )).days
    )
    retention = math.exp(-days_since / max(new_interval, 1))
    mastery = min(1.0, retention * (quality / 5))

    new_status = "mastered" if mastery > 0.8 else \
                 "developing" if mastery > 0.3 else "not_started"

    payload = {
        "student_id": student_id,
        "concept_id": concept_id,
        "topic": topic,
        "status": new_status,
        "mastery_level": round(mastery, 3),
        "review_interval_days": new_interval,
        "ease_factor": round(new_ef, 3),
        "last_reviewed": now.isoformat(),
        "next_review": next_review,
    }
    if new_status == "mastered" and (not existing.data or not existing.data[0].get("date_mastered")):
        payload["date_mastered"] = now.isoformat()

    if existing.data:
        sb.table("concept_status").update(payload) \
            .eq("student_id", student_id) \
            .eq("concept_id", concept_id).execute()
    else:
        sb.table("concept_status").insert(payload).execute()

    return payload


def register_misconception(
    student_id: str, concept_id: str, misconception_id: str, description: str
):
    """Registra ou incrementa misconception detectada."""
    sb = get_supabase()
    existing = sb.table("misconceptions") \
        .select("*") \
        .eq("student_id", student_id) \
        .eq("misconception_id", misconception_id) \
        .is_("resolved_at", "null") \
        .execute()

    if existing.data:
        sb.table("misconceptions") \
            .update({"attempts": existing.data[0]["attempts"] + 1}) \
            .eq("id", existing.data[0]["id"]).execute()
    else:
        sb.table("misconceptions").insert({
            "student_id": student_id,
            "concept_id": concept_id,
            "misconception_id": misconception_id,
            "description": description,
        }).execute()


def log_session(
    student_id: str,
    question: str,
    topic: str,
    model_used: str,
    fallback: bool,
    agents_output: dict,
    response_time_ms: int = None
) -> str:
    """Salva log completo da sessão e retorna o session_id."""
    sb = get_supabase()
    payload = {
        "student_id": student_id,
        "question": question,
        "topic": topic,
        "model_used": model_used,
        "fallback": fallback,
        "agents_output": agents_output,
    }
    if response_time_ms is not None:
        payload["response_time_ms"] = response_time_ms
    result = sb.table("session_log").insert(payload).execute()
    return result.data[0]["id"] if result.data else None


def log_broken_link(
    student_id: str,
    session_id: str,
    agent_name: str,
    url: str,
    note: str = None
):
    """Registra um report de link quebrado."""
    sb = get_supabase()
    sb.table("broken_link_reports").insert({
        "student_id": student_id,
        "session_id": session_id,
        "agent_name": agent_name,
        "url": url,
        "note": note,
    }).execute()


def get_student_portfolio(student_id: str, limit: int = 30) -> dict:
    """Retorna dados completos para a página /portfolio: sessões recentes + concepts."""
    sb = get_supabase()

    sessions = sb.table("session_log") \
        .select("id, question, topic, model_used, response_time_ms, created_at") \
        .eq("student_id", student_id) \
        .order("created_at", desc=True) \
        .limit(limit) \
        .execute().data or []

    concepts = sb.table("concept_status") \
        .select("concept_id, topic, status, mastery_level, last_reviewed, next_review, date_mastered") \
        .eq("student_id", student_id) \
        .execute().data or []

    due = get_concepts_due_for_review(student_id)

    return {
        "sessions": sessions,
        "concepts": concepts,
        "stats": {
            "total_sessions": len(sessions),
            "total_concepts": len(concepts),
            "mastered": sum(1 for c in concepts if c["status"] == "mastered"),
            "developing": sum(1 for c in concepts if c["status"] == "developing"),
            "due_count": len(due),
        },
    }


def get_student_progress(student_id: str) -> dict:
    """Retorna resumo do progresso para o painel do aluno."""
    sb = get_supabase()
    concepts = sb.table("concept_status") \
        .select("*").eq("student_id", student_id).execute().data or []
    misconceptions = sb.table("misconceptions") \
        .select("*") \
        .eq("student_id", student_id) \
        .is_("resolved_at", "null").execute().data or []
    due = get_concepts_due_for_review(student_id)

    return {
        "total_concepts": len(concepts),
        "mastered": sum(1 for c in concepts if c["status"] == "mastered"),
        "developing": sum(1 for c in concepts if c["status"] == "developing"),
        "concepts": concepts,
        "active_misconceptions": misconceptions,
        "due_for_review": due,
        "due_count": len(due),
    }
