import streamlit as st
from core import PhysicsOrchestrator
import time
from pypdf import PdfReader
import io
import os
from PIL import Image
from config import Config # Importa Config para acessar modelos e chaves
from typing import Dict, Any, Optional

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="TutorIAFisica - Multi-Model", layout="wide", page_icon="🌌")

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
    .pcloud-badge { background-color: #e3f2fd; color: #1976d2; padding: 10px; border-radius: 8px; border: 1px solid #bbdefb; margin-bottom: 15px; font-size: 0.9em; }
    .fallback-notification { background-color: #f8d7da; color: #721c24; padding: 10px; border-radius: 5px; border: 1px solid #f5c6cb; margin-bottom: 15px; font-weight: bold; }
    h1, h2, h3 { color: #1c2b46; }
    </style>
    """, unsafe_allow_html=True)

def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    return "
".join([page.extract_text() + "
" for page in reader.pages])

def main():
    st.title("🌌 TutorIAFisica: Mentor Multi-Model")
    st.caption("v4.2 | Seleção Flexível de Modelos com Fallback Automático")

    # --- BARRA LATERAL ---
    with st.sidebar:
        st.header("⚙️ Configurações de IA")
        
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
            st.rerun() # Reinicia a página para aplicar a mudança (ex: desabilitar upload de imagem)

        # Gerenciamento de Chaves API (requer chaves para modelo selecionado ou fallback)
        runtime_keys = {}
        keys_to_prompt = []
        
        # Identifica quais chaves API são necessárias com base na ordem de preferência
        # e quais estão faltando no .env. Prioriza o modelo selecionado.
        models_to_check_keys = [st.session_state.selected_model_display_name] + [
            m for m in Config.MODEL_PREFERENCE_ORDER if m != st.session_state.selected_model_display_name
        ]
        
        for model_name_to_check in models_to_check_keys:
            key_name = Config.get_provider_key_name(model_name_to_check)
            if key_name and not os.getenv(key_name): # Se a chave não está no .env
                if key_name not in keys_to_prompt:
                    keys_to_prompt.append(key_name)
        
        if keys_to_prompt:
            with st.container():
                st.warning(f"Chave API para **{st.session_state.selected_model_display_name}** não encontrada no `.env`.")
                for key_name_to_get in keys_to_prompt:
                    user_key = st.text_input(f"Cole sua chave {key_name_to_get}:", type="password", key=f"runtime_key_{key_name_to_get}")
                    if user_key:
                        runtime_keys[key_name_to_get] = user_key
                        st.success(f"Chave '{key_name_to_get}' inserida para esta sessão.")
        
        # Aviso sobre multimodalidade
        model_is_multimodal = Config.is_model_multimodal(st.session_state.selected_model_display_name)
        if not model_is_multimodal:
            st.warning("O modelo selecionado não suporta entrada de imagem. O upload de foto será ignorado.")

        st.divider()
        st.header("☁️ Repositório Cloud")
        pcloud_url = st.text_input("Link Público pCloud (Pasta):", placeholder="https://u.pcloud.link/...")
        st.caption("Crie um Link Público no pCloud e cole aqui para sincronizar PDFs.")

        st.divider()
        st.header("👨‍🏫 Notas Manuais")
        uploaded_file = st.file_uploader("Upload extra (PDF/TXT)", type=["pdf", "txt"])
        manual_notes = ""
        if uploaded_file:
            if uploaded_file.type == "application/pdf":
                manual_notes = extract_text_from_pdf(uploaded_file)
            else:
                manual_notes = uploaded_file.read().decode("utf-8")
            st.info("Notas manuais carregadas.")

    # --- ENTRADA DO ALUNO ---
    enunciado = st.text_area("Descreva sua dúvida de física:", height=100, placeholder="Ex: Explique a conservação de energia em um sistema...")

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
            
            # Instancia o Orchestrator com o modelo selecionado pelo usuário e chaves runtime
            orchestrator = PhysicsOrchestrator(
                selected_model_display_name=st.session_state.selected_model_display_name,
                runtime_keys=runtime_keys
            )
            
            img_obj = Image.open(input_image) if input_image else None
            
            # Feedback visual para o usuário sobre o modelo ativo e possível fallback
            status_message = f"Consultando modelo: **{st.session_state.selected_model_display_name}**..."
            # A verificação de fallback principal ocorre DENTRO do orchestrator.run, mas podemos mostrar um aviso inicial
            # Verifica se o modelo selecionado requer chave e ela está ausente
            needs_key = Config.get_provider_key_name(st.session_state.selected_model_display_name)
            if needs_key and not os.getenv(Config.get_provider_key_name(st.session_state.selected_model_display_name)) and not runtime_keys.get(Config.get_provider_key_name(st.session_state.selected_model_display_name)):
                 status_message = f"Modelo selecionado '{st.session_state.selected_model_display_name}' sem chave configurada. Tentando fallback..."
                 st.warning(f"Chave API para o modelo selecionado '{st.session_state.selected_model_display_name}' não encontrada. O sistema tentará modelos alternativos.")

            with st.status(status_message, expanded=True) as status:
                res = orchestrator.run(enunciado, manual_notes, pcloud_url, img_obj)
                st.session_state.last_result = res
                
                if res.fallback_occurred:
                    st.warning(f"O modelo primário falhou. Usando **{res.used_model_display_name}** para a resposta.")
                elif res.used_model_display_name:
                    st.success(f"Modelo ativo: **{res.used_model_display_name}**")
                else:
                    st.error("Não foi possível obter uma resposta de nenhum modelo disponível.")
                
                status.update(label="Análise Concluída!", state="complete", expanded=False)

        else:
            st.warning("Por favor, insira um enunciado ou anexe uma imagem.")

    # --- EXIBIÇÃO DOS RESULTADOS ---
    if "last_result" in st.session_state:
        res = st.session_state.last_result
        
        if res.ufsm_alignment:
            st.markdown(f'<div class="ufsm-badge">🏛️ UFSM: {res.ufsm_alignment["codigo"]} - {res.ufsm_alignment["nome"]}</div>', unsafe_allow_html=True)

        tab1, tab2, tab3, tab4 = st.tabs(["🧩 Diálogo Socrático", "📐 Solução Matemática", "🖼️ Visualização", "📚 Contexto UFSM"])

        with tab1:
            st.markdown('<div class="agent-box border-interprete">', unsafe_allow_html=True); st.write(res.pergunta_socratica); st.markdown('</div>', unsafe_allow_html=True)
        with tab2:
            st.markdown('<div class="agent-box border-solucionador">', unsafe_allow_html=True); st.markdown(res.solution_steps); st.markdown('</div>', unsafe_allow_html=True)
        with tab3:
            st.markdown('<div class="agent-box border-visualizador">', unsafe_allow_html=True); st.code(res.code_snippet, language="python"); st.markdown('</div>', unsafe_allow_html=True)
        with tab4:
            st.markdown('<div class="agent-box border-curador">', unsafe_allow_html=True); st.markdown(res.mapa_mental_markdown); st.markdown('</div>', unsafe_allow_html=True)

        # --- AVALIAÇÃO FORMATIVA ---
        st.divider()
        st.subheader("🎯 Verificação de Aprendizagem")
        
        # Controle de estado do quiz
        if 'quiz_generated' not in st.session_state: st.session_state.quiz_generated = False
        if 'quiz_question' not in st.session_state: st.session_state.quiz_question = ""
        if 'quiz_feedback' not in st.session_state: st.session_state.quiz_feedback = ""
        
        # Gerar a pergunta apenas uma vez por rodada de consulta principal
        if res.quiz_question and not st.session_state.quiz_generated:
            st.session_state.quiz_question = res.quiz_question
            st.session_state.quiz_generated = True
            st.session_state.quiz_feedback = "" # Limpa feedback anterior

        if st.session_state.quiz_generated:
            st.markdown('<div class="agent-box border-avaliador">', unsafe_allow_html=True)
            st.markdown(f"**Desafio do Avaliador:**

{st.session_state.quiz_question}")
            
            resposta_aluno = st.text_input("Sua resposta:", key="student_answer_input")
            
            if st.button("Enviar Resposta"):
                if resposta_aluno:
                    # Instancia o avaliador para obter o feedback
                    # Usa o modelo que foi usado para a resposta principal ou o fallback
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
                    # Poderia resetar a pergunta para não re-exibir o mesmo desafio, ou ter um botão "Novo Desafio"
                else:
                    st.warning("Por favor, digite uma resposta para o desafio.")
            
            # Exibe o feedback se houver
            if st.session_state.quiz_feedback:
                st.info(f"🗨️ **Feedback:**

{st.session_state.quiz_feedback}")
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
