# TutorIAFisica — Documentação Completa (Índice Central)

> **Versão:** v0.4 | **Data:** Abril 2026 | **Status:** Ativa

---

## 📋 Índice de Documentação

Bem-vindo! Abaixo você encontra a documentação completa do projeto, organizada por audiência e tópico.

### 👥 Para Usuários Finais

- **[README.md](README.md)** — Visão geral, funcionalidades principais, como usar o app
- **[docs/SOURCE_PIPELINE.md](docs/SOURCE_PIPELINE.md)** — Como o sistema prioriza fontes de conhecimento

### 🛠️ Para Desenvolvedores

**Setup e Primeira Execução:**
- **[docs/DEVELOPER_SETUP.md](docs/DEVELOPER_SETUP.md)** ⭐ **COMECE AQUI** — Guia passo-a-passo para configurar o ambiente
  - Pré-requisitos e dependências
  - Setup de cada provedor de IA (DeepSeek, Gemini, OpenAI, Claude, etc.)
  - Como testar conectividade
  - Troubleshooting

**Entendendo o Sistema:**
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — Arquitetura técnica detalhada
  - Pipeline de agentes (5 agentes especializados)
  - Diagrama de fluxo de dados
  - Classes principais (PhysicsState, TutorIAAgent, PhysicsOrchestrator)
  - Fallback de modelos, hierarquia de fontes, integrações

- **[CLAUDE.md](CLAUDE.md)** — Guia técnico para Claude Code
  - Padrões de código e convenções
  - Como adicionar novos agentes ou modelos
  - Debugging tips, importantes invariantes

**Histórico e Decisões:**
- **[legado.md](legado.md)** — Evolução histórica do sistema
  - Origem (FisicaIA 2025) até transformação (TutorIAFisica 2026)
  - Decisões arquiteturais e por que foram feitas
  - Problemas resolvidos durante desenvolvimento
  - Timeline completo de versões

### 🏗️ Stack e Deployment

**Stack Atual (v0.4):**
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** → Seção "Stack e Performance"
  - Streamlit 1.30+ (UI)
  - LiteLLM 1.20+ (Multi-provider LLM orchestration)
  - Python 3.11+
  - Integracões: pCloud, arXiv, DuckDuckGo, Semantic Scholar

**Stack Futuro (Planejado):**
- **[docs/STACK_FUTURO.md](docs/STACK_FUTURO.md)** — Roadmap de migração para v1.0
  - Frontend: Next.js + React (Cloudflare Pages)
  - Backend: FastAPI + Python (Render.com)
  - Database: Supabase (PostgreSQL + Auth)
  - Custo: R$ 0,00 (gratuito)

### 🗺️ Roadmaps (Trabalho Futuro)

Melhorias planejadas, organizadas por prioridade:

**UX/Design (15 issues, ~2 horas):**
- **[roadmaps/roadmap-ux-design.md](roadmaps/roadmap-ux-design.md)**
  - 🔴 Fase 1 CRÍTICA (30 min): CSS agent identity, quiz feedback, debug panel, pCloud data leak
  - 🟠 Fase 2 ALTA (45 min): Mobile responsiveness, sidebar hierarchy, onboarding
  - 🟡 Fase 3 POLISH (40 min): Confidence indicators, code cleanup, documentation

**Pedagógicas (7 melhorias, roadmap ongoing):**
- **[roadmaps/roadmap-pedagogico.md](roadmaps/roadmap-pedagogico.md)**
  - Student Model persistente (entre sessões)
  - Detecção explícita de misconceptions
  - Repetição espaçada adaptativa (SM-2)
  - Painel de progresso do aluno
  - Modo híbrido professor-IA

---

## 🚀 Como Começar

### Opção 1: Usar o App (Usuário)
1. Leia [README.md](README.md)
2. Clone o repositório
3. Siga o setup em [docs/DEVELOPER_SETUP.md](docs/DEVELOPER_SETUP.md)
4. Comece a fazer perguntas! ✨

### Opção 2: Contribuir (Desenvolvedor)
1. Leia [legado.md](legado.md) para entender a evolução
2. Leia [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) para entender o design
3. Siga [docs/DEVELOPER_SETUP.md](docs/DEVELOPER_SETUP.md) para setup
4. Consulte [CLAUDE.md](CLAUDE.md) para padrões de código
5. Escolha um roadmap e comece a contribuir!

### Opção 3: Migrar para Stack Futuro
1. Leia [docs/STACK_FUTURO.md](docs/STACK_FUTURO.md) (41K, bem detalhado)
2. Crie contas em Supabase, Render, Cloudflare Pages
3. Siga as etapas numeradas no documento

---

## 📁 Estrutura de Arquivos

```
TutorIAFisica/
├── README.md                           ← Visão geral para usuários
├── CLAUDE.md                           ← Guia para Claude Code
├── legado.md                           ← Histórico e decisões
│
├── src/
│   ├── app.py                          ← Streamlit UI
│   ├── core.py                         ← Orquestrador + agentes
│   ├── config.py                       ← Modelos, chaves, fallback
│   ├── utils/
│   │   ├── pcloud_manager.py           ← Integração pCloud
│   │   └── web_searcher.py             ← Buscas web
│   └── agents/                         ← Placeholder (agents em core.py)
│
├── data/
│   └── ufsm_syllabus.json              ← Disciplinas UFSM
│
├── docs/
│   ├── ARCHITECTURE.md                 ← Arquitetura detalhada
│   ├── SOURCE_PIPELINE.md              ← Hierarquia de fontes
│   ├── DEVELOPER_SETUP.md              ← Setup passo-a-passo
│   └── STACK_FUTURO.md                 ← Roadmap migração
│
├── roadmaps/
│   ├── roadmap-ux-design.md            ← 15 issues UX, 3 fases
│   └── roadmap-pedagogico.md           ← Melhorias pedagógicas
│
├── scripts/
│   ├── test_api_keys.py                ← Teste de conectividade
│   └── debug_materials.py              ← Debug de materiais
│
├── tests/
│   ├── test_hierarchy.py
│   ├── test_integration.py
│   ├── test_ufsm_matching.py
│   └── test_source_pipeline.py
│
├── .streamlit/
│   └── config.toml                     ← Configuração Streamlit
│
├── requirements.txt                     ← Dependências Python
├── .env                                 ← Variáveis de ambiente (git ignored)
├── .gitignore
└── TutorIAFisica_DOCUMENTACAO_COMPLETA.md ← Este arquivo

**Não incluir em repositório:**
- venv/ (virtual environment)
- __pycache__/
- .DS_Store
- .env (arquivo com chaves API)
```

---

## 🎯 Visão Geral Rápida (2 minutos)

### O que é TutorIAFisica?

Um **sistema de tutoria inteligente para Física** que funciona como um esquadrão de 5 agentes especializados:

1. 🔵 **Intérprete** — Faz perguntas reflexivas (método socrático)
2. 🟢 **Solucionador** — Resolve com rigor matemático (LaTeX, SI units)
3. 🟠 **Visualizador** — Cria gráficos interativos (Python)
4. 🟣 **Curador** — Conecta a materiais acadêmicos reais
5. 🔴 **Avaliador** — Cria quizes e feedback formativo

### Como funciona?

```
Aluno digita: "Como resolver f=ma para esta situação?"
    ↓
Sistema busca em 5 níveis de fontes:
  1. Notas do professor
  2. Documentos adotados na disciplina
  3. Ementa UFSM
  4. Portais .edu.br (busca web)
  5. Referências internacionais (arXiv, Scholar)
    ↓
Cada agente processa e produz:
  - Socratic question (why? how?)
  - Rigorous solution ($F = ma = ...$)
  - Interactive visualization
  - Real academic references
  - Quiz challenge
    ↓
Resposta em 4 abas + quiz opcional
```

### Por que é diferente?

- ✅ **Multiagente**: Cada dimensão tem um especialista
- ✅ **Socrático**: Não dá resposta direto, faz perguntas
- ✅ **Robusto**: 6 modelos de IA com fallback automático
- ✅ **Transparente**: Cita exatamente de onde veio cada informação
- ✅ **Adaptativo**: Busca web em tempo real para materiais atualizados

---

## 📊 Estatísticas do Projeto

| Métrica | Valor |
|---------|-------|
| **Linhas de código** | ~900 (Python) |
| **Documentação** | ~2500 linhas |
| **Agentes** | 5 (Intérprete, Solver, Viz, Curator, Evaluator) |
| **Modelos de IA suportados** | 9+ (DeepSeek, Gemini, Claude, OpenAI, Grok, etc.) |
| **Fontes de conhecimento** | 5 níveis + busca web |
| **Tempo de resposta** | 15-30s (sem web search) ou 25-50s (com web search) |
| **Linguagem** | Python 3.11+ |
| **Framework** | Streamlit 1.30+ |
| **Última atualização** | Abril 2026 |

---

## 🔗 Links Importantes

- **GitHub**: https://github.com/hansufsm/TutorIAFisica
- **Licença**: MIT (veja [LICENSE](LICENSE))
- **Autores**: Hans (UFSM) + Claude (Anthropic)

---

## 💡 Próximos Passos

1. **Se está começando**: Leia [docs/DEVELOPER_SETUP.md](docs/DEVELOPER_SETUP.md)
2. **Se vai contribuir**: Escolha um roadmap em `roadmaps/`
3. **Se vai migrar**: Siga [docs/STACK_FUTURO.md](docs/STACK_FUTURO.md)
4. **Se quer entender tudo**: Leia em ordem:
   - [legado.md](legado.md) (história)
   - [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) (design)
   - [docs/SOURCE_PIPELINE.md](docs/SOURCE_PIPELINE.md) (fontes)
   - [CLAUDE.md](CLAUDE.md) (código)

---

## 📞 Suporte

Se tem dúvidas ou encontrou um bug:

1. Consulte [docs/DEVELOPER_SETUP.md#troubleshooting](docs/DEVELOPER_SETUP.md#troubleshooting)
2. Verifique os roadmaps (pode ser um issue conhecido)
3. Abra uma issue em https://github.com/hansufsm/TutorIAFisica/issues

---

**Última atualização:** 26 de Abril de 2026 | **Versão:** 0.4 (Streamlit) | **Próxima versão:** v1.0 (FastAPI + Next.js)

*Documentação mantida com ❤️ pela comunidade TutorIAFisica*
