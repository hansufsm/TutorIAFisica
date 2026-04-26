import streamlit as st
import os
import time
from PIL import Image
from pypdf import PdfReader
from src.core import PhysicsOrchestrator
from src.config import Config

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="TutorIAFisica v3.5", layout="wide", page_icon="🌌")

# --- ESTILIZAÇÃO CSS ---
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
    </style>
    """, unsafe_allow_html=True)

def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    return "\n".join([page.extract_text() for page in reader.pages])

def main():
    st.title("🌌 TutorIAFisica: Mentor Acadêmico")
    st.caption("v3.5 | Suporte Multi-Model (Gemini & DeepSeek via LiteLLM)")

    # --- BARRA LATERAL ---
    with st.sidebar:
        st.header("🤖 Configurações de IA")
        model_choice = st.radio(
            "Escolha o Motor de Inteligência:",
            ["Gemini 2.0 (Padrão)", "DeepSeek (Reserva)"],
            help="Alterne para o DeepSeek se os créditos do Google terminarem."
        )
        
        selected_model = Config.PRIMARY_MODEL if "Gemini" in model_choice else Config.FALLBACK_MODEL
        st.info(f"Modelo Ativo: `{selected_model}`")

        st.divider()
        st.header("☁️ Repositório Cloud")
        pcloud_url = st.text_input("Link Público pCloud:", placeholder="https://u.pcloud.link/...")
        
        st.divider()
        st.header("📸 Entrada Visual")
        input_image = st.file_uploader("Foto do Exercício (Apenas Gemini)", type=["jpg", "png"])
        if input_image:
            st.image(input_image, caption="Imagem carregada", use_container_width=True)

        st.divider()
        st.header("👨‍🏫 Notas Manuais")
        uploaded_notes = st.file_uploader("Upload PDF extra", type=["pdf"])
        manual_notes = ""
        if uploaded_notes:
            manual_notes = extract_text_from_pdf(uploaded_notes)
            st.info("Notas manuais processadas.")

    # --- ENTRADA DO ALUNO ---
    enunciado = st.text_area("Descreva sua dúvida de física:", height=100)

    if st.button("🚀 Iniciar Análise do Esquadrão"):
        if enunciado or input_image:
            # Inicializa orquestrador com o modelo selecionado
            orchestrator = PhysicsOrchestrator(model_override=selected_model)
            img_obj = Image.open(input_image) if input_image else None
            
            with st.status(f"Ativando agentes via {model_choice}...", expanded=True) as status:
                res = orchestrator.run(enunciado, manual_notes, pcloud_url, img_obj)
                st.session_state.result = res
                status.update(label="Análise Concluída!", state="complete", expanded=False)

    # --- EXIBIÇÃO DOS RESULTADOS ---
    if "result" in st.session_state:
        res = st.session_state.result
        
        if res.ufsm_alignment:
            st.markdown(f'<div class="ufsm-badge">🏛️ UFSM: {res.ufsm_alignment["codigo"]} - {res.ufsm_alignment["nome"]}</div>', unsafe_allow_html=True)

        t1, t2, t3, t4 = st.tabs(["🧩 Intérprete", "📐 Solucionador", "🖼️ Visualizador", "📚 Curador"])

        with t1:
            st.markdown('<div class="agent-box border-interprete">', unsafe_allow_html=True)
            st.write(res.pergunta_socratica)
            st.markdown('</div>', unsafe_allow_html=True)
        with t2:
            st.markdown('<div class="agent-box border-solucionador">', unsafe_allow_html=True)
            st.markdown(res.solution_steps)
            st.markdown('</div>', unsafe_allow_html=True)
        with t3:
            st.markdown('<div class="agent-box border-visualizador">', unsafe_allow_html=True)
            st.code(res.code_snippet, language="python")
            st.markdown('</div>', unsafe_allow_html=True)
        with t4:
            st.markdown('<div class="agent-box border-curador">', unsafe_allow_html=True)
            st.markdown(res.mapa_mental_markdown)
            st.markdown('</div>', unsafe_allow_html=True)

        # --- AVALIAÇÃO FORMATIVA ---
        st.divider()
        st.subheader("🎯 Desafio de Verificação")
        st.markdown('<div class="agent-box border-avaliador">', unsafe_allow_html=True)
        st.markdown(res.quiz_question)
        ans = st.text_input("Sua resposta:")
        if st.button("Avaliar"):
            # Usa o mesmo modelo para avaliação
            evaluator_orchestrator = PhysicsOrchestrator(model_override=selected_model)
            feedback = evaluator_orchestrator.agents["evaluator"].ask(ans, res.quiz_question)
            st.info(f"🗨️ Feedback: {feedback}")
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
