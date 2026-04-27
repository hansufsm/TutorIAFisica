# Modo Referência — Guia de Uso

## O que é?

**Modo Referência** é uma forma de usar o TutorIAFisica **sem precisar de chave API**. Em vez de receber explicações geradas por inteligência artificial, você acessa material acadêmico local:

- 📚 **Ementa UFSM** — Tópicos da disciplina
- 📝 **Notas do Professor** — Material que você carregou
- 📗 **Documentos Adotados** — Livros ou slides da disciplina

## Quando Usar?

✅ **Use Modo Referência se:**
- Você não tem uma chave API de IA (sem créditos em Gemini, DeepSeek, etc)
- Quer explorar o material da disciplina sem depender de modelos LLM
- Está em uma sala de aula e quer ver o que o sistema tem sobre um tópico
- Quer aprender a "pesquisar" de forma estruturada no material local

❌ **Não use se:**
- Quer uma explicação completa com 5 dimensões pedagógicas
- Precisa de visualizações geradas por código
- Quer um quiz inteligente com feedback socrático

## Como Ativar?

1. Abra o TutorIAFisica
2. Na **barra lateral (sidebar)**, procure por **"🔬 Modo de Resposta"**
3. Selecione **"Modo Referência"** (em vez de "Modo IA")
4. Faça sua pergunta normalmente
5. Clique em **"🚀 Iniciar Análise do Esquadrão"**

```
🔬 Modo de Resposta
( ) Modo IA
(•) Modo Referência    ← Selecione aqui
```

## O que Você Vai Ver?

Quando ativa Modo Referência, o sistema exibe material em **5 abas**:

### 1️⃣ **Diálogo Socrático** (Azul)
```
⚠️ **Modo Referência** (sem explicação gerada por IA)

Para uma explicação completa, configure uma chave API na sidebar.

**Tópico Encontrado na UFSM:**
Disciplina: Física I (FSC1027)
Temas do ementário: Cinemática, Dinâmica, Trabalho e Energia, ...
```

### 2️⃣ **Solução Matemática** (Verde)
Exibe as **notas do professor** que você carregou (primeiros 1500 caracteres).

Se você não carregou notas:
```
*(Nenhuma nota do professor carregada)*
```

### 3️⃣ **Visualização** (Laranja)
Exibe **documentos adotados** (livros, slides) que você forneceu via pCloud.

Sem documentos adotados:
```
*(Nenhum documento adotado carregado)*
```

### 4️⃣ **Contexto UFSM** (Roxo)
Mostra a **ementa completa da disciplina encontrada**:
- Código (ex: FSC1027)
- Período (ex: 1º semestre)
- Lista de temas
- Bibliografia básica (até 5 livros)

### 5️⃣ **Meu Progresso** (Gráfico)
Exibe seu histórico de sessões (se você se identificou na sidebar).

## Exemplo Prático

**Você digita:** "O que é a Segunda Lei de Newton?"

**Modo Referência faz:**
1. Extrai palavras-chave: "segunda", "newton"
2. Busca na ementa UFSM por match
3. Encontra: **Física I (FSC1027)**
4. Exibe informações sobre Dinâmica da ementa

**Você vê:**
```
Tab 1 (Socrática):
  "Tópico encontrado: Física I - Dinâmica - Lei de Newton"

Tab 2 (Solução):
  Se carregou um PDF com suas notas sobre Newton, mostra aqui

Tab 3 (Visualização):
  Se tem documentos adotados com conteúdo sobre Newton

Tab 4 (Contexto):
  Ementa completa de Física I com todos os temas
```

## Limitações

❌ **O que NÃO funciona em Modo Referência:**

| Recurso | Modo IA | Modo Referência |
|---------|---------|-----------------|
| Explicação gerada por IA | ✅ | ❌ |
| Resolução de problemas | ✅ | ❌ |
| Código Plotly interativo | ✅ | ❌ |
| Quiz com feedback | ✅ | ❌ |
| Busca na web (arXiv, .edu.br) | ✅ | ❌ |
| Notas do professor (se carregadas) | ✅ | ✅ |
| Ementa UFSM | ✅ | ✅ |
| Documentos adotados (se fornecidos) | ✅ | ✅ |

## Como Sair do Modo Referência?

1. Volte à sidebar
2. Clique em **"Modo IA"** (em vez de "Modo Referência")
3. Insira uma chave API válida (ou deixe o sistema tentar fallback)
4. Clique em "Iniciar Análise" novamente

## Obtendo uma Chave API

Se quer passar para Modo IA, você precisa de uma chave de um modelo suportado:

- **DeepSeek** — https://platform.deepseek.com (mais barato)
- **Gemini** — https://aistudio.google.com (grátis com limite)
- **OpenAI** — https://platform.openai.com (pago)
- **Anthropic Claude** — https://console.anthropic.com (pago)

Siga o guia no arquivo **[API_KEYS.md](./API_KEYS.md)** para configurar.

## Dúvidas Frequentes

**P: Por que o Modo Referência não me dá uma resposta completa?**
A: Porque uma "resposta" com explicação, cálculo, visualização e quiz precisa de IA. O Modo Referência é apenas um navegador inteligente de material local — não substitui o Modo IA.

**P: Como adiciono minhas notas ao Modo Referência?**
A: Na sidebar, em **"📚 Materiais de Entrada"**, clique em **"Upload PDF/TXT"** e selecione seu arquivo. Ele vai aparecer na tab "Solução Matemática".

**P: Posso alterar a ordem de prioridade das fontes?**
A: Hoje não — a ordem é fixa: UFSM → Notas → Documentos Adotados. Essa prioridade reflete a hierarquia pedagógica do sistema.

**P: O que acontece se faço uma pergunta que não está no syllabus?**
A: O sistema busca a melhor correspondência. Pode encontrar uma disciplina relacionada (ex: "Relatividade" → Física IV) ou mostrar uma mensagem: "*(Tópico não encontrado na ementa da UFSM)*"

## Sugestões de Uso em Sala de Aula

1. **Exploração estruturada**: Alunos usam Modo Referência para navegar a ementa da disciplina
2. **Preparação pré-aula**: Examine o material local antes da aula com o professor
3. **Revisão**: Releia notas do professor sem gastar créditos de API
4. **Pesquisa**: Veja quais tópicos têm notas/documentos disponíveis e quais faltam

---

**Última atualização:** 2026-04-27
**Versão:** v4.3+
