# Deploy Frontend no Vercel

Frontend foi migrado de Cloudflare Workers para Vercel. Cron job para Supabase keep-alive agora é **nativo** no Vercel.

---

## Instruções Passo-a-Passo

### 1️⃣ Acessar Vercel

1. Abra https://vercel.com/
2. Clique **"Sign Up"** (ou login se já tem conta)
3. Conecte sua conta GitHub

### 2️⃣ Importar Repositório

1. Clique **"Add New..."** → **"Project"**
2. Procure seu repositório: `TutorIAFisica`
3. Clique **"Import"**

### 3️⃣ Configurar Projeto

Na tela de configuração do projeto, **ANTES de clicar Deploy**:

#### 🔴 CRITICAL: Root Directory

1. Localize o campo **"Root Directory"** (geralmente no topo da página de configuração)
2. **Clique no campo** (pode ser um dropdown ou input)
3. **Selecione ou digite:** `frontend`
   - ❌ Não deixe em branco (padrão é raiz do repositório)
   - ❌ Não use `./frontend` ou `/frontend`
   - ✅ Use apenas: `frontend`

Se essa configuração estiver errada, Vercel procura por `package.json` na raiz e não encontra Next.js.

### 4️⃣ Configurar Variáveis de Ambiente

Clique em **"Environment Variables"** e adicione:

#### Variável 1
- **Name:** `NEXT_PUBLIC_API_URL`
- **Value:** `https://tutor-ia-fisica-api.onrender.com`
- **Environments:** Production, Preview, Development (selecione todas)

#### Variável 2
- **Name:** `SUPABASE_URL`
- **Value:** `https://jqnmckhxdbpcwyzqxyvm.supabase.co`
- **Environments:** Production, Preview, Development

#### Variável 3
- **Name:** `SUPABASE_ANON_KEY`
- **Value:** (copie a chave completa do seu `.env` do projeto)
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Impxbm1ja2h4ZGJwY3d5enF4eXZtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzcyMzU3MjEsImV4cCI6MjA5MjgxMTcyMX0.dNE3wCLQS1xVluehFlHg5sw8tmykstKGyQf1QoI7C7I
```
- **Environments:** Production, Preview, Development

### 5️⃣ Deploy

Clique **"Deploy"**

Vercel vai:
1. Fazer clone do repositório
2. Instalar dependências (`npm install`)
3. Fazer build (`npm run build`)
4. Fazer deploy em produção

**Tempo esperado:** 2-3 minutos

### 6️⃣ Confirmar Deploy

Após o deploy, você recebe:
- ✅ Uma URL automática (ex: `https://tutoriafisica.vercel.app`)
- ✅ Cron job automaticamente agendado em `/api/keepalive`

---

## Verificar Cron Job

Após deploy, você pode confirmar que o cron job está configurado:

1. Vercel Dashboard → seu projeto → **Settings** → **Crons**
2. Você deve ver:
   ```
   /api/keepalive
   Schedule: 0 12 */5 * * (todo dia às 12:00 UTC a cada 5 dias)
   Status: Active
   ```

### Testar Manualmente

1. Clique no cron job
2. Clique **"Trigger"** ou **"Test"**
3. Você deve ver:
   ```json
   { "status": 200, "ok": true }
   ```

---

## Se Algo Dar Errado

### Build falhou
- Clique em "Deployments" e veja logs detalhados
- Procure por erro no `npm run build`

### Cron job não dispara
- Cheque se `SUPABASE_URL` e `SUPABASE_ANON_KEY` estão corretos
- Tente disparar manualmente em Settings → Crons

### API retorna erro 401
- Verifique se `SUPABASE_ANON_KEY` está completa (sem truncar)
- Copie de novo do `.env` do projeto local

---

## Próximas Etapas

1. Após deploy, guarde a URL gerada (ex: `https://tutoriafisica.vercel.app`)
2. Atualize `DEVLOG.md` com a nova URL de produção
3. Teste se SSE streaming funciona em produção

---

**Vercel URL gerada:** [após deploy] `https://...`  
**Cron job:** Dispara a cada 5 dias às 12:00 UTC  
**Status:** ⏳ Aguardando deploy manual
