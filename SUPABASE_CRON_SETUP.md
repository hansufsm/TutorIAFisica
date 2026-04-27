# Configuração do Cron Job Keep-Alive — Supabase

**⚠️ CRÍTICO:** Supabase Free pausa após 7 dias sem atividade. Este cron job mantém o banco ativo.

**Status:** ⏳ PENDENTE CONFIGURAÇÃO MANUAL

---

## Instruções Passo-a-Passo

### 1️⃣ Acessar cron-job.org

1. Abra https://cron-job.org/
2. Clique em **"Sign Up"** (gratuito, sem cartão de crédito)
3. Crie uma conta com email
4. Confirme email e faça login

### 2️⃣ Criar um novo Cron Job

1. Clique em **"Create Cronjob"**
2. Preencha os campos abaixo:

#### Campo 1: Title
```
Supabase Keep-Alive
```

#### Campo 2: URL
```
https://jqnmckhxdbpcwyzqxyvm.supabase.co/rest/v1/students?limit=1
```
(Isto faz um query leve na tabela `students` para manter o banco acordado)

#### Campo 3: HTTP Headers
Clique em **"Add HTTP Header"** e adicione:
- **Key:** `apikey`
- **Value:** `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Impxbm1ja2h4ZGJwY3d5enF4eXZtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzcyMzU3MjEsImV4cCI6MjA5MjgxMTcyMX0.dNE3wCLQS1xVluehFlHg5sw8tmykstKGyQf1QoI7C7I`

#### Campo 4: Frequency
- Selecione: **"Every 5 days"**
- Hora: **"at 12:00 (noon) UTC"**

#### Campo 5: Timeout
- Deixe como padrão (30 segundos)

### 3️⃣ Salvar e Verificar

1. Clique em **"Save"**
2. Dashboard deve mostrar: **"Status: OK"** (depois do primeiro acionamento)
3. Você receberá email de confirmação

---

## Verificação

Após 24h, você pode confirmar que funciona:
1. No dashboard do cron-job.org, veja "Last execution"
2. No Supabase console, você verá um request na aba "Database" → "Logs"
3. Banco permanecerá ativo indefinidamente

---

## URLs de Referência

- **Supabase Console:** https://app.supabase.com/
- **Cron Job Dashboard:** https://cron-job.org/
- **Documentação:** https://cron-job.org/en/documentation/

---

**Data de configuração:** [MANUAL - aguardando]  
**Próximo check:** 2026-05-04 (7 dias após)
