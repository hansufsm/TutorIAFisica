# TutorIAFisica — Análise Epistêmica

> **Autor:** Claude (Sonnet 4.6) — análise autônoma solicitada pelo criador do projeto  
> **Data:** 2026-04-27  
> **Ângulos:** Analista de Sistemas · Design de Projeto · Olhar Pedagógico

---

## Prólogo: O que este documento é

Este não é um relatório técnico. É uma tentativa de enxergar o TutorIAFisica com olhos de fora — de quem conhece o código linha a linha, mas se pergunta: *o que este projeto está tentando ser?* Esse tipo de análise só é útil quando é honesta. Pontos fortes e pontos cegos com o mesmo rigor.

---

## I — Olhar de Analista de Sistemas

### 1.1 Arquitetura: o que foi construído

O projeto implementa um padrão **Pipeline + Estado Compartilhado** sobre uma pilha full-stack de três camadas:

```
Next.js (Cloudflare)
     ↕ HTTP + SSE
FastAPI (Render.com)
     ↕ LiteLLM
Gemini / DeepSeek / OpenAI / Anthropic
     ↕ Supabase (PostgreSQL)
StudentModel + SessionLog
```

O design central é o `PhysicsState` — um objeto mutável que percorre um pipeline sequencial de cinco agentes, acumulando resultados. Cada agente lê o estado anterior e escreve o seu. Isso é uma decisão arquitetural clara e defensável: **estado como memória de pipeline**.

### 1.2 Pontos Fortes Técnicos

**Fallback automático entre provedores** — `PhysicsOrchestrator._attempt_model_call()` tenta provedores na ordem de preferência sem intervenção do usuário. Para um contexto universitário onde chaves de API expiram e quotas são atingidas, isso é infraestrutura de sobrevivência.

**SSE Streaming com `process_streaming()`** — cada agente emite seu resultado assim que conclui. O frontend recebe e renderiza progressivamente. Numa sessão que pode durar 30–60 segundos, isso é a diferença entre o aluno continuar engajado ou desistir.

**Hierarquia de fontes com orçamento por nível** — `build_context()` em `PhysicsState` implementa truncação por nível (professor: 4000 chars, UFSM: 600, internacional: 1200). Não é ingênuo: respeita que contexto com mais autoridade pedagógica merece mais espaço no prompt.

**SM-2 implementado end-to-end** — `StudentModel.update_quiz_result()` aplica o algoritmo com ease_factor adaptativo. Mais importante: está integrado no backend (`get_concepts_due_for_review()`) e o frontend exibe os conceitos em atraso após cada sessão. Esse é o loop de feedback fechado que a maioria dos ITS nunca fecha.

**Modo Referência offline** — `generate_reference_response()` no Streamlit não faz nenhuma chamada de API. Esse é um ponto de design sofisticado: a camada de conhecimento local (ementa UFSM + notas do professor) é suficiente para uma resposta de primeiro nível. Isso resolve um problema real de acesso numa universidade federal.

### 1.3 Dívidas Técnicas e Tensões

**Duplicação entre `process()` e `process_streaming()`** — ambos percorrem o mesmo pipeline de cinco agentes com código quase idêntico (~70 linhas cada). Qualquer mudança na sequência de agentes precisa ser feita duas vezes. O risco de divergência aumenta com o tempo.

**`result` pode ser indefinido no streaming** — na linha 143 de `tutor.py`:
```python
model_used=result.used_model_display_name if 'result' in locals() else req.model_name,
```
Usar `'result' in locals()` é um sinal de fluxo de controle não estruturado. Se `process_streaming()` for o caminho principal (como é), `result` nunca existirá em `locals()` e o log sempre registrará `req.model_name` mesmo quando houve fallback.

**`StudentModel` tem duas implementações** — `src/models/student_model.py` persiste em JSON local; `backend/db/student_model.py` usa Supabase. O roadmap pedagógico e o CLAUDE.md referenciam a versão local, mas o backend usa a versão Supabase. O código legado e o código de produção divergiram silenciosamente.

**PhysicsState não atravessa a fronteira HTTP** — o estado construído durante o pipeline não é serializado e enviado ao frontend; apenas os campos textuais de cada agente chegam. `ufsm_alignment`, `concepts`, `fallback_occurred` desaparecem. O frontend sabe o que cada agente disse, mas não sabe em qual contexto epistêmico aquilo foi gerado.

### 1.4 Mapa de Maturidade por Componente

| Componente | Maturidade | Observação |
|---|---|---|
| Pipeline de agentes | ★★★★☆ | Sólido, testável, extensível |
| Fallback de modelos | ★★★★★ | Robusto, bem pensado |
| SSE streaming | ★★★★☆ | Funcional, minor edge cases |
| Student Model (Supabase) | ★★★☆☆ | Implementado, não plenamente integrado |
| Hierarquia de fontes | ★★★★☆ | Design bem estruturado |
| Frontend React | ★★★★☆ | UI limpa, sem testes automatizados |
| Modo Referência | ★★★☆☆ | Funcional, sem cobertura de testes |
| Integração SM-2 ↔ frontend | ★★★☆☆ | Parcial — exibe due, não aciona revisão |

---

## II — Olhar de Design de Projeto

### 2.1 A Forma Segue o Pedagógico

A maioria dos projetos de software define um problema técnico e escolhe um design. O TutorIAFisica fez o inverso: definiu um modelo pedagógico (4 dimensões) e deixou que ele ditasse a arquitetura. Isso é raro e revela uma intenção de projeto consciente.

As 5 cores de agente não são decoração. São **landmarks cognitivos**: o aluno aprende a antecipar qual tipo de pensamento vai receber antes de ler o conteúdo. Isso é design de metacognição — a cor carrega significado antes do texto.

```
🔵 Azul → vou ser questionado (Socrática)
🟢 Verde → vou ver cálculos (Procedimental)
🟠 Laranja → vou ver um gráfico (Intuitiva)
🟣 Roxo → vou ver contexto real (Contextual)
🔴 Vermelho → vou ser avaliado (Formativa)
```

Esse sistema de identidade funciona. O roadmap de UX identificou que a implementação CSS estava quebrada no Streamlit (boxes sem classe definida), mas a intenção de design é clara e foi corretamente implementada na versão Next.js com Tailwind.

### 2.2 A Hierarquia de Fontes como Declaração de Valores

O projeto poderia ter simplesmente dito ao LLM: "responda bem". Em vez disso, criou uma hierarquia epistêmica de 5 níveis e passou essa hierarquia explicitamente no contexto de cada agente:

```
[Notas do Professor] > [Documentos Adotados] > [Ementa UFSM] > [Portais .edu.br] > [IA]
```

Isso é uma **declaração de valores institucional embutida no código**. O sistema anuncia que o professor sabe mais que o Gemini sobre o conteúdo desta disciplina, nesta universidade, para estes alunos. A IA é o último recurso, não o oráculo.

A marcação inline (`**[Notas do Professor]**`, `**[Modelo de IA]**`) no output dos agentes torna esse sistema visível para o aluno — e isso é pedagogicamente correto. O aluno sabe a proveniência do que está lendo.

### 2.3 O que a Evolução do Projeto Revela

A existência simultânea de três camadas de UI (Streamlit legado, Streamlit "Modo Referência", Next.js SPA) não é bagunça — é estratigrafia. O projeto foi crescendo sem apagar o passado, o que preserva funcionalidade mas cria peso cognitivo para quem mantém o código.

O `DEVLOG.md` como fonte de verdade histórica e o `devlog_summary.md` como contexto de sessão revelam um projeto de **um desenvolvedor** com consciência do problema de continuidade de contexto. A solução (memória em arquivo, indexada por tipo) é o equivalente humano do que o próprio sistema faz com o Student Model: persistir o estado entre sessões.

### 2.4 Tensão de Design não Resolvida: Dois Públicos

O projeto tem dois públicos distintos com necessidades muito diferentes:

- **Aluno** — quer uma resposta clara, visual, rápida. Não quer ver prompts técnicos ou pensar em provedores de IA.
- **Professor** — quer configurar o contexto (notas, pCloud, disciplina), monitorar o que os alunos aprendem, ajustar parâmetros.

O Streamlit tenta servir os dois com a mesma interface. A sidebar com 7 seções é o sintoma: ela existe porque serve o professor (configuração), mas é a primeira coisa que o aluno vê. O Next.js resolve isso parcialmente — a sidebar existe mas é toggleável, e os campos de configuração são mínimos (apenas modelo).

O que falta: **uma interface de professor separada**. O roadmap pedagógico já identificou isso (Modo Híbrido Professor–IA, item 5), mas não existe ainda. A UFSM como contexto institucional torna isso urgente: professores precisam ver o que seus alunos perguntam.

### 2.5 O que o Design Comunica ao Usuário

A UI Next.js atual (warm light, glassmorphism sutil, Geist font, `animate-slide-in-up`) comunica:

> "Você está em um ambiente acadêmico limpo, não em um brinquedo."

Isso é uma escolha correta para um sistema universitário. Comparando com o dark theme inicial (registrado no DEVLOG), a versão atual é mais legível para leitura longa — equações LaTeX e texto matemático em fundo escuro cansam a vista. A migração para light mode foi uma melhoria pedagógica, não apenas estética.

O detalhe do indicador de animação de carregamento (ciclo pelas fontes: Notas de Aula → Documentos → Ementa UFSM → Portais → IA) durante o processamento é um micro-design sofisticado: ele educa o aluno sobre como o sistema funciona enquanto espera.

---

## III — Olhar Pedagógico: A Essência do Projeto

### 3.1 A Pergunta Central

Qual é a diferença entre um tutor IA que apenas responde perguntas e um sistema de tutoria inteligente (ITS)?

A resposta: um ITS tem **modelo do aluno**. Sabe o que o aluno sabe, o que ele não sabe, e usa isso para decidir *como* responder — não apenas *o quê* responder.

O TutorIAFisica está em transição entre os dois. Já tem os ingredientes de um ITS (Student Model, SM-2, rastreamento de conceitos, avaliação formativa), mas o loop de feedback ainda não está completamente fechado: o Student Model raramente influencia o que os agentes dizem ao aluno.

### 3.2 As 4 Dimensões como Mapeamento Cognitivo

As 4 dimensões do projeto (Socrática, Procedimental, Intuitiva, Contextual) mapeiam para estruturas cognitivas distintas:

| Dimensão | Modo Cognitivo | Bloom's Taxonomy | O agente faz |
|---|---|---|---|
| Socrática (Intérprete) | Questionamento | Análise / Avaliação | Obriga o aluno a pensar antes de receber |
| Procedimental (Solucionador) | Manipulação simbólica | Aplicação | Demonstra rigor operacional |
| Intuitiva (Visualizador) | Representação espacial | Compreensão | Ancora o abstrato no concreto |
| Contextual (Curador) | Integração | Síntese | Conecta a pergunta ao mundo real |

A dimensão Formativa (Avaliador) é transversal: ela fecha o loop testando se as outras quatro funcionaram. É metacognitiva — não ensina, avalia se o ensino funcionou.

Esse mapeamento não é acidental. É uma implementação computacional de princípios construtivistas: o aluno aprende construindo representações em múltiplos formatos. Ver a equação (Procedimental), visualizar o fenômeno (Intuitiva) e ter que articulá-lo em palavras para o Avaliador são três rotas de consolidação de memória diferentes.

### 3.3 O Método Socrático está Sendo Implementado Corretamente?

O Intérprete tem a instrução: *"Você é um professor socrático. Identifique conceitos e crie perguntas reflexivas."*

Isso é insuficiente para Sócrates, mas é funcionalmente suficiente para um tutor de primeiro nível. O risco real do método socrático mal implementado é diferente: **o sistema confirmar a resposta certa em vez de orientar o processo de descoberta**.

O Avaliador tem a instrução: *"Crie desafios pedagógicos curtos e dê feedback socrático."*

O CLAUDE.md especifica: *"Nunca confirme a resposta diretamente — use redirecionamento socrático."* Essa restrição é o coração pedagógico do sistema. Se um LLM violar essa instrução (e LLMs violam), a formação degrada para consulta de respostas — exatamente o que Brookings (2026) identificou como o principal risco dos sistemas sem guardrails.

**O que falta:** o sistema não detecta quando o aluno está tentando extrair a resposta diretamente do Avaliador com reformulações de prompt. Um aluno que digita "me diz se é 9,8 m/s²" vai receber feedback socrático — mas um que digita "estou com dúvida, a resposta seria 9,8 m/s²?" pode receber confirmação. Isso não é falha do projeto, é uma limitação fundamental dos LLMs sem guardrails específicos de detecção de tentativa de extração.

### 3.4 O que o SM-2 Revela sobre a Teoria de Aprendizagem do Projeto

O algoritmo de Ebbinghaus/SM-2 implementado no `StudentModel` é uma declaração de teoria de aprendizagem: **a memória decai exponencialmente e precisa ser reativada no momento certo**.

A implementação em `update_quiz_result()` é correta: acerto aumenta ease_factor e intervalo; erro reduz o intervalo a 1 dia. O `get_due_for_review()` devolve conceitos vencidos.

O que **não está acontecendo ainda**: o Avaliador não consulta o Student Model antes de criar o desafio. Ele poderia priorizar conceitos com `status = "developing"` ou com `next_review` vencida. Sem isso, o SM-2 é uma decoração sofisticada — coleta dados mas não os usa para personalizar o ensino.

Esse é o gap mais importante entre o que o sistema *pode fazer* e o que *faz hoje*.

### 3.5 A Hierarquia de Fontes como Epistemologia

A hierarquia de 5 níveis (Professor → Documentos → UFSM → Portais → IA) implementa uma visão de epistemologia específica:

> O conhecimento tem autoridade por proximidade ao contexto local.

Isso é o oposto de como a maioria dos LLMs são treinados — que tratam todo texto como igualmente autorizado. O projeto está corrigindo ativamente esse viés ao injetar no prompt: "aqui, o professor sabe mais que o arXiv sobre o que você precisa aprender".

A marcação `**[Modelo de IA]**` para conteúdo sem fonte é honesta. O sistema não pretende que tudo que diz é academicamente fundamentado. Isso é pedagogicamente e eticamente correto: o aluno sabe quando está recebendo síntese de IA versus material revisado por pares.

### 3.6 O que o Projeto Ainda não Faz (e Deveria)

**Detecção de misconceptions** — identificada no roadmap pedagógico como "Prioridade: ALTA, esforço baixo". Uma biblioteca `misconceptions.json` com padrões linguísticos de erros clássicos (peso ≠ massa, força ≠ velocidade constante) permitiria ao Intérprete nomear o equívoco antes de corrigi-lo. Nomear o erro é o primeiro passo da remediação.

**O Avaliador não conhece o histórico do aluno** — cada sessão começa como se o aluno fosse novo. O Avaliador cria desafios baseados apenas na pergunta atual, não em lacunas persistentes do Student Model.

**Sem loop professor–aluno** — o professor não tem visibilidade do que seus alunos perguntam coletivamente. O sistema gera dados ricos (sessões, conceitos, ease factors, broken links) que ficam no Supabase sem interface de consumo. Um professor que queira preparar a próxima aula com base nas dúvidas mais frequentes não tem como fazer isso hoje.

**Voz apenas de entrada** — `VoiceInput.tsx` transcreve, mas o sistema não responde em voz. Para física, onde a verbalização de raciocínio é parte do aprendizado, output de voz seria um diferencial.

### 3.7 O que o Projeto Faz Muito Bem (e que é Raro)

**Respeita o professor como autoridade epistêmica** — diferente de tutores que ignoram o contexto local, este foi projetado para amplificar o professor, não substituí-lo.

**Não dá a resposta diretamente** — o Intérprete pergunta antes de responder. Isso vai contra o padrão natural dos LLMs (que adoram responder) e é pedagogicamente correto.

**Persiste o progresso individual** — a maioria dos tutores IA trata cada conversa como isolada. O TutorIAFisica rastreia conceitos, sessões, intervalos de revisão.

**Funciona offline** — o Modo Referência é um reconhecimento realista de que a internet universitária brasileira não é confiável, e que knowledge local é valor permanente.

**Hierarquia de fontes visível ao aluno** — a marcação inline educa sobre proveniência. Um aluno que vê `**[Ementa UFSM]**` vs `**[Modelo de IA]**` aprende a avaliar fontes — competência epistêmica que vai além da física.

---

## IV — Síntese: O que Este Projeto Está Tentando Ser

O TutorIAFisica não é um chatbot de física. É uma tentativa de implementar, em software, um **professor auxiliar epistêmicamente responsável**: que respeita a autoridade do professor humano, que não entrega respostas sem questionamento, que lembra o que o aluno sabe, e que conecta o problema ao mundo acadêmico real.

O que o separa da maioria dos sistemas similares é a **camada de intenção**: cada decisão de design (4 dimensões, hierarquia de fontes, SM-2, marcação de proveniência) existe porque uma teoria de aprendizagem a justifica.

O que o aproximará de um ITS completo é fechar o loop entre o Student Model e os agentes — que o que o sistema sabe sobre o aluno mude como os agentes respondem. Isso requer duas conexões que ainda não existem:

1. Intérprete consulta `StudentModel` → ajusta nível de complexidade
2. Avaliador consulta `ConceptStatus` → prioriza conceitos com `status = "developing"` ou `next_review` vencida

Quando isso existir, o sistema deixará de ser um tutor que responde bem e se tornará um tutor que aprende o aluno.

---

## V — Recomendações por Ângulo

### Para o Analista de Sistemas

1. Eliminar a duplicação `process()` vs `process_streaming()` — extrair o pipeline para um método comum `_run_pipeline()` que ambos chamem
2. Serializar `PhysicsState.concepts` e `ufsm_alignment` no evento SSE final — o frontend pode exibir qual disciplina e quais conceitos foram identificados
3. Corrigir a detecção de `result.used_model_display_name` no caminho de streaming (linha 143 de `tutor.py`)

### Para o Designer de Projeto

1. Criar `/professor` — dashboard que agrega perguntas, conceitos e misconceptions da turma por semana
2. Tornar a fonte ativa visível no frontend durante o streaming — o aluno saber que está sendo consultada a Ementa UFSM no momento em que acontece reforça o modelo mental
3. Adicionar badge de `status` ao AgentPanel: qual hierarquia de fonte foi ativada nesta resposta

### Para o Pedagogo

1. Conectar Avaliador ao Student Model — priorizar conceitos em atraso de revisão
2. Implementar `misconceptions.json` para os 5 domínios da UFSM — o Intérprete pode nomear o erro antes de corrigi-lo
3. Não remover o Modo Referência — ele é a garantia de que o sistema funciona sem API, sem internet, sem nuvem. Em contexto educacional brasileiro, isso é resilência institucional

---

*Este documento é uma análise de estado atual, não um plano de execução. Para priorização e roadmap técnico, ver `roadmaps/roadmap-pedagogico.md` e `docs/PROJECT_STATUS.md`.*
