# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**TutorIAFisica** is an AI-powered academic tutoring system for physics education at the university level. It orchestrates multiple specialized AI agents that work together through a shared state object to provide comprehensive explanations, mathematical solutions, visualizations, and formative assessment.

The system is a **full-stack application** with three deployable tiers:
- **Frontend**: Next.js SPA (React 18) deployed to Cloudflare Workers
- **Backend**: FastAPI REST API with SSE streaming deployed to Render.com
- **Legacy**: Streamlit prototype (still functional, used for reference mode)

Core technologies: **LiteLLM** for multi-provider AI orchestration, **Supabase** for database (PostgreSQL) and auth, **React Markdown** + **KaTeX** for mathematical rendering, **Streamlit** for the offline reference interface.

## High-Level Architecture

### Full-Stack Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                        │
│              Cloudflare Workers (tutoriafisica...)           │
│  - ChatInterface with SSE streaming from backend             │
│  - VoiceInput transcription (/api/transcribe)                │
│  - AgentPanel renders markdown + KaTeX for LaTeX             │
└─────────────────────────────────────────────────────────────┘
                              ↓ HTTP + SSE
┌─────────────────────────────────────────────────────────────┐
│                  Backend (FastAPI)                           │
│               Render.com (tutor-ia-fisica-api...)            │
│  - POST /tutor/ask, GET /tutor/ask/stream (SSE)              │
│  - POST /tutor/feedback for SM-2 spaced repetition           │
│  - Orchestrates PhysicsState + Agent Pipeline                │
│  - Supabase integration for persistent StudentModel          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│           LiteLLM Agent Orchestration (src/core.py)          │
│  - Interpreter, Solver, Visualizer, Curator, Evaluator      │
│  - Auto-fallback across multiple providers                   │
│  - Multimodal support (image encoding for Gemini, Claude)    │
└─────────────────────────────────────────────────────────────┘
```

### Design Pattern: Agent Orchestration with Shared State

The agent pipeline follows a **Pipeline + State Pattern** where:

1. **PhysicsState** (`src/core.py`): A single mutable state object that flows through the pipeline. It starts with user input and accumulates results from each agent (concepts, solution, code, etc.).

2. **Agent Pipeline**: Sequential agents process the problem:
   - **Interpreter** 🔵: Initial reasoning and physics domain classification
   - **Solver** 🟢: Mathematical rigor and SI unit consistency
   - **Visualizer** 🟠: Python visualization code generation
   - **Curator** 🟣: Real-world data enrichment and academic sourcing
   - **Evaluator** 🔴: Formative assessment via Socratic questioning

3. **PhysicsOrchestrator** (`src/core.py`): Coordinates the pipeline, validates outputs between agents, handles fallback logic, and tracks which model was actually used.

4. **SSE Streaming** (`backend/routers/tutor.py`): Backend exposes `/tutor/ask/stream` endpoint for real-time agent output streaming to frontend.

### Key Components

#### Backend (`backend/`)

- **main.py**: FastAPI application with CORS config and route mounting
- **routers/tutor.py**: 
  - `POST /tutor/ask` — synchronous request/response
  - `GET /tutor/ask/stream` — SSE streaming for real-time output
  - `POST /tutor/feedback` — SM-2 spaced repetition feedback collection
- **db/supabase_client.py**: Supabase (PostgreSQL) connection for StudentModel persistence
- **schemas/**: Request/response data models (TutorRequest, AgentOutput, TutorResponse)

#### Frontend (`frontend/`)

- **app/page.tsx**: Root layout with chat interface
- **components/ChatInterface.tsx**: Main chat component with model selector and SSE subscription
- **components/AgentPanel.tsx**: Renders individual agent output with markdown + KaTeX rendering
- **components/VoiceInput.tsx**: Mic button for transcription via `/api/transcribe`
- **lib/api.ts**: API client with SSE event handling and TypeScript types

#### Shared Core (`src/`)

- **app.py**: Streamlit UI (legacy, used for offline "Modo Referência"). Handles sidebar configuration, model/API key selection, image upload logic, and display of agent outputs with color-coded styling.
- **config.py**: Centralized configuration including:
  - `AVAILABLE_MODELS`: Maps friendly names to LiteLLM model IDs and capabilities (multimodal flag)
  - `MODEL_PREFERENCE_ORDER`: Fallback chain when the primary model fails
  - `get_provider_key_name()`: Maps model names to environment variable keys
  - `is_model_multimodal()`: Determines if image input should be enabled
- **core.py**: 
  - `TutorIAAgent`: Base class for all agents. Uses `litellm.completion()` for unified API calls and handles image encoding for multimodal models.
  - `PhysicsState`: Accumulates problem context and results
  - `PhysicsOrchestrator`: Runs the pipeline and implements fallback by catching `RateLimitError`, `AuthenticationError`, and `APIError`
  - `process_streaming()`: Yields agent outputs line-by-line for SSE streaming
- **models/student_model.py**: StudentModel class with SM-2 spaced repetition algorithm. Tracks:
  - Review intervals and easiness factors
  - Session count and last review timestamp
  - Question difficulty estimation
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

## Directory Structure

```
TutorIAFisica/
├── src/                          # Shared Python logic (agents, core, config)
│   ├── app.py                    # Streamlit UI (legacy, offline mode)
│   ├── core.py                   # Agent orchestration + PhysicsState
│   ├── config.py                 # Model config, API key handling
│   ├── agents/                   # (Reserved for future agent modules)
│   ├── models/student_model.py   # SM-2 spaced repetition tracking
│   └── utils/pcloud_manager.py   # Teacher materials from pCloud
├── backend/                      # FastAPI application
│   ├── main.py                   # FastAPI app + routes
│   ├── routers/tutor.py          # /tutor/ask, /tutor/ask/stream, /tutor/feedback
│   ├── schemas/                  # Pydantic request/response models
│   ├── db/supabase_client.py     # Supabase PostgreSQL client
│   └── requirements.txt          # Backend dependencies
├── frontend/                     # Next.js application
│   ├── src/app/                  # Next.js App Router
│   ├── src/components/           # React components (ChatInterface, AgentPanel, VoiceInput)
│   ├── src/lib/api.ts            # API client with SSE handling
│   ├── package.json
│   └── vercel.json               # Cloudflare Workers config
├── data/                         # Knowledge base
│   └── ufsm_syllabus.json        # UFSM physics syllabus + temas
├── docs/                         # Documentation
│   ├── DEVELOPER_SETUP.md        # Step-by-step environment setup
│   ├── DEVELOPER_MODO_REFERENCIA.md
│   ├── ARCHITECTURE.md
│   ├── DEPLOY_VERCEL.md
│   └── SOURCE_PIPELINE.md
├── test_*.py                     # Integration & unit tests
├── .env                          # API keys (local, not committed)
├── vercel.json                   # Root Vercel config (monorepo paths)
├── DEVLOG.md                     # Development history
└── CLAUDE.md                     # This file
```

## Development Commands

### Python Environment Setup

```bash
# Create virtual environment (one-time)
python3.11 -m venv venv
source venv/bin/activate

# Install shared dependencies
pip install -r requirements.txt
```

### Running Components

**Backend (FastAPI on http://localhost:8000):**
```bash
source venv/bin/activate
cd backend
python main.py
# or with auto-reload: uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend (Next.js on http://localhost:3000):**
```bash
cd frontend
npm install   # one-time
npm run dev
```

**Streamlit (Legacy, Offline Mode on http://localhost:8501):**
```bash
source venv/bin/activate
cd src
streamlit run app.py
```

### Running Tests

```bash
source venv/bin/activate
# Run all tests
pytest test_*.py -v

# Run specific test file
pytest test_integration.py -v

# Run with coverage
pytest test_*.py --cov=src --cov-report=html
```

### Linting & Type Checking

```bash
# Python (from root)
pylint src/ backend/

# Frontend (from frontend/)
cd frontend && npm run lint
```

## Environment Setup

### `.env` File (Project Root)

Create a `.env` file with these variables (required for both backend and Streamlit):

```bash
# LiteLLM Multi-Provider Keys
GEMINI_API_KEY=xxx
OPENAI_API_KEY=xxx
ANTHROPIC_API_KEY=xxx
DEEPSEEK_API_KEY=xxx
PERPLEXITY_API_KEY=xxx

# Supabase (for StudentModel persistence)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# Backend/Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000  # dev; use production URL in Vercel
```

### Code Execution Context

- **Backend**: FastAPI reads `.env` from project root via `python-dotenv`
- **Frontend**: Next.js reads `.env.local` and `vercel.json` environment variables; frontend env vars must be prefixed `NEXT_PUBLIC_`
- **Streamlit**: Reads `.env` from project root; working directory is `src/` when running `streamlit run app.py`

## Database & StudentModel (Spaced Repetition)

### Supabase Setup

TutorIAFisica uses **Supabase (PostgreSQL)** for:
- Persistent StudentModel storage (SM-2 algorithm state)
- Session history and progress tracking
- User authentication (future: Supabase Auth)

**Required Tables** (auto-created by migration or manual setup):

```sql
-- Students table
CREATE TABLE students (
  id BIGSERIAL PRIMARY KEY,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  session_count INT DEFAULT 0,
  total_score FLOAT DEFAULT 0.0
);

-- Student responses (for SM-2 tracking)
CREATE TABLE student_responses (
  id BIGSERIAL PRIMARY KEY,
  student_id BIGINT REFERENCES students(id),
  question_text TEXT,
  response_text TEXT,
  difficulty FLOAT DEFAULT 2.5,
  last_review TIMESTAMP,
  next_review TIMESTAMP,
  ease_factor FLOAT DEFAULT 2.5,
  interval INT DEFAULT 1,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Connection** (in `backend/db/supabase_client.py`):
- Uses `SUPABASE_URL` and `SUPABASE_KEY` from `.env`
- StudentModel methods read/write review state to `student_responses` table
- Cron job (Supabase scheduled function) triggers SM-2 calculations periodically

**Spaced Repetition Algorithm (SM-2):**
- Formula: `interval = interval * ease_factor` (if correct), `interval = 1` (if incorrect)
- Ease Factor: `ease = max(1.3, ease + (0.1 - (5 - grade) * (0.08 + (5 - grade) * 0.02)))`
- Implemented in `StudentModel.process_response(grade)` where `grade` is 0-5

### StudentModel API

Located in `src/models/student_model.py`:

```python
class StudentModel:
    def __init__(self, student_id: int, supabase_client)
    
    # Load persisted state from Supabase
    def load(self) -> None
    
    # Calculate next review date for a question
    def get_next_review(self, question_id: str) -> datetime
    
    # Process response (0-5 grade) and update SM-2 state
    def process_response(self, question_id: str, grade: int) -> dict
    
    # Get difficulty estimate for question
    def get_difficulty(self, question_id: str) -> float
    
    # Persist current state back to Supabase
    def save(self) -> None
```

**Usage in Backend:**
```python
# In /tutor/feedback endpoint
student_model = StudentModel(student_id=123, supabase_client=supabase)
student_model.load()
result = student_model.process_response(question_id="q123", grade=4)
student_model.save()
```

**Important:** Modo Referência does NOT increment `session_count` or interact with StudentModel (it's offline-only learning).

## Deployment

### Frontend (Cloudflare Workers via Vercel)

**Live:** https://tutoriafisica.hans-059.workers.dev

**Deploy Process:**
1. Vercel reads `vercel.json` at root (specifies `frontend/` as build directory)
2. Runs `cd frontend && npm run build` and outputs to `frontend/.next`
3. Cloudflare Workers integration auto-deploys built assets

**Environment Variables** (set in Vercel UI or via `vercel env`):
```
NEXT_PUBLIC_API_URL = https://tutor-ia-fisica-api.onrender.com
```

**Deployment Checklist:**
- [ ] `NEXT_PUBLIC_API_URL` points to backend URL
- [ ] Backend CORS allows Cloudflare domain
- [ ] `frontend/vercel.json` has correct `buildCommand` and `outputDirectory`
- [ ] All dependencies installed in `frontend/package.json`

### Backend (Render.com)

**Live:** https://tutor-ia-fisica-api.onrender.com

**Deploy Process:**
1. Render.com reads `render.yaml` at root
2. Builds Python environment, installs `backend/requirements.txt`
3. Starts FastAPI server on exposed port

**render.yaml** example:
```yaml
services:
  - type: web
    name: tutor-ia-fisica-api
    runtime: python
    buildCommand: pip install -r backend/requirements.txt
    startCommand: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11
      - key: SUPABASE_URL
        scope: build,run
      - key: SUPABASE_KEY
        scope: build,run
```

**Environment Variables** (set in Render dashboard):
```
SUPABASE_URL = https://xxx.supabase.co
SUPABASE_KEY = ey...
GEMINI_API_KEY = xxx
OPENAI_API_KEY = xxx
# ... all API keys from .env
```

**Database Cron Job** (Supabase Edge Function):
- Scheduled: every 5 days at 12:00 UTC (`0 12 */5 * *`)
- Purpose: Recalculate SM-2 review intervals for all students
- Code: in `SUPABASE_CRON_SETUP.md`

### Streamlit (Local Only)

Streamlit is not deployed. It runs locally for:
- Offline learning (Modo Referência)
- Development/testing
- Fallback if backend is down

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
- **SSE Streaming**: Backend sends agent output line-by-line via `process_streaming()`. Frontend subscribes with `EventSource` and updates UI progressively. Do not buffer full response before sending.
- **CORS**: Backend must allow frontend origin (Cloudflare Workers domain). Check `origins` in FastAPI `CORSMiddleware`.
- **Supabase Connection**: Always load StudentModel state before processing feedback. Call `.save()` after updates. Handle connection failures gracefully (log, don't crash endpoint).

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
