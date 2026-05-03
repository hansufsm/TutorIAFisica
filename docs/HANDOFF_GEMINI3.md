# Handoff — TutorIA Física UFSM
**Para:** Gemini 3 (ou próximo agente de desenvolvimento)  
**Data:** 2026-05-03  
**Branch ativa:** `claude/investigate-api-slowness-7lFm3`  
**Status:** Pronto para merge em `main` após validação do build

---

## O que é este projeto

**TutorIA Física** é um tutor de física universitária (UFSM) com 5 agentes de IA orquestrados:

| Agente | Cor | Papel |
|---|---|---|
| Intérprete | 🔵 Azul | Análise socrática — faz perguntas antes de resolver |
| Solucionador | 🟢 Verde | Resolução matemática com LaTeX e unidades SI |
| Visualizador | 🟠 Laranja | Código Python (Matplotlib/Plotly) auto-contido |
| Curador | 🟣 Roxo | Referências acadêmicas (UFSM → arXiv) |
| Avaliador | 🔴 Vermelho | Quiz socrático com SM-2 (espaçamento de repetição) |

**Stack:**
- Frontend: Next.js 14 (App Router) + Tailwind + Supabase Auth → Vercel
- Backend: FastAPI + LiteLLM + SSE streaming → Render.com
- DB: Supabase (PostgreSQL + pgvector + RLS)

---

## Estado atual do branch (commits não mergeados)

```
cdaf3eb  ui: painel de curiosidades depois da lista de fontes
0de2873  fix(print): PDF exportando + números ordinais nos agentes
12df707  feat: export liberado para visitantes
cd986b8  fix(sidebar): botão login visível com sidebar colapsada
fbe967d  fix(auth): detectar placeholder Supabase + mensagem PT-BR
075bc01  docs: DEVLOG + memory summary
a2b5674  feat: StudyNoteModal — apostila acumulada PDF + Markdown
2b27338  feat(sprint-4): Curriculum-aware + cron email SM-2
e1b8eb3  feat(sprint-3): Long-term RAG pgvector
7216b83  feat(sprint-2): Caderno Vivo + Knowledge Map
2eb43a8  feat(sprint-1): Supabase Auth Magic Link + SM-2 feedback
```

---

## Arquitetura — mapa de arquivos críticos

```
frontend/
  app/
    page.tsx                     — root, monta ChatInterface
    layout.tsx                   — AuthProvider wrapping
    login/page.tsx               — magic link login
    auth/callback/route.ts       — redirect após magic link
    portfolio/page.tsx           — caderno do aluno (Sprint 2)
    globals.css                  — design tokens + @media print
  components/
    ChatInterface.tsx            — componente principal (1000+ linhas)
    AgentPanel.tsx               — render de cada agente (ReactMarkdown+KaTeX)
    StudyNoteModal.tsx           — modal apostila PDF (NOVO)
    VoiceInput.tsx               — transcrição Whisper
  context/
    AuthContext.tsx              — Supabase Auth + signInWithMagicLink
  lib/
    api.ts                       — cliente SSE, tipos TypeScript
    supabase.ts                  — createBrowserClient

backend/
  main.py                        — FastAPI app + CORS
  routers/tutor.py               — GET /tutor/ask/stream (SSE)
  db/
    student_model.py             — SM-2 algorithm
    supabase_client.py           — conexão Supabase

src/
  core.py                        — PhysicsOrchestrator + 5 agentes + streaming
  config.py                      — AVAILABLE_MODELS, fallback order
  app.py                         — Streamlit UI (offline / Modo Referência)

data/
  ufsm_syllabus.json             — syllabus UFSM com campo `week` por tópico
```

---

## Funcionalidades implementadas (o que JÁ funciona)

### Auth
- Magic Link via Supabase Auth (`AuthContext.tsx:signInWithMagicLink`)
- Modo visitante — app funciona sem login; SM-2 e progresso não são salvos
- Sidebar: ícone LogIn quando colapsada + CTA "Entrar" quando expandida
- Erro de fetch no login exibe mensagem clara se Supabase não configurado

### Chat e streaming
- SSE token-by-token (`GET /tutor/ask/stream`)
- Agentes Fase 1 (Intérprete) → Fase 2 (Solver+Viz+Curator paralelos) → Fase 3 (Avaliador)
- Quick Mode ⚡ — só Intérprete + Solucionador (~15s)
- Cancelar e Trocar modelo mid-stream
- Timer calibrado por localStorage (mediana das últimas 10 respostas)
- Curiosidades de física rotacionam a cada 8s durante loading (APÓS lista de fontes)

### Export — Apostila de Estudos
- `.md` com YAML frontmatter completo (Obsidian-compatible):
  `title, date, student, session_id, model, response_time_s, week, discipline, topic, tags`
- `PDF` via `StudyNoteModal`:
  - Capa: badges disciplina/tópico/semana, pergunta, metadata
  - 5 seções com borda colorida por agente + número ordinal (`01.`, `02.`…)
  - Barras de progresso SM-2 por conceito
  - Temas semanais UFSM com status
  - Print CSS: `visibility:hidden` no body, `visibility:visible` no modal
- Export liberado para visitantes (sem login obrigatório)

### SM-2 (Espaçamento de Repetição)
- Algoritmo completo em `backend/db/student_model.py`
- `POST /tutor/feedback` ativado pelo frontend quando aluno responde quiz do Avaliador
- `due_for_review` retornado no SSE stream → exibido na UI

### Curriculum-aware (Sprint 4)
- `data/ufsm_syllabus.json` com campo `week` (1–15) por tópico
- `GET /tutor/weekly` retorna temas da semana atual do semestre
- Sidebar exibe "📅 Semana N do semestre" com disciplinas e temas
- Cron email SM-2: Supabase Edge Function dispara email quando conceitos vencem

### Long-term RAG (Sprint 3)
- Embeddings 1536-dim de sessões anteriores em `concept_status.embedding` (pgvector)
- Top-3 sessões similares injetadas no contexto do Intérprete

### Caderno Vivo + Knowledge Map (Sprint 2)
- Página `/portfolio` — histórico cronológico de sessões por tópico
- Knowledge Map: grafo de conceitos UFSM colorido por mastery

---

## O que AINDA NÃO funciona / próximas prioridades

### 🔴 Bloqueador imediato — Supabase não configurado no Vercel
**Problema:** `NEXT_PUBLIC_SUPABASE_URL` e `NEXT_PUBLIC_SUPABASE_ANON_KEY` têm valores placeholder no `.env.local` do repo. No Vercel Dashboard essas variáveis precisam ser configuradas com os valores reais.

**Onde pegar os valores:**
1. supabase.com → seu projeto → Settings → API
2. `Project URL` → `NEXT_PUBLIC_SUPABASE_URL`
3. `anon public key` → `NEXT_PUBLIC_SUPABASE_ANON_KEY`

**Onde adicionar:**
Vercel Dashboard → projeto tutoriafisica → Settings → Environment Variables → Production + Preview

**Variáveis do backend (Render.com):**
```
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=ey...  (service_role key, não anon)
GEMINI_API_KEY=...
OPENAI_API_KEY=...
```

### 🟡 Merge pendente
Branch `claude/investigate-api-slowness-7lFm3` → `main` após:
- [ ] `npm run build` sem erros de tipo no frontend
- [ ] Testar impressão PDF com equações LaTeX no Chrome e Safari
- [ ] Confirmar que Supabase vars estão no Vercel

### 🟢 Features sugeridas para próxima sessão

#### 1. Visualizador 2.0 — Simulações interativas embedded
Em vez de código Python estático, gerar HTML/JS auto-contido:
- Three.js para mecânica 3D (projéteis, forças)
- P5.js para ondas e oscilações
- Plotly com sliders para gráficos interativos
- Iframe sandboxed no Next.js — aluno arrasta sliders ao vivo

**Arquivo a modificar:** `src/core.py` (Visualizador `system_instruction`) + `frontend/components/AgentPanel.tsx` (render do iframe)

#### 2. Sessões Guiadas (`/sessao-guiada/{topico}`)
Scaffolding pedagógico fixo por tópico:
intro → exemplo resolvido → problema com hints → problema autônomo → quiz SM-2
~15 min, foco em uma única ideia, sem Q&A livre

#### 3. Mock Exam Generator
5 questões priorizando `mastery_level < 0.5` em `concept_status`.
Endpoint `POST /tutor/mock-exam` + página `/prova` no Next.js.

#### 4. TTS — Voz de saída
Já temos Whisper (voz de entrada via `VoiceInput.tsx`).
Adicionar TTS (OpenAI ou ElevenLabs) para ler resposta em voz alta.
Modo "fone de ouvido" para revisar enquanto caminha.

---

## Padrões e convenções a manter

### Agentes — cores obrigatórias (já usadas em 3 lugares)
```
Intérprete:   border #3B82F6  bg #EFF6FF  badge bg-indigo-100  text-indigo-700
Solucionador: border #22C55E  bg #F0FDF4  badge bg-green-100   text-green-700
Visualizador: border #F97316  bg #FFF7ED  badge bg-orange-100  text-orange-700
Curador:      border #A855F7  bg #FAF5FF  badge bg-purple-100  text-purple-700
Avaliador:    border #EF4444  bg #FFF1F2  badge bg-red-100     text-red-700
```
Estas cores aparecem em: `AgentPanel.tsx`, `StudyNoteModal.tsx`, `ChatInterface.tsx:AGENT_COLORS`. Qualquer novo componente que exiba agentes deve usar as mesmas.

### Hierarquia de fontes — citação inline
```
[Material do Professor]      ← pCloud (nível 1)
[Documento da Disciplina]    ← slides/livro adotado (nível 2)
[Ementa UFSM]               ← ufsm_syllabus.json (nível 3)
[Portal Acadêmico]           ← .edu.br (nível 4)
[Referência Internacional]   ← arXiv/Semantic Scholar (nível 5)
[Modelo de IA]               ← fallback sem fonte (nível 5)
```

### LaTeX
- Inline: `$F = ma$`
- Display: `$$\vec{F} = m\vec{a}$$`
- Unidades: `$v = 30\,\text{m/s}$`
- Análise dimensional explícita antes da substituição numérica

### Print CSS
Usar sempre `visibility:hidden`/`visible`, nunca `display:none` para esconder elementos e revelar um subelemento. `display:none` no pai bloqueia toda a subárvore.

---

## Comandos úteis

```bash
# Frontend dev
cd frontend && npm run dev          # http://localhost:3000
cd frontend && npm run build        # verifica tipos + build

# Backend dev
source venv/bin/activate
cd backend && python main.py        # http://localhost:8000

# Streamlit (offline / Modo Referência)
source venv/bin/activate
cd src && streamlit run app.py      # http://localhost:8501

# Testes
source venv/bin/activate
pytest test_*.py -v
```

---

## Variáveis de ambiente necessárias

**`.env` na raiz (backend + Streamlit):**
```
GEMINI_API_KEY=
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
DEEPSEEK_API_KEY=
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=ey...  (service_role)
```

**`frontend/.env.local` (Next.js dev):**
```
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=ey...  (anon public)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Vercel Dashboard (produção):**
```
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=ey...
NEXT_PUBLIC_API_URL=https://tutor-ia-fisica-api.onrender.com
```
