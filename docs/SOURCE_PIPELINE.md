# Source-Attributed Context Pipeline

## Overview

TutorIAFisica now uses a **hybrid knowledge system** that prioritizes different sources of information and clearly attributes the origin of each part of the answer.

```
┌─────────────────────────────────────────────────────┐
│                  STUDENT QUESTION                    │
└────────┬────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│          SOURCE COLLECTION & PRIORITIZATION          │
├─────────────────────────────────────────────────────┤
│  1. 📘 EMENTA UFSM (Local Syllabus)                 │
│     • Discipline name & code                         │
│     • Topic list from curriculum                     │
│     • Bibliography (first 3 items)                   │
│                                                      │
│  2. 📄 NOTAS DO PROFESSOR (Uploaded PDF/TXT)        │
│     • Manual notes teacher provides                  │
│     • Override/enrich UFSM content                   │
│                                                      │
│  3. ☁️ MATERIAL DO ALUNO (Session pCloud Link)      │
│     • Student-specific PDFs for this question       │
│     • Usually specific problem materials            │
│                                                      │
│  4. 📦 REPOSITÓRIO (Permanent pCloud Folder)        │
│     • Teacher's permanent materials folder          │
│     • General course resources                       │
│                                                      │
│  5. [Modelo de IA] (AI Model Knowledge)             │
│     • Fallback when no material matches             │
│     • General physics knowledge                      │
└─────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│            AGENT PIPELINE (5 Agents)                 │
├─────────────────────────────────────────────────────┤
│  All agents receive:                                 │
│  • Prioritized context with [SOURCE] labels         │
│  • Instruction to cite source when using material   │
│                                                      │
│  1. Intérprete (Interpreter)                        │
│  2. Solucionador (Solver)                           │
│  3. Visualizador (Visualizer)                       │
│  4. Curador (Curator)                               │
│  5. Avaliador (Evaluator)                           │
└────────┬────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│              ATTRIBUTED RESPONSE                      │
├─────────────────────────────────────────────────────┤
│  [Ementa UFSM]: Concept from curriculum             │
│  [Notas do Professor]: Application from notes       │
│  [Material do Aluno]: Specific example              │
│  [Modelo de IA]: Additional insight                 │
└─────────────────────────────────────────────────────┘
```

## Data Flow

### PhysicsState Field Separation

Before (mixed sources):
```python
state.teacher_notes = "UFSM + uploaded + pCloud + repo all together"
```

After (separated sources):
```python
state.ufsm_context = "Disciplina: Física I (FSC1027)..."
state.professor_notes_text = "Uploaded PDF/TXT content"
state.pcloud_session_text = "PDFs from session link"
state.pcloud_repo_text = "PDFs from permanent folder"
```

### Context Assembly

The `build_context()` method assembles these in priority order:

```python
def build_context(self) -> str:
    parts = []
    if self.ufsm_context:
        parts.append(f"### [EMENTA UFSM]\n{self.ufsm_context}")
    if self.professor_notes_text.strip():
        parts.append(f"### [NOTAS DO PROFESSOR]\n{self.professor_notes_text}")
    if self.pcloud_session_text.strip():
        parts.append(f"### [MATERIAL DO ALUNO - pCloud]\n{self.pcloud_session_text}")
    if self.pcloud_repo_text.strip():
        parts.append(f"### [REPOSITÓRIO DE MATERIAIS]\n{self.pcloud_repo_text}")
    return "\n\n".join(parts)
```

## User Interface

### Sidebar Configuration

```
⚙️ Configurações de IA
├─ Escolha o Motor de IA → [DeepSeek Chat ▼]
├─ Inserir chaves API (if needed)
│
👨‍🏫 Notas Manuais
└─ Upload extra (PDF/TXT)
│
📷 Entrada de Imagem
└─ Upload de Imagem (if model supports)
│
☁️ Material pCloud do Aluno
└─ Link Público pCloud (Pasta)
     "Link único por sessão — PDFs que o aluno envia para esta dúvida"
│
📦 Repositório Permanente
└─ Link pCloud Repositório (Professor)
     "Link fixo da pasta com todos os PDFs do professor"
```

### Status Display

After analysis, the system shows which sources were used:

```
📊 Fontes Utilizadas
📘 Ementa UFSM localizada e utilizada
📄 Notas do Professor incorporadas
☁️ Material do Aluno (pCloud) carregado
📦 Repositório Permanente consultado
```

Or if no materials were found:

```
📊 Fontes Utilizadas
✨ Resposta gerada pelo Modelo de IA (sem materiais de referência)
```

## Agent Instructions

All agents receive this instruction in their system prompt:

> "Ao utilizar informações do MATERIAL DE REFERÊNCIA, cite a fonte com o marcador correspondente: **[Ementa UFSM]**, **[Notas do Professor]**, **[Material do Aluno]** ou **[Repositório]**. Informações que vêm apenas do seu conhecimento devem ser marcadas como **[Modelo de IA]**."

## Example Response with Attribution

A typical response would look like:

---

**Conservação de Energia**

**[Ementa UFSM]** - Física I (FSC1027) trata da Energia como um dos temas principais. A disciplina cobre o conceito de trabalho e energia através de diversas abordagens.

**[Notas do Professor]** - Em nossa aula, discutimos que a energia mecânica total de um sistema isolado permanece constante quando apenas forças conservativas atuam.

**[Modelo de IA]** - Matematicamente, isso é expresso como: $E_{total} = KE + PE = \frac{1}{2}mv^2 + mgh = constante$

**[Material do Aluno]** - No exercício que você anexou, vemos a bola caindo de 10m. Aplicando a conservação:
- $PE_{inicial} = mgh = m \times 10 \times 10 = 100m$ J
- Quando $h = 0$: $KE_{final} = \frac{1}{2}mv^2 = 100m$, logo $v = \sqrt{200} = 14,1$ m/s

---

## Backwards Compatibility

The `teacher_notes` property is maintained for backwards compatibility:

```python
@property
def teacher_notes(self) -> str:
    """Concatenation of all notes for backwards compatibility."""
    parts = [self.professor_notes_text, self.pcloud_session_text, self.pcloud_repo_text]
    return "\n\n".join([p for p in parts if p.strip()])
```

Code that still references `state.teacher_notes` will continue to work.

## Testing

Run the test suites to verify source handling:

```bash
# Test source separation and prioritization
python test_source_pipeline.py

# Test UFSM matching and context extraction
python test_ufsm_matching.py
```

Both suites provide comprehensive validation of the source pipeline behavior.

## Implementation Files

- `src/core.py` — PhysicsState, build_context(), agent instructions
- `src/app.py` — Sidebar UI, repository link input, source status display
- `src/utils/pcloud_manager.py` — No changes (already handles URL fetching)
- `data/ufsm_syllabus.json` — Existing syllabus (now fully utilized)

## Future Enhancements

Possible improvements:

1. **Source Weights** — Allow teacher to configure which sources are prioritized
2. **Semantic Search** — Use embeddings to match relevant materials instead of substring matching
3. **Material Validation** — Verify extracted text quality before including in context
4. **Citation Links** — Track which pages/PDFs contributed to each response
5. **Student Dashboard** — Show students which materials were used for their answer
