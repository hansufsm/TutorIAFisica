# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**TutorIAFisica** is an AI-powered academic tutoring system for physics education at the university level. It orchestrates multiple specialized AI agents that work together through a shared state object to provide comprehensive explanations, mathematical solutions, visualizations, and formative assessment.

The system is built with **Streamlit** for the UI and **LiteLLM** for flexible model orchestration across multiple providers (Gemini, Claude, OpenAI, DeepSeek, Perplexity, Grok).

## High-Level Architecture

### Design Pattern: Agent Orchestration with Shared State

The system follows a **Pipeline + State Pattern** where:

1. **PhysicsState** (`src/core.py`): A single mutable state object that flows through the pipeline. It starts with user input and accumulates results from each agent (concepts, solution, code, etc.).

2. **Agent Pipeline**: Sequential agents process the problem:
   - **Interpreter**: Initial reasoning and physics domain classification
   - **Solver**: Mathematical rigor and SI unit consistency
   - **Visualizer**: Python visualization code generation
   - **Curator**: Real-world data enrichment and academic sourcing
   - **Evaluator**: Formative assessment via Socratic questioning

3. **PhysicsOrchestrator** (`src/core.py`): Coordinates the pipeline, validates outputs between agents, handles fallback logic, and tracks which model was actually used.

### Key Components

- **app.py**: Streamlit UI. Handles sidebar configuration, model/API key selection, image upload logic, and display of agent outputs with color-coded styling.
- **config.py**: Centralized configuration including:
  - `AVAILABLE_MODELS`: Maps friendly names to LiteLLM model IDs and capabilities (multimodal flag)
  - `MODEL_PREFERENCE_ORDER`: Fallback chain when the primary model fails
  - `get_provider_key_name()`: Maps model names to environment variable keys
  - `is_model_multimodal()`: Determines if image input should be enabled
- **core.py**: 
  - `TutorIAAgent`: Base class for all agents. Uses `litellm.completion()` for unified API calls and handles image encoding for multimodal models.
  - `PhysicsState`: Accumulates problem context and results
  - `PhysicsOrchestrator`: Runs the pipeline and implements fallback by catching `RateLimitError`, `AuthenticationError`, and `APIError`
- **utils/pcloud_manager.py**: Cloud storage integration for fetching teacher notes from pCloud (uses public link extraction and PDF processing via `requests` + `io.BytesIO`)

### API Key & Fallback Flow

1. **Sidebar Model Selection**: User picks a preferred model in `app.py`
2. **Key Management**: 
   - First checks `.env` (via `dotenv` in `config.py`)
   - If key missing, prompts for runtime input via `st.text_input()`
   - Passes API key to agent via the `api_key` parameter in `TutorIAAgent.ask()`
3. **Automatic Fallback**:
   - If selected model fails, orchestrator tries the next in `MODEL_PREFERENCE_ORDER`
   - User sees notification when fallback occurs
   - State tracks `used_model_display_name` and `fallback_occurred`

### Multimodal Handling

- Image upload is enabled/disabled based on `Config.is_model_multimodal(selected_model)`
- If user provides an image to a text-only model, a warning is logged but processing continues without the image
- Images are encoded as base64 JPEG in the message structure for multimodal models

### Modo Referência — Offline Knowledge Base (v4.3+)

**Feature:** Students can access UFSM syllabus + teacher notes **without API keys**.

- **Toggle:** Sidebar "🔬 Modo de Resposta" with "Modo IA" and "Modo Referência" options
- **No API calls:** `generate_reference_response()` in `app.py` (lines 105-188) fills PhysicsState with local materials only
- **Keyword extraction:** Regex `\b\w{4,}\b` extracts 4+ char words from question
- **UFSM search:** Reuses `PhysicsState._check_ufsm_syllabus()` for substring matching against discipline temas
- **Character limits:** All response fields truncated to 1500 chars to prevent UI overload
- **StudentModel isolation:** Modo Referência does NOT increment session count (not an "AI session")
- **Conditional branch:** Button logic (line 393-445) routes to `generate_reference_response()` or `orchestrator.run()` based on toggle

**User docs:** `docs/MODO_REFERENCIA.md`
**Developer docs:** `docs/DEVELOPER_MODO_REFERENCIA.md`
**Memory:** `/home/hans/.claude/projects/.../memory/feature_modo_referencia.md`

## Running the Application

```bash
# Activate virtual environment
source venv/bin/activate

# Ensure .env exists with API keys (see README for keys needed)
cat > .env << EOF
GEMINI_API_KEY=your_key
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
# ... other keys
EOF

# Run the Streamlit app
cd src
streamlit run app.py
```

The app starts on `http://localhost:8501` by default.

## Code Execution Context

- **Working Directory**: When running `streamlit run app.py`, the working directory is `src/`, so imports like `from config import Config` work directly.
- **Environment**: Uses `.env` file at project root (loaded via `python-dotenv`)
- **Session State**: Streamlit's `st.session_state` persists model selection and runtime API keys within a session

## Extending the System

### Adding a New Model

1. Update `Config.AVAILABLE_MODELS` in `config.py`:
   ```python
   "MyModel": {"id": "provider/model-id", "multimodal": True/False}
   ```

2. If it's a new provider, add the key name handling in `Config.get_provider_key_name()` and ensure the `.env` template documents it.

3. If fallback order matters, insert into `Config.MODEL_PREFERENCE_ORDER`.

### Adding a New Agent

1. Create an agent class in `src/` or `src/agents/`:
   ```python
   class MyAgent(TutorIAAgent):
       def __init__(self):
           super().__init__(
               name="MyAgent",
               system_instruction="Your specialized instructions..."
           )
   ```

2. In `PhysicsOrchestrator.process()`, instantiate and call:
   ```python
   agent = MyAgent()
   result = agent.ask(prompt, context=state.solution_steps, model_id=model_id, api_key=api_key)
   state.my_field = result
   ```

3. Ensure the agent handles images appropriately based on the model's multimodal capability.

## Important Invariants

- **State Accumulation**: Each agent in the pipeline reads from `PhysicsState` (prior results) and writes to it. Don't bypass this pattern—it enables debugging and supports formative feedback loops.
- **LiteLLM Errors**: Catch `RateLimitError`, `AuthenticationError`, and `APIError` for fallback logic. Other exceptions are unrecoverable.
- **Multimodal Images**: Always check `Config.is_model_multimodal()` before including images in the message. Base64 encoding is handled by `TutorIAAgent.ask()`.
- **API Keys**: Never hardcode API keys. Always read from `.env` first, then offer runtime input via Streamlit UI for missing keys.

## Debugging Tips

- Check `PhysicsState.used_model_display_name` and `fallback_occurred` to see which model actually ran
- Print agent outputs in the orchestrator loop to trace where the pipeline fails
- Use Streamlit's `st.write()` or `st.json()` to inspect state during development
- Watch for multimodal image encoding errors if models are switched—test with both text and image inputs

## Dependencies

Core dependencies in `requirements.txt`:
- `streamlit`: UI framework
- `litellm`: Unified LLM API abstraction
- `python-dotenv`: Environment variable loading
- `pypdf`: PDF text extraction
- `matplotlib`, `plotly`: Visualization libraries
- `Pillow`: Image handling
- `pandas`: Data processing
- `requests`: HTTP calls (for pCloud)
---

## Pedagogical Conventions

This section documents the educational design principles that must be respected by all agents
and any code that generates content for students. Claude Code should apply these conventions
when developing agents, writing `system_instruction` strings, or creating test content.

### The 4 Dimensions — Core Design Contract

Every student interaction is processed across four mandatory dimensions. Each agent owns one:

| Agent | Colour | Dimension | Contract |
|---|---|---|---|
| Interpreter | 🔵 Blue | Socratic | Ask before telling. Deconstruct the problem with reflective questions. Never deliver the full solution upfront. |
| Solver | 🟢 Green | Procedural | Strict SI units, dimensional analysis on every step, LaTeX for all equations. |
| Visualizer | 🟠 Orange | Intuitive | Produce runnable Python (Matplotlib or Plotly). Prefer interactive Plotly with sliders over static plots. |
| Curator | 🟣 Purple | Contextual | Cite real academic sources. Priority: UFSM material → .edu.br portals → arXiv / Semantic Scholar. |
| Evaluator | 🔴 Red | Formative | Quiz mode. Give hints, not answers. Never confirm the answer directly — use Socratic redirection. |

### Socratic Method — Implementation Rules

When writing `system_instruction` for the Interpreter or Evaluator agents:

1. **Probe before solving** — always surface at least one conceptual question before proceeding
2. **Layer complexity** — start with the simplest form of the question, escalate only if the student demonstrates understanding
3. **Validate understanding** — after the student responds, assess it and give constructive feedback, not the full answer
4. **Formative over summative** — the goal is learning process, not answer delivery

Example pattern for Interpreter `system_instruction`:
```
Antes de resolver, identifique: qual grandeza física está sendo perguntada?
Quais dados foram fornecidos? Existe alguma grandeza implícita que o aluno
pode ter esquecido? Faça UMA pergunta de cada vez.
```

### LaTeX Conventions (Solver agent)

All mathematical content must use LaTeX. Rules:

- Inline: `$F = ma$`
- Display (isolated equations): `$$\vec{F} = m\vec{a}$$`
- Units always in `\text{}`: `$v = 30\,\text{m/s}$`
- Dimensional analysis shown explicitly before numeric substitution:
  ```
  [F] = [m][a] = \text{kg} \cdot \text{m/s}^2 = \text{N}  ✓
  ```
- SI base units enforced — flag any non-SI input and convert before solving

### Source Hierarchy — Citation Format

When an agent response includes academic content, tag the source inline:

```
[Material do Professor]      ← pCloud teacher notes (Level 1, highest priority)
[Documento da Disciplina]    ← adopted textbooks/slides (Level 2)
[Ementa UFSM]               ← data/ufsm_syllabus.json (Level 3)
[Portal Acadêmico]           ← .edu.br web search result (Level 4)
[Referência Internacional]   ← arXiv, Semantic Scholar (Level 5)
[Modelo de IA]               ← no academic source found (Level 5, fallback)
```

Never mix levels — use the highest-priority source available and tag accordingly.

### Physics Topics (UFSM Syllabus Scope)

Agents must recognise and correctly classify questions from these domains:

- **Mechanics**: kinematics, Newton's laws, work-energy theorem, momentum, rotational motion
- **Thermodynamics**: temperature, heat, ideal gas laws, entropy, thermodynamic cycles
- **Electromagnetism**: Coulomb's law, electric field/potential, circuits (Ohm, Kirchhoff), magnetic field, Faraday's law
- **Waves & Optics**: SHM, wave equation, sound, geometric optics, interference, diffraction
- **Modern Physics**: photoelectric effect, special relativity basics, atomic models

The Interpreter agent must classify the question domain in `PhysicsState` before passing to Solver.

### Visualizer — Code Quality Rules

All code generated by the Visualizer must:

1. Be **self-contained** and **runnable as-is** (no missing imports, no placeholder data)
2. Include `plt.tight_layout()` or equivalent before `plt.show()`
3. Label all axes with quantity name **and unit**: `plt.xlabel("Tempo (s)")`
4. For Plotly: use `fig.update_layout(template="plotly_dark")` to match the app's dark theme
5. Prefer parametric sliders (`ipywidgets` or `st.slider`) for quantities the student can explore
6. Never generate code that requires external data files — embed sample data inline

### Evaluator — Formative Assessment Rules

When the Evaluator generates a quiz challenge:

- Base the question strictly on the topic just explained (no scope creep)
- Difficulty: start at recall level, escalate to application if student succeeds
- On correct answer: congratulate briefly, then ask a follow-up that deepens understanding
- On incorrect answer: identify the specific misconception, give a targeted hint, ask again
- Never reveal the answer in fewer than 2 failed attempts — maintain Socratic pressure
- Store challenge and student response in `PhysicsState.formative_challenge` for session continuity

---

## Development Log (DEVLOG)

To prevent losing context about what was done and when, this project maintains a dual devlog system:

### 📄 DEVLOG.md (Public, Versionized)
Located at `/home/hans/devworkspace/TutorIAFisica/DEVLOG.md`

**When to update:**
- After completing a major feature or phase
- When a significant milestone is reached
- Before committing related work

**Format:**
```markdown
## 📅 YYYY-MM-DD — Feature Name

**Commits:** `abc1234` + `def5678`

### O que foi feito
- ✅ Implementation detail 1
- ✅ Implementation detail 2

### Decisões/Desvios
- Note any departures from original plan

### Status
🟢 COMPLETO | 🟡 PARCIAL | ⏳ PENDENTE

### Próximo Passo
What's next logically
```

### 📌 Memory devlog_summary.md (Auto-Loaded)
Located at `/home/hans/.claude/projects/.../memory/devlog_summary.md`

**What it contains:**
- Executive summary of latest work session
- Current status and phase
- List of completed phases
- Next high-priority items
- Links to critical reference files

**Auto-loaded each session** — you see it in system context without reading.

### Usage Pattern

1. **During work:** Track in-progress status in your thinking
2. **End of session:** 
   - I will ask: "Quer registrar essa sessão no DEVLOG?"
   - Provide a summary with commit refs
   - Answer any follow-up questions about references
3. **Between sessions:** 
   - I load `devlog_summary.md` from memory
   - You resume context immediately
   - No need to re-read project status

### Why Dual System?

- **DEVLOG.md** = Full public history, discoverable via `git log`, shareable with team
- **devlog_summary.md** = Compressed context loaded into each session, prevents "cold start"
