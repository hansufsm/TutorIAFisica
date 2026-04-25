# TutorIAFisica 🌌 (v2.0 - 2026)

O **TutorIAFisica** é a evolução do projeto *FisicaIA*. Ele foi transformado de uma sequência de scripts em um ecossistema de agentes inteligentes focados em **Aprendizagem Significativa**, **Rigor Matemático** e **Curadoria Acadêmica**.

## 🚀 Inovações Pedagógicas (State-of-the-Art)

O projeto agora utiliza uma arquitetura de **Estado de Agentes**, onde cada interação é processada sob quatro dimensões fundamentais:

1.  **Dimensão Socrática (Intérprete):** Não entrega a resposta de imediato. Desconstrói o problema e desafia o aluno com perguntas reflexivas para validar a compreensão conceitual.
2.  **Dimensão Procedimental (Solucionador):** Foca na análise dimensional e no passo a passo matemático rigoroso, utilizando LaTeX para precisão científica.
3.  **Dimensão Intuitiva (Visualizador):** Gera código e gráficos dinâmicos para transformar equações abstratas em intuição física visual.
4.  **Dimensão Contextual (Curador):** Resgata a essência do projeto original, conectando o problema a:
    - **Aplicações Reais:** Ex: Desfibriladores, pintura eletrostática.
    - **Curadoria Acadêmica:** Links diretos para Universidades Federais (UFSM, UFRGS, USP).
    - **Recursos Multimodais:** Sugestão de vídeos e mapas mentais.
    - **Níveis de Desafio:** Exercícios extras (Médio e Desafio).

## 🛠️ Estrutura do Projeto

```text
TutorIAFisica/
├── src/
│   ├── app.py      # Frontend moderno em Streamlit (Tema Claro)
│   └── core.py     # Cérebro do sistema (Orquestrador e Agentes)
├── README.md       # Documentação do projeto
└── .gitignore      # Proteção de arquivos sensíveis
```

## 💻 Como Rodar

1. Clone o repositório.
2. Instale as dependências: `pip install streamlit`.
3. Execute o servidor:
   ```bash
   cd src
   streamlit run app.py
   ```

## 🗺️ Roadmap e Estratégia de Dados (Funcionalidades Futuras)

Para garantir a máxima precisão pedagógica, o projeto expandirá seu escopo de fontes seguindo uma hierarquia rigorosa de confiabilidade:

### 1. Fontes de Dados Prioritárias (Específicas)
- **Notas de Aula e Material do Docente:** Prioridade máxima para alinhamento com a didática específica da turma.
- **Documentos de Referência:** Apostilas e materiais autorais carregados pelo professor.

### 2. Base Institucional e Bibliográfica
- **Ementário UFSM:** Integração automática com a bibliografia básica e complementar das disciplinas de Física e Engenharia da UFSM.
- **Acervos Universitários:** Consultas a repositórios de Universidades Federais e Estaduais de renome.

### 3. Fontes Externas e Internacionais
- **Rede Universitária Confiável:** Prioridade para fontes em Língua Portuguesa (Ex: portais de IFs e Universidades Federais) seguida por referências internacionais de renome (Ex: MIT, Caltech, CERN).
- **Filtro de Relevância:** Bloqueio estrito de blogs, páginas pessoais ou sites de "resumos" sem validação acadêmica comprovada.

## 🛠️ Governança de Modelos e Contemporaneidade (2026)

O **TutorIAFisica** implementa um protocolo rigoroso de verificação para garantir que o motor de inteligência utilize modelos que representem o estado da arte no ensino de ciências.

### 1. Protocolo de Verificação de Modelos
Em abril de 2026, realizamos uma auditoria de compatibilidade que resultou na transição para a família de modelos **Gemini 2.x**. Este processo de modernização incluiu:
- **Discovery Dinâmico:** O sistema agora possui rotinas para listar e validar modelos disponíveis via `genai.list_models()`, evitando falhas por depreciação (ex: transição do 1.5 para 2.0/2.5).
- **Seleção por Performance:** Optou-se pelo modelo **`gemini-flash-latest`** (ou `2.0-flash`) devido ao equilíbrio superior entre latência de resposta socrática e precisão em LaTeX matemático.

### 2. Gestão de Cota e Orquestração Ética
Diferente de sistemas de chat comuns, o TutorIAFisica opera uma **Orquestração de Agentes em Cascata**. Para respeitar os limites de cota da infraestrutura e garantir a estabilidade pedagógica:
- **Sequential Delay (3s):** Implementação de intervalos estratégicos entre agentes para evitar erros `429 (Too Many Requests)`.
- **System Instructions Específicas:** Cada agente recebe um "blueprint" de comportamento contemporâneo, garantindo que o Intérprete nunca forneça a resposta antes do Solucionador, preservando o método socrático.

### 3. Resiliência à Obsolescência
O código foi refatorado para ser **Model-Agnostic**. A troca de um modelo de 2025 para um de 2026 exige apenas a alteração de uma constante, mantendo a integridade de toda a lógica de estado e curadoria acadêmica.

---
*Nota Técnica: Em 25 de Abril de 2026, o sistema foi validado com sucesso para lidar com temas complexos como Oscilações e Mecânica Clássica (ex: Pêndulo Simples) usando o motor Gemini 2.0.*
