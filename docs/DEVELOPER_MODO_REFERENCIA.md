# Modo Referência — Technical Documentation for Developers

## Overview

**Modo Referência** is an offline knowledge base access feature that allows students to browse UFSM curriculum + teacher notes without calling any LLM API.

**Key Files:**
- `src/app.py` — UI toggle, function `generate_reference_response()`, conditional branch logic
- `src/core.py` — `PhysicsState` class definition, `_check_ufsm_syllabus()` method
- `data/ufsm_syllabus.json` — UFSM disciplina metadata

**Commit:** 79b9547 (2026-04-27)

## Architecture

### Data Flow

```
User Input (Question)
    ↓
[Radio Toggle: "Modo IA" vs "Modo Referência"]
    ├─→ Modo IA
    │   ├─ Create PhysicsOrchestrator
    │   ├─ Call orchestrator.run() [hits APIs]
    │   └─ Update StudentModel session count
    │
    └─→ Modo Referência
        ├─ Call generate_reference_response()
        │   ├─ Extract keywords via regex
        │   ├─ Load pCloud URLs (async)
        │   ├─ Search UFSM syllabus
        │   └─ Fill PhysicsState fields [no APIs]
        ├─ Return PhysicsState
        └─ Display in 5 tabs (StudentModel NOT updated)
```

### PhysicsState Fields Used in Modo Referência

```python
state.raw_input = question               # User question
state.concepts = ["word1", "word2", ...] # Extracted via regex
state.professor_notes_text = "..."        # From manual PDF upload
state.pcloud_session_text = "..."         # From pCloud student link
state.pcloud_repo_text = "..."            # From pCloud repo link
state.adopted_docs_text = "..."           # From pCloud adopted docs
state.ufsm_alignment = {...}              # Full discipline dict (from syllabus)
state.ufsm_context = "..."                # Formatted ementa (from _check_ufsm_syllabus)

# Response fields (filled manually, not by agents)
state.pergunta_socratica = "⚠️ Modo Referência..."
state.solution_steps = "📝 Professor notes..."
state.code_snippet = "📗 Adopted docs..."
state.mapa_mental_markdown = "### 🏛️ Ementa..."
state.quiz_question = "*(Not available)*"

# Flags
state.used_model_display_name = None      # None = Modo Referência, str = Modo IA
state.fallback_occurred = False           # Always False for Modo Referência
```

## Code Walkthrough

### 1. Sidebar Toggle (app.py:340-347)

```python
st.markdown("## 🔬 Modo de Resposta")
response_mode = st.radio(
    "Como deseja a resposta?",
    ["Modo IA", "Modo Referência"],
    index=0,
    help="Modo IA: Full AI explanation (requires API). Modo Referência: Local material (no API)."
)
```

Stores selection in `response_mode` variable (scoped to main() function).

### 2. Function: generate_reference_response() (app.py:105-188)

**Signature:**
```python
def generate_reference_response(
    question: str,
    manual_notes: str = "",
    pcloud_url: str = "",
    repo_url: str = "",
    adopted_url: str = "",
    on_progress=None,
) -> PhysicsState:
```

**Step-by-step:**

#### a) Create PhysicsState instance
```python
state = PhysicsState(raw_input=question, teacher_notes=manual_notes, pcloud_url=pcloud_url)
```

#### b) Sync external data (pCloud URLs)
```python
state.sync_external_data(on_progress=on_progress, repo_url=repo_url, adopted_url=adopted_url)
```

This calls `PCloudManager.fetch_notes()` for each URL. Gracefully handles network errors (returns empty string on failure).

#### c) Extract keywords and search UFSM
```python
keywords = re.findall(r'\b\w{4,}\b', question.lower())
state.concepts = keywords[:3] if keywords else ["conceito"]
state._check_ufsm_syllabus()
```

**Regex explanation:**
- `\b` — word boundary
- `\w{4,}` — 4+ word characters (avoids common stop words like "o", "que", "é")
- `[:3]` — limit to first 3 keywords (avoid noise)
- Fallback: if no matches, use `["conceito"]` (generic placeholder)

**UFSM search** calls built-in method that does substring matching:
```python
# From core.py:91-92
for conceito in self.concepts:
    if conceito.lower() in t.lower():  # Substring match
        self.ufsm_alignment = d
        return
```

#### d) Fill response fields
```python
# Disclaimer
state.pergunta_socratica = "⚠️ **Modo Referência** (sem explicação gerada por IA)\n\n..."

# If UFSM topic found, append it
if state.ufsm_context:
    state.pergunta_socratica += f"\n\n**Tópico Encontrado na UFSM:**\n\n{state.ufsm_context}"

# Teacher notes (tab 2)
state.solution_steps = state.professor_notes_text[:1500] + "..." if len > 1500

# Adopted docs (tab 3)
state.code_snippet = state.adopted_docs_text[:1500] + "..." if len > 1500

# UFSM discipline info (tab 4)
state.mapa_mental_markdown = f"""
### 🏛️ Disciplina UFSM: {disc['nome']} ({disc['codigo']})
**Período:** {disc['periodo']}
**Temas:** {', '.join(disc['temas'])}
**Bibliografia:** {', '.join(disc['bibliografia_basica'][:5])}
"""

# Quiz (tab 5)
state.quiz_question = "*(Quiz não disponível em Modo Referência)*"

# Flags
state.used_model_display_name = None  # Signals "Modo Referência"
state.fallback_occurred = False
```

**Character limits:** All text fields truncated to 1500 chars to prevent UI overload.

### 3. Conditional Branch (app.py:393-445)

```python
if response_mode == "Modo Referência":
    res = generate_reference_response(
        question=enunciado,
        manual_notes=manual_notes,
        pcloud_url=pcloud_url,
        repo_url=pcloud_repo_url,
        adopted_url=adopted_docs_url,
        on_progress=st.write  # Displays progress in UI
    )
    st.session_state.last_result = res
    st.info("📚 **Modo Referência ativado** — exibindo apenas material local...")
else:
    # Modo IA: existing logic unchanged
    orchestrator = PhysicsOrchestrator(...)
    res = orchestrator.run(...)
    # Update StudentModel (only for Modo IA)
```

**Critical difference:** StudentModel update happens ONLY in the else branch (Modo IA). Modo Referência does NOT increment session count.

## Extension Points

### 1. Improve Keyword Extraction

Current: `re.findall(r'\b\w{4,}\b', question.lower())`

**Suggested improvements:**
- Remove physics stop words: "o", "que", "é", "como", "qual", "por", "uma"
- Handle compound terms: "segunda lei" as single concept, not separate
- Use spaCy/NLTK for lemmatization: "forças" → "força"

**Implementation:**
```python
def extract_physics_keywords(question: str, lang: str = "pt") -> list[str]:
    """Extract physics-relevant keywords from question."""
    stop_words = {"o", "que", "é", "como", "qual", "por", "uma", "de", "em", "para"}
    keywords = re.findall(r'\b\w{4,}\b', question.lower())
    return [k for k in keywords if k not in stop_words][:3]
```

### 2. Rank UFSM Matches by Relevance

Current: Takes first match (`return` in loop).

**Suggested improvement:**
- Score each discipline by match count (more keywords = higher score)
- Return top-ranked match instead of first

```python
def find_best_ufsm_match(self) -> Optional[dict]:
    """Find UFSM discipline with highest keyword overlap."""
    scores = {}
    for d in syllabus['disciplinas']:
        for t in d['temas']:
            for conceito in self.concepts:
                if conceito.lower() in t.lower():
                    scores[d['codigo']] = scores.get(d['codigo'], 0) + 1
    if scores:
        best_codigo = max(scores, key=scores.get)
        return next(d for d in syllabus if d['codigo'] == best_codigo)
    return None
```

### 3. Generate Simple Quiz from UFSM

Current: Quiz not available.

**Suggested improvement:** Generate matching quiz without LLM:
- Pick random tema from matched discipline
- Create true/false or fill-the-blank from ementa text

```python
def generate_reference_quiz(discipline: dict) -> str:
    """Create simple quiz from UFSM discipline."""
    tema = random.choice(discipline['temas'])
    return f"Qual destes é um tema de {discipline['nome']}? A) {tema} B) Relatividade"
```

### 4. Bibliography Direct Links

Current: Just displays titles.

**Suggested improvement:** Link to .edu.br or library catalog:
```python
def enrich_bibliography(bibliography_entries: list[str]) -> str:
    """Add links to library catalog or .edu.br databases."""
    # Could integrate with UFSM library API or scanned Semantic Scholar
    pass
```

### 5. Handle Physics Term Synonyms

Current: Simple substring match.

**Suggested improvement:**
```python
PHYSICS_SYNONYMS = {
    "força": ["força aplicada", "força resultante", "força líquida"],
    "energia": ["energia cinética", "energia potencial", "energia mecânica"],
}

def search_with_synonyms(self, concept: str):
    """Search UFSM including synonyms."""
    terms_to_search = [concept] + PHYSICS_SYNONYMS.get(concept, [])
    # ...
```

## Testing

### Unit Testing (Recommended)

**File to create:** `tests/test_modo_referencia.py`

```python
import pytest
from core import PhysicsState
from app import generate_reference_response

def test_keyword_extraction():
    """Test regex extracts 4+ char words."""
    keywords = re.findall(r'\b\w{4,}\b', "O que é força?".lower())
    assert keywords == ["força"]

def test_ufsm_match_newton():
    """Test Segunda Lei de Newton matches Física I."""
    state = PhysicsState(raw_input="Segunda Lei de Newton")
    state.concepts = ["segunda", "newton"]
    state._check_ufsm_syllabus()
    assert state.ufsm_alignment is not None
    assert "Física" in state.ufsm_alignment['nome']

def test_reference_response_no_api_calls(monkeypatch):
    """Verify no API keys are used in Modo Referência."""
    # Mock all API calls to fail
    monkeypatch.setenv("DEEPSEEK_API_KEY", "")
    monkeypatch.setenv("GEMINI_API_KEY", "")
    
    res = generate_reference_response("O que é energia?")
    assert res.used_model_display_name is None
    assert "Modo Referência" in res.pergunta_socratica

def test_truncation_1500_chars():
    """Test long materials are truncated to 1500 chars."""
    long_text = "x" * 3000
    state = PhysicsState(raw_input="test", teacher_notes=long_text)
    # After function processing:
    # state.solution_steps should be max 1500 + " ... (truncado)"
```

### Manual Testing Checklist

- [ ] Sidebar toggle exists and switches between modes
- [ ] Modo Referência: No API errors even without keys
- [ ] Modo Referência: UFSM topic appears for physics questions
- [ ] Modo Referência: Teacher notes (if uploaded) appear in tab 2
- [ ] Modo Referência: Quiz shows "not available" message
- [ ] Modo IA (with key): Full 5-agent pipeline runs
- [ ] StudentModel: Incremented only for Modo IA, not for Modo Referência
- [ ] Graceful failure: Off-topic question doesn't crash

## Performance Notes

- **Keyword extraction:** O(n) where n = number of words (negligible)
- **UFSM search:** O(d×t×c) where d=disciplines, t=themes, c=concepts. ~10ms typical
- **pCloud fetch:** ~500ms-2s per URL (network I/O bound)
- **Total Modo Referência:** ~1-3s vs 30-45s for Modo IA (orchestrator)

## Backward Compatibility

✅ **No breaking changes:**
- Existing Modo IA logic unchanged
- StudentModel update logic unchanged
- PhysicsState class unchanged (only new fields populated)
- UFSM search reuses existing `_check_ufsm_syllabus()` method

If you remove Modo Referência feature:
- Remove toggle from sidebar (line 342-347)
- Remove `generate_reference_response()` function (line 105-188)
- Simplify button branch logic back to just `orchestrator.run()`
- App still works with Modo IA only

## References

- **User guide:** `docs/MODO_REFERENCIA.md`
- **UFSM syllabus structure:** `data/ufsm_syllabus.json` (json schema)
- **PhysicsState:** `src/core.py` line 15-51
- **PCloudManager:** `src/utils/pcloud_manager.py`
- **WebSearcher:** `src/utils/web_searcher.py` (not used in Modo Referência)

---

**Last updated:** 2026-04-27
**Maintainer:** hansufsm
