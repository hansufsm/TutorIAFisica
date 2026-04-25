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
O `PhysicsOrchestrator` garante que o output de um agente seja validado e passado para o próximo, mantendo o contexto íntegro durante toda a sessão.

### Resiliência de API
O motor implementa um sistema de `time.sleep()` entre chamadas para respeitar os limites de cota de APIs de nível gratuito (Free Tier), garantindo estabilidade em demonstrações de sala de aula.
