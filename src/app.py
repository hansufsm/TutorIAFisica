import streamlit as st
from core import PhysicsOrchestrator, Evaluator
import time
from pypdf import PdfReader
import io

# Configuração da Página para Tema Claro e Layout Largo
st.set_page_config(page_title="TutorIAFisica - Mentor de Física", layout="wide", page_icon="🌌")

# Estilização Customizada para Tema Claro
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

    # Sidebar
    with st.sidebar:
        st.header("👨‍🏫 Área do Professor")
        uploaded_file = st.file_uploader("Notas de Aula (PDF/TXT)", type=["pdf", "txt"])
        teacher_notes = ""
        if uploaded_file:
            if uploaded_file.type == "application/pdf":
                teacher_notes = extract_text_from_pdf(uploaded_file)
            else:
                teacher_notes = uploaded_file.read().decode("utf-8")
            st.success("✅ Notas carregadas!")
        
        st.divider()
        st.header("📚 Institucional")
        st.info("Sincronizado com o Ementário UFSM (Curso 102/679).")

    # Área de Entrada
    enunciado = st.text_area("Descreva o problema ou conceito de física:", height=100)

    if st.button("🚀 Ativar Esquadrão"):
        if enunciado:
            orchestrator = PhysicsOrchestrator()
            with st.status("O Esquadrão está analisando e preparando desafios...", expanded=True) as status:
                res = orchestrator.run(enunciado, teacher_notes=teacher_notes)
                st.session_state.last_result = res
                status.update(label="Análise Concluída!", state="complete", expanded=False)

    # Verifica se há resultados para exibir
    if "last_result" in st.session_state:
        res = st.session_state.last_result
        
        if res.ufsm_alignment:
            st.markdown(f"""<div class="ufsm-badge">🏛️ CONFORMIDADE UFSM: {res.ufsm_alignment['codigo']} - {res.ufsm_alignment['nome']}</div>""", unsafe_allow_html=True)

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

        # SEÇÃO DE DESAFIO (Avaliação Formativa)
        st.divider()
        st.subheader("🎯 Desafio do Esquadrão (Verificação de Aprendizagem)")
        st.markdown('<div class="agent-box border-avaliador">', unsafe_allow_html=True)
        st.markdown(f"**O Avaliador propõe:**\n\n{res.quiz_question}")
        
        resposta_aluno = st.text_input("Sua resposta para o desafio:")
        if st.button("Enviar Resposta"):
            if resposta_aluno:
                evaluator = Evaluator("Avaliador", "")
                with st.spinner("O Avaliador está analisando sua resposta..."):
                    feedback = evaluator.evaluate_answer(res.quiz_question, resposta_aluno)
                st.info(f"🗨️ **Feedback do Avaliador:**\n\n{feedback}")
            else:
                st.warning("Por favor, digite uma resposta para o desafio.")
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
