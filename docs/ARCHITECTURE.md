# Arquitetura do TutorIAFisica

## Visão Geral
O sistema opera através de uma **Orquestração de Agentes Independentes** baseada em um objeto de estado compartilhado (`PhysicsState`).

### Fluxo de Processamento (Pipeline)
1. **Input:** O aluno descreve um problema ou conceito.
2. **Interpreter:** Realiza o "Reasoning" (Raciocínio) inicial, classificando a área da física e gerando a estratégia pedagógica.
3. **Solver:** Recebe o contexto e foca exclusivamente no rigor matemático e na consistência de unidades (SI).
4. **Visualizer:** Traduz a solução em código Python para geração de gráficos.
5. **Curador:** Enriquece a resposta com dados do mundo real e fontes acadêmicas.

### Comunicação entre Agentes
O `PhysicsOrchestrator` garante que o output de um agente seja validado e passado para o próximo. O novo agente **Avaliador** encerra o ciclo gerando desafios de verificação.

### Integração pCloud (Cloud-First)
- **Mecanismo:** Utiliza a API `showpublink` e `getpublinkdownload` do pCloud.
- **Fluxo:** O sistema extrai o `code` do link público, lista arquivos PDF e os processa em memória (buffer) via `requests` e `io.BytesIO`.
- **Independência:** O sistema é agnóstico à infraestrutura local, permitindo deploy em nuvem sem dependência de drivers de sincronização.

### Avaliação Formativa
O motor agora possui uma via de feedback de mão dupla. O aluno não é apenas um receptor; ele é desafiado pelo agente **Avaliador**, que utiliza técnicas de "andaime cognitivo" para corrigir erros sem entregar a resposta final prematuramente.
