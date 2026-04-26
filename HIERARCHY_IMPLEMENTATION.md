# Hierarquia de 5 Fontes com Busca Web — Implementação Completa ✅

## 🎯 O que foi Implementado

Um sistema transparente de priorização de fontes de conhecimento com busca web em tempo real para portais acadêmicos brasileiros e bases internacionais.

### Hierarquia de Prioridades

```
1️⃣  MATERIAIS DO PROFESSOR (Nível 1)
    ├── Notas de Aula (upload PDF/TXT)
    └── Repositório Permanente (pCloud)

2️⃣  DOCUMENTOS ADOTADOS NA DISCIPLINA (Nível 2)
    └── PDFs de livros/materiais adotados

3️⃣  EMENTA UFSM (Nível 3)
    ├── Temas da disciplina
    └── Bibliografia básica

4️⃣  PORTAIS ACADÊMICOS .edu.br (Nível 4)
    └── Busca web em tempo real (DuckDuckGo)

5️⃣  REFERÊNCIAS INTERNACIONAIS (Nível 5)
    ├── arXiv (artigos open access)
    └── Semantic Scholar (papers e citações)

📄 MATERIAL DO ALUNO (Fora da hierarquia)
    └── Link pCloud da sessão (fornecido pelo aluno)
```

---

## 📁 Arquivos Modificados

### Novo
- **`src/utils/web_searcher.py`** — 3 métodos de busca:
  - `search_edu_br(topic)` → Portais .edu.br via DuckDuckGo
  - `search_arxiv(topic)` → arXiv API (open)
  - `search_semantic_scholar(topic)` → Semantic Scholar API (open)

### Alterados
- **`requirements.txt`** — Adiciona `duckduckgo-search>=6.0.0`
- **`src/core.py`**:
  - PhysicsState: 3 novos campos (`adopted_docs_text`, `web_edu_br_text`, `intl_refs_text`)
  - `build_context()` reescrito com 5 níveis + truncação
  - Novo método `sync_web_sources()` para busca web após Intérprete
  - PhysicsOrchestrator.run() aceita `adopted_url` e `enable_web_search`
  - Instruções dos agentes atualizadas para citar os novos tipos de fonte
  
- **`src/app.py`**:
  - Novos campos sidebar: "Documentos Adotados" e "Busca Web Inteligente"
  - Painel de "Fontes Utilizadas" mostra hierarquia numerada
  - Passa novos parâmetros para orchestrator.run()

---

## 🧪 Testes

✅ **test_hierarchy.py** — 6 testes sobre separação e priorização de fontes
✅ **test_integration.py** — 4 testes sobre fluxo de contexto com orchestrator
✅ **Sintaxe**: core.py e app.py aprovados em `py_compile`

---

## 🎮 Como Usar

### 1. Habilitar Busca Web (Padrão: Ativado)

No sidebar, há toggle "🌐 Busca Web Inteligente":
- ✅ **Ativado**: Sistema busca em portais .edu.br + arXiv automaticamente (10-15s adicionais)
- ❌ **Desativado**: Apenas materiais locais (mais rápido)

### 2. Adicionar Materiais em Cada Nível

| Nível | Campo no Sidebar | Tipo |
|-------|------------------|------|
| 1 | 📄 Notas Manuais | Upload PDF/TXT |
| 1 | 📦 Repositório do Professor | Link pCloud |
| 2 | 📗 Documentos Adotados | Link pCloud ou URL direta |
| 3 | _(automático)_ | UFSM Syllabus |
| 4 | _(automático se toggle ✓)_ | Busca web |
| 5 | _(automático se toggle ✓)_ | arXiv + Semantic Scholar |

### 3. Ver Quais Fontes Foram Usadas

Após análise, painel "📊 Fontes Utilizadas" mostra:
```
1️⃣ Materiais do Professor: Notas do Professor + Repositório
2️⃣ Documentos Adotados incorporados
3️⃣ Ementa UFSM localizada e utilizada
4️⃣ Portais Acadêmicos .edu.br consultados
5️⃣ Referências Internacionais (arXiv/Semantic Scholar)
☁️ Material do Aluno incorporado
```

---

## 📊 Exemplo de Resposta com Atribuição

A resposta agora cita a origem:

```
[Ementa UFSM] Física II (FSC1028) trata de Eletromagnetismo...

[Notas do Professor] Em nossa aula, observamos que o potencial...

[Material do Aluno] No exercício que você enviou, temos a seguinte...

[Referências Internacionais] Estudos em arXiv mostram que...

[Modelo de IA] Adicionalmente, podemos aplicar o conceito de...
```

---

## ⚙️ Detalhes Técnicos

### Context Assembly (Ordem Fixa)

```python
# Em build_context():
1. Nível 1: professor_notes_text + pcloud_repo_text (até 4000 chars)
2. Nível 2: adopted_docs_text (até 2000 chars)
3. Nível 3: ufsm_context (até 600 chars)
4. Nível 4: web_edu_br_text (até 1500 chars)
5. Nível 5: intl_refs_text (até 1200 chars)
+ Extra: pcloud_session_text (até 2000 chars)
```

### Web Search Flow

```
1. User asks question
2. Interpreter identifies concepts
3. sync_web_sources() called (if enabled)
   ├── Busca .edu.br com tópicos identificados
   └── Consulta arXiv + Semantic Scholar
4. build_context() monta contexto completo com 5 níveis
5. Agentes recebem contexto priorizado
```

### Timeout & Performance

- arXiv: 10s timeout
- Semantic Scholar: 10s timeout (pode falhar com 429, tratado gracefully)
- DuckDuckGo: 10s timeout
- Total de busca web: ~15-20s (execução sequencial)

---

## 🔧 Configuração Padrão

- **Busca web**: Habilitada por padrão (`enable_web_search=True`)
- **Documenti Adotados**: Campo opcional, vazio se não fornecido
- **Truncação**: Aplicada per-source para controlar tamanho do contexto
- **Exclusão automática**: Fontes vazias não aparecem no contexto final

---

## 📚 Commits

```
3ec4df1 feat: Implement 5-level source hierarchy with web search
52be5b9 test: Add comprehensive test for 5-level source hierarchy
32064d3 test: Add integration test for orchestrator with 5-level hierarchy
```

---

## ✨ Próximos Passos (Opcional)

1. **Parallelizar web search** — Usar `asyncio` para buscar 3 fontes em paralelo (~5s em vez de 15s)
2. **Caching de resultados** — Cache por sessão com TTL de 1 hora
3. **Score de relevância** — Usar BM25 ou embedding similarity para reordenar resultados
4. **UI melhorada** — Mostrar quais portais .edu.br foram consultados
5. **Fallback graceful** — Se web search falhar, continuar com local materials

---

## 🎓 Impacto Educacional

✅ **Transparência**: Alunos veem de onde veio cada informação
✅ **Confiabilidade**: Respostas ancoradas em ementa UFSM + materiais do professor
✅ **Pesquisa**: Acesso automático a arXiv e portais acadêmicos .edu.br
✅ **Eficiência**: Busca em tempo real apenas para tópicos relevantes (após Intérprete)
✅ **Controle**: Professor escolhe se ativa busca web ou não

---

## 🚀 Status

**IMPLEMENTAÇÃO COMPLETA E TESTADA** ✅

- [x] Nova hierarquia de 5 fontes
- [x] Busca web em portais .edu.br (DuckDuckGo)
- [x] APIs arXiv e Semantic Scholar
- [x] UI sidebar com novos campos
- [x] Painel de fontes utilizadas com hierarquia
- [x] Testes unitários
- [x] Testes de integração
- [x] Commits e push para GitHub

**Pronto para uso! 🎉**
