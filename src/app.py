import streamlit as st
from core import PhysicsOrchestrator, Evaluator
import time
from pypdf import PdfReader
import io
import os

# Configuração da Página
st.set_page_config(page_title="TutorIAFisica - Mentor Acadêmico", layout="wide", page_icon="🌌")

# Estilização
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #31333f; }
    .agent-box { padding: 20px; border-radius: 10px; margin-bottom: 15px; border: 1px solid #e6e9ef; background-color: #f8f9fa; }
    .border-interprete { border-left: 8px solid #007bff; }
    .border-solucionador { border-left: 8px solid #28a745; }
    .border-visualizador { border-left: 8px solid #fd7e14; }
    .border-curador { border-left: 8px solid #6f42c1; }
    .border-avaliador { border-left: 8px solid #dc3545; background-color: #fff5f5; }
    .ufsm-badge { background-color: #fff3cd; color: #856404; padding: 15px; border-radius: 8px; border: 1px solid #ffeeba; margin-bottom: 20px; font-weight: bold; }
    .pcloud-badge { background-color: #e3f2fd; color: #1976d2; padding: 10px; border-radius: 8px; border: 1px solid #bbdefb; margin-bottom: 15px; font-size: 0.9em; }
    h1, h2, h3 { color: #1c2b46; }
    </style>
    """, unsafe_allow_html=True)

def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def main():
    st.title("🌌 TutorIAFisica: Mentor Acadêmico")
    st.markdown("---")

    # Barra Lateral
    with st.sidebar:
        st.header("☁️ Repositório Cloud")
        pcloud_base = os.path.expanduser("~/pCloudDrive/TutorIA_Notes")
        if os.path.exists(pcloud_base):
            st.success("☁️ pCloud Drive Conectado")
        else:
            st.warning("⚠️ pCloud não detectado em ~/pCloudDrive")

        st.divider()
        st.header("👨‍🏫 Notas Manuais")
        uploaded_file = st.file_uploader("Upload extra (PDF/TXT)", type=["pdf", "txt"])
        manual_notes = ""
        if uploaded_file:
            if uploaded_file.type == "application/pdf":
                manual_notes = extract_text_from_pdf(uploaded_file)
            else:
                manual_notes = uploaded_file.read().decode("utf-8")
            st.info("Notas manuais adicionadas ao contexto.")

    # Entrada do Aluno
    enunciado = st.text_area("O que vamos estudar hoje?", height=100, placeholder="Ex: Explique as leis de Kepler.")

    if st.button("🚀 Iniciar Aula"):
        if enunciado:
            orchestrator = PhysicsOrchestrator()
            with st.status("Sincronizando com pCloud e ativando Agentes...", expanded=True) as status:
                res = orchestrator.run(enunciado, teacher_notes=manual_notes)
                st.session_state.last_result = res
                status.update(label="Sincronização e Análise concluídas!", state="complete", expanded=False)

    # Exibição de Resultados
    if "last_result" in st.session_state:
        res = st.session_state.last_result
        
        # Alertas de Contexto
        col_badges1, col_badges2 = st.columns(2)
        with col_badges1:
            if res.ufsm_alignment:
                st.markdown(f"""<div class="ufsm-badge">🏛️ UFSM: {res.ufsm_alignment['codigo']} - {res.ufsm_alignment['nome']}</div>""", unsafe_allow_html=True)
        with col_badges2:
            if res.pcloud_notes_found:
                st.markdown(f"""<div class="pcloud-badge">✅ Sincronizado com pCloud: Notas de aula do professor incorporadas.</div>""", unsafe_allow_html=True)

        tab1, tab2, tab3, tab4 = st.tabs(["🧩 Diálogo Socrático", "📐 Solução Matemática", "🖼️ Visualização", "📚 Contexto UFSM"])

        with tab1:
            st.markdown('<div class="agent-box border-interprete">', unsafe_allow_html=True)
            st.write(res.pergunta_socratica)
            st.markdown('</div>', unsafe_allow_html=True)
        with tab2:
            st.markdown('<div class="agent-box border-solucionador">', unsafe_allow_html=True)
            st.markdown(res.solution_steps)
            st.markdown('</div>', unsafe_allow_html=True)
        with tab3:
            st.markdown('<div class="agent-box border-visualizador">', unsafe_allow_html=True)
            st.code(res.code_snippet, language="python")
            st.markdown('</div>', unsafe_allow_html=True)
        with tab4:
            st.markdown('<div class="agent-box border-curador">', unsafe_allow_html=True)
            st.markdown(res.mapa_mental_markdown)
            st.markdown('</div>', unsafe_allow_html=True)

        # Seção de Desafio
        st.divider()
        st.subheader("🎯 Verificação de Aprendizagem")
        st.markdown('<div class="agent-box border-avaliador">', unsafe_allow_html=True)
        st.markdown(f"**Desafio do Avaliador:**\n\n{res.quiz_question}")
        
        resposta_aluno = st.text_input("Sua resposta:")
        if st.button("Enviar Resposta"):
            evaluator = Evaluator("Avaliador", "")
            with st.spinner("Analisando..."):
                feedback = evaluator.evaluate_answer(res.quiz_question, resposta_aluno)
            st.info(f"🗨️ **Feedback:** {feedback}")
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
