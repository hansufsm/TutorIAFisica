# TutorIAFisica — Controle de Projeto

> Documento de rastreamento: o que foi previsto, o que foi feito, quando e por quê.  
> Atualizar sempre que uma etapa mudar de estado.

---

## Legenda de Status

| Símbolo | Significado |
|---|---|
| ✅ | Completo — funcionando em produção |
| 🟡 | Parcial — implementado mas com ressalvas |
| ⏳ | Pendente — previsto, não iniciado |
| ❌ | Bloqueado ou descartado |
| ⚡ | Não previsto no roadmap original — surgiu durante o desenvolvimento |

---

## Stack Atual em Produção

```
Aluno → Cloudflare Workers (Next.js)
           ↓ HTTPS + SSE streaming
         Render.com (FastAPI + Python)
           ↓ supabase-py
         Supabase (PostgreSQL + pgvector)
```

**URLs de Produção:**
- **Frontend:** https://tutoriafisica.hans-059.workers.dev/
- **Backend:** https://tutor-ia-fisica-api.onrender.com
- **Health check:** https://tutor-ia-fisica-api.onrender.com/health

---

## Etapas do Roadmap (STACK_FUTURO.md)

### ✅ Etapa 0 — Contas e Serviços
**Status:** Completo  
**Data:** 2026-04-27  
**Commits:** `cffc841` (documentação), `0803ae1` (infra config files)

| Item | Status |
|---|---|
| Supabase criado (região SP) | ✅ |
| Render.com conta + GitHub conectado | ✅ |
| Cloudflare conta configurada | ✅ |
| `.env` preparado com chaves Supabase | ✅ |
| Cron job keep-alive (cron-job.org) | ⏳ **PENDENTE** |

> ⚠️ **Ação necessária:** Configurar cron job em https://cron-job.org para manter Supabase ativo.  
> URL: `https://[supabase-id].supabase.co/rest/v1/students?limit=1`  
> Frequência: A cada 5 dias ao meio-dia UTC

---

### ✅ Etapa 1 — Schema do Supabase
**Status:** Completo  
**Data:** 2026-04-27  
**Commit:** `0803ae1`  
**Arquivo:** `supabase/migrations/001_initial_schema.sql`

| Tabela | Status |
|---|---|
| `students` — perfis dos alunos | ✅ |
| `concept_status` — SM-2 por conceito | ✅ |
| `misconceptions` — gaps detectados | ✅ |
| `session_log` — histórico de sessões | ✅ |
| pgvector extension | ✅ |
| RLS policies ativas | ✅ |
| Índices de performance | ✅ |

---

### ✅ Etapa 2 — Backend FastAPI
**Status:** Completo e em produção  
**Data:** 2026-04-27  
**Commits:** `8c2f58f` (implementação), `6f796a8` (fix field mappings), `2b2ee07`, `e423706` (CORS fixes)  
**URL:** https://tutor-ia-fisica-api.onrender.com

| Arquivo | Status |
|---|---|
| `backend/main.py` | ✅ |
| `backend/requirements.txt` | ✅ |
| `backend/Dockerfile` | ✅ |
| `backend/routers/tutor.py` | ✅ |
| `backend/routers/student.py` | ✅ |
| `backend/schemas/request.py` | ✅ |
| `backend/schemas/response.py` | ✅ |
| `backend/db/supabase_client.py` | ✅ |
| `backend/db/student_model.py` | ✅ |
| `GET /health` respondendo | ✅ |
| `GET /models` respondendo | ✅ |
| `POST /tutor/ask` (sync) | ✅ |
| `POST /tutor/ask/stream` (SSE) | ✅ |
| `POST /tutor/feedback` | ✅ |
| Deploy automático no Render | ✅ |
| `render.yaml` na raiz | ✅ |

**Desvios do planejado:**
- CORS: configurado com `allow_origins=["*"]` em vez de whitelist específica (solução pragmática após problemas com CORS em produção)
- OPTIONS handler explícito adicionado para preflight requests
- `visualization_code` e `formative_challenge` removidos do TutorResponse (campos não existiam no PhysicsState real)

---

### ✅ Etapa 3 — `process_streaming()` em `src/core.py`
**Status:** Completo  
**Data:** 2026-04-27  
**Commit:** `8c2f58f`

| Item | Status |
|---|---|
| Método `process_streaming()` implementado | ✅ |
| Faz yield `(agent_name, content)` progressivamente | ✅ |
| Usado pelo endpoint `/tutor/ask/stream` | ✅ |
| Fallback para `process()` se streaming não disponível | ✅ |
| Métodos existentes intactos (Regra de Ouro respeitada) | ✅ |

---

### 🟡 Etapa 4 — Frontend Next.js
**Status:** Parcial — estrutura criada, componentes simplificados  
**Data:** 2026-04-27  
**Commits:** `3004730`, `26b341b`, `2b5cd38`

| Item | Previsto no STACK_FUTURO | Status atual |
|---|---|---|
| Next.js inicializado em `frontend/` | ✅ | ✅ |
| `frontend/src/app/page.tsx` | ✅ | ✅ |
| `frontend/src/app/layout.tsx` | ✅ | ✅ |
| `frontend/src/lib/api.ts` | ✅ | ⏳ **PENDENTE** |
| `frontend/src/components/ChatInterface.tsx` | ✅ | ⏳ **PENDENTE** |
| `frontend/src/components/AgentPanel.tsx` | ✅ | ⏳ **PENDENTE** |
| `frontend/src/components/VoiceInput.tsx` | ✅ | ⏳ **PENDENTE** |
| `frontend/src/components/ProgressMap.tsx` | ✅ | ⏳ **PENDENTE** |
| SSE streaming (agentes progressivos) | ✅ | ⏳ **PENDENTE** |
| KaTeX para renderização de LaTeX | ✅ | ⏳ **PENDENTE** |
| Seletor de modelo no UI | ✅ | ⏳ **PENDENTE** |

> ⚠️ **Situação atual:** O frontend mostra a interface básica (Cloudflare Workers), mas os componentes específicos da arquitetura planejada (`ChatInterface`, `AgentPanel`, etc.) ainda não foram implementados. A página atual provavelmente exibe o `page.tsx` mínimo criado para o deploy.

---

### ✅ Etapa 5 — Deploy em Produção
**Status:** Completo  
**Data:** 2026-04-27  
**Commits:** `26b341b` (Cloudflare Workers config), `cffc841` (deployment guide)

| Item | Status |
|---|---|
| `render.yaml` criado | ✅ |
| Backend no Render.com (auto-deploy por push) | ✅ |
| Frontend no Cloudflare Workers (não Pages) | ✅ |
| `wrangler.jsonc` configurado | ✅ |
| `open-next.config.ts` configurado | ✅ |
| `NEXT_PUBLIC_API_URL` apontando para Render | ✅ |

**Desvio do planejado:** Usado Cloudflare **Workers** em vez de **Pages** (documentado em `DEPLOYMENT_GUIDE.md`). Pages não suporta arquivos server do Next.js; Workers + @opennextjs/cloudflare foi a solução correta.

---

### ✅ Etapa 6 — Desenvolvimento Local
**Status:** Completo  
**Data:** 2026-04-27  
**Commit:** `0803ae1`

| Item | Status |
|---|---|
| `docker-compose.yml` criado | ✅ |
| Opção sem Docker documentada | ✅ |

---

## Features Não Previstas no STACK_FUTURO ⚡

Desenvolvidas por necessidade pedagógica ou correção de UX durante o projeto.

### ⚡ 5-Level Source Hierarchy (2026-04-26)
**Commit:** `3ec4df1`  
**Por quê:** Necessário para priorizar fontes (professor > adotados > UFSM > .edu.br > internacional) de forma estruturada e rastreável.  
**O que faz:** `build_context()` em PhysicsState monta contexto priorizado com tags de origem `[Material do Professor]`, `[Ementa UFSM]`, etc.

---

### ⚡ Phase 1 UX — Correções Críticas (2026-04-26)
**Commit:** `391931b`  
**Por quê:** Bugs visíveis encontrados após revisão inicial: classes CSS desalinhadas, quiz nunca exibindo feedback, debug panel exposto ao usuário.  
**Corrigiu:** 4 bugs (CSS classes, quiz state, debug panel, pCloud URL exposta)

---

### ⚡ Phase 2 UX — Mobile + Sidebar + Onboarding (2026-04-26)
**Commit:** `bebff5d`  
**Por quê:** 40% de usuários em mobile sem acesso usável; sidebar sem hierarquia visual.  
**Adicionou:** Media queries para mobile (≤768px), sidebar reorganizada em grupos, onboarding expandível, upload de imagem condicional por modelo.

---

### ⚡ Student Model Persistente (2026-04-26)
**Commit:** `8449aa9`  
**Por quê:** Alicerce pedagógico — sem memória entre sessões, o sistema recomeça do zero sem saber o que o aluno já viu ou onde errou.  
**O que faz:**
- `src/models/student_model.py` — `StudentModel` + `ConceptStatus` + SM-2
- Persistência em `data/students/{slug}.json`
- Progress dashboard (treemap Plotly) na Tab 5
- Notificação de revisões pendentes
- Quiz self-evaluation atualiza SM-2

> **Relação com Supabase:** O StudentModel local (JSON) coexiste com o StudentModel no Supabase (backend). Para o Streamlit app (src/), usa-se JSON local. Para o FastAPI app (backend/), usa-se Supabase.

---

### ⚡ Modo Referência (2026-04-27)
**Commit:** `79b9547`  
**Por quê:** Alunos sem créditos de API ficavam com o app quebrado. Proposta: fallback honesto que exibe material local sem chamar nenhuma API.  
**O que faz:**
- Toggle "🔬 Modo de Resposta" na sidebar (Modo IA / Modo Referência)
- `generate_reference_response()` em `src/app.py` — sem LLM, usa keyword matching no syllabus UFSM
- Exibe ementa UFSM, notas do professor, documentos adotados
- Não atualiza StudentModel (não é sessão de IA)

---

### ⚡ Simplificação de Modelos (2026-04-27)
**Commit:** `3ec3441`  
**Por quê:** Simplificação operacional — manter apenas modelos ativos, comentar os demais.  
**Resultado:** DeepSeek Chat (primário) + Gemini 2.0 Flash (fallback). Outros modelos comentados em `config.py`.

---

### ⚡ Phase 3 Polish (2026-04-27)
**Commit:** `6a51c17`  
**Por quê:** Auditoria de dead code e UX rough edges identificou 12 problemas específicos.  
**Corrigiu:**
- CSS `.agent-box` e `.ufsm-badge` faltavam no `<style>` (tabs sem estilo visual)
- Error strings fluindo para tabs como conteúdo (helper `display_content_or_error()`)
- Tab 3 em Modo Referência usando `st.code()` em vez de `st.markdown()`
- Botão "Desafie-me!" visível em Modo Referência
- `runtime_keys` atribuído duas vezes
- `build_context()` chamado duas vezes em cada chamada (6 ocorrências)
- Dead fields em PhysicsState removidos
- `st.toast()` ao mudar modelo

---

## O Que Ainda Falta ⏳

### Prioridade Alta

| Item | De onde vem | Por quê | Esforço estimado |
|---|---|---|---|
| **Frontend componentes completos** (ChatInterface, AgentPanel, VoiceInput, ProgressMap) | Etapa 4 do STACK_FUTURO | Interface atual não tem streaming de agentes nem suporte a LaTeX/KaTeX no Next.js | ~2-3h |
| **api.ts no frontend** | Etapa 4 | Sem isso o frontend não chama o backend | ~30min |
| **Cron job keep-alive Supabase** | Etapa 0 | Banco pausa após 7 dias — perda de dados | 5min |

### Prioridade Média

| Item | De onde vem | Por quê | Esforço estimado |
|---|---|---|---|
| **Spinner "acordando servidor"** | Nota do STACK_FUTURO | Render cold start (~30s) parece bug ao usuário | ~20min |
| **Misconception detection** | Arquitetura Supabase | Tabela criada mas nunca populada | ~1h |
| **`/student/{email}/progress` no frontend** | STACK_FUTURO | Endpoint existe, frontend não usa | ~30min |
| **Integração StudentModel local → Supabase** | Necessidade de unificação | JSON local e Supabase são paralelos; migrar para Supabase unifica | ~2h |

### Prioridade Baixa / Futuro

| Item | De onde vem | Por quê | Esforço estimado |
|---|---|---|---|
| pgvector busca semântica | STACK_FUTURO (avançado) | Embedding de conceitos para busca fuzzy | ~3h |
| Auth com Supabase Auth | STACK_FUTURO | Alunos identificados por email, sem senha — opcional | ~2h |
| CI/CD GitHub Actions | DEPLOYMENT_GUIDE.md futuro | Auto-deploy testado | ~1h |
| Upgrade para tiers pagos | STACK_FUTURO nota | Render Pro ($12/mês) elimina cold starts | — |

---

## Histórico de Commits por Fase

```
2026-04-26
  3ec4df1  feat: 5-level source hierarchy
  391931b  fix: Phase 1 UX (4 critical bugs)
  bebff5d  ux: Phase 2 (mobile + sidebar + onboarding)
  8449aa9  feat: Student Model Persistente (SM-2 + progress)
  6e782fd  docs: Reorganize STACK_FUTURO.md

2026-04-27
  8c2f58f  feat: FastAPI backend + process_streaming
  6f796a8  fix: backend field mappings
  0803ae1  infra: deployment config files (render.yaml, Dockerfile, supabase SQL)
  3004730  feat: minimal Next.js frontend
  26b341b  setup: Cloudflare Workers (@opennextjs/cloudflare)
  2b5cd38  chore: build:cloudflare script
  1af374f  fix: CORS — add Cloudflare URL
  e423706  fix: CORS allow_origins=["*"]
  2b2ee07  fix: OPTIONS handler for preflight
  cffc841  docs: DEPLOYMENT_GUIDE.md (Cloudflare Workers + Render)
  809710c  fix: remove non-existent PhysicsState attrs from response
  3ec3441  chore: simplify models (DeepSeek + Gemini 2.0 Flash)
  79b9547  feat: Modo Referência (offline KB access)
  3c62560  docs: MODO_REFERENCIA.md + DEVELOPER_MODO_REFERENCIA.md
  6a51c17  refactor: Phase 3 Polish (12 cleanup items)
```

---

## Convenções de Manutenção

1. **Toda feature nova** deve ter uma linha neste arquivo: `data`, `commit`, `por quê`, `o que faz`
2. **Bugs críticos** em produção devem ser documentados na seção de desvios da etapa afetada
3. **Mudanças de arquitetura** devem atualizar as seções "Stack Atual em Produção" e "Etapas do Roadmap"
4. Manter o documento em `docs/PROJECT_STATUS.md` — é o único lugar de verdade sobre o estado do projeto

---

*Última atualização: 2026-04-27 — Após Phase 3 Polish (commit 6a51c17)*
