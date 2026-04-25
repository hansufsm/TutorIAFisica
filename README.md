# 🌌 TutorIAFisica: Mentor Inteligente de Física (v3.5)

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![Compliance](https://img.shields.io/badge/compliance-ISO_Quality_Standards-green)]()
[![AI Model](https://img.shields.io/badge/AI-Gemini_2.0_Flash-blueviolet)](https://ai.google.dev/)

O **TutorIAFisica** é um ecossistema de tutoria acadêmica modular, projetado para o ensino superior. Esta versão (v3.5) implementa uma arquitetura baseada em **Separação de Preocupações (SoC)** e **Design Modular**.

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
├── assets/              # Estilizações CSS e recursos visuais
├── docs/                # Documentação técnica e planos de estudo
└── requirements.txt     # Dependências do projeto
```

---

## 🛡️ Compliance e Segurança

- **Gestão de Segredos:** Implementação rigorosa de arquivos `.env` para proteção de chaves de API.
- **Validação de Startup:** O sistema valida todas as variáveis de ambiente antes da inicialização para evitar falhas em tempo de execução.
- **Orquestração Ética:** Delays estratégicos integrados para respeitar as cotas das APIs (Rate Limiting) e garantir a estabilidade do serviço.
- **Data Privacy:** Processamento de arquivos e imagens em memória (RAM), garantindo que dados de alunos e professores não sejam persistidos sem autorização.

---

## 🚀 Como Executar

1. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Configure o seu `.env`** com a `GEMINI_API_KEY`.
3. **Inicie o portal:**
   ```bash
   streamlit run src/app.py
   ```

---
*Projeto arquitetado para escalabilidade acadêmica e integridade institucional.*
