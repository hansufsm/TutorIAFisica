import streamlit as st
from core import PhysicsOrchestrator, TutorIAAgent, PhysicsState
from pypdf import PdfReader
import os, re
from PIL import Image
from config import Config
from models.student_model import StudentModel
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="TutorIAFisica - Multi-Model", layout="wide", page_icon="🌌")

# --- ESTILIZAÇÃO CSS ---
# Revisado para garantir a correta delimitação da string multi-linha e clareza.
# O erro 'unterminated string literal' na linha 33 em execuções anteriores foi provavelmente devido a um detalhe de parsing.
st.markdown("""
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.4/dist/katex.min.js"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.4/dist/contrib/auto-render.min.js"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.4/dist/katex.min.css">

    <style>
    /* Estilização Geral */
    .stApp { background-color: #ffffff; color: #31333f; }

    /* Customização das bolhas de chat */
    .stChatMessage { border-radius: 15px; padding: 15px; margin-bottom: 15px; border: 1px solid #e6e9ef; }

    /* KaTeX - não interferir com renderização */
    .katex, .katex-html {
        font-family: "Cambria Math", "KaTeX Gyre Termes", serif !important;
        color: #0a0a0a !important;
    }
    .katex-display {
        overflow-x: auto;
        overflow-y: hidden;
        margin: 0.5em 0 !important;
    }

    /* Identidade visual por Agente (Bordas Laterais e Fundo da Mensagem) */
    /* Usando os nomes dos agentes como classes auxiliares ou seletor de nome */
    /* Nota: A seleção direta de st.chat_message é complexa, então aplicamos estilos gerais */
    /* e adicionamos classes/identificadores se possível, ou usamos o nome do bot como teste */

    /* Exemplo de como seria se tivéssemos classes por nome: */
    /* [data-actor="Intérprete"] .stChatMessage { border-left: 8px solid #007bff; background-color: #e6f0ff; } */
    /* Mas como isso não é diretamente exposto, aplicamos estilos mais genéricos ou baseados em data-testid se disponível. */
    /* Tentativa de Targetizar baseado na estrutura atual: */
    div[data-testid="stChatMessage"] > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div[data-baseweb="box"] {
        border-left: 8px solid #1f77b4; /* Azul para Intérprete */
        background-color: #e6f0ff; /* Fundo levemente azulado */
    }
    div[data-testid="stChatMessage"] > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div[data-baseweb="box"] div[data-testid="stChatMessageName"] { /* Pode precisar de ajuste fino */
        color: #1f77b4; font-weight: bold;
    }

    /* Usando classes diretas para os agentes de forma mais previsível se possível. */
    /* Este é um fallback, caso a estrutura interna do Streamlit mude */
    .agent-solucionador, .border-solucionador { border-left: 8px solid #28a745; background-color: #e9f7ec; } /* Verde */
    .agent-visualizador, .border-visualizador { border-left: 8px solid #fd7e14; background-color: #fff9e9; } /* Laranja */
    .agent-curador, .border-curador { border-left: 8px solid #6f42c1; background-color: #f3f0f9; } /* Roxo */
    .agent-avaliador, .border-avaliador { border-left: 8px solid #dc3545; background-color: #fff5f5; } /* Vermelho */
    .border-interprete { border-left: 8px solid #007bff; background-color: #e6f0ff; } /* Azul */

    /* Container para conteúdo dos agentes */
    .agent-box { padding: 1rem; border-radius: 8px; margin: 0.5rem 0; }

    /* Badge de disciplina UFSM */
    .ufsm-badge { background-color: #f0f4f8; border-left: 4px solid #7c3aed; padding: 0.75rem; margin: 1rem 0; border-radius: 4px; font-weight: 600; }

    /* Scrollbar personalizada — light theme colors */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #ffffff; }
    ::-webkit-scrollbar-thumb { background: #d0d2d8; border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover { background: #a8adb8; }

    /* Mobile Responsiveness */
    @media (max-width: 768px) {
      /* Reduce padding on mobile */
      .main { padding: 0.5rem; }

      /* Reduce font sizes */
      h1 { font-size: 1.5rem; }
      h2 { font-size: 1.25rem; }
      h3 { font-size: 1.1rem; }

      /* Full-width buttons */
      button { width: 100%; }

      /* Better textarea on mobile */
      textarea { font-size: 16px; /* Prevents zoom-on-focus */ }

      /* Reduce sidebar padding */
      [data-testid="stSidebar"] { padding: 0.5rem; }
    }

    @media (max-width: 480px) {
      /* Extra-small phones */
      h1 { font-size: 1.25rem; }
      h2 { font-size: 1.1rem; }
      button { padding: 0.5rem 1rem; }
      .main { padding: 0.25rem; }
    }
    </style>
    """, unsafe_allow_html=True)

def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    return " ".join([page.extract_text() + " " for page in reader.pages])

def generate_reference_response(
    question: str,
    manual_notes: str = "",
    pcloud_url: str = "",
    repo_url: str = "",
    adopted_url: str = "",
    on_progress=None,
) -> PhysicsState:
    """
    Gera resposta apenas com material de referência local, sem chamar API.

    Retorna PhysicsState preenchido com:
    - ufsm_alignment e ufsm_context (busca no ementário)
    - Notas do professor e documentos carregados
    - Mensagem clara que é Modo Referência
    """
    state = PhysicsState(raw_input=question, teacher_notes=manual_notes, pcloud_url=pcloud_url)

    # Sincroniza dados externos (pCloud, notas)
    state.sync_external_data(on_progress=on_progress, repo_url=repo_url, adopted_url=adopted_url)

    # Tenta extrair conceitos da pergunta via keyword matching simples
    # Tokeniza a pergunta e busca no syllabus
    keywords = re.findall(r'\b\w{4,}\b', question.lower())
    state.concepts = keywords[:3] if keywords else ["conceito"]

    # Busca match no ementário UFSM
    state._check_ufsm_syllabus()

    # Preenche campos com mensagem de Modo Referência
    state.pergunta_socratica = (
        "⚠️ **Modo Referência** (sem explicação gerada por IA)\n\n"
        "Para uma explicação completa, configure uma chave API na sidebar e selecione 'Modo IA'."
    )

    # Se encontrou tópico na UFSM, exibe a ementa
    if state.ufsm_context:
        state.pergunta_socratica += f"\n\n**Tópico Encontrado na UFSM:**\n\n{state.ufsm_context}"

    # Exibe notas do professor se disponíveis
    if state.professor_notes_text.strip():
        state.solution_steps = (
            "**📝 Notas do Professor:**\n\n" +
            state.professor_notes_text[:1500] +  # Limita a 1500 chars para não sobrecarregar
            ("\n\n... (truncado)" if len(state.professor_notes_text) > 1500 else "")
        )
    else:
        state.solution_steps = "*(Nenhuma nota do professor carregada)*"

    # Exibe documentos adotados se disponíveis
    if state.adopted_docs_text.strip():
        state.code_snippet = (
            "**📗 Documentos Adotados:**\n\n" +
            state.adopted_docs_text[:1500] +
            ("\n\n... (truncado)" if len(state.adopted_docs_text) > 1500 else "")
        )
    else:
        state.code_snippet = "*(Nenhum documento adotado carregado)*"

    # Exibe ementa no mapa mental
    if state.ufsm_alignment:
        disc = state.ufsm_alignment
        state.mapa_mental_markdown = f"""
### 🏛️ Disciplina UFSM: {disc.get('nome', 'N/A')} ({disc.get('codigo', 'N/A')})

**Período:** {disc.get('periodo', 'N/A')}

**Temas da Ementa:**
{chr(10).join(f"- {t}" for t in disc.get('temas', []))}

**Bibliografia Básica:**
{chr(10).join(f"- {b}" for b in disc.get('bibliografia_basica', [])[:5])}
"""
    else:
        state.mapa_mental_markdown = "*(Tópico não encontrado na ementa da UFSM)*"

    # Avaliador: sem quiz em Modo Referência
    state.quiz_question = "*(Quiz não disponível em Modo Referência)*"

    # Flag: Modo Referência não conta como "modelo utilizado"
    state.used_model_display_name = None
    state.fallback_occurred = False

    return state

def is_error_string(content: str) -> bool:
    """Check if content is an error message from failed LLM calls."""
    return isinstance(content, str) and content.strip().startswith("Erro:")

def display_content_or_error(content: str, content_type: str = "markdown"):
    """Display content or show error warning if it's an error string."""
    if not content:
        st.info("*(Sem resposta)*")
        return
    if is_error_string(content):
        st.warning(f"❌ Falha ao processar: {content}")
        return
    if content_type == "markdown":
        st.markdown(content, unsafe_allow_html=True)
    elif content_type == "math":
        st.markdown(content, unsafe_allow_html=True)
    elif content_type == "code":
        st.code(content, language="python")

def display_math_content(content: str):
    """Exibe conteúdo com suporte melhorado a LaTeX/KaTeX."""
    if not content:
        return
    st.markdown(content, unsafe_allow_html=True)

def main():
    st.title("🌌 TutorIAFisica: Mentor Multi-Model")
    st.caption("v4.3 | Seleção Flexível de Modelos com Fallback Automático e Gerenciamento de Chaves")

    # --- ONBOARDING ---
    with st.expander("ℹ️ Como usar o TutorIAFisica (clique para expandir)", expanded=False):
        st.markdown("""
        ### 🎓 Você tem um esquadrão de 4 especialistas

        **🔵 Intérprete** — Faz perguntas reflexivas para você pensar (método socrático)
        **🟢 Solucionador** — Resolve com rigor matemático e unidades SI
        **🟠 Visualizador** — Cria gráficos e código interativo
        **🟣 Curador** — Conecta sua dúvida a materiais acadêmicos reais

        ### 📝 Passos Básicos

        1. **Descreva sua dúvida** na caixa de texto (abaixo)
        2. **Opcionalmente:** carregue um PDF/imagem ou links de materiais (sidebar)
        3. **Clique "Iniciar Análise"** para processar
        4. **Veja 4 respostas** em abas diferentes (uma por especialista)
        5. **Clique "Desafie-me!"** para testar seu conhecimento com um quiz

        ### ❓ FAQ

        **P: Por que 4 respostas diferentes?**
        A: Cada agente tem uma perspectiva pedagógica diferente. Juntas, criam uma compreensão profunda.

        **P: O que é "método socrático"?**
        A: Técnica onde o professor (aqui, o Intérprete) faz perguntas em vez de dar respostas diretas. Você aprende questionando.

        **P: Como funciona a busca de materiais?**
        A: O sistema busca em 5 níveis: suas notas → documentos adotados → ementa UFSM → portais .edu.br → arXiv & Semantic Scholar.

        **P: Posso usar isso offline?**
        A: Não, precisa de internet (chaves de API de modelos LLM + busca web).
        """)

    # --- BARRA LATERAL ---
    with st.sidebar:
        st.markdown("## 🎓 Identificação do Aluno")
        student_id_input = st.text_input("Nome ou Matrícula:", placeholder="ex: João Silva ou 202312345", key="student_id_input")
        if student_id_input and st.session_state.get("student_id") != student_id_input:
            st.session_state.student_id = student_id_input
            st.session_state.student_model = StudentModel.load(student_id_input, data_dir="data/students")
            st.success(f"✅ Identificado como: **{student_id_input}**")

        st.divider()
        st.markdown("## ⚙️ Configurações de IA")

        # Seleção de Modelo
        available_model_names = list(Config.AVAILABLE_MODELS.keys())
        default_model_name = Config.DEFAULT_MODEL_DISPLAY_NAME
        default_index = available_model_names.index(default_model_name) if default_model_name in available_model_names else 0

        selected_model_display_name = st.selectbox(
            "Escolha o Motor de IA:",
            available_model_names,
            index=default_index,
            key="model_selector"
        )

        # Persistência da escolha do modelo na sessão
        if "selected_model_display_name" not in st.session_state:
            st.session_state.selected_model_display_name = selected_model_display_name

        current_selection_in_state = st.session_state.selected_model_display_name
        if current_selection_in_state != selected_model_display_name:
            st.session_state.selected_model_display_name = selected_model_display_name
            st.toast(f"✅ Modelo atualizado para: **{selected_model_display_name}**")
            st.rerun() # Reinicia a página para aplicar a mudança (ex: desabilitar upload de imagem)

        # Gerenciamento de Chaves API
        keys_to_prompt_names = []

        # Identifica quais chaves API são necessárias com base na ordem de preferência
        # e quais estão faltando no .env. Prioriza o modelo selecionado.
        models_to_check_keys = [st.session_state.selected_model_display_name] + [
            m for m in Config.MODEL_PREFERENCE_ORDER if m != st.session_state.selected_model_display_name
        ]

        for model_name_to_check in models_to_check_keys:
            key_name = Config.get_provider_key_name(model_name_to_check)
            if key_name and not os.getenv(key_name): # Se a chave não está no .env
                if key_name not in keys_to_prompt_names:
                    keys_to_prompt_names.append(key_name)

        if keys_to_prompt_names:
            with st.container():
                st.warning(f"Chave API para **{st.session_state.selected_model_display_name}** não encontrada no `.env`.")
                for key_name_to_get in keys_to_prompt_names:
                    user_key = st.text_input(f"Cole sua chave {key_name_to_get}:", type="password", key=f"runtime_key_{key_name_to_get}")
                    if user_key:
                        st.success(f"Chave '{key_name_to_get}' inserida para esta sessão.")

        model_is_multimodal = Config.is_model_multimodal(st.session_state.selected_model_display_name)

        st.divider()
        st.markdown("## 📚 Materiais de Entrada")

        st.markdown("### 👨‍🏫 Notas Manuais")
        st.markdown("*Suas anotações, resumos, ou PDF do material didático*")
        uploaded_file = st.file_uploader("Upload PDF/TXT", type=["pdf", "txt"], key="manual_upload")
        manual_notes = ""
        if uploaded_file:
            if uploaded_file.type == "application/pdf":
                manual_notes = extract_text_from_pdf(uploaded_file)
                if not manual_notes.strip():
                    st.warning("⚠️ PDF sem texto extraível (pode ser escaneado). Conteúdo não será enviado aos agentes.")
                else:
                    st.info(f"✅ PDF carregado ({len(manual_notes)} caracteres extraídos).")
            else:
                manual_notes = uploaded_file.read().decode("utf-8")
                st.info(f"✅ TXT carregado ({len(manual_notes)} caracteres).")

        st.markdown("### 📷 Entrada de Imagem (Opcional)")
        if model_is_multimodal:
            st.markdown("*Foto de diagrama, equação manuscrita, ou gráfico*")
            input_image = st.file_uploader("Upload PNG/JPG", type=["png", "jpg", "jpeg", "webp"], key="image_upload")
        else:
            st.info(f"❌ **{st.session_state.selected_model_display_name}** não processa imagens. Modelos com suporte: Gemini, Claude, OpenAI Vision.")
            input_image = None

        st.divider()
        st.markdown("## ☁️ Materiais do Professor & Disciplina")

        st.markdown("### ☁️ Material da Sessão (Seu pCloud)")
        st.markdown("*Exercícios ou recursos que você está trabalhando nesta sessão*")
        pcloud_url = st.text_input("Link pCloud da sua sessão:", placeholder="https://u.pcloud.com/#/publink?code=SEU_CODIGO", key="pcloud_session")

        st.markdown("### 📦 Repositório Permanente (Professor)")
        st.markdown("*Materiais do professor (mantidos entre semestres)*")
        pcloud_repo_url = st.text_input("Link pCloud Repositório:", key="pcloud_repo_url", placeholder="https://u.pcloud.com/#/publink?code=...")

        st.markdown("### 📗 Documentos Adotados")
        st.markdown("*PDFs de livros ou materiais oficialmente adotados*")
        adopted_docs_url = st.text_input("Link pCloud Livros/Slides:", key="adopted_docs_url", placeholder="https://u.pcloud.com/#/publink?code=...")

        st.divider()
        st.markdown("## 🔍 Processamento")

        st.markdown("### 🌐 Busca Web Inteligente")
        web_search_enabled = st.checkbox("Consultar portais acadêmicos + arXiv", value=True, key="web_search_toggle", help="Adiciona ~10-15 segundos, conecta dúvida a pesquisa real")

        st.divider()
        st.markdown("## 🔬 Modo de Resposta")
        response_mode = st.radio(
            "Como deseja a resposta?",
            ["Modo IA", "Modo Referência"],
            index=0,
            help="Modo IA: Explicação completa com os 5 agentes (requer API). Modo Referência: Material local (ementário UFSM + notas do professor, sem API)."
        )

    # --- NOTIFICAÇÃO DE REVISÕES PENDENTES ---
    if "student_model" in st.session_state and st.session_state.student_model:
        due = st.session_state.student_model.get_due_for_review()
        if due:
            due_list = ", ".join(c.topic for c in due[:5])
            st.info(f"📅 **{len(due)} conceito(s) para revisar hoje:** {due_list}")

    # --- ENTRADA DO ALUNO ---
    enunciado = st.text_area("Descreva sua dúvida de física:", height=100, placeholder="Ex: calcule o tempo de queda de uma bola de 2kg largada do repouso a 4,3 metros de altura")

    if st.button("🚀 Iniciar Análise do Esquadrão"):
        if enunciado or input_image:
            # Obtém as chaves runtime inseridas pelo usuário
            runtime_keys = {}
            # Verifica todas as chaves necessárias para os modelos na ordem de preferência
            for model_name_in_order in Config.MODEL_PREFERENCE_ORDER:
                 key_name = Config.get_provider_key_name(model_name_in_order)
                 if key_name and not os.getenv(key_name): # Se a chave não está no .env
                     runtime_key_input = st.session_state.get(f"runtime_key_{key_name}")
                     if runtime_key_input:
                         runtime_keys[key_name] = runtime_key_input

            img_obj = Image.open(input_image) if input_image else None

            with st.status("🔄 Iniciando análise...", expanded=True) as status:
                # Branch: Modo Referência vs. Modo IA
                if response_mode == "Modo Referência":
                    # Gera resposta apenas com material de referência (sem chamar API)
                    res = generate_reference_response(
                        question=enunciado,
                        manual_notes=manual_notes,
                        pcloud_url=pcloud_url,
                        repo_url=pcloud_repo_url,
                        adopted_url=adopted_docs_url,
                        on_progress=st.write
                    )
                    st.session_state.last_result = res
                    st.info("📚 **Modo Referência ativado** — exibindo apenas material local. Configure uma chave API e selecione 'Modo IA' para resposta com IA.")
                else:
                    # Modo IA: usa orchestrator com modelos LLM
                    orchestrator = PhysicsOrchestrator(
                        selected_model_display_name=st.session_state.selected_model_display_name,
                        runtime_keys=runtime_keys
                    )

                    # Verifica se o modelo selecionado requer chave e ela está ausente
                    needs_key = Config.get_provider_key_name(st.session_state.selected_model_display_name)
                    if needs_key and not os.getenv(needs_key) and not runtime_keys.get(needs_key):
                         st.warning(f"Chave API para o modelo selecionado '{st.session_state.selected_model_display_name}' não encontrada. O sistema tentará modelos alternativos.")

                    res = orchestrator.run(
                        enunciado,
                        manual_notes,
                        pcloud_url,
                        repo_url=pcloud_repo_url,
                        adopted_url=adopted_docs_url,
                        enable_web_search=web_search_enabled,
                        image=img_obj,
                        on_progress=st.write
                    )
                    st.session_state.last_result = res

                    # Update Student Model (apenas para Modo IA)
                    if "student_model" in st.session_state and st.session_state.student_model and res.concepts:
                        discipline = res.ufsm_alignment["nome"] if res.ufsm_alignment else ""
                        st.session_state.student_model.update_after_session(res.concepts, discipline)
                        st.session_state.student_model.save("data/students")
                        st.session_state.last_seen_concept_id = re.sub(r"[^\w]", "_", res.concepts[0].lower()) if res.concepts else ""

                    if res.fallback_occurred:
                        provider_label = Config.get_provider_label(res.used_model_display_name)
                        model_id = Config.get_model_id(res.used_model_display_name)
                        st.warning(f"⚠️ Fallback ativo — Respondido por **{res.used_model_display_name}** · {provider_label} · `{model_id}`")
                    elif res.used_model_display_name:
                        provider_label = Config.get_provider_label(res.used_model_display_name)
                        model_id = Config.get_model_id(res.used_model_display_name)
                        st.success(f"🤖 Respondido por **{res.used_model_display_name}** · {provider_label} · `{model_id}`")
                    else:
                        st.error("Não foi possível obter uma resposta de nenhum modelo disponível.")

                st.divider()
                st.subheader("📊 Fontes Utilizadas (Hierarquia)")
                sources_used = []

                # Nível 1
                prof_combined = []
                if res.professor_notes_text.strip():
                    prof_combined.append("Notas do Professor")
                if res.pcloud_repo_text.strip():
                    prof_combined.append("Repositório")
                if prof_combined:
                    st.write(f"**1️⃣ Materiais do Professor:** {' + '.join(prof_combined)}")
                    sources_used.append("Professor")

                # Nível 2
                if res.adopted_docs_text.strip():
                    st.write("**2️⃣ Documentos Adotados** incorporados")
                    sources_used.append("Adotados")

                # Nível 3
                if res.ufsm_context:
                    st.write("**3️⃣ Ementa UFSM** localizada e utilizada")
                    sources_used.append("UFSM")

                # Nível 4
                if res.web_edu_br_text.strip():
                    st.write("**4️⃣ Portais Acadêmicos .edu.br** consultados")
                    sources_used.append(".edu.br")

                # Nível 5
                if res.intl_refs_text.strip():
                    st.write("**5️⃣ Referências Internacionais** (arXiv/Semantic Scholar)")
                    sources_used.append("Internacional")

                # Fora da hierarquia
                if res.pcloud_session_text.strip():
                    st.write("☁️ **Material do Aluno** incorporado")
                    sources_used.append("Aluno")

                if not sources_used:
                    st.info("✨ Resposta gerada pelo **Modelo de IA** (sem materiais de referência)")

                status.update(label="✅ Análise Concluída!", state="complete", expanded=False)

        else:
            st.warning("Por favor, insira um enunciado ou anexe uma imagem.")

    # --- EXIBIÇÃO DOS RESULTADOS ---
    if "last_result" in st.session_state:
        res = st.session_state.last_result
        
        if res.ufsm_alignment:
            st.markdown(f'<div class="ufsm-badge">🏛️ UFSM: {res.ufsm_alignment["codigo"]} - {res.ufsm_alignment["nome"]}</div>', unsafe_allow_html=True)

        tab1, tab2, tab3, tab4, tab5 = st.tabs(["🧩 Diálogo Socrático", "📐 Solução Matemática", "🖼️ Visualização", "📚 Contexto UFSM", "📊 Meu Progresso"])

        with tab1:
            st.markdown('<div class="agent-box border-interprete">', unsafe_allow_html=True)
            display_content_or_error(res.pergunta_socratica, "markdown")
            st.markdown('</div>', unsafe_allow_html=True)
        with tab2:
            st.markdown('<div class="agent-box border-solucionador">', unsafe_allow_html=True)
            display_content_or_error(res.solution_steps, "math")
            st.markdown('</div>', unsafe_allow_html=True)
        with tab3:
            st.markdown('<div class="agent-box border-visualizador">', unsafe_allow_html=True)
            if res.used_model_display_name is None:
                # Modo Referência: code_snippet é markdown, não código Python
                display_content_or_error(res.code_snippet, "markdown")
            else:
                # Modo IA: code_snippet é código Python
                display_content_or_error(res.code_snippet, "code")
            st.markdown('</div>', unsafe_allow_html=True)
        with tab4:
            st.markdown('<div class="agent-box border-curador">', unsafe_allow_html=True)
            display_content_or_error(res.mapa_mental_markdown, "markdown")
            st.markdown('</div>', unsafe_allow_html=True)

        with tab5:
            sm = st.session_state.get("student_model")
            if sm and sm.concepts:
                records = sm.to_dataframe_records()
                df = pd.DataFrame(records)
                fig = px.treemap(
                    df, path=["topic", "concept"], values="times_seen",
                    color="mastery", color_continuous_scale=["#FF4B4B", "#FFA500", "#00CC44"],
                    hover_data=["status", "times_seen"],
                    title=f"Mapa de Domínio — {sm.student_id} ({sm.session_count} sessões)",
                )
                st.plotly_chart(fig, use_container_width=True)

                due = sm.get_due_for_review()
                if due:
                    st.subheader("📅 Revisões Sugeridas Hoje")
                    for c in due:
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"**{c.topic}** ({c.ufsm_discipline or 'Geral'})")
                        with col2:
                            st.write(f"Nível: {c.mastery_level:.0%}")

                total = len(sm.concepts)
                mastered = sum(1 for c in sm.concepts.values() if c.status in ("mastered", "consolidated"))
                st.metric("Conceitos Vistos", total)
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Dominados", mastered)
                with col2:
                    total_q = sum(c.quiz_attempts for c in sm.concepts.values())
                    correct_q = sum(c.quiz_correct for c in sm.concepts.values())
                    acc = f"{correct_q/total_q:.0%}" if total_q > 0 else "–"
                    st.metric("Acerto no Quiz", acc)
            else:
                st.info("Identifique-se na sidebar e faça sua primeira sessão para ver seu progresso aqui.")

        # --- AVALIAÇÃO FORMATIVA ---
        st.divider()
        st.subheader("🎯 Verificação de Aprendizagem")
        
        # Controle de estado do quiz
        if 'quiz_visible' not in st.session_state: st.session_state.quiz_visible = False
        if 'quiz_question' not in st.session_state: st.session_state.quiz_question = ""
        if 'quiz_feedback' not in st.session_state: st.session_state.quiz_feedback = ""
        
        # Botão para ativar o desafio (não disponível em Modo Referência)
        if res.used_model_display_name is not None:  # Modo IA only
            if st.button("Desafie-me! Quero testar meu conhecimento"):
                st.session_state.quiz_visible = True
            st.session_state.quiz_question = res.quiz_question # Armazena a pergunta gerada
            st.session_state.quiz_feedback = "" # Limpa feedback anterior
            st.session_state.quiz_answer_submitted = False # Reinicia o estado de submissão
            # Não resetar last_result aqui, pois queremos manter a resposta principal visível.

        # Exibe os campos do quiz se estiverem visíveis
        if st.session_state.quiz_visible:
            st.markdown('<div class="agent-box border-avaliador">', unsafe_allow_html=True)
            st.markdown(f"**Desafio do Avaliador:**\n\n{st.session_state.quiz_question}")

            resposta_aluno = st.text_input("Sua resposta:", key="student_answer_input")

            col1, col2 = st.columns([2, 1])
            with col1:
                quiz_self_eval = st.radio("Você entendeu?", ["✅ Entendi", "❌ Ainda tenho dúvida"], horizontal=True, key="quiz_self_eval")
            with col2:
                send_button = st.button("Enviar Resposta")

            if send_button:
                if resposta_aluno:
                    # Instancia o avaliador para obter o feedback
                    # Usa o modelo que respondeu à consulta principal ou o fallback
                    model_for_eval_display = res.used_model_display_name if res.used_model_display_name else st.session_state.selected_model_display_name
                    evaluator_model_id = Config.get_model_id(model_for_eval_display)

                    evaluator = TutorIAAgent("Avaliador", "Você é o 'Avaliador Pedagógico'. Dê feedback socrático.")

                    with st.spinner("Avaliador analisando..."):
                        # Chama o método de avaliação
                        feedback = evaluator.ask(
                            prompt=resposta_aluno,
                            context=st.session_state.quiz_question, # Contexto é a própria pergunta para avaliação
                            model_id=evaluator_model_id # Usa o modelo que está ativo/foi usado
                        )

                    st.session_state.quiz_feedback = feedback
                    st.session_state.quiz_answer_submitted = True # Marca que uma resposta foi enviada
                    st.session_state.quiz_visible = False # Esconde campos de resposta após enviar

                    # Update Student Model com resultado do quiz
                    if "student_model" in st.session_state and st.session_state.get("last_seen_concept_id"):
                        correct = quiz_self_eval == "✅ Entendi"
                        st.session_state.student_model.update_quiz_result(st.session_state.last_seen_concept_id, correct)
                        st.session_state.student_model.save("data/students")

                    st.rerun() # Reexecuta a página para exibir o feedback fora do bloco quiz_visible
                else:
                    st.warning("Por favor, digite uma resposta para o desafio.")

            st.markdown('</div>', unsafe_allow_html=True)

        # Exibe o feedback fora do bloco quiz_visible — sempre aparece após enviar
        if st.session_state.get("quiz_feedback"):
            st.markdown('<div class="agent-box border-avaliador">', unsafe_allow_html=True)
            st.info(f"🗨️ **Feedback:**\n\n{st.session_state.quiz_feedback}")
            # Botão para pedir um novo desafio (resetando o estado do quiz)
            if st.button("Pedir Novo Desafio"):
                st.session_state.quiz_generated = False
                st.session_state.quiz_question = ""
                st.session_state.quiz_feedback = ""
                st.session_state.last_result = None # Limpa resultados anteriores para recarregar
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
