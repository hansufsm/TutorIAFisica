# Design & UX Review — TutorIAFisica

**Data da Revisão:** 2026-04-26  
**Status:** Auditoria Completa — Plano de Melhorias Pronto para Implementação

---

## 📋 Executive Summary

O app atual possui **uma arquitetura pedagógica excelente** mas **sofre de problemas críticos de implementação visual e UX**:

- ❌ **15+ bugs e UX issues identificados** (desde críticos até menores)
- ❌ **Sistema de identidade visual de agentes completamente quebrado** (classes CSS vazias)
- ❌ **Quiz feedback nunca aparece** para o aluno (bug lógico no setState)
- ❌ **Sidebar overcrowded** — 7 seções sem agrupamento hierárquico
- ❌ **Não responsivo** — layout forçado quebra em mobile
- ❌ **Painel de debug exposto** ao usuário final
- ✅ **Corrigível** — todas as issues têm soluções diretas

---

## 🔴 Issues Críticos (Implementar Primeiro)

### 1. **Agent Identity System Broken** (Máxima Prioridade)
**Arquivo:** `src/app.py` linhas 14-66 (CSS) e linhas 293-323 (HTML que usa as classes)

**Problema:**
- Classes usadas em HTML: `.agent-box`, `.border-interprete`, `.border-solucionador`, `.border-visualizador`, `.border-curador`, `.border-avaliador`
- Classes definidas em CSS: `.agent-solucionador`, `.agent-visualizador`, `.agent-curador`, `.agent-avaliador`
- **Mismatch completo** — as classes de HTML não existem em CSS, então nenhum estilo aplica
- Resultado: Os agent boxes (respostas dos agentes) aparecem sem bordas coloridas, sem backgrounds, invisíveis
- O README promete "identificação visual por agente", mas está 100% quebrado na implementação

**Impacto Pedagógico:**
- A cor é uma dimensão pedagógica importante (README seção "Identidade Visual")
- Alunos não conseguem visualmente associar respostas aos agentes
- A "Dimensão Socrática" (azul), "Procedimental" (verde), etc. ficam invisíveis

**Solução:**
```css
/* Adicionar estas regras ao <style> block */
.agent-box { padding: 15px; border-radius: 8px; margin-bottom: 15px; }

.border-interprete { 
  border-left: 8px solid #1f77b4; 
  background-color: #e6f0ff; 
}
.border-solucionador { 
  border-left: 8px solid #28a745; 
  background-color: #e9f7ec; 
}
.border-visualizador { 
  border-left: 8px solid #fd7e14; 
  background-color: #fff9e9; 
}
.border-curador { 
  border-left: 8px solid #6f42c1; 
  background-color: #f3f0f9; 
}
.border-avaliador { 
  border-left: 8px solid #dc3545; 
  background-color: #fff5f5; 
}

.ufsm-badge { 
  padding: 12px; 
  border-left: 4px solid #007bff; 
  background-color: #e7f3ff; 
  margin-bottom: 15px; 
  font-weight: 500; 
}
```

**Esforço:** ~5 minutos

---

### 2. **Quiz Feedback Never Displays** (Bug Crítico)
**Arquivo:** `src/app.py` linhas 322-359

**Problema:**
```python
if st.session_state.quiz_visible:
    # ... renderiza pergunta e input ...
    if st.button("Enviar Resposta"):
        # ... processa resposta ...
        st.session_state.quiz_visible = False  # ← AQUI!
        
    # ← Este bloco nunca executa porque quiz_visible foi setado para False acima
    if st.session_state.quiz_feedback:
        st.info(f"🗨️ **Feedback:**{st.session_state.quiz_feedback}")
```

- Quando o aluno envia a resposta, `quiz_visible` é imediatamente setado para False
- Isso faz com que o `if st.session_state.quiz_visible:` bloco termine no próximo render
- O feedback fica salvo em `quiz_feedback` mas nunca é renderizado
- O aluno vê: "Resposta enviada" → página recarrega → desaparece tudo (vazio)

**Impacto:** O módulo de Avaliação Formativa (feature pedagógica importante) está completamente inoperante.

**Solução:**
```python
if st.session_state.quiz_visible:
    # ... renderiza pergunta ...
    if st.button("Enviar Resposta"):
        # ... processa feedback ...
        st.session_state.quiz_visible = False
    
    # IMPORTANTE: Este bloco agora está FORA do "if st.button"
    # e executa ANTES da próxima rerun
    if st.session_state.quiz_feedback:
        st.info(f"🗨️ **Feedback:** {st.session_state.quiz_feedback}")
        if st.button("Pedir Novo Desafio"):
            st.session_state.quiz_generated = False
            st.session_state.quiz_question = ""
            st.session_state.quiz_feedback = ""
            st.rerun()
```

Alternativamente, mover o feedback display para fora do `quiz_visible` check:
```python
if st.session_state.quiz_feedback and not st.session_state.quiz_visible:
    st.info(f"🗨️ **Feedback:** {st.session_state.quiz_feedback}")
    if st.button("Pedir Novo Desafio"):
        # ...
        st.rerun()
```

**Esforço:** ~10 minutos (precisa testar o fluxo)

---

### 3. **Debug Panel Exposed to Students** (Security/UX Issue)
**Arquivo:** `src/app.py` linhas 194-201

**Problema:**
```python
with st.status("🔍 Verificando materiais de entrada...", expanded=False) as debug_status:
    st.write(f"📝 Enunciado: {len(enunciado)} caracteres")
    st.write(f"📄 Notas do professor: {len(manual_notes)} caracteres")
    # ... etc
```

- Este é um **painel de debug do desenvolvedor**
- Mostra informações internas: caracteres de entrada, toggle state, etc.
- Está exposto a todos os usuários finais (estudantes)
- Não há forma de desabilitá-lo sem editar código

**Impacto:** 
- Poluição visual desnecessária
- Pode confundir alunos
- Não agrega valor pedagógico

**Solução:**
```python
# Opção 1: Remover completamente (simplest)
# (Apagar linhas 194-201)

# Opção 2: Mover para sidebar como debug toggle (mais flexível)
DEBUG_MODE = st.sidebar.checkbox("🔧 Debug Info", value=False, key="debug_mode")
if st.button("🚀 Iniciar Análise"):
    if DEBUG_MODE:
        with st.status("🔍 Debug Info", expanded=False):
            st.write(f"📝 Enunciado: {len(enunciado)} chars")
            # ...
```

**Recomendação:** Remover completamente. A informação não é útil para estudantes.

**Esforço:** ~2 minutos

---

### 4. **pCloud Placeholder Contains Real URL** (Data Leak Risk)
**Arquivo:** `src/app.py` linha 160

**Problema:**
```python
pcloud_url = st.text_input(
    "Link Público pCloud (Pasta):", 
    placeholder="https://u.pcloud.com/#/publink?code=YwnXZ5JRkIVuJIKjhmWtlGzorl0jp6UeX"
)
```

- Este placeholder contém uma URL **que pode ser um link real**
- Se alguém ir para essa URL, pode acessar um pCloud compartilhado de verdade
- Isso é um **data leak risk** se foi usado em teste/desenvolvimento com dados sensíveis

**Solução:**
```python
placeholder="https://u.pcloud.com/#/publink?code=XXXXXXXXXXXXXXXXXXXXX"
# ou
placeholder="https://u.pcloud.com/#/publink?code=example"
```

**Esforço:** ~1 minuto

---

## 🟡 Issues Importantes (Implementar em Segundo)

### 5. **Image Upload Header Always Renders**
**Arquivo:** `src/app.py` linhas 152-156

**Problema:**
```python
st.divider()
st.header("📷 Entrada de Imagem")  # ← Always renders
if model_is_multimodal:
    input_image = st.file_uploader(...)
else:
    input_image = None
```

Quando o modelo não é multimodal:
- O header `📷 Entrada de Imagem` aparece
- Mas nenhum uploader widget aparece abaixo
- Fica confuso: por que tem um header vazio?

**Solução:**
```python
if model_is_multimodal:
    st.divider()
    st.header("📷 Entrada de Imagem")
    input_image = st.file_uploader("Upload de Imagem (foto do problema):", type=["png", "jpg", "jpeg", "webp"])
else:
    st.divider()
    st.info("📷 Este modelo não suporta entrada de imagem. Forneça descrições textuais dos diagramas.")
    input_image = None
```

**Esforço:** ~5 minutos

---

### 6. **Scrollbar Colors Clash with Light Theme**
**Arquivo:** `src/app.py` linhas 62-64

**Problema:**
```css
::-webkit-scrollbar-track { background: #0e1117; }        /* Dark (GitHub Dark) */
::-webkit-scrollbar-thumb { background: #30363d; border-radius: 10px; }
```

- Scrollbars estão em cores de **dark mode** (GitHub Dark palette: `#0e1117`, `#30363d`)
- Mas o page background é branco (`#ffffff`)
- Resultado: scrollbar aparece como uma barra preta feia contra fundo branco

**Solução:**
```css
::-webkit-scrollbar-track { background: #f0f2f6; }     /* Light, matches Streamlit secondaryBackgroundColor */
::-webkit-scrollbar-thumb { background: #c8cbd2; border-radius: 10px; }
```

**Esforço:** ~2 minutos

---

### 7. **Sidebar Has No Grouping Hierarchy**
**Arquivo:** `src/app.py` linhas 83-177

**Problema:**
Sidebar tem 7 seções planas (todas `st.header`):
1. ⚙️ Configurações de IA
2. 👨‍🏫 Notas Manuais
3. 📷 Entrada de Imagem
4. ☁️ Material pCloud do Aluno
5. 📦 Repositório Permanente
6. 📗 Documentos Adotados
7. 🌐 Busca Web Inteligente

Aluno vê: 7 coisas soltas. Sem estrutura. Alto **cognitive load** na primeira vez.

**Solução:** Usar `st.subheader` e `st.caption` para criar hierarquia:
```python
st.header("⚙️ Configurações de IA")
# ... model selector, keys ...

st.divider()
st.subheader("📚 Materiais de Referência")
st.caption("Forneça materiais para enriquecer as respostas")

st.subheader("👨‍🏫 Notas Manuais")
# ... uploader ...

st.subheader("📷 Entrada de Imagem")
# ... uploader ...

st.subheader("📦 Repositórios")
st.caption("Links para materiais armazenados em cloud")

# ... etc
```

**Esforço:** ~15 minutos (refatorar e testar layout)

---

### 8. **No Onboarding / Instructions**
**Arquivo:** `src/app.py` linhas 164-165

**Problema:**
```python
# --- ENTRADA DO ALUNO ---
enunciado = st.text_area("Descreva sua dúvida de física:", ...)
```

- Aluno vê um textarea vazio
- Nenhuma instruções sobre o que o app faz
- Nenhum exemplo de pergunta
- Nenhuma explicação das 4 dimensões pedagógicas

**Solução:** Adicionar onboarding antes do textarea:
```python
st.markdown("""
## 🧠 Como Funciona

TutorIAFisica analisa sua dúvida em **4 dimensões**:

1. 🔵 **Socrática** — Perguntas reflexivas para validar conceitos
2. 🟢 **Procedimental** — Cálculos rigorosos com validação dimensional
3. 🟠 **Intuitiva** — Visualizações e simulações interativas
4. 🟣 **Contextual** — Aplicações reais e conexões académicas

### Exemplo de Pergunta
*"Um capacitor de placa paralela com área 10 cm² e separação 1 mm é carregado a 100V. Qual é a energia armazenada?"*

Ou faça uma pergunta conceitual:
*"Por que a conservação de energia é importante em circuitos?"*

---
""")

enunciado = st.text_area("Descreva sua dúvida de física:", height=100, ...)
```

**Esforço:** ~10 minutos

---

## 🟢 Issues Menores (Nice to Have)

### 9. **Version String Mismatch**
- README: "v2026"
- app.py: "v4.3"
- CLAUDE.md: Várias versões mencionadas

**Solução:** Centralizar em um arquivo `src/VERSION` ou `config.py`:
```python
__version__ = "2026.1"  # Year.Release
```

**Esforço:** ~5 minutos

---

### 10. **Quiz Markdown Missing Spaces**
**Arquivo:** `src/app.py` linhas 324, 353

```python
# ANTES
f"**Desafio do Avaliador:**{st.session_state.quiz_question}"
f"🗨️ **Feedback:**{st.session_state.quiz_feedback}"

# DEPOIS
f"**Desafio do Avaliador:** {st.session_state.quiz_question}"
f"🗨️ **Feedback:** {st.session_state.quiz_feedback}"
```

**Esforço:** ~1 minuto

---

### 11. **Quiz Generated State is Dead Code**
**Arquivo:** `src/app.py` linha 309

```python
if 'quiz_generated' not in st.session_state: 
    st.session_state.quiz_generated = False
```

- Inicializado mas nunca lido
- Nunca condiciona nenhum comportamento
- Remover ou documentar uso

**Esforço:** ~2 minutos

---

### 12. **README vs UI Mismatch: Dark Mode Description**
**Arquivo:** `README.md` linha 172

README says:
> O portal utiliza um **Dark Mode** confortável...

Mas o tema é totalmente `background-color: #ffffff` branco.

**Solução:** Corrigir README:
> O portal utiliza um **Light Mode** claro e profissional...

**Esforço:** ~1 minuto

---

### 13. **Redundant KaTeX CDN Load**
**Arquivo:** `src/app.py` linhas 15-17 e `config.toml` linha 9

- KaTeX é carregado **manualmente via CDN** em app.py
- Streamlit 1.30+ já tem KaTeX **nativo** (ativado por padrão)
- Resultado: 2 instâncias competindo, possíveis conflitos

**Solução:** Remover a carga manual, usar apenas Streamlit nativo:
```python
# REMOVER linhas 15-17 de app.py
# Manter config.toml como está (Streamlit cuida do rest)
```

**Esforço:** ~2 minutos (depois testar math rendering)

---

### 14. **Runtime Keys Dict Initialized Twice**
**Arquivo:** `src/app.py` linhas 108 e 184

- Inicializado em line 108 (sidebar, nunca preenchido)
- Re-inicializado em line 184 (button handler)
- Código confuso, mas funciona na prática

**Solução:** Remover linha 108, deixar apenas a inicialização dentro do button handler.

**Esforço:** ~3 minutos

---

### 15. **model_is_multimodal Calculated Twice**
**Arquivo:** `src/app.py` linhas 132, 153

```python
model_is_multimodal = Config.is_model_multimodal(st.session_state.selected_model_display_name)  # line 132

if model_is_multimodal:  # line 153 — redundant check
    input_image = st.file_uploader(...)
else:
    input_image = None
```

Minor: Calcular uma vez, reuso.

**Esforço:** ~2 minutos

---

### 16. **st.rerun() on Model Change Has No Debounce**
**Arquivo:** `src/app.py` lines 103-105

```python
if current_selection_in_state != selected_model_display_name:
    st.session_state.selected_model_display_name = selected_model_display_name
    st.rerun()  # ← Instant, no debounce
```

Aluno muda model selector → página recarrega imediatamente, perdendo qualquer texto digitado.

Considerar: debounce com callback ou confirmação.

**Esforço:** ~10 minutos (se implementar debounce)

---

### 17. **Intérprete Color Mismatch**
- primaryColor em config.toml: `#007bff`
- Intérprete accent definido em CSS deep-selector: `#1f77b4`

Ambos são azuis mas diferentes. Usar um ou outro consistentemente.

**Esforço:** ~2 minutos

---

## 📱 Mobile Responsiveness Issues

**layout="wide" força scroll horizontal em phones.**

Solução: Adicionar CSS media query:
```css
@media (max-width: 768px) {
  .stApp {
    max-width: 100vw;
    overflow-x: hidden;
  }
}
```

**Esforço:** ~5 minutos

---

## 📊 Prioridade de Implementação

| Prioridade | Issues | Tempo Total | Impacto |
|---|---|---|---|
| 🔴 **Crítica** | 1, 2, 3, 4 | ~30 min | Quebra funcionalidade |
| 🟡 **Alta** | 5, 6, 7, 8 | ~45 min | UX e educação |
| 🟢 **Média** | 9-15, 16 | ~40 min | Code quality |
| ⚪ **Baixa** | 17, 18+ | ~15 min | Polish |

**Total Estimado:** ~2 horas para todas as correções

---

## 🚀 Recomendação

**Fase 1 (Imediato - 30 min):**
- ✅ Fix agent identity CSS (Issue #1)
- ✅ Fix quiz feedback logic (Issue #2)
- ✅ Remove debug panel (Issue #3)
- ✅ Fix pCloud placeholder (Issue #4)

**Fase 2 (Sprint Próximo - 45 min):**
- ✅ Image upload conditional rendering (Issue #5)
- ✅ Scrollbar colors (Issue #6)
- ✅ Sidebar grouping (Issue #7)
- ✅ Onboarding content (Issue #8)

**Fase 3 (Polish - 40 min):**
- ✅ Version consistency
- ✅ Code cleanup (dead variables, redundant calculations)
- ✅ Mobile responsiveness

---

## 📝 Checklist de Implementação

- [ ] Backlog issues criadas no GitHub
- [ ] Prioridades atribuídas
- [ ] Testes de regressão planeados
- [ ] Screenshot antes/depois documentados
- [ ] CHANGELOG atualizado
