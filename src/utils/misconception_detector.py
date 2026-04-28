import json
import os
from typing import Optional


class MisconceptionDetector:
    _data: Optional[dict] = None

    @classmethod
    def _load(cls) -> dict:
        if cls._data is None:
            path = os.path.join(os.path.dirname(__file__), "../../data/misconceptions.json")
            with open(path, encoding="utf-8") as f:
                cls._data = json.load(f)
        return cls._data

    @classmethod
    def check(cls, text: str) -> list[dict]:
        """Retorna lista de misconceptions detectadas no texto da pergunta do aluno."""
        data = cls._load()
        found = []
        text_lower = text.lower()
        for domain, items in data.items():
            for mc in items:
                for pattern in mc.get("trigger_patterns", []):
                    if pattern.lower() in text_lower:
                        found.append({
                            "id": mc["id"],
                            "domain": domain,
                            "description": mc["description"],
                            "socratic_probe": mc["socratic_probe"],
                        })
                        break  # um match por misconception é suficiente
        return found

    @classmethod
    def build_context_block(cls, misconceptions: list[dict]) -> str:
        """Monta bloco de contexto para injetar no prompt do Intérprete."""
        if not misconceptions:
            return ""
        lines = ["### [MISCONCEPTIONS COMUNS NESTE TÓPICO — use para guiar sua abordagem socrática]"]
        for mc in misconceptions[:3]:
            lines.append(f"- **{mc['description']}**")
            lines.append(f"  Probe sugerido: \"{mc['socratic_probe']}\"")
        return "\n".join(lines)
