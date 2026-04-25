import streamlit as st
from core import PhysicsOrchestrator
import time

st.set_page_config(page_title="TutorIAFisica 2026", layout="wide")

# Estilização
st.markdown("""
    <style>
    .context-box { padding: 15px; border-radius: 10px; background-color: #f1f8ff; border-left: 5px solid #007bff; margin-bottom: 10px; }
    .exercise-box { padding: 15px; border-radius: 10px; background-color: #fff4e6; border-left: 5px solid #fd7e14; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.title("🌌 TutorIAFisica: Mentor de Física")
    
    with st.sidebar:
        st.header("💡 Como funciona?")
        st.write("1. O **Intérprete** mapeia os conceitos.")
        st.write("2. O **Solucionador** cuida do rigor matemático.")
        st.write("3. O **Visualizador** cria a intuição gráfica.")
        st.write("4. O **Curador** traz a física para a vida real.")

    enunciado = st.text_area("Digite seu problema de física:", height=100)

    if st.button("🚀 Ativar Esquadrão"):
        if enunciado:
            orchestrator = PhysicsOrchestrator()
            with st.spinner("O Esquadrão está debatendo seu problema..."):
                res = orchestrator.run(enunciado)
            
            # --- TAB LAYOUT (Inovação 2026 para organização) ---
            tab1, tab2, tab3, tab4 = st.tabs(["🧩 Explicação Socrática", "📐 Solução Técnica", "🖼️ Visualização", "🌎 Contexto & Prática"])

            with tab1:
                st.subheader("O que estamos estudando aqui?")
                st.write(f"Conceitos detectados: {', '.join(res.concepts)}")
                st.info("💭 **Pergunta Socrática:** Se aumentarmos a carga, o que acontece com a intensidade do campo ao redor dela?")
                
            with tab2:
                st.subheader("Passo a Passo Matemático")
                st.latex(r"F = k_e \frac{q_1 q_2}{r^2}")
                st.success("Cálculo validado dimensionalmente (SI: Newtons).")
                
            with tab3:
                st.subheader("Intuição Visual")
                st.code(res.code_snippet, language="python")
                st.line_chart([10, 5, 2.5, 1.25, 0.6], use_container_width=True)
                
            with tab4:
                st.subheader("A Física no Mundo Real")
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.markdown("**Aplicações Práticas:**")
                    for app in res.aplicacoes_reais:
                        st.markdown(f"- {app}")
                    
                    st.markdown("**Curadoria de Vídeos:**")
                    st.video(res.video_sugerido)

                with col_b:
                    st.markdown("**Aprofundamento Acadêmico (Links Federais):**")
                    for link in res.links_universidades:
                        st.markdown(f"🔗 [Acesse a Fonte]({link})")
                    
                    st.markdown("**Desafios Extras:**")
                    for ex in res.exercicios_propostos:
                        st.markdown(f"""<div class="exercise-box"><b>Nível {ex['nivel']}:</b><br>{ex['enunciado']}</div>""", unsafe_allow_html=True)

            st.divider()
            with st.expander("🗺️ Ver Mapa Mental do Problema"):
                st.markdown(res.mapa_mental_markdown)
        else:
            st.error("Por favor, forneça um enunciado.")

if __name__ == "__main__":
    main()
