# TutorIAFisica — Roadmap de Deploy: Stack Gratuito 2026

**Objetivo:** Migrar de Streamlit → FastAPI + Next.js + Supabase  
**Deploy:** Cloudflare Pages (frontend) + Render.com (backend) + Supabase (PostgreSQL)  
**Custo total:** R$ 0,00 (gratuito ilimitado)  
**Tempo estimado:** 6-8 horas (primeira vez)

---

## 📋 Navegação Rápida

| Seção | Público | Tempo | Pré-requisito |
|---|---|---|---|
| **[Decisão Inicial](#decisão-inicial)** | Todos | 2 min | — |
| **[Etapa 0: Contas](#-etapa-0--contas-e-serviços)** | Todos | 15 min | — |
| **[Etapa 1: Banco de Dados](#-etapa-1--schema-do-supabase)** | Backend devs | 10 min | Etapa 0 ✅ |
| **[Etapa 2: Backend FastAPI](#-etapa-2--backend-fastapi)** | Backend devs | 90 min | Etapa 0 + 1 ✅ |
| **[Etapa 3: Modificar core.py](#-etapa-3--modificação-em-srccore-py)** | Python devs | 20 min | Etapa 2 ✅ |
| **[Etapa 4: Frontend Next.js](#-etapa-4--frontend-nextjs)** | Frontend devs | 60 min | Etapa 0 ✅ |
| **[Etapa 5: Deploy Produção](#-etapa-5--deploy-em-produção)** | DevOps | 20 min | Etapa 2 + 4 ✅ |
| **[Etapa 6: Local Dev](#-etapa-6--desenvolvimento-local)** | Todos (opcional) | 15 min | Etapa 2 + 4 ✅ |
| **[Troubleshooting](#-troubleshooting)** | Quando errar | 5-30 min | Sempre disponível |

---

## ⚡ Decisão Inicial

### Qual é o seu caso?

**CASO A: Começar do zero (novo repositório ou fresh start)**  
→ Siga a ordem: **Etapa 0 → 1 → 2 → 3 → 4 → 5**  
→ Tempo: 4-5 horas | Recomendado para novos contribuidores

**CASO B: Migrar do Streamlit existente**  
→ Siga a ordem: **Etapa 0 → 1 → 2 → 3 → 4 → 5**  
→ Tempo: 5-8 horas | Integrar `StudentModel` existente no banco (Etapa 1)

**CASO C: Apenas desenvolvimento local sem deploy**  
→ Pule para: **Etapa 6** (docker-compose)  
→ Tempo: 15 minutos

**CASO D: Só backend (frontend já existe)**  
→ Siga: **Etapa 0 → 1 → 2 → 3 → 5**  
→ Pule Etapa 4

---

## 🗺️ Diagrama de Dependências

```
ETAPA 0 (Contas)
   ├─→ ETAPA 1 (Schema SQL) [Supabase]
   │     └─→ ETAPA 2 (Backend) [Render.com]
   │           └─→ ETAPA 3 (core.py mods) [Python]
   │                 └─→ ETAPA 5 (Deploy) [Render]
   │
   └─→ ETAPA 4 (Frontend) [Cloudflare Pages]
         └─→ ETAPA 5 (Deploy) [Cloudflare]

ETAPA 6 (Local Dev) — pode ser feita em paralelo com 2-4
```

---

## ⚠️ Problemas Comuns ANTES de Começar

| Problema | Solução | Seção |
|----------|---------|-------|
| "Meu Supabase continua pausado" | Configurar cron job | [Avisos Importantes](#avisos-importantes) |
| "Render dorme e fica lento" | Esperar 30s na 1ª requisição | [Avisos Importantes](#avisos-importantes) |
| "Como saber se está funcionando?" | Ver [Verificação](#verificação-por-etapa) | Após cada etapa |
| "Preciso do .env antes de começar?" | Sim, preparar em Etapa 0 | [Etapa 0](#-etapa-0--contas-e-serviços) |

---

## LEIA ANTES DE QUALQUER COISA

### 🔴 Regra de Ouro — Não Mexer em Arquivos Críticos

**NUNCA modificar** os seguintes arquivos — contêm a inteligência do sistema:
- `src/core.py` — PhysicsOrchestrator, PhysicsState, TutorIAAgent (**exceção:** adicionar só `process_streaming()` em Etapa 3)
- `src/agents/` — todos os 5 agentes especializados
- `src/config.py` — modelos, chaves, fallback
- `src/utils/pcloud_manager.py` — integração pCloud
- `data/ufsm_syllabus.json` — ementa UFSM

**A única exceção permitida:**  
Adicionar o método `process_streaming()` em `src/core.py` (Etapa 3) — não tocar em nada já existente.

> ✅ Tudo que for novo vai em `/backend` ou `/frontend`, deixando `/src` intacto

### Stack alvo

```
[Aluno]
   │
   ▼
Cloudflare Pages          → Frontend Next.js/React (GRATUITO ilimitado)
   │ HTTPS + SSE streaming
   ▼
Render.com                → Backend FastAPI Python (GRATUITO, dorme 15min idle)
   │ supabase-py
   ▼
Supabase                  → PostgreSQL + Auth + pgvector (GRATUITO 500MB)
   │
   ├── tabela: students          (perfis dos alunos)
   ├── tabela: concept_status    (Student Model por aluno)
   ├── tabela: session_log       (histórico de sessões)
   ├── tabela: misconceptions    (misconceptions detectadas)
   └── storage: materials        (fallback pCloud → Supabase Storage)
```

### Estrutura final do repositório

```
TutorIAFisica/
├── src/                          ← INTACTO (apenas +process_streaming)
│   ├── agents/
│   ├── utils/
│   ├── config.py
│   └── core.py
├── backend/                      ← NOVO
│   ├── main.py
│   ├── routers/
│   │   ├── tutor.py
│   │   └── student.py
│   ├── schemas/
│   │   ├── request.py
│   │   └── response.py
│   ├── db/
│   │   ├── supabase_client.py
│   │   └── student_model.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                     ← NOVO
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx
│   │   │   ├── layout.tsx
│   │   │   └── globals.css
│   │   ├── components/
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── AgentPanel.tsx
│   │   │   ├── VoiceInput.tsx
│   │   │   └── ProgressMap.tsx
│   │   └── lib/
│   │       └── api.ts
│   ├── package.json
│   └── .env.local
├── supabase/
│   └── migrations/
│       └── 001_initial_schema.sql
├── data/                         ← INTACTO
├── .env                          ← adicionar vars do Supabase
├── docker-compose.yml            ← NOVO (dev local)
├── render.yaml                   ← NOVO (deploy Render)
└── CLAUDE.md                     ← atualizar ao final
```

---

## 🟦 ETAPA 0 — Contas e Serviços

**Tempo:** ~15 min | **Pré-requisito:** — | **Output:** 3 contas + arquivo `.env`

### 0.1 — Criar Contas (passo a passo)

#### 1️⃣ **Supabase** (banco de dados PostgreSQL gratuito)

1. Acesse https://supabase.com
2. Clique "Sign Up" → crie conta com GitHub ou email
3. Clique "New Project"
   - Name: `tutor-ia-fisica`
   - Region: `South America (São Paulo)` (mais perto, melhor latência)
   - Database Password: guarde em local seguro
4. Aguarde ~2 minutos (criação do banco)
5. Quando pronto, vá para **Settings → API** e anote:
   ```
   SUPABASE_URL=https://xxxx.supabase.co
   SUPABASE_ANON_KEY=eyJ...
   SUPABASE_SERVICE_KEY=eyJ...
   ```
   > ⚠️ **GOTCHA:** `SERVICE_KEY` (acesso admin) nunca vai no frontend. Só backend e variáveis de ambiente.

#### 2️⃣ **Render.com** (servidor backend gratuito)

1. Acesse https://render.com
2. Clique "Sign Up" → conecte sua conta GitHub
3. **Você conectará ao repositório em Etapa 5.1**, não precisa fazer nada agora
4. Anote seu email (vai precisar para deploy automático)

#### 3️⃣ **Cloudflare Pages** (hospedagem frontend gratuita)

1. Acesse https://pages.cloudflare.com
2. Clique "Sign Up" → crie conta ou use GitHub
3. **Você conectará em Etapa 5.2**, por enquanto só confirme acesso

---

### 0.2 — Preparar `.env`

Na **raiz do repositório**, criar/atualizar `.env`:

```bash
# SUPABASE (do Etapa 0.1)
SUPABASE_URL=https://xxxxxxxxxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# DEPLOY
FRONTEND_URL=https://tutor-ia-fisica.pages.dev

# LLM KEYS (copiar do .env existente)
GEMINI_API_KEY=AIza...
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
# ... outras chaves já existentes
```

> ✅ **Verificação:** Confirme que `.env` tem essas 3 linhas Supabase

---

### 0.3 — Ativar Keep-Alive do Supabase (Etapa 0.3)

**🔴 CRÍTICO:** Supabase Free pausa após 7 dias sem atividade. Configure agora para evitar perder dados.

1. Acesse https://cron-job.org
2. Clique "Sign Up" (gratuito, sem cartão)
3. Clique "Create Cronjob"
   - **Title:** `Supabase Keep-Alive`
   - **URL:** `https://xxxx.supabase.co/rest/v1/students?limit=1`  
     (substitua `xxxx` pela sua instância)
   - **HTTP Headers:** Adicionar campo:
     ```
     Key: apikey
     Value: [cole aqui seu SUPABASE_ANON_KEY]
     ```
   - **Frequency:** `Every 5 days at 12:00 (noon) UTC`
4. Clique "Save"

> ✅ **Verificação:** Dashboard do cron-job deve mostrar "Status: OK" após 5 dias

---

### ✓ Etapa 0 Completa?

Responda sim a todos:
- [ ] Supabase: projeto criado, URL e chaves anotadas
- [ ] Render.com: conta criada e GitHub conectado
- [ ] Cloudflare Pages: conta criada
- [ ] `.env`: arquivo preparado com 3 chaves Supabase
- [ ] Cron job: configurado em cron-job.org

👉 **Próximo:** Etapa 1 (criar schema SQL)

---

## 🟩 ETAPA 1 — Schema do Supabase

**Tempo:** ~10 min | **Pré-requisito:** Etapa 0 ✅ | **Output:** 4 tabelas + RLS policies

### 1.1 — Criar arquivo SQL

Criar arquivo na raiz:
```bash
mkdir -p supabase/migrations
touch supabase/migrations/001_initial_schema.sql
```

### 1.2 — Copiar schema completo

Editar `supabase/migrations/001_initial_schema.sql`:

### `supabase/migrations/001_initial_schema.sql`

```sql
-- Habilitar extensão pgvector para embeddings futuros (Student Model)
CREATE EXTENSION IF NOT EXISTS vector;

-- Perfis dos alunos
CREATE TABLE students (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email        TEXT UNIQUE,                    -- via Supabase Auth
  name         TEXT,
  created_at   TIMESTAMPTZ DEFAULT NOW(),
  last_seen    TIMESTAMPTZ DEFAULT NOW()
);

-- Student Model: status de cada conceito por aluno
CREATE TABLE concept_status (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id          UUID REFERENCES students(id) ON DELETE CASCADE,
  concept_id          TEXT NOT NULL,           -- ex: "newton_segunda_lei"
  topic               TEXT NOT NULL,           -- ex: "Dinâmica"
  status              TEXT DEFAULT 'not_started',
    -- 'not_started' | 'developing' | 'mastered' | 'consolidated'
  mastery_level       FLOAT DEFAULT 0.0,       -- 0.0 a 1.0
  review_interval_days INT DEFAULT 1,          -- algoritmo SM-2
  ease_factor         FLOAT DEFAULT 2.5,       -- fator de facilidade SM-2
  last_reviewed       TIMESTAMPTZ,
  next_review         TIMESTAMPTZ,
  date_introduced     TIMESTAMPTZ DEFAULT NOW(),
  date_mastered       TIMESTAMPTZ,
  embedding           vector(1536),            -- para busca semântica futura
  UNIQUE(student_id, concept_id)
);

-- Misconceptions detectadas por aluno
CREATE TABLE misconceptions (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id    UUID REFERENCES students(id) ON DELETE CASCADE,
  concept_id    TEXT NOT NULL,
  misconception_id TEXT NOT NULL,             -- ex: "mc_forca_velocidade"
  description   TEXT,
  detected_at   TIMESTAMPTZ DEFAULT NOW(),
  resolved_at   TIMESTAMPTZ,                  -- null = ainda ativa
  attempts      INT DEFAULT 1
);

-- Log de sessões
CREATE TABLE session_log (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id    UUID REFERENCES students(id) ON DELETE CASCADE,
  question      TEXT NOT NULL,
  topic         TEXT,
  model_used    TEXT,
  fallback      BOOLEAN DEFAULT FALSE,
  agents_output JSONB,                        -- saída completa dos 5 agentes
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX idx_concept_student ON concept_status(student_id);
CREATE INDEX idx_concept_next_review ON concept_status(next_review);
CREATE INDEX idx_misconceptions_student ON misconceptions(student_id, resolved_at);
CREATE INDEX idx_session_student ON session_log(student_id, created_at DESC);

-- Row Level Security: cada aluno só acessa seus próprios dados
ALTER TABLE students ENABLE ROW LEVEL SECURITY;
ALTER TABLE concept_status ENABLE ROW LEVEL SECURITY;
ALTER TABLE misconceptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE session_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY "aluno acessa próprios dados" ON concept_status
  FOR ALL USING (student_id = auth.uid());

CREATE POLICY "aluno acessa próprias misconceptions" ON misconceptions
  FOR ALL USING (student_id = auth.uid());

CREATE POLICY "aluno acessa próprias sessões" ON session_log
  FOR ALL USING (student_id = auth.uid());
```

### 1.3 — Executar SQL no Supabase

1. Abra https://supabase.com/dashboard
2. Selecione projeto `tutor-ia-fisica`
3. Vá para **SQL Editor** (menu esquerdo)
4. Clique "+ New Query"
5. **Cole todo o conteúdo** de `supabase/migrations/001_initial_schema.sql`
6. Clique **"Run"** (canto superior direito)

Você deve ver:
```
✓ CREATE EXTENSION IF NOT EXISTS vector;
✓ CREATE TABLE students;
✓ CREATE TABLE concept_status;
✓ CREATE TABLE misconceptions;
✓ CREATE TABLE session_log;
✓ CREATE INDEX ... (5 indices)
✓ ALTER TABLE ... ENABLE ROW LEVEL SECURITY; (4 vezes)
✓ CREATE POLICY ... (3 policies)
```

### 1.4 — Verificar Tabelas

1. No menu esquerdo, clique **"Table Editor"**
2. Confirme que aparecem:
   - `students` (0 linhas)
   - `concept_status` (0 linhas)
   - `misconceptions` (0 linhas)
   - `session_log` (0 linhas)

> ✅ Se as 4 tabelas aparecem, Etapa 1 está concluída

### ✓ Etapa 1 Completa?

- [ ] Arquivo SQL criado em `supabase/migrations/001_initial_schema.sql`
- [ ] SQL executado no Supabase (sem erros)
- [ ] 4 tabelas visíveis em Table Editor
- [ ] RLS policies ativas (todas com "ON")

👉 **Próximo:** Etapa 2 (backend FastAPI)

---

## 🟨 ETAPA 2 — Backend FastAPI

**Tempo:** ~90 min | **Pré-requisito:** Etapa 0 + 1 ✅ | **Output:** Backend em `backend/` pronto para deploy

### 2.1 — Criar Estrutura de Diretórios

```bash
# Na raiz do repositório (onde está src/, data/, etc.)
mkdir -p backend/routers backend/schemas backend/db

# Criar __init__.py em cada pasta
touch backend/__init__.py
touch backend/routers/__init__.py
touch backend/schemas/__init__.py
touch backend/db/__init__.py
```

**Estrutura esperada:**
```
TutorIAFisica/
├── src/                  ← INTACTO
├── data/                 ← INTACTO
├── backend/              ← NOVO
│   ├── __init__.py
│   ├── main.py           ← criar em 2.9
│   ├── requirements.txt   ← criar em 2.2
│   ├── Dockerfile        ← criar em 2.10
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── tutor.py      ← criar em 2.7
│   │   └── student.py    ← criar em 2.8
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── request.py    ← criar em 2.5
│   │   └── response.py   ← criar em 2.6
│   └── db/
│       ├── __init__.py
│       ├── supabase_client.py  ← criar em 2.3
│       └── student_model.py    ← criar em 2.4
```

### 2.2 `backend/requirements.txt`

```
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
python-dotenv>=1.0.0
pydantic>=2.0.0
python-multipart>=0.0.9
supabase>=2.0.0
# dependências já existentes — copiar do requirements.txt raiz:
litellm
pypdf
matplotlib
plotly
Pillow
pandas
requests
openai
```

### 2.3 `backend/db/supabase_client.py`

```python
import os
from supabase import create_client, Client

_client: Client | None = None

def get_supabase() -> Client:
    """Retorna cliente Supabase singleton."""
    global _client
    if _client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY")
        if not url or not key:
            raise RuntimeError(
                "SUPABASE_URL e SUPABASE_SERVICE_KEY devem estar no .env"
            )
        _client = create_client(url, key)
    return _client
```

### 2.4 `backend/db/student_model.py`

```python
"""
CRUD do Student Model no Supabase.
Implementa algoritmo SM-2 para repetição espaçada.
"""
import math
from datetime import datetime, timedelta, timezone
from uuid import UUID
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
    agents_output: dict
):
    """Salva log completo da sessão."""
    get_supabase().table("session_log").insert({
        "student_id": student_id,
        "question": question,
        "topic": topic,
        "model_used": model_used,
        "fallback": fallback,
        "agents_output": agents_output,
    }).execute()


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
```

### 2.5 `backend/schemas/request.py`

```python
from pydantic import BaseModel
from typing import Optional

class TutorRequest(BaseModel):
    question: str
    student_email: str = "anonimo@ufsm.br"
    student_name: str = "Aluno"
    model_name: str = "Gemini 3.0 Preview"
    image_base64: Optional[str] = None
    image_media_type: Optional[str] = None

class EvaluatorFeedback(BaseModel):
    student_email: str
    concept_id: str
    topic: str
    correct: bool
    quality: int = 3    # 0-5
```

### 2.6 `backend/schemas/response.py`

```python
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
```

### 2.7 `backend/routers/tutor.py`

```python
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
        result_state = state

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
```

### 2.8 `backend/routers/student.py`

```python
from fastapi import APIRouter
from backend.db.student_model import get_or_create_student, get_student_progress

router = APIRouter(prefix="/student", tags=["student"])

@router.get("/{email}/progress")
async def get_progress(email: str):
    student = get_or_create_student(email)
    return get_student_progress(student["id"])
```

### 2.9 `backend/main.py`

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from backend.routers import tutor, student

load_dotenv()

app = FastAPI(
    title="TutorIAFisica API",
    version="2026.2.0",
    description="Backend dos 5 agentes + Student Model (Supabase)"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.getenv("FRONTEND_URL", "http://localhost:3000"),
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tutor.router)
app.include_router(student.router)

@app.get("/health")
def health():
    return {"status": "ok", "version": "2026.2.0"}

@app.get("/models")
def list_models():
    from config import Config
    return {name: {"multimodal": info["multimodal"]}
            for name, info in Config.AVAILABLE_MODELS.items()}
```

### 2.10 `backend/Dockerfile`

```dockerfile
FROM python:3.11-slim
WORKDIR /app

COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY src/ ./src/
COPY data/ ./data/
COPY backend/ ./backend/

EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### ✓ Etapa 2 Completa?

Para verificar:
```bash
cd TutorIAFisica
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload
```

Você deve ver:
```
Uvicorn running on http://127.0.0.1:8000
```

Testes rápidos no navegador:
- GET `http://localhost:8000/health` → `{"status":"ok","version":"2026.2.0"}`
- GET `http://localhost:8000/models` → lista de modelos disponíveis

> ✅ Se ambos funcionam, backend está pronto

---

## 🟧 ETAPA 3 — Modificação em `src/core.py`

**Tempo:** ~20 min | **Pré-requisito:** Etapa 2 ✅ | **Output:** Método `process_streaming()` adicionado

### 3.1 — Regra de Ouro (repete)

⚠️ **ATENÇÃO:** Apenas **ADICIONAR** o método abaixo. Não edite nenhum método existente.

```python
# ADICIONAR dentro da classe PhysicsOrchestrator em src/core.py

def process_streaming(self, state, model_id=None, api_key=None):
    """
    Versão generator de process().
    Faz yield (agent_name, content) após cada agente.
    Permite SSE no backend FastAPI.
    """
    # ATENÇÃO: substituir pelos nomes reais dos métodos internos
    # que já existem no process(). Se process() for sequencial,
    # refatorar em métodos _run_* privados antes de usar este método.

    steps = [
        ("Intérprete",   "_run_interpreter"),
        ("Solucionador", "_run_solver"),
        ("Visualizador", "_run_visualizer"),
        ("Curador",      "_run_curator"),
        ("Avaliador",    "_run_evaluator"),
    ]
    for agent_name, method_name in steps:
        try:
            fn = getattr(self, method_name, None)
            if fn:
                result = fn(state, model_id=model_id, api_key=api_key)
            else:
                # fallback: chamar process() e extrair do state
                # (usar este fallback se os métodos não forem separados)
                result = f"[{agent_name}: método interno não encontrado]"
            yield (agent_name, result)
        except Exception as e:
            yield (agent_name, f"[Erro em {agent_name}: {str(e)}]")
```

> **INSTRUÇÃO PARA CLAUDE CODE:** Antes de implementar `process_streaming()`,
> ler o `process()` atual em `src/core.py` integralmente. Se o processo dos
> agentes estiver inline (não em métodos separados), refatorar primeiro:
> extrair cada bloco de agente para um método `_run_interpreter()`,
> `_run_solver()`, etc. — sem mudar comportamento, apenas organizar.
> Depois implementar `process_streaming()` usando esses métodos.

### ✓ Etapa 3 Completa?

```bash
# No VS Code, abra src/core.py
# Procure pela classe PhysicsOrchestrator
# Confirme que o método process_streaming() existe (novo método)
# Nenhum outro método deve ter sido modificado
```

---

## 🟪 ETAPA 4 — Frontend Next.js

**Tempo:** ~60 min | **Pré-requisito:** Etapa 0 ✅ | **Output:** Frontend em `frontend/` pronto para deploy

### 4.1 — Inicializar Next.js

```bash
npx create-next-app@latest frontend \
  --typescript --tailwind --eslint --app --src-dir \
  --import-alias "@/*" --no-git

cd frontend

npm install \
  react-markdown remark-math rehype-katex katex \
  react-syntax-highlighter @types/react-syntax-highlighter \
  plotly.js react-plotly.js @types/plotly.js \
  lucide-react
```

### 4.2 `frontend/.env.local`

```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=TutorIA Física — UFSM
```

### 4.3 `frontend/src/lib/api.ts`

```typescript
const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface AgentOutput {
  agent_name: string;
  color: string;
  dimension: string;
  content: string;
  source_tag?: string;
}

export interface TutorResponse {
  agents: AgentOutput[];
  used_model: string;
  fallback_occurred: boolean;
  visualization_code?: string;
  formative_challenge?: string;
  due_for_review: DueReview[];
}

export interface DueReview {
  concept_id: string;
  topic: string;
  mastery_level: number;
}

export interface TutorRequest {
  question: string;
  student_email?: string;
  student_name?: string;
  model_name?: string;
  image_base64?: string;
  image_media_type?: string;
}

export async function askTutorStream(
  req: TutorRequest,
  onAgent: (a: AgentOutput) => void,
  onDone: (due: DueReview[]) => void,
  onError: (e: string) => void
): Promise<void> {
  const res = await fetch(`${API}/tutor/ask/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!res.ok) { onError(await res.text()); return; }

  const reader = res.body!.getReader();
  const dec = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    for (const line of dec.decode(value).split("\n")) {
      if (!line.startsWith("data: ")) continue;
      const data = JSON.parse(line.slice(6));
      if (data.is_final) { onDone(data.due_for_review ?? []); break; }
      if (data.error) { onError(data.error); break; }
      onAgent(data as AgentOutput);
    }
  }
}

export async function getStudentProgress(email: string) {
  const res = await fetch(`${API}/student/${encodeURIComponent(email)}/progress`);
  return res.json();
}

export async function submitFeedback(
  studentEmail: string, conceptId: string,
  topic: string, correct: boolean, quality: number
) {
  await fetch(`${API}/tutor/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ student_email: studentEmail, concept_id: conceptId,
      topic, correct, quality }),
  });
}
```

### 4.4 `frontend/src/components/AgentPanel.tsx`

```typescript
"use client";
import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import "katex/dist/katex.min.css";
import { AgentOutput } from "@/lib/api";

const ICONS: Record<string, string> = {
  "Intérprete": "🔵", "Solucionador": "🟢",
  "Visualizador": "🟠", "Curador": "🟣", "Avaliador": "🔴",
};

export function AgentPanel({
  agent, streaming
}: { agent: AgentOutput; streaming?: boolean }) {
  return (
    <div className="rounded-xl border p-4 mb-3 bg-gray-900/80 backdrop-blur"
      style={{ borderColor: agent.color + "66" }}>
      <div className="flex items-center gap-2 mb-3">
        <span>{ICONS[agent.agent_name] ?? "🤖"}</span>
        <span className="font-semibold text-sm" style={{ color: agent.color }}>
          {agent.agent_name}
        </span>
        <span className="text-xs text-gray-500">— {agent.dimension}</span>
        {streaming && (
          <span className="ml-auto text-xs text-gray-500 animate-pulse">
            ✦ gerando...
          </span>
        )}
      </div>
      <div className="prose prose-invert prose-sm max-w-none text-gray-200">
        <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>
          {agent.content}
        </ReactMarkdown>
      </div>
    </div>
  );
}
```

### 4.5 `frontend/src/components/VoiceInput.tsx`

```typescript
"use client";
import { useState } from "react";
import { Mic, MicOff } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function VoiceInput({ onTranscript }: { onTranscript: (t: string) => void }) {
  const [rec, setRec] = useState(false);
  const [mr, setMr] = useState<MediaRecorder | null>(null);

  async function start() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const recorder = new MediaRecorder(stream);
    const chunks: BlobPart[] = [];
    recorder.ondataavailable = e => chunks.push(e.data);
    recorder.onstop = async () => {
      const blob = new Blob(chunks, { type: "audio/webm" });
      const fd = new FormData();
      fd.append("file", blob, "audio.webm");
      const res = await fetch(`${API}/tutor/transcribe`, { method: "POST", body: fd });
      const { text } = await res.json();
      onTranscript(text);
    };
    recorder.start();
    setMr(recorder);
    setRec(true);
  }

  return (
    <button onClick={rec ? () => { mr?.stop(); setRec(false); } : start}
      className={`p-3 rounded-xl border transition-all ${
        rec ? "bg-red-600 border-red-400 animate-pulse" : "bg-gray-800 border-gray-700 hover:border-blue-500"
      }`} title={rec ? "Parar" : "Falar"}>
      {rec ? <MicOff size={18} /> : <Mic size={18} />}
    </button>
  );
}
```

### 4.6 `frontend/src/components/ChatInterface.tsx`

```typescript
"use client";
import { useState } from "react";
import { AgentPanel } from "./AgentPanel";
import { VoiceInput } from "./VoiceInput";
import { askTutorStream, AgentOutput, DueReview } from "@/lib/api";

const MODELS = [
  "Gemini 3.0 Preview", "Gemini 2.0 Flash",
  "Claude 3 Sonnet", "GPT-3.5 Turbo", "DeepSeek Chat",
];

export function ChatInterface() {
  const [question, setQuestion] = useState("");
  const [agents, setAgents] = useState<AgentOutput[]>([]);
  const [loading, setLoading] = useState(false);
  const [streamingAgent, setStreamingAgent] = useState<string | null>(null);
  const [model, setModel] = useState(MODELS[0]);
  const [due, setDue] = useState<DueReview[]>([]);
  const [error, setError] = useState<string | null>(null);

  async function submit() {
    if (!question.trim() || loading) return;
    setLoading(true);
    setAgents([]);
    setError(null);

    await askTutorStream(
      { question, model_name: model, student_email: "aluno@ufsm.br" },
      (agent) => {
        setStreamingAgent(agent.agent_name);
        setAgents(prev => [...prev, agent]);
      },
      (dueList) => { setDue(dueList); setStreamingAgent(null); setLoading(false); },
      (err) => { setError(err); setLoading(false); }
    );
  }

  return (
    <div className="flex flex-col h-screen bg-gray-950 text-white">

      {/* Banner de revisões pendentes */}
      {due.length > 0 && (
        <div className="bg-blue-900/40 border-b border-blue-700 px-6 py-2 text-sm text-blue-200 flex gap-4 items-center">
          <span>📚 {due.length} conceito(s) para revisar:</span>
          {due.map(d => (
            <span key={d.concept_id} className="px-2 py-0.5 bg-blue-800 rounded-lg text-xs">
              {d.concept_id} ({Math.round(d.mastery_level * 100)}%)
            </span>
          ))}
        </div>
      )}

      {/* Respostas dos agentes */}
      <div className="flex-1 overflow-y-auto p-6 space-y-1">
        {agents.length === 0 && !loading && (
          <div className="flex items-center justify-center h-full text-gray-600 text-sm">
            Digite uma dúvida de física para começar ↓
          </div>
        )}
        {agents.map((a, i) => (
          <AgentPanel key={i} agent={a}
            streaming={streamingAgent === a.agent_name} />
        ))}
        {error && (
          <div className="text-red-400 text-sm p-4 bg-red-900/20 rounded-lg">
            ⚠️ {error}
          </div>
        )}
      </div>

      {/* Input */}
      <div className="border-t border-gray-800 p-4 bg-gray-950">
        <div className="flex gap-2 items-end max-w-4xl mx-auto">
          <textarea
            className="flex-1 bg-gray-900 rounded-xl p-3 text-sm resize-none
                       border border-gray-700 focus:border-blue-500 outline-none
                       placeholder-gray-600"
            rows={3}
            placeholder="Ex: Qual é a diferença entre massa e peso? Por que objetos caem com a mesma aceleração?"
            value={question}
            onChange={e => setQuestion(e.target.value)}
            onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); submit(); } }}
          />
          <div className="flex flex-col gap-2">
            <VoiceInput onTranscript={t => setQuestion(t)} />
            <button onClick={submit} disabled={loading || !question.trim()}
              className="px-5 py-3 rounded-xl bg-blue-600 hover:bg-blue-500
                         disabled:opacity-40 disabled:cursor-not-allowed
                         font-medium text-sm transition-colors whitespace-nowrap">
              {loading ? "⏳" : "Perguntar →"}
            </button>
          </div>
        </div>
        <div className="flex justify-center mt-2">
          <select value={model} onChange={e => setModel(e.target.value)}
            className="text-xs bg-gray-800 border border-gray-700 rounded-lg px-3 py-1 text-gray-400">
            {MODELS.map(m => <option key={m}>{m}</option>)}
          </select>
        </div>
      </div>
    </div>
  );
}
```

### 4.7 `frontend/src/app/page.tsx`

```typescript
import { ChatInterface } from "@/components/ChatInterface";
export default function Home() { return <ChatInterface />; }
```

### 4.8 `frontend/src/app/layout.tsx`

```typescript
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
const font = Inter({ subsets: ["latin"] });
export const metadata: Metadata = {
  title: "TutorIA Física — UFSM",
  description: "Mentor inteligente para ensino de física universitária",
};
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR" className="dark">
      <body className={`${font.className} bg-gray-950 text-white antialiased`}>
        {children}
      </body>
    </html>
  );
}
```

### ✓ Etapa 4 Completa?

```bash
cd frontend
npm run dev
```

Você deve ver:
```
▲ Next.js 15.0.0
- Local:        http://localhost:3000
```

Teste no navegador:
- Abra http://localhost:3000
- Você verá a interface de chat
- Clique no botão de voz (deve pedir permissão)

> ✅ Se a interface aparecer, frontend está pronto

---

## 🔴 ETAPA 5 — Deploy em Produção

**Tempo:** ~20 min | **Pré-requisito:** Etapa 2 + 4 ✅ | **Output:** App ao vivo em produção

### 5.1 — Configurar `render.yaml` (deploy backend)

Na **raiz do repositório**, criar `render.yaml`:

### `render.yaml` (na raiz)

```yaml
services:
  - type: web
    name: tutor-ia-fisica-api
    runtime: docker
    dockerfilePath: ./backend/Dockerfile
    dockerContext: .
    plan: free
    envVars:
      - key: SUPABASE_URL
        sync: false          # preencher no dashboard do Render
      - key: SUPABASE_SERVICE_KEY
        sync: false
      - key: FRONTEND_URL
        value: https://tutor-ia-fisica.pages.dev
      - key: GEMINI_API_KEY
        sync: false
      - key: OPENAI_API_KEY
        sync: false
      - key: ANTHROPIC_API_KEY
        sync: false
    healthCheckPath: /health
    autoDeploy: true
```

### 5.2 — Ativar Deploy Automático no Render

1. Acesse https://render.com/dashboard
2. Clique **"New"** → **"Blueprint"**
3. Selecione repositório `TutorIAFisica`
4. Render vai detectar `render.yaml` automaticamente
5. Preencher variáveis de ambiente (clicar cada uma):
   - `SUPABASE_URL` → colar valor do .env
   - `SUPABASE_SERVICE_KEY` → colar valor do .env
   - `FRONTEND_URL` → `https://tutor-ia-fisica.pages.dev`
   - `GEMINI_API_KEY`, `OPENAI_API_KEY`, etc. → colar chaves existentes
6. Clique **"Deploy"**

Você verá:
```
Services building... (2-3 minutos)
✓ tutor-ia-fisica-api deployed
```

Anote a URL gerada: `https://tutor-ia-fisica-api.onrender.com`

### 5.3 — Ativar Deploy Automático no Cloudflare Pages

1. Acesse https://pages.cloudflare.com/
2. Clique **"Create a project"** → **"Connect to Git"**
3. Selecione `TutorIAFisica`
4. Preencher build settings:
   - **Framework preset:** Next.js
   - **Build command:** `cd frontend && npm install && npm run build`
   - **Build output directory:** `frontend/.next`
   - **Root directory:** (deixar vazio ou `/`)
5. Adicionar variável de ambiente:
   - **NEXT_PUBLIC_API_URL** = `https://tutor-ia-fisica-api.onrender.com`
6. Clique **"Save and Deploy"**

Você verá:
```
✓ Deployment successful
Your site is now live at: https://tutor-ia-fisica.pages.dev
```

### 5.4 — Verificar `.gitignore`

Confirmar que `.gitignore` contém:
```gitignore
.env
.env.local
frontend/.env.local
frontend/node_modules/
frontend/.next/
__pycache__/
*.pyc
venv/
data/students/
```

> ⚠️ **IMPORTANTE:** `.env` nunca deve ir para Git (contém chaves API)

### ✓ Etapa 5 Completa?

- [ ] Backend ao vivo em Render (GET /health retorna 200)
- [ ] Frontend ao vivo em Cloudflare Pages (página abre)
- [ ] Fazer uma pergunta no app de produção
- [ ] Confirmar que 5 agentes aparecem

👉 **Próximo:** Etapa 6 (local dev, opcional)

---

## 🔵 ETAPA 6 — Desenvolvimento Local Completo (Opcional)

**Tempo:** ~15 min | **Pré-requisito:** Etapa 2 + 4 ✅ | **Output:** Docker Compose setup para dev local

### 6.1 — Usar Docker (recomendado)

### 6.2 — Com Docker Compose

Criar `docker-compose.yml` na raiz:

### `docker-compose.yml`

```yaml
version: "3.9"
services:
  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile
    ports:
      - "8000:8000"
    env_file: .env
    volumes:
      - ./src:/app/src
      - ./data:/app/data
      - ./backend:/app/backend
    environment:
      FRONTEND_URL: http://localhost:3000

  frontend:
    image: node:20-alpine
    working_dir: /app
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
    command: sh -c "npm install && npm run dev"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    depends_on:
      - backend
```

### 6.3 — Rodar Localmente

#### Opção A: Com Docker (recomendado)

```bash
# Na raiz do repositório
docker-compose up

# Você verá:
# backend_1   | Uvicorn running on http://0.0.0.0:8000
# frontend_1  | ▲ Next.js running on http://localhost:3000
```

#### Opção B: Sem Docker (dois terminais)

**Terminal 1 — Backend:**
```bash
cd TutorIAFisica
source venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd TutorIAFisica/frontend
npm install
npm run dev
```

### ✓ Etapa 6 Completa?

- [ ] Arquivo `docker-compose.yml` criado na raiz
- [ ] Backend rodando em `http://localhost:8000` (com ou sem Docker)
- [ ] Frontend rodando em `http://localhost:3000`
- [ ] Conseguir fazer uma pergunta no chat e ver 5 agentes progressivamente

---

## 🆘 Troubleshooting — Quando Algo Dá Errado

### Erro: "SUPABASE_URL não definida"

```
RuntimeError: SUPABASE_URL e SUPABASE_SERVICE_KEY devem estar no .env
```

**Solução:**
1. Confirme que `.env` existe na raiz do repositório (não em `backend/`)
2. Confirme que contém `SUPABASE_URL=...` e `SUPABASE_SERVICE_KEY=...`
3. Reinicie o servidor: `Ctrl+C` → `uvicorn backend.main:app --reload`

---

### Erro: "Connection refused" ao chamar API

```
Error: fetch failed: connection refused (127.0.0.1:8000)
```

**Solução:**
1. Confirme backend está rodando: `uvicorn backend.main:app --reload`
2. Confirme porta correta: `http://localhost:8000/health` deve responder
3. No frontend `.env.local`, confirme `NEXT_PUBLIC_API_URL=http://localhost:8000`

---

### Erro: "pgvector extension not found"

```sql
ERROR: extension "vector" does not exist
```

**Solução:**
1. Supabase já habilita automaticamente. Se você vê esse erro:
2. Vá para **SQL Editor** → **Extensions** (menu esquerdo)
3. Procure `vector` e clique "Enable"
4. Execute o SQL novamente

---

### Erro: "Render build fails"

```
Building... FAILED
```

**Solução:**
1. Verificar logs no Render dashboard:
   - Clique no serviço `tutor-ia-fisica-api`
   - Vá para **Logs** (botão superior direito)
   - Procure pela mensagem de erro
2. Erros comuns:
   - **"requirements.txt not found"** → Confirmar `backend/requirements.txt` está commitado
   - **"Port already in use"** → Mudar em `backend/main.py` de 8000 para 8001
   - **"Missing dependencies"** → Adicionar em `backend/requirements.txt` e fazer `git push`

---

### Erro: "Frontend não consegue conectar ao backend"

```
Failed to fetch /tutor/ask
```

**Solução:**
1. Backend está online? Testar em `https://tutor-ia-fisica-api.onrender.com/health`
2. CORS está ativo? Em `backend/main.py`, confirmar que `FRONTEND_URL` está na lista de `allow_origins`
3. `NEXT_PUBLIC_API_URL` correto em Cloudflare Pages? Deve ser URL de produção do Render, não localhost

---

### Erro: "Supabase free pausado"

```
Cannot connect to database
```

**Solução:**
1. Este é o problema da Etapa 0.3!
2. Você esqueceu de configurar o cron job em cron-job.org
3. Configurar agora: https://cron-job.org → New Cronjob → URL Supabase
4. Supabase volta em ~5 minutos

---

### Dúvida: "Quanto tempo demora a primeira resposta?"

```
Aguardando 30-50 segundos...
```

**Explicação:** Render Free tier "dorme" se não usar por 15 min. Primeira requisição sempre demora ~30s (cold start). Requisições subsequentes são rápidas.

**Solução:** Mostrar mensagem no frontend: "Acordando o servidor... ⏳ Primeira resposta pode demorar 30s"

---

## 🎯 ORDEM DE EXECUÇÃO — Passo a Passo

### Se você é iniciante:
1. **Etapa 0** (15 min): Criar contas e `.env`
2. **Etapa 1** (10 min): Schema SQL
3. **Etapa 2** (90 min): Backend FastAPI
4. **Etapa 3** (20 min): Adicionar `process_streaming()`
5. **Etapa 4** (60 min): Frontend Next.js
6. **Etapa 5** (20 min): Deploy produção
7. **Etapa 6** (15 min): Local dev (opcional)

**Total:** ~4-5 horas

### Se você só quer dev local:
1. **Etapa 0** (15 min): Criar `.env` com variáveis (dummy é ok)
2. **Etapa 1** (10 min): Schema SQL
3. **Etapa 2** (90 min): Backend
4. **Etapa 3** (20 min): Modificação core.py
5. **Etapa 4** (60 min): Frontend
6. **Etapa 6** (15 min): Docker Compose

**Total:** ~3.5 horas | **Resultado:** Rodando em localhost

### Se você já tem backend e quer só frontend:
1. **Etapa 0** (5 min): Confirmar `.env`
2. **Etapa 4** (60 min): Frontend
3. **Etapa 5.3** (10 min): Deploy frontend

**Total:** ~1.5 horas

---

## ✅ CHECKLIST FINAL

### Infra & Setup
- [ ] **Etapa 0:** Contas criadas (Supabase, Render, Cloudflare)
- [ ] **Etapa 0:** `.env` preparado com 3 chaves Supabase
- [ ] **Etapa 0:** Cron job ativo em cron-job.org

### Backend (Python)
- [ ] **Etapa 1:** SQL schema executado no Supabase (4 tabelas visíveis)
- [ ] **Etapa 2:** Todos os arquivos criados (`backend/main.py`, `routers/`, `schemas/`, `db/`)
- [ ] **Etapa 2:** `pip install -r backend/requirements.txt` funciona sem erros
- [ ] **Etapa 2:** `GET /health` retorna `{"status":"ok"}`
- [ ] **Etapa 2:** `GET /models` lista modelos disponíveis
- [ ] **Etapa 3:** `process_streaming()` adicionado em `src/core.py` (sem tocar em nada)

### Frontend (TypeScript/React)
- [ ] **Etapa 4:** Next.js inicializado em `frontend/`
- [ ] **Etapa 4:** Todos os componentes criados (`ChatInterface.tsx`, `AgentPanel.tsx`, etc.)
- [ ] **Etapa 4:** `npm run dev` funciona em http://localhost:3000
- [ ] **Etapa 4:** Interface apareça no navegador

### Integração Local
- [ ] **Integração:** Post `/tutor/ask` retorna 5 agentes
- [ ] **Integração:** Sessão aparece no Supabase dashboard
- [ ] **Integração:** Frontend conecta ao backend e exibe agentes

### Deploy em Produção
- [ ] **Etapa 5:** `render.yaml` criado na raiz
- [ ] **Etapa 5:** Render.com: blueprint conectado e build bem-sucedido
- [ ] **Etapa 5:** Cloudflare Pages: projeto conectado e site ao vivo
- [ ] **Etapa 5:** App de produção funciona end-to-end

### Documentação & Cleanup
- [ ] **Etapa 6:** `docker-compose.yml` criado (opcional, mas recomendado)
- [ ] **Final:** `.gitignore` inclui `.env`, `node_modules/`, etc.
- [ ] **Final:** CLAUDE.md atualizado com nova arquitetura (FastAPI + Next.js + Supabase)

---

## 🔐 Variáveis de Ambiente — Referência Completa

### Arquivo: `.env` (raiz do projeto)

⚠️ **NUNCA commitar este arquivo** — contém chaves API secretas

```bash
# SUPABASE (obter em https://supabase.com/dashboard/project/xxx/settings/api)
SUPABASE_URL=https://xxxxxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# DEPLOY
FRONTEND_URL=https://tutor-ia-fisica.pages.dev

# LLM KEYS (copiadas do .env anterior, não mudar)
GEMINI_API_KEY=AIza...
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DEEPSEEK_API_KEY=...
GROK_API_KEY=...
# ... demais chaves já existentes
```

### Arquivo: `frontend/.env.local`

⚠️ **NUNCA commitar este arquivo** — pode conter URLs sensíveis em dev

```bash
# EM DESENVOLVIMENTO (localhost)
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=TutorIA Física — UFSM

# EM PRODUÇÃO (Render)
NEXT_PUBLIC_API_URL=https://tutor-ia-fisica-api.onrender.com
NEXT_PUBLIC_APP_NAME=TutorIA Física — UFSM
```

### Arquivo: `render.yaml` (raiz)

Usado apenas para deploy automático — definir variáveis no dashboard do Render:
- `SUPABASE_URL` → colar do `.env`
- `SUPABASE_SERVICE_KEY` → colar do `.env`
- `FRONTEND_URL` → `https://tutor-ia-fisica.pages.dev`
- `GEMINI_API_KEY`, `OPENAI_API_KEY`, etc. → colar do `.env`

### Checklist de Variáveis

| Variável | Localização | Obrigatória? | Valor de Exemplo |
|----------|-------------|---------|---|
| `SUPABASE_URL` | `.env` | ✅ SIM | `https://xxxx.supabase.co` |
| `SUPABASE_SERVICE_KEY` | `.env` | ✅ SIM | `eyJ...` (tipo JWT) |
| `SUPABASE_ANON_KEY` | `.env` | ⚠️ Opcional | `eyJ...` (tipo JWT) |
| `FRONTEND_URL` | `.env` + `render.yaml` | ✅ SIM | `https://tutor-ia-fisica.pages.dev` |
| `GEMINI_API_KEY` | `.env` | ⚠️ Opcional | `AIza...` |
| `OPENAI_API_KEY` | `.env` | ⚠️ Opcional | `sk-...` |
| `ANTHROPIC_API_KEY` | `.env` | ⚠️ Opcional | `sk-ant-...` |
| `NEXT_PUBLIC_API_URL` | `frontend/.env.local` | ✅ SIM | `http://localhost:8000` (dev) ou `https://render.onrender.com` (prod) |
| `NEXT_PUBLIC_APP_NAME` | `frontend/.env.local` | ⚠️ Opcional | `TutorIA Física — UFSM` |

---

## ⚠️ AVISOS IMPORTANTES — Leia Antes de Deploy

### 🔴 CRÍTICO: Supabase Free pausa após 7 dias sem atividade

**Problema:**  
Seu banco de dados será pausado automaticamente se não tiver requisições por 7 dias. Você perde acesso até reativar.

**Solução:**  
Configurar cron job gratuito em https://cron-job.org (OBRIGATÓRIO):
1. **Title:** `Supabase Keep-Alive`
2. **URL:** `https://XXXX.supabase.co/rest/v1/students?limit=1` (substitua XXXX)
3. **HTTP Header:** `apikey: SUA_ANON_KEY` (copiado do .env)
4. **Frequency:** `Every 5 days at noon UTC`
5. Clique "Save" e confirme que aparece "Status: OK"

> 💡 **Dica:** Fazer isso logo em Etapa 0, não espere até o final

---

### 🟡 AVISO: Render.com free tier "dorme" após 15 min sem uso

**Problema:**  
Primeira requisição após inatividade demora ~30-50 segundos (cold start).

**Experiência do usuário:**  
```
Frontend → aguarda resposta lenta → app parece "travado" → usuário sai frustrado
```

**Solução (frontend):**  
Mostrar spinner com mensagem: `"🔄 Acordando servidor... isso pode demorar até 30s"`

```typescript
// Em ChatInterface.tsx, ao enviar pergunta:
if (firstRequest) {
  setStatus("⏳ Primeiro acesso — acordando o servidor... (pode demorar 30s)");
}
```

**Solução (backend):**  
Implementar timeout de 45s nas requisições:
```python
# Em backend/main.py
@app.middleware("http")
async def timeout_middleware(request, call_next):
    try:
        return await asyncio.wait_for(call_next(request), timeout=45)
    except asyncio.TimeoutError:
        return JSONResponse({"error": "Timeout"}, status_code=504)
```

---

### 🔐 CRÍTICO: Segurança — Nunca Expor Chaves no Frontend

**❌ NUNCA:**
- Incluir `SUPABASE_SERVICE_KEY` em `.js`/`.ts` do frontend (acesso admin total)
- Expor chaves LLM (`OPENAI_API_KEY`, etc.) no cliente (roubo de créditos)
- Hardcod ar `API_KEY` em commits do Git

**✅ SEMPRE:**
- Ler chaves somente do `.env` (ou variáveis de ambiente do servidor)
- Passar chaves apenas via backend → frontend via endpoints auth
- Usar `SUPABASE_ANON_KEY` se precisar auth no frontend (acesso restrito por RLS)

**Verificação:**
```bash
# Procure no código-fonte por padrões perigosos:
grep -r "SUPABASE_SERVICE_KEY" src/
grep -r "OPENAI_API_KEY" frontend/
grep -r "sk-" .
```

---

### 📍 AVISO: URLs de Deploy Hardcoded

**Problema:**  
Desenvolvedores frequentemente hardcodam `http://localhost:8000` no frontend.

**Solução:**  
Usar sempre `.env`:
```typescript
// ✅ CORRETO
const API_URL = process.env.NEXT_PUBLIC_API_URL;

// ❌ ERRADO
const API_URL = "http://localhost:8000";
```

Configurar em:
- **Dev:** `.env.local` → `NEXT_PUBLIC_API_URL=http://localhost:8000`
- **Prod:** Cloudflare dashboard → `NEXT_PUBLIC_API_URL=https://tutor-ia-fisica-api.onrender.com`

---

### 🚨 GOTCHA: CORS Errors em Produção

**Problema:**  
```
Access to XMLHttpRequest at 'https://api.render.com' from 'https://pages.cloudflare.com'
has been blocked by CORS policy
```

**Causa:**  
`FRONTEND_URL` em `.env`/`render.yaml` não bate com URL real do Cloudflare Pages.

**Solução:**  
1. Confirmar URL do Cloudflare Pages (ex: `https://tutor-ia-fisica.pages.dev`)
2. Adicionar em `backend/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.getenv("FRONTEND_URL"),  # ← deve bater com URL de produção
        "http://localhost:3000",     # ← para dev local
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### 📊 NOTA: Performance — Streaming de Agentes

Implementamos `process_streaming()` para enviar agentes progressivamente em vez de esperar pelos 5.

**Ganho de UX:**
- Sem streaming: usuário espera 30-45s por tudo
- Com streaming: vê resultado do Intérprete em 5s, depois Solucionador, etc.

Se o frontend não mostra agentes progressivamente, verifique:
1. Endpoint `/tutor/ask/stream` está ativo em `backend/routers/tutor.py`?
2. Frontend está escutando SSE (`EventSource` ou `fetch` com streaming)?
3. Algum middleware está buffering a resposta?

---

## 🎯 Próximos Passos Após Deploy

1. **Monitorar:** Acessar Render/Supabase dashboards regularmente
2. **Testar:** Fazer uma pergunta por semana para manter Supabase ativo
3. **Iterar:** Adicionar features (voice, misconception detection, etc.) via backend + frontend
4. **Migrar:** Quando pronto, considerar upgrade para tier pago (Render Pro: $12/mês, Supabase Pro: $25/mês)
