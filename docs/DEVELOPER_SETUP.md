# TutorIAFisica — Developer Setup Guide

> Guia completo e passo-a-passo para configurar o TutorIAFisica em seu ambiente de desenvolvimento

**Tempo estimado:** 30-45 minutos (depende de quantos provedores você quer habilitar)

---

## 🎯 Visão Geral

TutorIAFisica usa múltiplos provedores de IA com fallback automático:

| Provedor | Tipo | Free Tier | Multimodal | Padrão? |
|---|---|---|---|---|
| **DeepSeek** | Chat | ✅ Sim | ❌ Não | ✅ Sim |
| **Google Gemini** | Multimodal | ✅ Sim | ✅ Sim | ❌ Fallback |
| **xAI / Grok** | Chat | ✅ Sim (limitado) | ✅ Sim | ❌ Fallback |
| **OpenAI GPT-3.5** | Chat | ❌ Pago | ❌ Não | ❌ Fallback |
| **Anthropic Claude** | Chat | ❌ Pago | ✅ Sim | ❌ Fallback |
| **Perplexity** | Chat | ❌ Pago | ❌ Não | ❌ Fallback |

**Serviços sem chave API (gratuitos, sem registro):**
- 🔍 arXiv — Academic papers (API pública)
- 🔍 Semantic Scholar — Citations (API pública, rate limit generoso)
- 🔍 DuckDuckGo — Web search (Python package)
- ☁️ pCloud — Teacher materials (links públicos compartilhados)

---

## 📋 Pré-requisitos

### Hardware
- Qualquer máquina com 4GB RAM (Streamlit é leve)
- ~500MB disco para venv + dependências
- Conexão à internet (óbvio)

### Software

**Python 3.11+** (testado em 3.12.3)
```bash
# Verificar versão
python3 --version    # Deve retornar 3.11+ ou 3.12+
# Se tiver só Python 2.7 ou 3.10, atualize primeiro
```

**Git** (para clonar repositório)
```bash
git --version       # Deve retornar 2.x+
```

**curl** ou **wget** (para testar APIs)
```bash
curl --version
# ou
wget --version
```

---

## 🚀 Passo 1: Clone e Ambiente Virtual

### 1.1 Clonar repositório
```bash
git clone https://github.com/hansufsm/TutorIAFisica.git
cd TutorIAFisica
```

### 1.2 Criar venv (ambiente virtual isolado)

**Linux / Mac:**
```bash
python3.12 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

Você deve ver `(venv)` no prompt de shell, indicando que o venv está ativo.

### 1.3 Instalar dependências
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Isso instala:
- `streamlit>=1.30.0` — UI framework
- `litellm>=1.20.0` — Abstração multi-provider LLM
- `python-dotenv>=1.0.0` — Leitura de variáveis de ambiente
- `matplotlib>=3.8.0`, `plotly>=5.18.0` — Visualizações
- `pypdf>=4.0.0` — Extração de texto de PDFs
- `requests>=2.31.0` — HTTP requests
- `Pillow>=10.0.0` — Processamento de imagens
- `duckduckgo-search>=6.0.0` — Busca web

**Teste se funcionou:**
```bash
python -c "import streamlit; print(streamlit.__version__)"
```

---

## 🔑 Passo 2: Configurar API Keys

Você precisa de **pelo menos UMA** chave para usar o app. Recomenda-se:

### Opção A: Mínimo (recomendado para começar)

Escolha **uma** das seguintes:

#### **DeepSeek (padrão, free tier generoso)**

1. Acesse https://platform.deepseek.com
2. Crie conta (email + senha)
3. Clique "API Keys" no menu
4. Clique "Create API Key"
5. Copy a chave (formato: `sk-...`)

**Free tier:** 10 milhões tokens/mês grátis (suficiente para prototipagem)

#### **Google Gemini (multimodal, ideal se quer imagens)**

1. Acesse https://aistudio.google.com
2. Clique "Get API key"
3. Copy a chave (formato: `AIzaSy...`)

**Free tier:** 60 requisições por minuto, ilimitado por dia

#### **xAI / Grok (multimodal, novel)**

1. Acesse https://x.ai/api
2. Crie conta ou use X.com credentials
3. Clique "Create API Key"
4. Copy a chave (formato: `xai-...`)

**Free tier:** Limitado, mas funciona para teste

### Opção B: Completo (múltiplos provedores, fallback ativo)

Registre-se em todos que puder:

#### **2. OpenAI GPT-3.5 Turbo**
1. https://platform.openai.com
2. Criar conta + adicionar método de pagamento
3. "API keys" → "Create new secret key"
4. Copy `sk-...`

**Custo:** $0.0015/1K input tokens, $0.002/1K output tokens

#### **3. Anthropic Claude**
1. https://console.anthropic.com
2. Criar conta
3. "API Keys" → "Create Key"
4. Copy `sk-ant-...`

**Custo:** $3/1M input, $15/1M output tokens (mais caro)

#### **4. Perplexity (online search capability)**
1. https://www.perplexity.ai/api
2. Criar conta
3. "API Keys" → "Create"
4. Copy `pplx-...`

**Custo:** Variável, $5 crédito inicial

---

## 📝 Passo 3: Criar arquivo `.env`

Na **raiz do projeto** (`TutorIAFisica/.env`), crie um arquivo com suas chaves:

```bash
cat > .env << 'EOF'
# ============= MODELO PADRÃO (escolha UM) =============
DEEPSEEK_API_KEY=sk-abc123...

# OU:
# GEMINI_API_KEY=AIzaSyAbc123...

# ============= OPCIONAIS (habilitam fallback) =============
# Descomente os que tiver chave
# OPENAI_API_KEY=sk-proj-abc123...
# ANTHROPIC_API_KEY=sk-ant-abc123...
# XAI_API_KEY=xai-abc123...
# PERPLEXITY_API_KEY=pplx-abc123...
EOF
```

**Importante:**
- NÃO use aspas ao redor das chaves
- NÃO cometa `.env` para GitHub (já está em `.gitignore`)
- Linhas com `#` são comentários — descomente as chaves que tem

---

## 🧪 Passo 4: Testar Conectividade

```bash
python scripts/test_api_keys.py
```

**Saída esperada:**
```
================================================================================
🧪 TESTE DE CHAVES API
================================================================================

✅  DeepSeek Chat          oi
✅  Gemini 1.5 Flash       Olá! Como posso ajudar?
⏭️  OpenAI GPT-3.5 Turbo   chave OPENAI_API_KEY ausente no .env
...
```

Se tiver ❌ em uma chave que você adicionou, verifique:
- Copiou a chave corretamente (sem espaços)
- A chave tem saldo/quotas disponível
- Conectividade à internet

---

## ▶️ Passo 5: Iniciar o App

```bash
cd src
streamlit run app.py
```

**Saída esperada:**
```
You can now view your Streamlit app in your browser.

  URL: http://localhost:8501
```

Abra http://localhost:8501 no navegador.

**Teste básico:**
1. Digite uma pergunta simples: "Como calcular velocidade média?"
2. Clique "Processar Pergunta"
3. Você deve ver 4 respostas em abas diferentes

Se algo quebrar, veja [Troubleshooting](#troubleshooting) abaixo.

---

## 📚 Passo 6: Usar Materiais do Professor

### 6.1 Upload de PDF (Notas Manuais)

Na sidebar do app:
1. Clique "📄 Notas Manuais"
2. Clique "Browse files"
3. Selecione um PDF (suas anotações, livro, etc.)
4. O app extrairá texto automaticamente

### 6.2 Repositório Permanente (pCloud)

Para compartilhar materiais persistentemente com o app:

**Criar link pCloud:**
1. Acesse https://pcloud.com
2. Crie uma pasta (ex: "Fisica1_Notas")
3. Upload PDFs/TXTs para essa pasta
4. Clique direito na pasta → "Get public link"
5. Copy o link (formato: `https://u.pcloud.com/#/publink?code=abc123...`)

**Usar no app:**
1. Na sidebar, cole o link em "📦 Repositório Permanente"
2. Clique "Processar Pergunta"
3. O app baixará os PDFs de pCloud automaticamente

**Nota:** Qualquer pessoa com o link pode acessar. Se sensível, use um link com expiração ou senha.

### 6.3 Documentos Adotados (Livros/Slides da Disciplina)

Mesmo processo que 6.2, mas em um campo separado.

---

## 🔧 Passo 7: Configuração Avançada (Opcional)

### 7.1 Streamlit Config

Edite `.streamlit/config.toml` para customizar:

```toml
[theme]
primaryColor = "#007bff"      # Cor primária (azul)
backgroundColor = "#ffffff"   # Fundo branco (light mode)
textColor = "#31333f"         # Texto cinza escuro

[client]
showErrorDetails = false      # Esconder detalhes de erro de usuários

[logger]
level = "info"               # Verbosidade de logs
```

### 7.2 Adicionar Novo Modelo

Para habilitar um novo modelo (ex: Claude):

**1. Edite `src/config.py`:**
```python
"Claude 3.5 Sonnet": {
    "id": "claude-3-5-sonnet-20241022",
    "multimodal": True
}
```

**2. Adicione à ordem de fallback:**
```python
MODEL_PREFERENCE_ORDER = [
    "DeepSeek Chat",
    "Claude 3.5 Sonnet",  # ← novo
    "Gemini 1.5 Flash",
    # ...
]
```

**3. Adicione chave ao `.env`:**
```
ANTHROPIC_API_KEY=sk-ant-...
```

**4. Restart app:**
```bash
# Ctrl+C para parar
streamlit run app.py  # reinicia
```

---

## 🧠 Passo 8: Entender o Sistema

### Arquitetura em 30 segundos

```
Usuário digita pergunta
    ↓
PhysicsOrchestrator (orquestrador)
    ↓
┌─────────────────────────────────────────────────┐
│ 1. Intérprete (🔵)  → Método socrático         │
│ 2. Solucionador (🟢) → Rigor matemático        │
│ 3. Visualizador (🟠) → Gráficos interativos   │
│ 4. Curador (🟣)     → Materiais acadêmicos    │
│ 5. Avaliador (🔴)   → Quiz formativo          │
└─────────────────────────────────────────────────┘
    ↓
Resposta com 4 abas + quiz opcional
```

### Fluxo de Dados

```
User Input
    ↓ (sync_external_data)
PhysicsState {
  professor_notes: texto do PDF
  pcloud_repo: conteúdo do repositório
  ufsm_context: match com ementa UFSM
  web_edu_br_text: busca .edu.br live
  intl_refs_text: arXiv + Semantic Scholar
}
    ↓ (build_context)
Contexto priorizado (5 níveis, truncado)
    ↓ (orchestrator.run)
Agentes recebem contexto + modelo LLM
    ↓
4 respostas + quiz
```

---

## 🧪 Passo 9: Rodar Testes

```bash
# Testes de hierarquia de fontes
python test_hierarchy.py

# Testes de integração
python test_integration.py

# Testes de UFSM matching
python test_ufsm_matching.py

# Testes de pipeline completo
python test_source_pipeline.py
```

Todos devem passar (✅).

---

## 🔍 Troubleshooting

### "ModuleNotFoundError: No module named 'streamlit'"

Você esqueceu de instalar dependências ou não ativou o venv.

```bash
source venv/bin/activate  # ativar venv
pip install -r requirements.txt
```

### "AuthenticationError: Invalid API key"

Chave API incorreta ou com saldo zerado.

```bash
python scripts/test_api_keys.py  # mostra qual falhou
# Verifique a chave em https://platform.deepseek.com (ou outro provedor)
```

### "StreamlitAPIException: Cannot write to AppSession"

Você rodou `python src/app.py` em vez de `streamlit run app.py`.

```bash
cd src
streamlit run app.py    # correto!
```

### "pCloud link not found / 404"

O link expirou ou foi deletado.

```bash
# Crie um novo link:
# 1. Acesse https://pcloud.com
# 2. Pasta → Get public link
# 3. Cole novo link na sidebar
```

### Resposta não aparece / demora muito

Possíveis causas:
- 🌐 Conexão lenta (aguarde)
- 🔌 Serviço de IA down (teste com outro modelo)
- 📊 Busca web habilitada (desabilite o toggle "🌐 Busca Web Inteligente")

---

## 📞 Obter Ajuda

Se algo não funciona:

1. Verifique este guia novamente (procure sua erro no Troubleshooting)
2. Rode `python scripts/test_api_keys.py` para diagnosticar
3. Verifique logs do Streamlit (última aba do navegador, botão "≡")
4. Abra issue em https://github.com/hansufsm/TutorIAFisica/issues

---

## 📚 Próximos Passos

Depois de funcionar:

- Leia [ARCHITECTURE.md](ARCHITECTURE.md) para entender o pipeline
- Verifique [SOURCE_PIPELINE.md](SOURCE_PIPELINE.md) para a hierarquia de 5 fontes
- Consulte [legado.md](../legado.md) para entender decisões de design
- Veja roadmaps em `roadmaps/` para contribuir com melhorias

---

## 🛠️ Para Contribuidores

Se quer modificar código:

### Adicionar novo agente
1. Crie classe em `src/agents/` ou direto em `src/core.py`
2. Herde de `TutorIAAgent`
3. Implemente `ask()` method
4. Adicione ao pipeline em `PhysicsOrchestrator.run()`

### Adicionar novo modelo
(Veja seção 7.2 acima)

### Rodar em modo debug
```bash
# Edite .streamlit/config.toml:
[logger]
level = "debug"

# Restart app
streamlit run app.py --logger.level=debug
```

---

**Pronto!** 🎉 Você pode agora usar TutorIAFisica para tutoria inteligente de Física.
