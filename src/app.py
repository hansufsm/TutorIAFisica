import streamlit as st
from core import PhysicsOrchestrator
import time

# Configuração da Página
st.set_page_config(page_title="TutorIAFisica - Mentor de Física", layout="centered", page_icon="🌌")

# Injeção de CSS para Estilização de Agentes e Dark Mode
st.markdown("""
    <style>
    /* Estilização Geral */
    .stApp { background-color: #0e1117; }
    
    /* Customização das bolhas de chat */
    .stChatMessage {
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 10px;
        border: 1px solid #30363d;
    }
    
    /* Cores das equações LaTeX */
    .katex { color: #58a6ff; font-size: 1.1em; }
    
    /* Identidade visual por Agente (Bordas Laterais) */
    [data-testimonial-name="Intérprete"] { border-left: 6px solid #1f77b4 !important; }
    [data-testimonial-name="Solucionador"] { border-left: 6px solid #2ca02c !important; }
    [data-testimonial-name="Visualizador"] { border-left: 6px solid #ff7f0e !important; }
    [data-testimonial-name="Curador"] { border-left: 6px solid #9467bd !important; }
    
    /* Scrollbar personalizada */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #0e1117; }
    ::-webkit-scrollbar-thumb { background: #30363d; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.title("🌌 TutorIAFisica")
    st.caption("Seu esquadrão de especialistas em Física | Gemini 2.0 Dynamic")

    # Inicializa histórico de chat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Exibe mensagens do histórico
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar=msg["avatar"]):
            st.markdown(msg["content"])

    # Input do aluno
    if prompt := st.chat_input("Pergunte sobre mecânica, eletromagnetismo, óptica..."):
        # Adiciona pergunta do aluno
        st.session_state.messages.append({"role": "user", "content": prompt, "avatar": "👤"})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # Processamento
        orchestrator = PhysicsOrchestrator()
        
        # O esquadrão responde em sequência
        with st.status("Ativando Esquadrão de Especialistas...", expanded=True) as status:
            # 1. Intérprete
            st.write("🧩 **Intérprete** analisando lógica...")
            res = orchestrator.run(prompt) # Note: run() já executa todos internamente
            status.update(label="Análise Concluída!", state="complete", expanded=False)

        # Exibição das respostas dos Agentes
        
        # 1. Intérprete
        with st.chat_message("Intérprete", avatar="🧩"):
            content = f"**Conceitos:** {', '.join(res.concepts)}\n\n{res.pergunta_socratica}"
            st.markdown(content)
            st.session_state.messages.append({"role": "Intérprete", "content": content, "avatar": "🧩"})

        # 2. Solucionador
        with st.chat_message("Solucionador", avatar="📐"):
            st.markdown("### 📐 Passo a Passo Matemático")
            st.markdown(res.solution_steps)
            st.session_state.messages.append({"role": "Solucionador", "content": res.solution_steps, "avatar": "📐"})

        # 3. Visualizador
        with st.chat_message("Visualizador", avatar="🖼️"):
            st.markdown("### 🖼️ Representação Visual")
            st.code(res.code_snippet, language="python")
            st.session_state.messages.append({"role": "Visualizador", "content": "Visualização gerada.", "avatar": "🖼️"})

        # 4. Curador
        with st.chat_message("Curador", avatar="📚"):
            st.markdown("### 📚 Contexto Acadêmico")
            st.markdown(res.mapa_mental_markdown)
            st.session_state.messages.append({"role": "Curador", "content": res.mapa_mental_markdown, "avatar": "📚"})

if __name__ == "__main__":
    main()
