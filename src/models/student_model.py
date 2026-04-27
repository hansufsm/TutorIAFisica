from dataclasses import dataclass, asdict
from datetime import date, timedelta
import json, os, re


@dataclass
class ConceptStatus:
    concept_id: str
    topic: str
    ufsm_discipline: str
    first_seen: str
    last_seen: str
    times_seen: int
    quiz_attempts: int
    quiz_correct: int
    ease_factor: float
    interval_days: int
    next_review: str

    @property
    def mastery_level(self) -> float:
        if self.quiz_attempts == 0:
            return 0.1
        acc = self.quiz_correct / self.quiz_attempts
        interval_score = min(1.0, self.interval_days / 30)
        return round(acc * 0.7 + interval_score * 0.3, 2)

    @property
    def status(self) -> str:
        m = self.mastery_level
        if m < 0.25:
            return "not_started"
        if m < 0.55:
            return "developing"
        if m < 0.85:
            return "mastered"
        return "consolidated"


class StudentModel:
    def __init__(self, student_id: str):
        self.student_id = student_id
        self.created_at = date.today().isoformat()
        self.updated_at = date.today().isoformat()
        self.concepts: dict[str, ConceptStatus] = {}
        self.session_count: int = 0

    def _path(self, data_dir: str) -> str:
        slug = re.sub(r"[^\w-]", "_", self.student_id.lower().strip())
        return os.path.join(data_dir, f"{slug}.json")

    def save(self, data_dir: str = "data/students"):
        os.makedirs(data_dir, exist_ok=True)
        self.updated_at = date.today().isoformat()
        payload = {
            "student_id": self.student_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "session_count": self.session_count,
            "concepts": {k: asdict(v) for k, v in self.concepts.items()},
        }
        with open(self._path(data_dir), "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, student_id: str, data_dir: str = "data/students") -> "StudentModel":
        sm = cls(student_id)
        path = sm._path(data_dir)
        if not os.path.exists(path):
            return sm
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            sm.created_at = data.get("created_at", sm.created_at)
            sm.updated_at = data.get("updated_at", sm.updated_at)
            sm.session_count = data.get("session_count", 0)
            for k, v in data.get("concepts", {}).items():
                sm.concepts[k] = ConceptStatus(**v)
        except Exception as e:
            print(f"Aviso: erro ao carregar StudentModel: {e}")
        return sm

    def update_after_session(self, concepts: list[str], discipline_name: str = ""):
        today = date.today().isoformat()
        for raw in concepts:
            cid = re.sub(r"[^\w]", "_", raw.lower().strip())
            if cid in self.concepts:
                c = self.concepts[cid]
                c.times_seen += 1
                c.last_seen = today
                if c.interval_days == 0:
                    c.interval_days = 1
                    c.next_review = (date.today() + timedelta(days=1)).isoformat()
            else:
                self.concepts[cid] = ConceptStatus(
                    concept_id=cid,
                    topic=raw.strip(),
                    ufsm_discipline=discipline_name,
                    first_seen=today,
                    last_seen=today,
                    times_seen=1,
                    quiz_attempts=0,
                    quiz_correct=0,
                    ease_factor=2.5,
                    interval_days=1,
                    next_review=(date.today() + timedelta(days=1)).isoformat(),
                )
        self.session_count += 1

    def update_quiz_result(self, concept_id: str, correct: bool):
        if concept_id not in self.concepts:
            return
        c = self.concepts[concept_id]
        c.quiz_attempts += 1
        if correct:
            c.quiz_correct += 1
            if c.interval_days <= 1:
                new_interval = 6
            else:
                new_interval = round(c.interval_days * c.ease_factor)
            c.ease_factor = min(3.0, c.ease_factor + 0.1)
            c.interval_days = new_interval
        else:
            c.interval_days = 1
            c.ease_factor = max(1.3, c.ease_factor - 0.2)
        c.next_review = (date.today() + timedelta(days=c.interval_days)).isoformat()

    def get_due_for_review(self) -> list[ConceptStatus]:
        today = date.today().isoformat()
        return [c for c in self.concepts.values() if c.next_review <= today]

    def to_dataframe_records(self) -> list[dict]:
        return [
            {
                "topic": c.ufsm_discipline or "Geral",
                "concept": c.topic,
                "mastery": c.mastery_level,
                "status": c.status,
                "times_seen": c.times_seen,
            }
            for c in self.concepts.values()
        ]
