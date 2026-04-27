# TutorIAFisica — Histórico de Evolução e Decisões Arquiteturais

> Registro histórico do sistema desde sua origem em FisicaIA (2025) até TutorIAFisica (2026)

---

## Origem: FisicaIA (2025)

**Contexto:** Projeto inicial de script único para análise de problemas de Física usando IA.

**Características:**
- Sequência de scripts independentes
- Sem orquestração de agentes
- Resposta linear: pergunta → resposta direta (modelo único)
- Foco em rigor matemático e LaTeX

**Limitações que levaram à evolução:**
- Não havia separação de responsabilidades (tudo em um script)
- Impossível trocar de modelo de IA facilmente
- Sem feedback pedagógico estruturado (método socrático)
- Sem conexão a materiais acadêmicos reais

---

## Transformação: TutorIAFisica (2026)

Reescrita completa como **ecossistema de agentes inteligentes** orquestrados.

### v0.1 — Pipeline Básico (Abril 2025 - primeiras semanas)

**Decisão:** Implementar padrão **Pipeline + State**

- **PhysicsState:** Objeto mutável central que flui através do pipeline
- **5 Agentes especializados:**
  - 🔵 **Intérprete** — Método socrático, perguntas reflexivas
  - 🟢 **Solucionador** — Rigor matemático, análise dimensional, LaTeX
  - 🟠 **Visualizador** — Código Python interativo (Matplotlib/Plotly)
  - 🟣 **Curador** — Conexão a materiais acadêmicos reais (UFSM, portais)
  - 🔴 **Avaliador** — Avaliação formativa, perguntas de quiz

- **TutorIAAgent:** Classe base abstraindo chamadas a LLM
- **PhysicsOrchestrator:** Coordenador que executa o pipeline

**Por que?** (argumentação arquitetural)
- Separação de responsabilidades — cada agente é um especialista
- Reutilizabilidade — cada agente pode ser testado isoladamente
- Flexibilidade — fácil adicionar novos agentes
- State como source of truth — debugging facilitado

---

### v0.2 — Gerenciamento de Modelos com Fallback (Abril 2026 - semana 2)

**Decisão:** Usar **LiteLLM** para abstração multi-provider

```python
AVAILABLE_MODELS = {
    "Gemini 3.0 Preview": {"id": "gemini/gemini-1.5-pro", "multimodal": True},
    "Claude 3.5 Sonnet": {"id": "claude-3-5-sonnet-20241022", "multimodal": True},
    "DeepSeek Chat": {"id": "deepseek/deepseek-chat", "multimodal": False},
    # ...mais modelos
}

MODEL_PREFERENCE_ORDER = [
    "DeepSeek Chat",
    "Grok 2 Vision",
    "Gemini 1.5 Flash",
    "OpenAI GPT-3.5 Turbo",
    # ...fallback chain
]
```

**Por que LiteLLM?** (vs SDKs individuais de cada provedor)
- ✅ Uma única API para múltiplos provedores (reduz linhas de código)
- ✅ Fallback automático incorporado (suporte nativo)
- ✅ Rate limit handling centralizado
- ✅ Logging e métricas unificadas
- ❌ Overhead minúsculo, mas não relevante para tutoria

**Sistema de API Keys:**
- Primária: Lê do `.env` via `os.getenv()`
- Fallback: Input runtime via Streamlit sidebar (`st.text_input`)
- Vantagem: Não forçar arquivo `.env` para usuários básicos

**Suporte Multimodal Condicional:**
- Cada modelo tem flag `multimodal: True/False` em `config.py`
- UI desabilita upload de imagem para modelos texto-only
- Aviso claro se modelo não suporta multimodal

---

### v0.3 — Source-Attributed Context Pipeline (Abril 2026 - semana 3)

**Decisão:** Separar explicitamente as fontes de conhecimento no `PhysicsState`

```python
# Antes (v0.1):
context = teacher_notes + student_materials + pcloud_repo

# Depois (v0.3):
state.professor_notes_text = teacher_notes      # nível 1a
state.pcloud_session_text = student_materials   # material do aluno
state.pcloud_repo_text = repo_content           # nível 1b repositório
state.ufsm_context = ""                         # nível 3 (UFSM match)
```

**Impacto:**
- Citação inline: `[Notas do Professor]`, `[Ementa UFSM]`, `[Modelo de IA]`
- Transparência: Estudante sabe de onde veio cada informação
- Rastreabilidade: Qual material gerou qual resposta?

**UFSM Syllabus Matching:**
- Adição de `data/ufsm_syllabus.json` (temas e disciplinas UFSM)
- Método `_check_ufsm_syllabus()` mapeia pergunta → disciplina oficial
- Exemplo: "potencial elétrico" → Física II (FSC1028)

**Por que?** (educação baseada em evidência)
- Springer ITS Guidelines (2023): "Attribution of sources is critical for trust"
- OECD Outlook 2026: "Transparency about knowledge origins improves learning outcomes"

---

### v0.4 — Hierarquia de 5 Fontes + Busca Web em Tempo Real (Abril 2026 - semana 4)

**Decisão:** Implementar priorização de fontes com busca web automática

```
Nível 1: Materiais do Professor (4000 chars max)
  └─ professor_notes_text + pcloud_repo_text
Nível 2: Documentos Adotados (2000 chars max)
  └─ adopted_docs_text (PDFs da disciplina)
Nível 3: Ementa UFSM (600 chars max)
  └─ ufsm_context (local match)
Nível 4: Portais Acadêmicos .edu.br (1500 chars max)
  └─ web_edu_br_text (busca DuckDuckGo live)
Nível 5: Referências Internacionais (1200 chars max)
  └─ intl_refs_text (arXiv + Semantic Scholar)

Extra: Material do Aluno (2000 chars max)
  └─ pcloud_session_text (fora da hierarquia)
```

**Novo Módulo: `WebSearcher`**
```python
class WebSearcher:
    @staticmethod
    def search_edu_br(topic) → duckduckgo-search (free, sem API key)
    
    @staticmethod
    def search_arxiv(topic) → export.arxiv.org/api (free, sem API key)
    
    @staticmethod
    def search_semantic_scholar(topic) → api.semanticscholar.org (free, sem API key)
```

**Fluxo de Pipeline Atualizado:**
```
1. sync_external_data()          → carrega: professor, repo, adotados, pCloud
2. Agente Intérprete             → identifica conceitos + dimensões
3. _check_ufsm_syllabus()        → encontra disciplina (nível 3)
4. sync_web_sources()             → busca .edu.br + arXiv (se toggle ativo)
5. build_context()                → monta contexto com 5 níveis + truncação
6. Agentes restantes             → Solucionador, Visualizador, Curador, Avaliador
```

**Decisões de Design:**
- **Por que apenas search após Intérprete?** Eficiência: busca apenas tópicos relevantes
- **Por que truncação?** Evitar contexto gigante que consume tokens (economia de custos)
- **Por que DuckDuckGo?** Sem API key, aceita filtros site:, rápido
- **Por que arXiv + Semantic Scholar?** Open access gratuito, qualidade academic
- **Por que toggle de web search?** Alguns usuários preferem respostas rápidas (local only)

---

## Decisões Arquiteturais Documentadas

### 1. Por que LiteLLM e não SDKs individuais?

**Alternativas consideradas:**
- ❌ `openai` + `anthropic` + `google` SDKs (separado)
  - ❌ 3x mais código
  - ❌ Fallback manual complexo
  - ❌ Sem logging centralizado
- ✅ **LiteLLM** (usado)
  - ✅ Uma API para tudo
  - ✅ Fallback automático
  - ✅ Erro handling unificado

**Resultado:** `TutorIAAgent.ask()` é method único que funciona com qualquer modelo

---

### 2. Por que Streamlit e não FastAPI+React nativo?

**Alternativas consideradas:**
- ❌ Implementar do zero com FastAPI + React
  - ❌ 10x mais tempo de desenvolvimento
  - ❌ DevOps complexity (dockerização, deployment)
- ✅ **Streamlit** (usado em 2026)
  - ✅ Deploy em 1 comando (`streamlit run app.py`)
  - ✅ State management automático
  - ✅ Componentes UI prontos (sliders, text_input, expanders)
  - ✅ KaTeX integrado nativamente (desde v1.30)

**Planificação futura:** `TutorIAFisica_roadmap_deploy.md` → migração para FastAPI+Next.js (docs/STACK_FUTURO.md) com pCloud → Supabase

---

### 3. Por que pCloud para notas do professor (não Google Drive)?

**Alternativas consideradas:**
- ❌ Google Drive API
  - ❌ OAuth 2.0 complexo
  - ❌ Quota limits (1000 chamadas/100s por usuário)
  - ❌ Requer autenticação do usuário
- ✅ **pCloud** (usado)
  - ✅ Links públicos sem auth
  - ✅ API pública generosa (showpublink, getpublinkdownload)
  - ✅ Professor já usava pCloud → sem onboarding extra

**Implementação:** `src/utils/pcloud_manager.py`
- Detecta URL pCloud ou direct link
- Tenta EU endpoint, fallback global endpoint
- Extrai PDF com `pypdf` via BytesIO (in-memory)

---

### 4. Por que hierarquia de 5 níveis (não flat)?

**Alternativas consideradas:**
- ❌ Tudo igual (flat context)
  - ❌ Notas genéricas da internet > notas do professor (problema!)
  - ❌ Sem controle sobre relevância
- ✅ **Hierarquia de 5 níveis** (usado)
  - ✅ Respeita autoridade pedagógica (professor > internet genérica)
  - ✅ Suporta curadoria institucional (UFSM ementário)
  - ✅ Fallback gracioso (se sem professor notes → tenta UFSM → tenta web)

**Fundamentação:** OECD Digital Education Outlook (2026) recomenda "prioritize institutional sources over generic AI responses"

---

### 5. Por que não usar ChatGPT Turbo como default (em vez de DeepSeek)?

**Decisão: DeepSeek Chat como modelo default**

- ✅ Free tier generoso
- ✅ Sem throttling excessivo
- ✅ Latência aceitável para tutoria

Mas: OpenAI, Claude, Gemini todos suportados — fallback automático trata da indisponibilidade.

---

## Problemas Resolvidos Durante Desenvolvimento

### 1. **URLs Diretas (filedn.com) Não Funcionavam**

**Problema:** `PCloudManager` assumia só pCloud links
```python
# v0.3 — quebrava com filedn.com
url = "https://filedn.com/SomeFile.pdf"
result = PCloudManager.fetch_notes(url)  # → erro, não é pCloud
```

**Solução:** Método `_fetch_from_direct_url()` que detecta URL não-pCloud e baixa com `requests`
```python
if "pcloud.com" not in url:
    return self._fetch_from_direct_url(url)
```

**Aprendizado:** Validar assunções sobre entrada de usuário

---

### 2. **LaTeX/KaTeX Não Renderizava Corretamente**

**Problema:** Equações apareciam como texto puro `$F = ma$`

**Solução (v0.2):** Usar KaTeX nativo do Streamlit (desde v1.30), remover CDN manual
```toml
# Remover:
# <script src="https://cdn.jsdelivr.net/npm/katex"></script>

# Streamlit renderiza automaticamente:
st.markdown("$F = ma$")
```

---

### 3. **Semantic Scholar Retornava 429 (Rate Limit)**

**Problema:** API falha durante testes intensivos

**Solução (v0.4):** Graceful degradation — se arXiv funciona, não falhar se Semantic Scholar tira timeout
```python
try:
    scholar_results = WebSearcher.search_semantic_scholar(topic)
except Exception:
    scholar_results = ""  # continue com arXiv
```

---

### 4. **pCloud EU vs Global Endpoint**

**Problema:** pCloud Europe endpoint (`eapi.pcloud.com`) falha em alguns casos

**Solução:** Fallback automático global endpoint (`api.pcloud.com`)
```python
try:
    response = requests.post(PCLOUD_API_URL, ...)  # EU
except:
    response = requests.post(PCLOUD_GLOBAL_URL, ...)  # Global fallback
```

---

## Tecnologias Avaliadas MAS NÃO ESCOLHIDAS

| Tecnologia | Por que não | Alternativa escolhida |
|---|---|---|
| Chroma (vector DB) | Overkill para fonte de 5 níveis | Busca por conceitos sem embeddings |
| Pinecone | Custo, vendor lock-in | arXiv + DuckDuckGo search |
| Langchain | Overhead, overkill | LiteLLM direto |
| TensorFlow/PyTorch | Não precisamos treinar modelos | Chamar APIs de modelos prontos |
| Docker | Desenvolvimento em venv suficiente | Docker planejado em STACK_FUTURO.md |
| PostgreSQL | Streamlit não precisa de DB persistente | Supabase planejado para v2 |

---

## Timeline Completa

| Data | Versão | Evento | Autor |
|---|---|---|---|
| ~2025-03 | v0.0 | FisicaIA — scripts únicos | Hans |
| 2026-04-20 | v0.1 | Reescrita como 5-agent pipeline | Hans + Claude |
| 2026-04-22 | v0.2 | Multi-provider LiteLLM + fallback | Hans + Claude |
| 2026-04-24 | v0.3 | Source attribution + UFSM matching | Hans + Claude |
| 2026-04-26 | v0.4 | 5-level hierarchy + web search | Hans + Claude |
| 2026-04-26 | v0.5 | Design review audit (15 issues) | Claude Code (Explore) |
| 2026-04-26 | v1.0 | Documentation reorganization | Hans + Claude (IN PROGRESS) |

---

## Próximos Passos (Roadmaps Abertos)

1. **UX/Design Improvements** (`roadmaps/roadmap-ux-design.md`) — 15 issues, 3 fases, ~2 horas
2. **Pedagogical Enhancements** (`roadmaps/roadmap-pedagogico.md`) — Student Model persistente, repetição espaçada
3. **Stack Migration** (`docs/STACK_FUTURO.md`) — FastAPI + Next.js + Supabase, gratuito

---

*Documento preserva a evolução arquitetural e decisões de design. Consulte para entender por que o sistema é como é.*
