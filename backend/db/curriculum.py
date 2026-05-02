"""
Lógica de currículo temporal: mapeia semana atual do semestre UFSM
aos temas esperados por disciplina.
"""
import json
import os
from datetime import date

_SYLLABUS_PATH = os.path.join(os.path.dirname(__file__), "../../data/ufsm_syllabus.json")


def _load_syllabus() -> dict:
    with open(_SYLLABUS_PATH, encoding="utf-8") as f:
        return json.load(f)


def get_current_week() -> int:
    """Retorna semana atual do semestre (1-15). Retorna 0 fora do período letivo."""
    data = _load_syllabus()
    start = date.fromisoformat(data.get("semestre_inicio", "2026-03-09"))
    end   = date.fromisoformat(data.get("semestre_fim",   "2026-07-04"))
    today = date.today()
    if today < start or today > end:
        return 0
    return min((today - start).days // 7 + 1, 15)


def get_current_topics() -> list[dict]:
    """
    Retorna temas esperados para a semana atual em cada disciplina.
    Ex: [{"disciplina_codigo": "FSC1027", "disciplina_nome": "Física I",
          "semana": 9, "tema": "Energia"}]
    """
    data = _load_syllabus()
    week = get_current_week()
    if week == 0:
        return []

    result = []
    for disc in data["disciplinas"]:
        cronograma = sorted(disc.get("cronograma", []), key=lambda x: x["semana"])
        if not cronograma:
            continue
        current_tema = None
        for item in cronograma:
            if item["semana"] <= week:
                current_tema = item["tema"]
        if current_tema:
            result.append({
                "disciplina_codigo": disc["codigo"],
                "disciplina_nome": disc["nome"],
                "semana": week,
                "tema": current_tema,
            })
    return result


def build_curriculum_context_block(week: int, topics: list[dict]) -> str:
    """Formata bloco de contexto curricular para injetar no Intérprete."""
    if not topics:
        return ""
    lines = [f"### [CURRÍCULO UFSM — Semana {week} do semestre]",
             "Temas atualmente em curso nas disciplinas:"]
    for t in topics:
        lines.append(f"- **{t['disciplina_nome']} ({t['disciplina_codigo']})**: {t['tema']}")
    lines.append("Se a pergunta do aluno se relacionar com estes temas, priorize-os na abordagem.")
    return "\n".join(lines)
