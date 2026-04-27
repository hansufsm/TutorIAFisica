# TutorIAFisica — Roadmap de Melhorias Pedagógicas (2026)

> Documento gerado a partir de pesquisa no estado da arte em sistemas de tutoria
> inteligente (ITS) com IA. Fontes: Scientific Reports, OECD Digital Education Outlook
> 2026, Brookings Global Task Force, arXiv, PMC. Objetivo: posicionar o TutorIAFisica
> na vanguarda pedagógica global.

---

## Contexto: O que a ciência diz

Um RCT publicado na Scientific Reports (Kestin et al., 2025) demonstrou que tutores IA
bem projetados produzem ganhos de aprendizagem significativamente maiores que aulas
presenciais com aprendizagem ativa — em menos tempo. O diferencial não é o modelo de IA
usado, mas o **design pedagógico**.

O Brookings Global Task Force (jan/2026), após consultar líderes de 50+ países, concluiu
que "sob as condições atuais, os riscos superam os benefícios" — não porque a IA não
funciona, mas porque a maioria das implementações **não tem guardrails pedagógicos**.

O TutorIAFisica já tem esses guardrails (4 dimensões, método socrático, LaTeX, hierarquia
de fontes). O que se segue são as melhorias para ir além.

---

## O que sistemas de vanguarda fazem que o TutorIAFisica ainda não faz

| Capacidade | Sistemas que já têm | TutorIAFisica hoje |
|---|---|---|
| Student Model persistente entre sessões | Khanmigo, Rimac ITS, Physics-STAR | ❌ PhysicsState só existe na sessão |
| Detecção explícita de misconceptions | AutoTutor, Rimac, MathAgent | ⚠️ Implícita no Intérprete |
| Repetição espaçada adaptativa | Anki, Gizmo, BeFreed | ❌ Não implementada |
| Painel de progresso do aluno | Khanmigo, Coursera | ❌ Não implementado |
| Modo híbrido professor–IA | Sistemas OECD recomendados | ❌ Não implementado |
| Interface de voz | GPT-4o Voice, Tutor Kai | ❌ Não implementado |
| Forgetting curves individuais | Anki, sistemas de pesquisa 2025 | ❌ Não implementado |

---

## 7 Melhorias — Do mais urgente ao mais ambicioso

---

### 1. 🧠 Student Model Persistente
**Prioridade: CRÍTICA — é o alicerce de todas as outras melhorias**

#### Problema atual
O `PhysicsState` é descartado ao fim de cada sessão. O sistema não tem memória do aluno:
não sabe o que ele já aprendeu, onde errou, nem o que está esquecendo. Cada sessão começa
do zero.

#### O que implementar
Nova classe `StudentModel` persistida em JSON (localmente ou no pCloud), por aluno,
com a seguinte estrutura:

```python
# src/models/student_model.py

@dataclass
class ConceptStatus:
    concept_id: str           # ex: "newton_segunda_lei"
    topic: str                # ex: "Dinâmica"
    status: str               # "not_started" | "developing" | "mastered" | "consolidated"
    mastery_level: float      # 0.0 a 1.0
    misconceptions: list[str] # misconceptions detectadas
    date_introduced: str
    date_mastered: str | None
    last_reviewed: str | None
    next_review: str | None   # calculado pelo algoritmo SM-2
    review_interval_days: int # intervalo atual de repetição
    session_history: list[dict]  # [{date, correct, response_snippet}]

class StudentModel:
    student_id: str
    concepts: dict[str, ConceptStatus]
    open_questions: list[str]  # dúvidas não resolvidas
    session_log: list[dict]    # log de sessões

    def save(self, path: str): ...
    def load(self, path: str): ...
    def get_due_for_review(self) -> list[ConceptStatus]: ...
    def update_after_interaction(self, concept_id, correct: bool): ...
```

#### Integração com o pipeline existente
- `PhysicsOrchestrator.process()` carrega o `StudentModel` antes de iniciar o pipeline
- O `Intérprete` consulta o modelo para ajustar nível de complexidade
- O `Avaliador` consulta misconceptions registradas antes de criar desafios
- Ao final da sessão, o orquestrador salva o modelo atualizado
- Path de persistência: `data/students/{student_id}.json`

#### Referência acadêmica
> "Tutores que atualizam dinamicamente o student model durante diálogos ensinam de
> forma mais eficiente do que versões com modelo estático." — Rimac ITS, Springer 2021

---

### 2. 🎯 Detecção Explícita de Misconceptions
**Prioridade: ALTA — impacto pedagógico imediato, esforço baixo**

#### Problema atual
O sistema responde à pergunta do aluno, mas não identifica sistematicamente quando uma
resposta revela uma concepção equivocada estabelecida (misconception clássica de física).

#### O que implementar
Arquivo `data/misconceptions.json` mapeando tópico → misconceptions conhecidas:

```json
{
  "dinamica": [
    {
      "id": "mc_forca_velocidade",
      "description": "Confundir força com velocidade constante",
      "trigger_patterns": ["força mantém o movimento", "precisa de força para andar"],
      "socratic_probe": "Se não houver força alguma sobre um objeto em movimento, o que acontece com ele?"
    },
    {
      "id": "mc_peso_massa",
      "description": "Usar peso e massa como sinônimos",
      "trigger_patterns": ["meu peso é 70kg", "peso em quilogramas"],
      "socratic_probe": "Qual seria seu peso na Lua? E sua massa?"
    }
  ],
  "eletromagnetismo": [
    {
      "id": "mc_campo_sem_carga",
      "description": "Acreditar que campo elétrico não existe sem carga de teste",
      "trigger_patterns": ["campo só existe quando", "precisa de carga para ter campo"],
      "socratic_probe": "O campo elétrico criado por uma carga depende de existir outra carga para medi-lo?"
    }
  ]
}
```

#### Integração
- Novo método `MisconceptionDetector.check(student_response, topic)` em `src/utils/`
- Chamado pelo `Intérprete` antes de passar para o `Solucionador`
- Se detectar misconception: registra no `StudentModel` + passa contexto para o `Avaliador`
- O `Avaliador` prioriza a misconception no desafio socrático

---

### 3. 🔁 Repetição Espaçada com Algoritmo SM-2
**Prioridade: ALTA — depende do Student Model (melhoria 1)**

#### O que é
O SM-2 é o algoritmo base do Anki. Calcula o intervalo ótimo de revisão com base no
histórico de acertos/erros do aluno — intervalo aumenta com acertos, reduz com erros.

#### O que implementar

```python
# src/utils/spaced_repetition.py

def calculate_next_review(concept: ConceptStatus, correct: bool, quality: int) -> int:
    """
    quality: 0-5 (0=blackout, 5=perfeito)
    Retorna próximo intervalo em dias.
    Baseado no algoritmo SM-2 (Anki).
    """
    if not correct or quality < 3:
        return 1  # revisar amanhã
    
    if concept.review_interval_days == 0:
        return 1
    elif concept.review_interval_days == 1:
        return 6
    else:
        ease_factor = max(1.3, concept.ease_factor + 0.1 - (5 - quality) * 0.08)
        return round(concept.review_interval_days * ease_factor)
```

#### UX no Streamlit
No início de cada sessão, verificar `StudentModel.get_due_for_review()`:

```python
due = student_model.get_due_for_review()
if due:
    st.info(f"📚 Você tem {len(due)} conceito(s) prontos para revisão.")
    if st.button("Revisar antes de continuar"):
        # Avaliador gera desafio baseado nos conceitos em atraso
```

#### Referência acadêmica
> "A repetição espaçada intervém em momentos críticos de decaimento de memória —
> exatamente quando o esquecimento é iminente mas ainda não ocorreu — maximizando
> o reforço de memória." — International Journal of Asian Social Science Research, 2025

---

### 4. 📊 Painel de Progresso do Aluno
**Prioridade: MÉDIA — depende do Student Model**

#### O que implementar
Nova aba no Streamlit: `📊 Meu Progresso`

```python
# src/app.py — nova tab

with tab_progresso:
    if student_model:
        # Mapa de calor da ementa
        concepts_df = student_model.to_dataframe()
        fig = px.treemap(
            concepts_df,
            path=["topic", "concept_id"],
            color="mastery_level",
            color_continuous_scale=["#FF4B4B", "#FFA500", "#00CC44"],
            title="Mapa de Domínio por Tópico"
        )
        st.plotly_chart(fig, use_container_width=True)

        # Próximas revisões
        due = student_model.get_due_for_review()
        if due:
            st.subheader("📅 Revisões Sugeridas")
            for c in due:
                st.write(f"- **{c.concept_id}** — última revisão: {c.last_reviewed}")

        # Misconceptions ativas
        active_mc = student_model.get_active_misconceptions()
        if active_mc:
            st.subheader("⚠️ Pontos de Atenção")
            for mc in active_mc:
                st.warning(f"{mc.description}")
```

---

### 5. 🤝 Modo Híbrido Professor–IA
**Prioridade: MÉDIA-ALTA — diferencial estratégico para uso institucional UFSM**

#### O que implementar
View separada `/professor` (protegida por senha simples) que agrega dados da turma:

- **Mapa de calor coletivo**: quais tópicos a turma domina / tem dificuldade
- **Misconceptions mais frequentes**: ranking das concepções equivocadas mais detectadas
- **Perguntas recorrentes**: clustering automático das dúvidas mais enviadas
- **Alerta de lacunas**: alunos com `mastery_level < 0.3` em tópicos críticos (sem identificação)

#### Referência acadêmica
> "O modelo ótimo de tutoria é híbrido humano-IA, onde professores monitoram e guiam
> o uso do LLM, enquanto a tutoria libera o professor do ensino de conteúdo para
> atividades que promovem habilidades cognitivas avançadas." — Brookings, fev/2026

---

### 6. 🔊 Interface de Voz
**Prioridade: MÉDIA — diferencial de UX, poucos sistemas acadêmicos BR têm**

#### O que implementar
Integrar entrada/saída de voz via OpenAI Realtime API ou Gemini Live:

```python
# src/utils/voice_interface.py

# Opção A: OpenAI Realtime API (gpt-4o-realtime-preview)
# Opção B: Gemini Live API
# Opção C: Whisper (STT) + TTS separados (mais simples, menos latência)

# Implementação mínima viável com Whisper + gTTS:
import openai
from gtts import gTTS

def transcribe_audio(audio_bytes: bytes) -> str:
    """Speech-to-text via Whisper."""
    result = openai.audio.transcriptions.create(
        model="whisper-1",
        file=("audio.webm", audio_bytes, "audio/webm")
    )
    return result.text

def synthesize_speech(text: str, lang: str = "pt") -> bytes:
    """Text-to-speech via gTTS."""
    tts = gTTS(text=text, lang=lang)
    # retorna bytes do MP3
```

No Streamlit: botão de microfone com `st.audio_input()` (disponível no Streamlit ≥ 1.31).

#### Referência acadêmica
> "Desenvolvimentos em LLMs multimodais como GPT-4o superam problemas de latência
> e incapacidade de interpretar sotaques que afetavam sistemas anteriores."
> — Computing Education Research, Koli Calling 2025

---

### 7. 🧬 Forgetting Curves Individuais (Nível Pesquisa)
**Prioridade: ALTA a longo prazo — é o que separa um tutor adaptativo de um chatbot**

#### O que é
Cada aluno tem velocidade de esquecimento diferente para cada tópico. O SM-2 simples
usa um fator de facilidade universal. O nível de vanguarda é modelar a curva de
esquecimento individualmente, por conceito, por aluno.

#### O que implementar (versão simplificada viável)

```python
# Extensão do StudentModel

@dataclass
class ForgettingCurve:
    """Modelo de Ebbinghaus personalizado por aluno+conceito."""
    stability: float      # quão estável está a memória (dias até 90% retenção)
    difficulty: float     # dificuldade intrínseca do conceito para este aluno
    last_review: datetime
    
    def retention_at(self, days_since_review: float) -> float:
        """R = e^(-t/S) — fórmula de Ebbinghaus."""
        import math
        return math.exp(-days_since_review / self.stability)
    
    def should_review(self, threshold: float = 0.85) -> bool:
        delta = (datetime.now() - self.last_review).days
        return self.retention_at(delta) < threshold
```

#### Referência acadêmica
> "Abordagens atuais tratam a memória do aluno como estática. O trabalho de vanguarda
> ajusta dinamicamente persona e memória por meio de curvas de esquecimento
> individualizadas, alinhando o tutor com a dinâmica temporal natural da aprendizagem
> humana." — AAAI 2025, Teaching According to Students' Aptitude

---

## Prioridade de Implementação

```
FASE 1 — Fundação (implementar primeiro)
├── [1] Student Model persistente        ← alicerce de tudo
└── [2] Detecção de misconceptions       ← impacto imediato, esforço baixo

FASE 2 — Adaptatividade
├── [3] Repetição espaçada (SM-2)        ← depende do Student Model
└── [4] Painel de progresso             ← depende do Student Model

FASE 3 — Diferenciação
├── [5] Modo híbrido professor–IA        ← valor institucional UFSM
└── [6] Interface de voz                ← diferencial de UX

FASE 4 — Vanguarda de pesquisa
└── [7] Forgetting curves individuais   ← nível publicação acadêmica
```

---

## Arquivos a criar / modificar por fase

### Fase 1
```
src/models/                          ← criar pasta
src/models/__init__.py
src/models/student_model.py          ← classe StudentModel + ConceptStatus
src/utils/misconception_detector.py  ← MisconceptionDetector
data/misconceptions.json             ← biblioteca de misconceptions UFSM
data/students/                       ← criar pasta (gitignore esta pasta)
core.py                              ← integrar StudentModel no pipeline
```

### Fase 2
```
src/utils/spaced_repetition.py       ← algoritmo SM-2
app.py                               ← tab "Meu Progresso" + aviso de revisões
```

### Fase 3
```
src/views/professor.py               ← dashboard do professor
src/utils/voice_interface.py         ← STT/TTS
app.py                               ← roteamento /professor + botão de voz
requirements.txt                     ← adicionar gtts, openai (se não tiver)
```

### Fase 4
```
src/models/forgetting_curve.py       ← modelo de Ebbinghaus por aluno
src/models/student_model.py          ← integrar ForgettingCurve no ConceptStatus
```

---

## Invariantes a manter em todas as fases

- **State Accumulation**: `StudentModel` entra no `PhysicsState` como campo adicional,
  nunca substitui o padrão existente de pipeline
- **Chaves API**: nunca hardcodar — `StudentModel` não armazena chaves
- **Privacidade**: dados de alunos ficam locais ou no pCloud do professor; nunca
  trafegam para APIs de IA sem anonimização
- **Fallback**: se `StudentModel` não carregar, sistema funciona normalmente sem ele
- **LiteLLM errors**: manter captura de `RateLimitError`, `AuthenticationError`, `APIError`

---

## Referências Principais

- Kestin et al. (2025). *AI tutoring outperforms in-class active learning*. Scientific Reports 15, 17458.
- OECD (2026). *Digital Education Outlook 2026*.
- Brookings Global Task Force (jan/2026). *A New Direction for Students in an AI World*.
- Honebein & Reigeluth (2025). *ITS effectiveness: features and conditions*. npj Science of Learning.
- Teaching According to Students' Aptitude (2025). AAAI — personalized math tutor with forgetting curves.
- Path to Conversational AI Tutors (2026). arXiv:2602.19303 — integração ITS clássico + GenAI.
- Physics-STAR framework (2024). arXiv:2406.10934 — LLM tutoring em física com STAR approach.
- Rimac ITS (Springer, 2021). *Linking Dialogue with Student Modelling for Conceptual Physics*.
