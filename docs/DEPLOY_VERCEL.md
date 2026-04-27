# Deploy Vercel — Guia Completo de Operação

**Frontend TutorIAFisica** foi migrado de **Cloudflare Workers** para **Vercel** em abril de 2026.

Esta documentação cobre a migração, configuração de ambiente, deploy e operação do cron job nativo.

---

## 1. Estado da Migração

### Antes (Cloudflare Workers) ❌
- Adapter: `@opennextjs/cloudflare` (OpenNext)
- Configuração: `wrangler.jsonc` + `open-next.config.ts`
- Cron job: Serviço externo (cron-job.org) — **instável**, falhas de autenticação
- URL: `https://tutoriafisica.hans-059.workers.dev`

### Depois (Vercel) ✅
- Runtime: Node.js nativo no Vercel
- Configuração: `vercel.json` com cron schedule declarativo
- Cron job: **Nativo** ao Vercel — integrado, confiável
- URL: `https://<seu-projeto>.vercel.app` (ou domínio customizado)

### Arquivos Removidos
```
❌ wrangler.jsonc
❌ open-next.config.ts
❌ @opennextjs/cloudflare (dependência)
```

### Arquivos Criados/Atualizados
```
✅ vercel.json — schedule do cron job
✅ frontend/src/app/api/keepalive/route.ts — endpoint do cron
✅ render.yaml — atualizado FRONTEND_URL para placeholder Vercel
✅ frontend/.env.local — adicionado SUPABASE_* vars (local dev)
```

---

## 2. Variáveis de Ambiente

### Configurar no Painel Vercel

Na tela de **Project Settings → Environment Variables**, adicione:

| Nome | Valor | Ambientes | Secreto? |
|---|---|---|---|
| `NEXT_PUBLIC_API_URL` | `https://tutor-ia-fisica-api.onrender.com` | Prod, Preview, Dev | ❌ |
| `SUPABASE_URL` | `https://jqnmckhxdbpcwyzqxyvm.supabase.co` | Prod, Preview, Dev | ❌ |
| `SUPABASE_ANON_KEY` | (copie do `.env` local) | Prod, Preview, Dev | ✅ Marcar como Secreto |

**Notas:**
- `NEXT_PUBLIC_*` são expostas ao browser — não coloque dados sensíveis
- `SUPABASE_ANON_KEY` é seguro no Vercel (secrets não entram em git)
- Local dev: copie estas vars para `frontend/.env.local` (NÃO versionado)

### Adicionar Var no Render Dashboard

Após deploy Vercel, você receberá uma URL automática (ex: `https://tutoriafisica.vercel.app`). 

Copie esta URL e **atualize em Render.com**:
1. Vá para **Render Dashboard** → seu projeto backend (`tutor-ia-fisica-api`)
2. Clique **Settings** → **Environment**
3. Encontre ou crie var `FRONTEND_URL`
4. Cole: `https://tutoriafisica.vercel.app` (sua URL Vercel gerada)
5. Clique **Save**

Isto permite que o backend validar requisições CORS da sua URL de produção.

---

## 3. Passo-a-Passo: Deploy no Painel Vercel

### Pré-requisito
- Conta GitHub conectada ao repositório `TutorIAFisica`
- Conta Vercel (crie em https://vercel.com se não tiver)

### Passos

#### 1. Acessar Vercel
- Abra https://vercel.com
- Faça login (use GitHub se já conectado)

#### 2. Importar Repositório
- Clique **"Add New..."** → **"Project"**
- Procure `TutorIAFisica` na lista de repositórios GitHub
- Clique **"Import"**

#### 3. Configurar Raiz (CRÍTICO — veja troubleshooting se errar)
Na tela de configuração, **ANTES de Deploy**:
- **Root Directory:** 
  - ❌ **NÃO deixe em branco** (procura por package.json na raiz)
  - ❌ **NÃO use** `./frontend` ou `/frontend`
  - ✅ **USE:** `frontend` (exatamente assim)
  - Se estiver errado aqui, você terá erro "No Next.js version detected"
- Framework: auto-detecta Next.js (se Root Directory correto)
- Build Command: padrão (`npm run build`)
- Output Directory: `.next` (padrão)

#### 4. Configurar Variáveis de Ambiente
Clique **"Environment Variables"** e adicione as 3 vars da seção anterior.

#### 5. Deploy
Clique **"Deploy"**

Vercel fará:
1. Clone do repositório
2. `npm install` no diretório `frontend`
3. `npm run build`
4. Deploy ao CDN global

**Tempo esperado:** 2–3 minutos

#### 6. Confirmação
Após sucesso:
- ✅ Green "Production Deployment" badge
- ✅ URL automática (ex: `tutoriafisica.vercel.app`)
- ✅ Cron job agendado automaticamente

---

## 4. Configuração do Cron Job

### O Que Faz
O endpoint `/api/keepalive` toca a base Supabase a cada 5 dias ao meio-dia UTC (12:00), evitando que a instância Supabase durma em plano gratuito.

### Schedule Atual
```json
// vercel.json
{
  "crons": [{
    "path": "/api/keepalive",
    "schedule": "0 12 */5 * *"
  }]
}
```

**Sintaxe:** `minute hour day-of-month month day-of-week`

- `0` = minuto 0
- `12` = hora 12 (UTC)
- `*/5` = a cada 5 dias (1º, 6º, 11º, ...)
- `*` = qualquer mês
- `*` = qualquer dia da semana

### Verificar Após Deploy

1. **Painel Vercel:**
   - Projeto → **Settings** → **Crons**
   - Deve mostrar: `/api/keepalive` com schedule `0 12 */5 * *`
   - Status: **Active**

2. **Testar Manualmente:**
   - Clique no cron job
   - Clique **"Trigger"** ou **"Test"**
   - Resultado esperado: `{ "status": 200, "ok": true }`

3. **Verificar Logs:**
   - Projeto → **Deployments** → últimos logs
   - Procure por: `keepalive triggered` ou `Supabase pinged`

### Editar Schedule

Se precisar mudar o schedule (ex: a cada 3 dias):
1. Edite `vercel.json` → `schedule: "0 12 */3 * *"`
2. Faça commit e push
3. Vercel redeploy automaticamente (se autoDeploy habilitado)
4. Confirme em **Settings → Crons**

---

## 5. Integração com Backend Render

### CORS Configuration

O backend (`tutor-ia-fisica-api.onrender.com`) tem CORS configurado:
```python
allow_origins=["*"]  # temporário; endurecido pós-deploy
```

**Após deploy Vercel**, atualize para:
```python
allow_origins=[
    "https://tutoriafisica.vercel.app",  # produção Vercel
    "http://localhost:3000",              # dev local
    # adicione domínios customizados se aplicável
]
```

**Como atualizar:**
1. Edite `backend/main.py` (ou arquivo de CORS)
2. Substitua URL no `allow_origins`
3. Commit e push
4. Render redeploy automático

### Keep-Alive Flow

```
Vercel Cron (a cada 5 dias, 12:00 UTC)
    ↓
/api/keepalive (route.ts — server-side)
    ↓
GET https://tutor-ia-fisica-api.onrender.com/health
    ↓
Backend responde: { "status": "ok" }
    ↓
Supabase tab "touched" — não dorme
```

Se o cron falhar:
- Vercel tentará novamente em 12:05 UTC
- Máximo 3 tentativas automáticas
- Verifique logs em **Deployments** se houver falhas repetidas

---

## 6. Rollback Strategy

Se precisar voltar para Cloudflare:

### Opção A: Reverter Commits
```bash
git revert <commit-hash-da-migracao>
git push
```
Cloudflare redeploy automático via Wrangler se habilitado.

### Opção B: Manter Vercel, Trocar Endpoint
1. Em `vercel.json`, remova o cron job
2. Reative `cron-job.org` manualmente (ou outro serviço)
3. Configure URL de callback: `https://tutoriafisica.vercel.app/api/keepalive`

### Estratégia Recomendada
- **Não fazer rollback manual** — automático via GitHub integração
- Se houver problema: abra issue, reverta commit, deixe CI rodar
- Verificar em **Vercel Dashboard → Deployments** antes de assumir falha

---

## 7. Checklist Pós-Deploy

### ✅ Imediatamente Após Sucesso

- [ ] Vercel dashboard mostra "Production" em verde
- [ ] URL gerada acessível: `https://<seu-projeto>.vercel.app`
- [ ] Cron job aparece em **Settings → Crons** com status **Active**
- [ ] Disparar cron manualmente: deve retornar `{ "status": 200, "ok": true }`

### ✅ Nos Próximos 5-10 Minutos

- [ ] Testar rota de healthcheck: `curl https://<seu-projeto>.vercel.app/api/keepalive`
- [ ] Verificar Vercel logs: **Deployments** → últimos logs sem erros
- [ ] Confirmar Supabase keepalive: cron deve ter tocado `last_keepalive_timestamp`

### ✅ Integração com Backend

- [ ] Atualizar `FRONTEND_URL` no Render Dashboard
- [ ] Atualizar `allow_origins` no backend para nova URL Vercel
- [ ] Testar SSE streaming: conectar frontend → backend, verificar `/tutor/ask/stream`

### ✅ Documentação

- [ ] Atualizar `DEVLOG.md` com:
  - Data do deploy Vercel
  - URL de produção gerada
  - Timestamp do primeiro cron bem-sucedido
- [ ] Guardar commit hash da migração para referência futura

---

## 8. Troubleshooting

### "No Next.js version detected" — Erro na Import

**Erro exato:**
```
Warning: Could not identify Next.js version, ensure it is defined as a project dependency.
Error: No Next.js version detected. Make sure your package.json has "next" in 
either "dependencies" or "devDependencies".
```

**Causa:** Root Directory não foi configurado para `frontend`

**Solução:**
1. **Volte para a página de import** (ou project settings)
2. Localize campo **"Root Directory"**
3. Mude para: `frontend` (EXATAMENTE assim, sem `./` ou `/`)
4. Clique **Save** ou **Redeploy**
5. Aguarde build novamente

**Verificação rápida:**
- Vercel dashboard → projeto → **Settings** → **General**
- Procure por **"Root Directory"** — deve mostrar `frontend`

---

### Build Falhou no Vercel

**Erro típico:** `next build` com import issues ou TypeScript (após Root Directory correto)

**Solução:**
1. Clique em **Deployments** → build falhado → **View Details**
2. Role até o final: procure por `error` em vermelho
3. Verifique:
   - `frontend/tsconfig.json` com `baseUrl` e `paths` corretos
   - `frontend/next.config.js` sem referências a Cloudflare
   - `node_modules` — rode `npm install` localmente e teste `npm run build`
4. Commit fix, push, Vercel redeploy automático

### Cron Job Não Dispara

**Verificar:**
1. **Painel Vercel:**
   - **Settings → Crons** → status é **Active**?
   - Se **Paused**: clique **Resume**

2. **Variáveis de Ambiente:**
   - `SUPABASE_URL` e `SUPABASE_ANON_KEY` definidas?
   - Copie do `.env` local e valide: sem espaços, sem truncamento

3. **Logs:**
   - **Deployments** → filtro de time recente
   - Procure por linhas com `cron` ou `keepalive`
   - Se houver `401` ou `403`: revise chaves Supabase

4. **Teste Manual:**
   - **Settings → Crons** → clique no cron job
   - Clique **"Test"** ou **"Trigger"**
   - Se retorna erro: veja mensagem exata

### API Retorna 401/403

**Causa:** Chave Supabase incorreta ou vencida

**Solução:**
1. Vá para Supabase dashboard
2. **Project Settings** → **API** → copie `anon public key` completo
3. Vercel dashboard → **Settings → Environment Variables**
4. Atualize `SUPABASE_ANON_KEY` com valor novo
5. Redeploy manualmente: **Deployments** → clique três-pontos → **Redeploy**
6. Teste cron manualmente em **Settings → Crons**

### SSE Streaming Não Funciona em Produção

**Verificar:**
1. Frontend consegue se conectar a backend?
   - Abra DevTools → **Network** → filtro `ask` ou `stream`
   - Deve ver requisição para `https://tutor-ia-fisica-api.onrender.com/tutor/ask/stream`
   - Status: `200` e `Transfer-Encoding: chunked`

2. CORS bloqueado?
   - DevTools → **Console** → procure por erro `CORS` em vermelho
   - Se houver: backend `allow_origins` não inclui URL Vercel
   - Solução: atualize backend (seção 5)

3. Backend down?
   - Teste manualmente: `curl https://tutor-ia-fisica-api.onrender.com/health`
   - Deve retornar `{ "status": "ok" }`
   - Se erro: verifique Render dashboard status

---

## 9. Referências Rápidas

### Arquivos Críticos
- `vercel.json` — schedule do cron job
- `frontend/src/app/api/keepalive/route.ts` — handler do cron
- `render.yaml` — FRONTEND_URL da aplicação
- `backend/main.py` — configuração CORS (atualize pós-deploy)

### URLs de Produção
- **Frontend:** `https://<seu-projeto>.vercel.app`
- **Backend:** `https://tutor-ia-fisica-api.onrender.com`
- **Supabase:** `https://jqnmckhxdbpcwyzqxyvm.supabase.co`

### Documentação Relacionada
- `VERCEL_DEPLOY_GUIDE.md` — passo-a-passo manual (no raiz, legacy)
- `DEVLOG.md` — histórico de migração (2026-04-27)
- `CLAUDE.md` — arquitetura geral do projeto
- `DEPLOYMENT_GUIDE.md` — guia de deploys de componentes individuais

### Suporte
- **Vercel Docs:** https://vercel.com/docs/crons
- **Next.js API Routes:** https://nextjs.org/docs/app/building-your-application/routing/route-handlers
- **Supabase Status:** https://status.supabase.com

---

**Última atualização:** 2026-04-27  
**Versão:** 1.0 (Migração Vercel completa)
