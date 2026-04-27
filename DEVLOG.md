# DEVLOG — TutorIAFisica

Histórico de desenvolvimento, organized by session and major milestones.

---

## 📅 2026-04-27 — Etapa 4 Frontend Components Complete

**Commits:** `f72bcc3` (PROJECT_STATUS.md) + `d882410` (frontend components)

### O que foi feito
- ✅ Commitado `docs/PROJECT_STATUS.md` — documento de controle de projeto rastreando STACK_FUTURO vs implementação real
- ✅ Instaladas dependências npm no frontend: `react-markdown`, `remark-math`, `rehype-katex`, `katex`, `lucide-react`
- ✅ Criado `frontend/src/lib/api.ts` — client SSE com tipos TypeScript (AgentOutput, TutorResponse, DueReview)
- ✅ Criado `frontend/src/components/AgentPanel.tsx` — renderiza resposta de agente com markdown + KaTeX
- ✅ Criado `frontend/src/components/VoiceInput.tsx` — botão de microfone, chama `/tutor/transcribe`
- ✅ Criado `frontend/src/components/ChatInterface.tsx` — interface principal com streaming SSE, seletor de modelo
- ✅ Atualizado `frontend/src/app/page.tsx` — agora usa `<ChatInterface />`
- ✅ Corrigido `frontend/tsconfig.json` — adicionado baseUrl + paths para alias `@/*`
- ✅ Build Next.js passa sem erros: TypeScript + webpack limpo

### Decisões/Desvios do STACK_FUTURO
- **MODELS list:** Reduzida a `["DeepSeek Chat", "Gemini 2.0 Flash"]` (reflete config atual em `src/config.py`)
- **TutorResponse type:** Removidos `visualization_code` e `formative_challenge` (campos não existem no backend real)
- **VoiceInput fix:** Corrigido `mr.stream.getTracks()` para pass TypeScript strict check

### Status
🟢 **COMPLETO** — Etapa 4 do STACK_FUTURO.md implementada. Frontend pronto para SSE streaming.

### Próximo Passo
Testar dev server (`npm run dev`) e verificar conexão real com backend `/tutor/ask/stream`.

### Referências
- [Como falar com o Claude Code efetivamente — "O falso problema"](https://akitaonrails.com/2026/04/15/como-falar-com-o-claude-code-efetivamente/#o-falso-problema) — Padrão de comunicação efetiva com Claude Code

---

## 📅 2026-04-27 — Phase 3 Polish Complete

**Commit:** `6a51c17`

### O que foi feito
- ✅ Erro strings nas tabs (A1) — criados helpers `is_error_string()` e `display_content_or_error()` em `app.py`
- ✅ CSS classes (A2) — adicionadas regras `.agent-box` e `.ufsm-badge` no bloco `<style>`
- ✅ Tab 3 markdown vs code (A3) — branch condicional para `st.markdown()` vs `st.code()`
- ✅ Quiz labels spacing (A4) — adicionado `\n\n` entre label e conteúdo
- ✅ Quiz button guard (A5) — botão "Desafie-me!" escondido em Modo Referência
- ✅ Dead code cleanup (B1-B5) — removidas duplicações, dead fields, otimizadas chamadas
- ✅ UX minor (C1-C2) — placeholders vazios e toast no model change

### Status
🟢 **COMPLETO** — Auditoria de Phase 3 concluída, 12 issues resolvidas.

---

## 📅 2026-04-27 — Modo Referência + Student Model + Project Control Doc

**Commits:** `79b9547` (Modo Referência) + `8449aa9` (Student Model persistente) + `f72bcc3` (PROJECT_STATUS.md)

### O que foi feito
- ✅ Implemented `generate_reference_response()` — offline KB access sem API
- ✅ Sidebar toggle "🔬 Modo de Resposta" — escolher entre Modo IA e Modo Referência
- ✅ UFSM syllabus keyword matching — regex `\b\w{4,}\b` extrai conceitos
- ✅ StudentModel com SM-2 — spaced repetition, progress tracking
- ✅ Criado `docs/PROJECT_STATUS.md` — controle centralizado de STACK_FUTURO vs real

### Status
🟢 **COMPLETO** — Modo offline funcional, studentmodel persistente, projeto documentado.

---

## 📅 2026-04-26 — Backend FastAPI + SSE Streaming

**Commits:** `8c2f58f` + `6f796a8` + `0803ae1` + mais CORS fixes

### O que foi feito
- ✅ Backend FastAPI (Render.com) — `/tutor/ask`, `/tutor/ask/stream`, `/tutor/feedback`
- ✅ SSE streaming — `process_streaming()` em `src/core.py`
- ✅ Supabase integration — `backend/db/supabase_client.py`
- ✅ Deploy automático — `render.yaml` configurado
- ✅ CORS — resolvido com `allow_origins=["*"]` + OPTIONS handler explícito

### Status
🟢 **LIVE** — Backend em https://tutor-ia-fisica-api.onrender.com

---

## 🎯 Próximas Prioridades

| Item | Esforço | Impacto | Status |
|---|---|---|---|
| Testar frontend dev server | 10 min | Alto | ⏳ |
| Cron job keep-alive Supabase | 5 min | Crítico | ⏳ |
| Frontend deploy Cloudflare Workers | 20 min | Alto | ⏳ |
| Misconception detection | 1h | Médio | ⏳ |
| StudentModel local ↔ Supabase unificação | 2h | Médio | ⏳ |

---

## 📋 Referências Rápidas

- **PROJECT_STATUS.md** — Mapa completo de STACK_FUTURO vs implementado
- **CLAUDE.md** — Arquitectura, patterns, como estender
- **DEVELOPER_MODO_REFERENCIA.md** — Design técnico do Modo Referência
- **Backend API docs** → `/health` no https://tutor-ia-fisica-api.onrender.com

---

*Última atualização: 2026-04-27 — Após Etapa 4 frontend*
