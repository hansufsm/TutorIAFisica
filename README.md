# 🌌 TutorIAFisica: Mentor Inteligente de Física

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/framework-Streamlit-FF4B4B)](https://streamlit.io/)
[![AI Model](https://img.shields.io/badge/AI-Gemini_2.0_Flash-blueviolet)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

O **TutorIAFisica** é um portal de tutoria inteligente de nova geração, projetado para o ensino superior de física e engenharia. Ele utiliza um **Multi-Agent System (MAS)** para decompor problemas complexos em dimensões pedagógicas distintas.

---

## 🤖 O Esquadrão de Agentes

| Agente | Avatar | Especialidade | Objetivo Pedagógico |
| :--- | :---: | :--- | :--- |
| **Intérprete** | 🧩 | Semântica e Lógica | Reduzir o erro de interpretação e estimular o pensamento crítico. |
| **Solucionador**| 📐 | Cálculo e Rigor | Demonstrar o fluxo matemático correto com análise dimensional. |
| **Visualizador**| 🖼️ | Intuição Gráfica | Traduzir equações em representações visuais dinâmicas (Python). |
| **Curador** | 📚 | Contexto e Fontes | Conectar a teoria ao mundo real e a fontes acadêmicas confiáveis. |

---

## 🛠️ Arquitetura e Tecnologia

### Stack Tecnológica
- **Frontend:** Streamlit (Interface de Chat Dinâmica)
- **Backend:** Python 3.11+
- **Orquestração:** Lógica de Estado (Stateful Orchestration)
- **LLM:** Google Gemini 2.0 Flash (API)

### Hierarquia de Fontes (Roadmap)
1. Materiais do Professor (Notas de Aula)
2. Documentos Adotados na Disciplina
3. Bibliografia Básica (Ementário UFSM)
4. Portais Acadêmicos Federais (.edu.br)
5. Referências Internacionais de Renome

---

## 🚀 Instalação e Uso

### Pré-requisitos
- Python 3.11 ou superior
- Uma chave de API do Gemini (Google AI Studio)

### Configuração
1. **Clone o repositório:**
   ```bash
   git clone https://github.com/hansufsm/TutorIAFisica.git
   cd TutorIAFisica
   ```

2. **Crie e ative o ambiente virtual:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure sua chave API:**
   Crie um arquivo `.env` na raiz do projeto:
   ```env
   GEMINI_API_KEY=SUA_CHAVE_AQUI
   ```

5. **Inicie o portal:**
   ```bash
   cd src
   streamlit run app.py
   ```

---

## 🎨 Guia de Estilo
O portal utiliza um **Dark Mode** customizado para reduzir a fadiga visual, com identificação cromática por agente:
- 🔵 **Azul:** Intérprete
- 🟢 **Verde:** Solucionador
- 🟠 **Laranja:** Visualizador
- 🟣 **Roxo:** Curador

---
*Projeto concebido e modernizado em 2026 para revolucionar a educação científica.*
