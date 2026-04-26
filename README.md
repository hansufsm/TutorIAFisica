# 🌌 TutorIAFisica: Mentor Multi-Model

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/framework-Streamlit-FF4B4B)](https://streamlit.io/)
[![AI Orchestration](https://img.shields.io/badge/Orchestration-LiteLLM-FF5733)](https://github.com/BerriAI/litellm)
[![Compliance](https://img.shields.io/badge/compliance-Secure%20API%20Keys-brightgreen)]()
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

O **TutorIAFisica** é um ecossistema de tutoria acadêmica modular, projetado para o ensino superior. Esta versão (v4.2) introduz a capacidade de **seleção flexível de modelos de IA** com fallback automático, garantindo disponibilidade e otimização de custos.

---

## 🤖 Motores de IA (Modelos Disponíveis)

O TutorIAFisica agora suporta múltiplos provedores de LLM através do LiteLLM, com seleção manual e fallback automático:

### 1. Seleção de Modelo
Na barra lateral, você pode escolher o motor de IA preferido entre os seguintes:
- **Gemini 3.0 Preview** (Multimodal, Padrão)
- Gemini 2.0 Flash (Multimodal)
- Gemini 1.5 Flash (Multimodal)
- OpenAI GPT-3.5 Turbo (Texto)
- Claude 3 Sonnet (Texto)
- Claude 3 Haiku (Texto)
- Claude 3 Opus (Texto)
- Perplexity Online (Texto)
- DeepSeek Chat (Texto)
- Manusc Model (Placeholder para modelos locais/customizados)

### 2. Gerenciamento de Chaves API
- **Autenticação:** As chaves API são primariamente carregadas do arquivo `.env` (recomendado para segurança).
- **Input Runtime:** Se a chave para o modelo selecionado ou um modelo de fallback necessário não for encontrada no `.env`, um campo de texto aparecerá na sidebar para você colar a chave para aquela sessão.

### 3. Mecanismo de Fallback Automático
- Se o modelo selecionado falhar (ex: `RateLimitError`, `AuthenticationError`, `APIError`), o sistema tentará automaticamente os modelos na seguinte ordem de preferência:
    1. Gemini 3.0 Preview
    2. Gemini 1.5 Flash
    3. OpenAI GPT-3.5 Turbo
    4. Claude 3 Sonnet
    5. Claude 3 Haiku
    6. Claude 3 Opus
    7. Perplexity Online
    8. DeepSeek Chat
    9. Manusc Model (se configurado)
- **Notificação:** Você será informado na interface se um fallback ocorrer.

### 4. Limitações Multimodais
- Modelos marcados como text-only (ex: DeepSeek Chat, GPT-3.5 Turbo) não processarão imagens. A função de upload de foto será desabilitada ou exibirá um aviso nesses casos.

---

## 🚀 Como Executar

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
    # MANUSC_API_KEY=SUA_CHAVE_MANUSC # Se aplicável
    ```

5.  **Inicie o portal:**
    ```bash
    cd src
    streamlit run app.py
    ```
    *No app, selecione seu modelo preferido e cole as chaves API na sidebar se elas não estiverem no `.env`.*

---

## 🎨 Guia de Estilo
O portal usa um **Dark Mode** confortável, com identificação visual por agente e cores distintas:
- 🔵 **Azul:** Intérprete
- 🟢 **Verde:** Solucionador
- 🟠 **Laranja:** Visualizador
- 🟣 **Roxo:** Curador
- Vermelho: Avaliador (para desafios)

---
*Projeto arquitetado para escalabilidade acadêmica, flexibilidade de modelos e integridade de dados.*
