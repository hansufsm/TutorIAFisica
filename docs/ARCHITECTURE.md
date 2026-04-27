# Arquitetura do TutorIAFisica — Design Detalhado

> **Status:** v0.4 (Abril 2026) | **Python:** 3.11+ | **Framework:** Streamlit 1.30+ | **Orquestração:** LiteLLM 1.20+

---

## 🎯 Visão Geral

TutorIAFisica opera como um **pipeline de agentes especializados** que trabalham sequencialmente sobre um **objeto de estado compartilhado** (`PhysicsState`).

Modelo: **Agent Orchestration Pattern** — padrão de design onde múltiplos LLM agents independentes processam dados em fases, cada um adicionando sua expertise.

```
┌─────────────────────────────────────────────────────────────────┐
│  INPUT: "Como resolver f=ma para uma situação específica?"      │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                ┌───────────▼───────────┐
                │  PhysicsState         │
                │ (shared mutable data) │
                └───────────┬───────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
    [1] INT         [2] SOL             [3] VIZ
    Interpreta      Resolve             Visualiza
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                ┌───────────▼───────────┐
                │   [4] CUR  [5] AVA    │
                │   Contextualiza       │
                │   Questiona           │
                └───────────┬───────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│ OUTPUT: 4 abas (Socrática | Matemática | Visualização | Context)│
│         + Quiz opcional (Avaliador)                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🧠 Classes Principais

### 1. `PhysicsState` (src/core.py, ~150 linhas)

**Responsabilidade:** Acumular contexto e resultados através do pipeline.

**Campos críticos:**
```python
class PhysicsState:
    # Entrada
    raw_input: str                    # Pergunta do aluno
    image_input: Optional[Image]      # Imagem opcional (diagram, equation)
    pcloud_url: str                   # Link pCloud da sessão
    
    # Contexto de Fontes (hierarquia de 5 níveis)
    professor_notes_text: str         # Nível 1a: notas do professor
    pcloud_repo_text: str             # Nível 1b: repositório permanente
    adopted_docs_text: str            # Nível 2: documentos adotados
    ufsm_context: str                 # Nível 3: ementa UFSM
    web_edu_br_text: str              # Nível 4: portais .edu.br (busca)
    intl_refs_text: str               # Nível 5: referências internacionais
    pcloud_session_text: str          # Extra: material do aluno
    
    # Metadados
    concepts: List[str]               # Conceitos identificados pelo Intérprete
    ufsm_alignment: str               # Qual disciplina UFSM se alinha
    
    # Saídas de cada agente
    pergunta_socratica: str           # Output Intérprete
    solucao: str                      # Output Solucionador
    codigo_visualizacao: str          # Output Visualizador
    mapa_mental_markdown: str         # Output Curador
    desafio_avaliador: str            # Output Avaliador (quiz)
    quiz_feedback: str                # Feedback após resposta do aluno
    
    # Metadata do modelo
    used_model_display_name: str      # Qual modelo foi usado
    fallback_occurred: bool           # Se houve fallback automático
```

**Métodos:**
- `build_context()` → Monta contexto em ordem de prioridade (5 níveis + truncação)
- `sync_external_data()` → Baixa materiais de pCloud, URL diretas
- `sync_web_sources()` → Busca web (.edu.br, arXiv, Semantic Scholar)
- `_check_ufsm_syllabus()` → Localiza disciplina UFSM relacionada

---

### 2. `TutorIAAgent` (src/core.py, ~80 linhas)

**Responsabilidade:** Interface unificada para chamar qualquer LLM via LiteLLM.

```python
class TutorIAAgent:
    def __init__(self, name: str, system_instruction: str):
        self.name = name
        self.system_instruction = system_instruction
    
    def ask(self, prompt: str, context: str = "", model_id: str = "", 
            api_key: str = "", image: Optional[Image] = None) → str:
        # 1. Construir mensagem (text + image se multimodal)
        # 2. Chamar litellm.completion()
        # 3. Tratar erros (rate limit, auth, API down)
        # 4. Retornar texto
        
        if image and is_model_multimodal(model_id):
            # Codificar imagem como base64
            image_b64 = encode_image_base64(image)
            # Incluir no message content
```

**Agentes concretos** (herdam de `TutorIAAgent`):

| Agente | Nome | Responsabilidade | Exemplo de Output |
|--------|------|---|---|
| 🔵 **Intérprete** | `InterpreterAgent` | Identifica conceitos, faz perguntas socráticas | "Qual grandeza está sendo pedida? Qual você já conhece?" |
| 🟢 **Solucionador** | `SolverAgent` | Rigor matemático, SI, dimensional analysis | "$F = ma = 5 \text{ kg} \times 2 \text{ m/s}^2 = 10 \text{ N}$" |
| 🟠 **Visualizador** | `VisualizerAgent` | Código Python runnable (Matplotlib/Plotly) | `import matplotlib.pyplot as plt` ... |
| 🟣 **Curador** | `CuratorAgent` | Materiais acadêmicos, referências reais | "[Ementa UFSM] FSC1028 aborda..." |
| 🔴 **Avaliador** | `EvaluatorAgent` | Quiz, perguntas formativas, feedback socrático | "Sua resposta toca um ponto importante, mas..." |

---

### 3. `PhysicsOrchestrator` (src/core.py, ~200 linhas)

**Responsabilidade:** Coordenar o pipeline, fallback, logging.

```python
class PhysicsOrchestrator:
    def __init__(self, selected_model_display_name: str, runtime_keys: Dict):
        self.selected_model = selected_model_display_name
        self.runtime_keys = runtime_keys  # API keys passadas via UI
        self.interpretar = InterpreterAgent()
        self.solucionador = SolverAgent()
        # ... outros agentes
    
    def run(self, input_data: str, teacher_notes: str = "", 
            pcloud_url: str = "", repo_url: str = "", 
            adopted_url: str = "", enable_web_search: bool = True,
            image: Optional[Image] = None, on_progress = None) → PhysicsState:
        
        state = PhysicsState(raw_input=input_data, pcloud_url=pcloud_url, ...)
        
        # 1. Carregar materiais externos
        state.sync_external_data(on_progress, repo_url, adopted_url)
        
        # 2. Intérprete (identifica conceitos)
        state.pergunta_socratica = self.interpretar.ask(
            input_data, context=state.build_context(), ...)
        
        # 3. Check UFSM match
        state._check_ufsm_syllabus()
        
        # 4. Busca web (se toggle ativo)
        if enable_web_search:
            state.sync_web_sources(on_progress)
        
        # 5. Rebuild context com web sources
        full_context = state.build_context()
        
        # 6. Agentes paralelos (ou sequenciais, conforme config)
        # Nota: em Streamlit, não há paralelismo real, mas podemos:
        for agent_name, agent in [("Solucionador", self.solucionador), ...]:
            try:
                output = agent.ask(..., context=full_context, ...)
                # Guardar output em state
            except (RateLimitError, AuthenticationError, APIError):
                # Fallback automático
                self.selected_model = MODEL_PREFERENCE_ORDER.next()
                # Retry com novo modelo
        
        return state
```

**Fallback Logic:**
```
User escolhe DeepSeek
    ↓ (tenta chamar)
Se sucesso → volta resultado
Se falha (RateLimitError, AuthenticationError, APIError):
    → Tenta modelo #2 (Grok 2 Vision)
    → Se falha, tenta #3 (Gemini 1.5 Flash)
    → ... até 8 tentativas
    → Se todas falham → erro para o usuário
```

---

## 📊 Fluxo de Dados (Pipeline)

### Entrada do Usuário
```
└── Pergunta de texto
    ├── Opcional: arquivo PDF (notas)
    ├── Opcional: imagem (diagrama, equação)
    └── Opcional: links (pCloud, GitHub, etc.)
```

### Fase 1: Load Context (3-5 segundos)
```
sync_external_data():
  ├── PDFs carregados pelo usuário
  │   └─ PdfReader.extract_text() via pypdf
  ├── pCloud repositório (repo_url)
  │   └─ PCloudManager.fetch_notes() via requests
  ├── Documentos adotados (adopted_url)
  │   └─ Mesmo que acima
  └─ Resultado: professor_notes_text, pcloud_repo_text, etc. populados
```

### Fase 2: Interpreter Agent (2-3 segundos)
```
Agente 🔵 Intérprete recebe:
  ├─ raw_input (pergunta do aluno)
  └─ contexto vazio (sem materiais ainda)

Output: pergunta_socratica (questão reflexiva)
Efeito colateral: state.concepts populado (["força", "trabalho", ...])
```

### Fase 3: UFSM Matching (< 1 segundo, local)
```
_check_ufsm_syllabus():
  ├─ Procura conceitos em state.concepts
  ├─ Match contra data/ufsm_syllabus.json
  ├─ Localiza disciplina UFSM (ex: "Física II - FSC1028")
  └─ state.ufsm_context preenchido com matching content
```

### Fase 4: Web Search (opcional, 10-15 segundos se ativo)
```
sync_web_sources():
  ├─ DuckDuckGo("força newton site:.edu.br")
  │  └─ web_edu_br_text preenchido
  ├─ arXiv API("force AND newton")
  │  └─ intl_refs_text preenchido (parte 1)
  └─ Semantic Scholar API("force newton")
     └─ intl_refs_text preenchido (parte 2)
```

### Fase 5: Build Complete Context (< 1 segundo)
```
build_context() → string de até ~10.000 caracteres:

### [NOTAS DO PROFESSOR] (4000 chars max)
...

### [DOCUMENTOS ADOTADOS] (2000 chars max)
...

### [EMENTA UFSM] (600 chars max)
...

### [PORTAIS ACADÊMICOS .edu.br] (1500 chars max)
...

### [REFERÊNCIAS INTERNACIONAIS] (1200 chars max)
...

### [MATERIAL DO ALUNO] (2000 chars max)
...
```

### Fase 6: Parallel Agents (4 agentes, 10-20 segundos total)
```
Cada agente recebe:
  ├─ prompt específico
  ├─ contexto completo (5 níveis)
  ├─ modelo selecionado (com fallback)
  └─ API key (do .env ou runtime)

Agentes:
  ├─ 🟢 Solucionador → solucao (LaTeX + passos)
  ├─ 🟠 Visualizador → codigo_visualizacao (Python)
  ├─ 🟣 Curador → mapa_mental_markdown (recursos)
  └─ 🔴 Avaliador → desafio_avaliador (quiz)

(Nota: Em Streamlit puro, execução é sequencial, não paralela)
```

### Saída (4 abas + Quiz)
```
├─ Aba 1 [🔵 Socrática]: pergunta_socratica
├─ Aba 2 [🟢 Procedural]: solucao
├─ Aba 3 [🟠 Intuição]: codigo_visualizacao + renderizado
├─ Aba 4 [🟣 Contextual]: mapa_mental_markdown
└─ Botão extra: "Desafie-me!" → quiz via desafio_avaliador
```

---

## 🔐 Hierarquia de Fontes (5 Níveis)

**Ordem de prioridade (em contexto):**

```
1. PROFESSOR (Level 1)           ← Máxima autoridade local
   ├─ Notas manuais upload
   └─ Repositório pCloud permanente

2. DISCIPLINA (Level 2)          ← Curadoria de origem
   └─ Documentos oficialmente adotados

3. INSTITUCIONAL (Level 3)       ← Fonte oficial UFSM
   └─ Ementa + temas + bibliografia

4. WEB BRASILEIRA (Level 4)      ← Pesquisa em tempo real
   └─ Portais .edu.br, repositórios federais

5. INTERNACIONAL (Level 5)       ← Open access global
   ├─ arXiv (papers)
   └─ Semantic Scholar (citações)

EXTRA: ALUNO (sem hierarquia)    ← Materiais específicos da sessão
   └─ pCloud sessão (exercícios, trabalhos)
```

**Truncação por nível:**
```
Max chars por nível: professor(4000) > adotados(2000) > ufsm(600) > web(1500) > intl(1200)
→ Evita contexto gigante (eficiência de tokens)
```

**Citação inline:**
Agents instruídos a citar: `[Notas do Professor]`, `[Ementa UFSM]`, `[Portais .edu.br]`, `[Referências Internacionais]`, `[Modelo de IA]`

---

## 🔄 Fluxo de Fallback de Modelos

```python
MODEL_PREFERENCE_ORDER = [
    "DeepSeek Chat",                  # Free, chat-only, default
    "Grok 2 Vision",                  # Free, multimodal, alternative
    "Gemini 1.5 Flash",               # Free, multimodal, fast
    "OpenAI GPT-3.5 Turbo",           # Paid, text-only
    "Claude 3.5 Sonnet",              # Paid, multimodal
    "Claude 3 Haiku",                 # Paid, text-only
    "Claude 3 Opus",                  # Paid, smartest but slow
    "Perplexity Sonar",               # Paid, online search
    "Manusc Model",                   # Placeholder
]
```

**Em caso de erro:**
1. Catch `litellm.RateLimitError` → próximo modelo
2. Catch `litellm.AuthenticationError` → próximo modelo
3. Catch `litellm.APIError` → próximo modelo
4. Se 8 falhas → retornar erro ao usuário

**UI Feedback:**
- Se fallback ocorreu → mostrar badge "🔄 Modelo utilizado: [novo modelo]"

---

## 📁 Estrutura de Arquivos

```
TutorIAFisica/
├── src/
│   ├── app.py                    # UI Streamlit (365 linhas)
│   ├── core.py                   # Orquestrador + agentes (438 linhas)
│   ├── config.py                 # Modelos, chaves, fallback (94 linhas)
│   ├── agents/                   # Placeholder (agents em core.py)
│   ├── utils/
│   │   ├── pcloud_manager.py     # Integração pCloud (85 linhas)
│   │   └── web_searcher.py       # DuckDuckGo, arXiv, Scholar (137 linhas)
│   └── __init__.py
│
├── data/
│   └── ufsm_syllabus.json        # Disciplinas UFSM (60 linhas)
│
├── docs/
│   ├── ARCHITECTURE.md           # ← Este arquivo
│   ├── SOURCE_PIPELINE.md        # Detalhe de hierarquia
│   ├── DEVELOPER_SETUP.md        # Setup passo-a-passo
│   └── STACK_FUTURO.md           # Roadmap de migração
│
└── requirements.txt               # 10 dependências
```

---

## 🔗 Integrações Externas

| Serviço | Tipo | Auth | Função |
|---------|------|------|--------|
| **DeepSeek** | API | API Key | LLM padrão |
| **Gemini** | API | API Key | LLM multimodal |
| **Claude** | API | API Key | LLM alternativo |
| **OpenAI** | API | API Key | LLM alternativo |
| **Grok** | API | API Key | LLM multimodal |
| **pCloud** | API | Nenhuma* | Armazenamento de notas |
| **arXiv** | API | Nenhuma | Papers acadêmicos |
| **Semantic Scholar** | API | Nenhuma | Citações |
| **DuckDuckGo** | Search | Nenhuma | Busca .edu.br |

*pCloud usa links públicos sem autenticação de API

---

## 📊 Complexidade e Performance

| Operação | Tempo | Notas |
|----------|-------|-------|
| Load contexto | 3-5s | PDF parsing + pCloud fetch |
| Interpreter | 2-3s | Chamada LLM pequena |
| UFSM match | <1s | Local regex-like |
| Web search | 10-15s | 3 APIs em série (pode paralelizar) |
| Autres agents | 10-20s | 4 LLM calls em série |
| **Total** | **27-54s** | Sem web: 15-30s |

---

## 🎓 Convenções Pedagógicas

Todos os agentes seguem:
- ✅ LaTeX para equações (`$...$` ou `$$...$$`)
- ✅ Unidades SI consistentes
- ✅ Análise dimensional explícita
- ✅ Método socrático (Intérprete e Avaliador)
- ✅ Citação de fontes inline

---

*Para mais detalhes, consulte `legado.md` (evolução histórica) e roadmaps (melhorias futuras).*
