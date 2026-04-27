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
- [Sobre minha experiência criando algo 100% com IA](https://www.tabnews.com.br/DeividSouSan/sobre-minha-experiencia-criando-algo-100-por-cento-com-ia) — Case study de desenvolvimento com IA

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

## 📅 2026-04-27 — Frontend Testing + Deployment ✅ LIVE

**Commits:** `38c6eab` + `a8e115f` (Cloudflare config + deployment)

### O que foi feito
- ✅ Testado dev server (`npm run dev`) — ChatInterface, voice input, model selector funcionando
- ✅ Build Cloudflare Workers — `npm run build:cloudflare` passa sem erros
- ✅ Corrigido `next.config.js` — adicionado `output: 'standalone'` para OpenNext/Cloudflare
- ✅ Configurado `wrangler.jsonc` com account_id
- ✅ **DEPLOYED** para Cloudflare Workers — https://tutoriafisica.hans-059.workers.dev
- ✅ Criado `SUPABASE_CRON_SETUP.md` — guia passo-a-passo para cron job Supabase

### Status
🟢 **COMPLETO** — Frontend Etapa 4 em produção com SSE streaming, KaTeX, voice input

---

## 📅 2026-04-27 — Migrate Frontend: Cloudflare → Vercel (com cron job nativo)

**Commit:** `8af1afe`

### O que foi feito
- ✅ Removido `@opennextjs/cloudflare` (adapter específico para Workers)
- ✅ Removido `wrangler.jsonc` e `open-next.config.ts`
- ✅ Simplificado `next.config.js` (sem standalone output)
- ✅ Criado `frontend/vercel.json` com cron schedule: `0 12 */5 * *` (a cada 5 dias ao meio-dia UTC)
- ✅ Criado `frontend/src/app/api/keepalive/route.ts` — API route chamada pelo cron
- ✅ Build Next.js passa sem erros (rota `/api/keepalive` como server-side dynamic)

### Por quê mudou
Cron-job.org falhou com 401/400 (problemas de autenticação). Vercel tem cron jobs **nativos** via `vercel.json` que chamam rotas de API internas — mais confiável e sem serviços externos.

### Status
🟡 **CÓDIGO PRONTO** — Frontend migrado, aguardando deploy manual no Vercel

---

## 🎯 Próximas Prioridades

| Item | Esforço | Impacto | Status |
|---|---|---|---|
| **Deploy frontend no Vercel** | 10 min (manual) | 🔴 **CRÍTICO** | ⏳ |
| Testar cron job após deploy | 5 min | Alto | ⏳ |
| Testar SSE streaming em produção | 10 min | Alto | ⏳ |
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
