# 🌌 TutorIAFisica: Mentor Multi-Model IA

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/framework-Streamlit-FF4B4B)](https://streamlit.io/)
[![AI Orchestration](https://img.shields.io/badge/Orchestration-LiteLLM-FF5733)](https://github.Pcloud.com/BerriAI/litellm)
[![Compliance](https://img.shields.io/badge/compliance-Secure%20API%20Keys-brightgreen)]()
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

O **TutorIAFisica** é um ecossistema de tutoria acadêmica modular, projetado para o ensino superior. Esta versão (v4.3) introduz a **Seleção Flexível de Modelos de IA** com fallback automático, gerenciamento híbrido de chaves API e um **Módulo de Avaliação Formativa Interativa**.

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

## 🎨 Guia de Estilo
O portal utiliza um **Dark Mode** confortável, com identificação visual por agente:
- 🔵 **Azul:** Intérprete
- 🟢 **Verde:** Solucionador
- 🟠 **Laranja:** Visualizador
- 🟣 **Roxo:** Curador
- Vermelho: Avaliador (para desafios)

---
*Projeto arquitetado para escalabilidade acadêmica, flexibilidade de modelos e integridade de dados.*
