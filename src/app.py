import streamlit as st
from core import PhysicsOrchestrator
import time

st.set_page_config(page_title="TutorIAFisica 2026", layout="wide", page_icon="🌌")

# Estilização
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #f8f9fa; border-radius: 5px; padding: 10px; }
    .stTabs [aria-selected="true"] { background-color: #007bff; color: white; }
    div.stButton > button:first-child { background-color: #007bff; color: white; height: 3em; width: 100%; border-radius: 8px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.title("🌌 TutorIAFisica: Mentor Inteligente")
    st.caption("Arquitetura 2026 conectada ao Gemini 1.5 Flash")
    
    with st.sidebar:
        st.header("💡 Sistema de Agentes")
        st.info("Cada aba representa a análise de um especialista diferente do esquadrão.")
        st.divider()
        st.markdown("### 📚 Fontes Curadas")
        st.write("Prioridade: .edu.br | .gov.br")

    enunciado = st.text_area("Descreva seu problema ou dúvida de física:", height=120, placeholder="Ex: Qual a velocidade de escape da Terra?")

    if st.button("🚀 Consultar Esquadrão"):
        if enunciado:
            orchestrator = PhysicsOrchestrator()
            
            with st.status("O Esquadrão está analisando seu problema...", expanded=True) as status:
                st.write("🔍 **Intérprete** mapeando conceitos...")
                # The actual work happens here
                res = orchestrator.run(enunciado)
                status.update(label="Análise Concluída!", state="complete", expanded=False)
            
            # Layout em Abas
            tab1, tab2, tab3, tab4 = st.tabs([
                "🧩 Diálogo Socrático", 
                "📐 Solução Matemática", 
                "🖼️ Visualização", 
                "🌎 Contexto Acadêmico"
            ])

            with tab1:
                st.subheader("Análise Conceitual")
                st.write(res.pergunta_socratica)
                
            with tab2:
                st.subheader("Passo a Passo Rigoroso")
                st.markdown(res.solution_steps)
                
            with tab3:
                st.subheader("Código de Simulação")
                st.code(res.code_snippet, language="python")
                st.info("Copie o código acima e rode em um ambiente Python para ver o gráfico.")
                
            with tab4:
                st.subheader("Física no Mundo Real e Fontes")
                st.markdown(res.mapa_mental_markdown)

            st.divider()
            st.success("🤖 Feedback: O esquadrão utilizou dados científicos para esta resposta.")
        else:
            st.error("Por favor, digite uma pergunta.")

if __name__ == "__main__":
    main()
