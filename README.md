# 🌌 TutorIAFisica: Mentor Inteligente para Ensino de Física

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/framework-Streamlit-FF4B4B)](https://streamlit.io/)
[![AI Orchestration](https://img.shields.io/badge/Orchestration-LiteLLM-FF5733)](https://github.com/BerriAI/litellm)
[![Compliance](https://img.shields.io/badge/compliance-Secure%20API%20Keys-brightgreen)]()
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## 📚 Sobre o Projeto

O **TutorIAFisica** é a evolução do projeto **FisicaIA (2025)**, transformado de uma sequência de scripts em um **ecossistema de agentes inteligentes** focados em **Aprendizagem Significativa**, **Rigor Matemático** e **Curadoria Acadêmica**.

Projetado para o ensino superior de física, esta versão (v2026) implementa uma **arquitetura de orquestração de agentes** que não apenas entregam respostas, mas dialogam com o aluno através do método socrático, validam dimensionalidade, geram visualizações intuitivas e conectam o conhecimento a recursos acadêmicos reais.

---

## 🧠 As 4 Dimensões da Tutoria Inteligente

O TutorIAFisica processa cada dúvida do aluno em **quatro dimensões fundamentais**, garantindo uma resposta holística:

### 🔵 **Dimensão Socrática** (Intérprete)
Não entrega a resposta de imediato. Desconstrói o problema e desafia o aluno com perguntas reflexivas para validar a compreensão conceitual. Foca no diálogo e na construção de entendimento.

### 🟢 **Dimensão Procedimental** (Solucionador)
Foca na análise dimensional e no passo a passo matemático rigoroso. Valida unidades de medida, aplica formulas com precisão e utiliza **LaTeX** para clareza científica absoluta.

### 🟠 **Dimensão Intuitiva** (Visualizador)
Transforma equações abstratas em **intuição física visual**. Gera código Python funcional (Matplotlib, Plotly) e simulações interativas que permitem exploração dinâmica.

### 🟣 **Dimensão Contextual** (Curador)
Conecta o problema a:
- 🔗 **Aplicações Reais:** Desfibriladores, pintura eletrostática, circuitos práticos
- 📚 **Curadoria Acadêmica:** Links diretos para repositórios de Universidades Federais (UFSM, UFRGS, USP)
- 📹 **Recursos Multimodais:** Sugestão de vídeos, mapas mentais, exercícios extras

---

## 🤖 Motores de IA e Gerenciamento de Fallback

### 1. Seleção de Modelo
Na barra lateral, você pode escolher seu motor de IA preferido entre os disponíveis:
- Gemini 3.0 Preview (Multimodal, Padrão)
- Gemini 2.0 Flash (Multimodal)
- Gemini 1.5 Flash (Multimodal)
- OpenAI GPT-3.5 Turbo (Texto)
- Claude 3 Sonnet (Texto)
- Claude 3 Haiku (Texto)
- Claude 3 Opus (Texto)
- Perplexity Online (Texto)
- DeepSeek Chat (Texto)
- Manusc Model (Placeholder)

### 2. Gerenciamento de Chaves API
- **Configuração:** Chaves API são lidas primariamente do arquivo `.env`.
- **Input Runtime:** Se a chave para o modelo selecionado ou um modelo de fallback necessário não for encontrada no `.env`, um campo de texto (`st.text_input`) aparecerá na sidebar para inserção manual naquela sessão.

### 3. Mecanismo de Fallback Automático
- **Ordem de Preferência:** Se o modelo primário selecionado falhar (ex: `RateLimitError`, `AuthenticationError`, `APIError` do LiteLLM), o sistema tentará automaticamente os modelos na seguinte ordem:
    1. Gemini 3.0 Preview
    2. Gemini 1.5 Flash
    3. OpenAI GPT-3.5 Turbo
    4. Claude 3 Sonnet
    5. Claude 3 Haiku
    6. Claude 3 Opus
    7. Perplexity Online
    8. DeepSeek Chat
    9. Manusc Model
- **Notificação:** O usuário será informado na interface se um fallback automático ocorrer.

### 4. Limitações Multimodais
- Modelos marcados como text-only (ex: DeepSeek Chat, GPT-3.5 Turbo) não processarão imagens. O upload de foto será desabilitado ou exibirá um aviso claro nesse caso.

---

## 🚀 Inovações Pedagógicas (State-of-the-Art)

### Multimodalidade Nativa
- Suporte para entrada via **fotos de diagramas e equações manuscritas** (Gemini 1.5+ Pro)
- Reconhecimento automático de símbolos e conversão para LaTeX

### Modo Socrático Avançado
- A IA prioriza **perguntas fundamentais** antes de entregar a solução completa
- Feedback em tempo real: validação de compreensão conceitual
- Desafios pedagógicos interativos com avaliação formativa

### Simulações Executáveis
- Geração automática de **ambientes interativos** em Streamlit e Plotly
- Controles deslizantes para exploração paramétrica de fenômenos
- Visualização dinâmica de conceitos abstratos

### Hierarquia de Fontes (v2026)
- **Nível 1:** Materiais do Professor (notas + repositório)
- **Nível 2:** Documentos Adotados na Disciplina
- **Nível 3:** Ementa UFSM (temas + bibliografia)
- **Nível 4:** Portais Acadêmicos .edu.br (busca web em tempo real)
- **Nível 5:** Referências Internacionais (arXiv, Semantic Scholar)

Cada resposta cita a origem: `[Ementa UFSM]`, `[Material do Professor]`, `[Referências Internacionais]`, `[Modelo de IA]`

---

## 🎯 Módulo de Avaliação Formativa Interativa

Após a explicação principal, um botão **"Desafie-me! Quero testar meu conhecimento"** permite iniciar um quiz rápido.

-   **Geração de Desafios:** O agente `Avaliador` cria perguntas baseadas no tópico discutido.
-   **Interação:** O aluno digita a resposta e envia.
-   **Feedback Socrático:** O sistema avalia a resposta e oferece pistas construtivas em vez de dar a resposta correta diretamente.
-   **Novo Desafio:** Após receber feedback, o aluno pode pedir um novo desafio.

---

## 🏗️ Estrutura do Projeto (Modular Design)

```text
TutorIAFisica/
├── src/
│   ├── agents/          # Especialistas de IA (Intérprete, Matemático, etc.)
│   ├── utils/           # Módulos de suporte (Integração Cloud, PDF)
│   ├── app.py           # Interface de usuário em Streamlit
│   ├── config.py        # Central de configurações e compliance
│   └── core.py          # Orquestrador principal do esquadrão
├── data/
│   └── ufsm_syllabus.json # Base de dados institucional UFSM
├── docs/                # Documentação técnica e planos de estudo
├── .streamlit/config.toml # Configurações de tema do Streamlit
├── requirements.txt     # Dependências do projeto
├── .env                 # Variáveis de ambiente (chaves API, etc.)
└── .gitignore           # Arquivos ignorados pelo Git
```

---

## 🚀 Instalação e Execução

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/hansufsm/TutorIAFisica.git
    cd TutorIAFisica
    ```
2.  **Crie e ative o ambiente virtual:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    # ou .\venv\Scripts\activate # Windows
    ```
3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure suas chaves API:**
    Crie um arquivo `.env` na raiz do projeto (`~/devworkspace/TutorIAFisica/`) e adicione suas chaves:
    ```env
    GEMINI_API_KEY=SUA_CHAVE_GEMINI
    DEEPSEEK_API_KEY=SUA_CHAVE_DEEPSEEK
    OPENAI_API_KEY=SUA_CHAVE_OPENAI
    ANTHROPIC_API_KEY=SUA_CHAVE_CLAUDE
    PERPLEXITY_API_KEY=SUA_CHAVE_PERPLEXITY
    MANUSC_API_KEY=SUA_CHAVE_MANUSC # Se aplicável
    ```
5.  **Inicie o portal:**
    ```bash
    cd src
    streamlit run app.py
    ```
    *No app, selecione seu modelo preferido na sidebar. Se a chave API não estiver no `.env`, um campo aparecerá para inserção runtime.*

---

## 🎨 Identidade Visual

O portal utiliza um **Dark Mode** confortável, com identificação visual pelas **4 dimensões pedagógicas**:

| Cor | Agente | Dimensão |
|-----|--------|----------|
| 🔵 **Azul** | Intérprete | Socrática |
| 🟢 **Verde** | Solucionador | Procedimental |
| 🟠 **Laranja** | Visualizador | Intuitiva |
| 🟣 **Roxo** | Curador | Contextual |
| 🔴 **Vermelho** | Avaliador | Avaliação Formativa |

---

## 🎓 Impacto Educacional

O **TutorIAFisica** foi concebido como **evolução pedagógica para o ensino de engenharia e física**, transformando:

- ❌ **Antes:** Tutoria linear (pergunta → resposta direta)
- ✅ **Agora:** Tutoria multidimensional (conceito → reflexão → solução → visualização → contextualização)

### Objetivos Alcançados
- ✨ **Transparência:** Alunos veem de onde vem cada informação
- 🎯 **Personalização:** Seleção de modelos e controle de busca web
- 📚 **Curadoria:** Conexão a materiais acadêmicos reais de universidades federais
- 🔬 **Rigor:** Validação dimensional e LaTeX científico
- 💡 **Intuição:** Visualizações interativas de conceitos abstratos

---

## 📖 Recursos Adicionais

- **CLAUDE.md** — Arquitetura técnica para futuros desenvolvedores
- **HIERARCHY_IMPLEMENTATION.md** — Detalhes da hierarquia de fontes (v2026)
- **docs/SOURCE_PIPELINE.md** — Pipeline de integração de fontes
- **IMPLEMENTATION_SUMMARY.md** — Resumo de features implementadas

---

*Desenvolvido para elevar o padrão do ensino superior de Física através da Inteligência Artificial.*
*Arquitetado para escalabilidade acadêmica, flexibilidade de modelos e integridade de dados.*
