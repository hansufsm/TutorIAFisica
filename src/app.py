import streamlit as st
from core import PhysicsOrchestrator
import time
from pypdf import PdfReader
import io

# Configuração da Página
st.set_page_config(page_title="TutorIAFisica - Mentor de Física", layout="centered", page_icon="🌌")

# Injeção de CSS para Estilização de Agentes, Dark Mode e Selo UFSM
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .stChatMessage { border-radius: 15px; padding: 15px; margin-bottom: 10px; border: 1px solid #30363d; }
    .katex { color: #58a6ff; font-size: 1.1em; }
    [data-testimonial-name="Intérprete"] { border-left: 6px solid #1f77b4 !important; }
    [data-testimonial-name="Solucionador"] { border-left: 6px solid #2ca02c !important; }
    [data-testimonial-name="Visualizador"] { border-left: 6px solid #ff7f0e !important; }
    [data-testimonial-name="Curador"] { border-left: 6px solid #9467bd !important; }
    
    .ufsm-badge {
        background-color: #f1c40f;
        color: #2c3e50;
        padding: 10px;
        border-radius: 10px;
        border: 2px solid #f39c12;
        margin-bottom: 15px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def main():
    st.title("🌌 TutorIAFisica")
    st.caption("Seu esquadrão de especialistas em Física | Alinhamento Institucional UFSM")

    # Sidebar para Notas do Professor
    with st.sidebar:
        st.header("👨‍🏫 Área do Professor")
        uploaded_file = st.file_uploader("Carregar Notas de Aula (PDF/TXT)", type=["pdf", "txt"])
        teacher_notes = ""
        
        if uploaded_file is not None:
            if uploaded_file.type == "application/pdf":
                teacher_notes = extract_text_from_pdf(uploaded_file)
            else:
                teacher_notes = uploaded_file.read().decode("utf-8")
            st.success("✅ Notas de aula carregadas!")

        st.divider()
        st.header("💡 Sistema de Agentes")
        st.info("O esquadrão está sincronizado com o ementário oficial da UFSM.")

    # Inicializa histórico de chat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Exibe mensagens do histórico
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar=msg["avatar"]):
            st.markdown(msg["content"])

    # Input do aluno
    if prompt := st.chat_input("Pergunte sobre mecânica, eletromagnetismo, óptica..."):
        st.session_state.messages.append({"role": "user", "content": prompt, "avatar": "👤"})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        orchestrator = PhysicsOrchestrator()
        
        with st.status("Consultando o esquadrão e o ementário UFSM...", expanded=True) as status:
            res = orchestrator.run(prompt, teacher_notes=teacher_notes)
            status.update(label="Análise Concluída!", state="complete", expanded=False)

        # 1. Alinhamento Institucional UFSM (Destaque)
        if res.ufsm_alignment:
            d = res.ufsm_alignment
            st.markdown(f"""
                <div class="ufsm-badge">
                    🏛️ ALINHAMENTO INSTITUCIONAL UFSM<br>
                    Disciplina: {d['codigo']} - {d['nome']} ({d['periodo']}º Período)<br>
                    Bibliografia Básica recomendada no curso 102/679: {', '.join(d['bibliografia_basica'])}
                </div>
            """, unsafe_allow_html=True)

        # Exibição das respostas dos Agentes
        with st.chat_message("Intérprete", avatar="🧩"):
            content = f"**Conceitos:** {', '.join(res.concepts)}\n\n{res.pergunta_socratica}"
            st.markdown(content)
            st.session_state.messages.append({"role": "Intérprete", "content": content, "avatar": "🧩"})

        with st.chat_message("Solucionador", avatar="📐"):
            st.markdown("### 📐 Passo a Passo Matemático")
            st.markdown(res.solution_steps)
            st.session_state.messages.append({"role": "Solucionador", "content": res.solution_steps, "avatar": "📐"})

        with st.chat_message("Visualizador", avatar="🖼️"):
            st.markdown("### 🖼️ Representação Visual")
            st.code(res.code_snippet, language="python")
            st.session_state.messages.append({"role": "Visualizador", "content": "Visualização gerada.", "avatar": "🖼️"})

        with st.chat_message("Curador", avatar="📚"):
            st.markdown("### 📚 Contexto Acadêmico")
            st.markdown(res.mapa_mental_markdown)
            st.session_state.messages.append({"role": "Curador", "content": res.mapa_mental_markdown, "avatar": "📚"})

if __name__ == "__main__":
    main()
