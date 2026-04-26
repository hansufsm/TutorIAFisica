import streamlit as st
from core import PhysicsOrchestrator
import time
from pypdf import PdfReader
import io
import os
from PIL import Image
from config import Config # Importa Config para acessar modelos e chaves

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
    h1, h2, h3 { color: #1c2b46; }
    /* Estilo para desabilitar seletor de imagem */
    .disabled-upload label { color: #999 !important; cursor: not-allowed !important; }
    </style>
    """, unsafe_allow_html=True)

def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    return "
".join([page.extract_text() for page in reader.pages])

def main():
    st.title("🌌 TutorIAFisica: Mentor Inteligente")
    st.caption("v4.0 | Multi-Model Selection & Fallback")

    # --- BARRA LATERAL ---
    with st.sidebar:
        st.header("⚙️ Configurações de IA")
        
        # Modelo Selecionável
        available_model_names = list(Config.AVAILABLE_MODELS.keys())
        selected_model_display_name = st.selectbox(
            "Escolha o Motor de Inteligência:",
            available_model_names,
            index=available_model_names.index(Config.DEFAULT_MODEL_DISPLAY_NAME) if Config.DEFAULT_MODEL_DISPLAY_NAME in available_models else 0
        )
        
        # Armazena a seleção na sessão para uso posterior
        if "selected_model_display_name" not in st.session_state:
            st.session_state.selected_model_display_name = selected_model_display_name
        
        # Atualiza a seleção se mudou
        if st.session_state.selected_model_display_name != selected_model_display_name:
            st.session_state.selected_model_display_name = selected_model_display_name
            st.rerun() # Reinicia a página para atualizar UI (ex: desabilitar upload de imagem)

        # Verificação e input condicional de chaves API
        model_needs_key = not Config.get_provider_key_name(st.session_state.selected_model_display_name) == None # Se o modelo requer chave
        
        runtime_keys = {}
        api_keys_missing_for_selection = []
        
        # Verifica a chave para o modelo selecionado
        key_name = Config.get_provider_key_name(st.session_state.selected_model_display_name)
        if key_name and not os.getenv(key_name):
            api_keys_missing_for_selection.append(key_name)
            
        # Adiciona verificação para modelos de fallback que podem ser necessários
        # Simplificado: Assume que se o selecionado falha, verificamos o próximo
        # Idealmente, isso seria mais dinâmico baseado na ordem de preferência e chaves disponíveis.
        # Por agora, apenas informamos sobre a necessidade de chaves para os modelos selecionáveis.

        if api_keys_missing_for_selection:
            st.warning(f"Chave API necessária para **{st.session_state.selected_model_display_name}** não encontrada no `.env`.")
            for key_name_to_get in api_keys_missing_for_selection:
                user_key = st.text_input(f"Cole sua chave {key_name_to_get}:", type="password", key=f"runtime_key_{key_name_to_get}")
                if user_key:
                    runtime_keys[key_name_to_get] = user_key
                    st.success("Chave inserida para esta sessão.")
        
        model_is_multimodal = Config.is_model_multimodal(st.session_state.selected_model_display_name)
        if not model_is_multimodal:
            st.warning("O modelo selecionado não suporta entrada de imagem. A função de upload de foto será desabilitada.")

        st.divider()
        st.header("☁️ Repositório Cloud")
        pcloud_url = st.text_input("Link Público pCloud (Pasta):", placeholder="https://u.pcloud.link/...")
        st.caption("Crie um Link Público no pCloud e cole aqui para sincronizar PDFs.")

        st.divider()
        st.header("👨‍🏫 Notas Manuais")
        uploaded_file = st.file_uploader("Upload extra (PDF)", type=["pdf", "txt"])
        manual_notes = ""
        if uploaded_file:
            if uploaded_file.type == "application/pdf":
                manual_notes = extract_text_from_pdf(uploaded_file)
            else:
                manual_notes = uploaded_file.read().decode("utf-8")
            st.info("Notas manuais carregadas.")

    # --- ENTRADA DO ALUNO ---
    # Campos de entrada desabilitados se o modelo não for multimodal e houver imagem
    image_upload_disabled = False
    if not Config.is_model_multimodal(st.session_state.selected_model_display_name):
        image_upload_disabled = True

    enunciado = st.text_area("Descreva sua dúvida de física:", height=100, 
                             placeholder="Ex: Explique a segunda lei da termodinâmica.")
    
    # Se for multimodal e não estiver desabilitado, mostra o uploader
    if not image_upload_disabled:
        input_image = st.file_uploader("Ou anexe uma imagem do seu exercício", type=["jpg", "jpeg", "png"])
        if input_image:
            st.image(input_image, caption="Imagem carregada", use_container_width=True)
    else:
        # Se multimodal estiver desabilitado, o campo não aparece
        pass

    if st.button("🚀 Iniciar Análise do Esquadrão"):
        if enunciado or input_image:
            # Obtém as chaves runtime inseridas pelo usuário
            runtime_keys = {}
            for model_name in Config.MODEL_PREFERENCE_ORDER:
                key_name = Config.get_provider_key_name(model_name)
                if key_name and not os.getenv(key_name): # Se a chave não está no .env
                    runtime_key_input = st.session_state.get(f"runtime_key_{key_name}")
                    if runtime_key_input:
                        runtime_keys[key_name] = runtime_key_input
            
            orchestrator = PhysicsOrchestrator(
                selected_model_display_name=st.session_state.selected_model_display_name,
                runtime_keys=runtime_keys
            )
            
            img_obj = Image.open(input_image) if input_image else None
            
            with st.status(f"Consultando modelo: **{st.session_state.selected_model_display_name}**...", expanded=True) as status:
                res = orchestrator.run(enunciado, manual_notes, pcloud_url, img_obj)
                st.session_state.last_result = res
                
                if res.fallback_occurred:
                    st.warning(f"O modelo principal falhou. Usando **{res.used_model_display_name}** para a resposta.")
                elif res.used_model_display_name:
                    st.success(f"Modelo ativo: **{res.used_model_display_name}**")
                else:
                    st.error("Não foi possível obter uma resposta de nenhum modelo.")
                
                status.update(label="Análise Concluída!", state="complete", expanded=False)

        else:
            st.warning("Por favor, insira um enunciado ou anexe uma imagem.")

    # --- EXIBIÇÃO DOS RESULTADOS ---
    if "last_result" in st.session_state:
        res = st.session_state.last_result
        
        if res.ufsm_alignment:
            st.markdown(f'<div class="ufsm-badge">🏛️ UFSM: {res.ufsm_alignment["codigo"]} - {res.ufsm_alignment["nome"]}</div>', unsafe_allow_html=True)

        t1, t2, t3, t4 = st.tabs(["🧩 Diálogo Socrático", "📐 Solução Matemática", "🖼️ Visualização", "📚 Contexto UFSM"])

        with t1:
            st.markdown('<div class="agent-box border-interprete">', unsafe_allow_html=True); st.write(res.pergunta_socratica); st.markdown('</div>', unsafe_allow_html=True)
        with t2:
            st.markdown('<div class="agent-box border-solucionador">', unsafe_allow_html=True); st.markdown(res.solution_steps); st.markdown('</div>', unsafe_allow_html=True)
        with t3:
            st.markdown('<div class="agent-box border-visualizador">', unsafe_allow_html=True); st.code(res.code_snippet, language="python"); st.markdown('</div>', unsafe_allow_html=True)
        with t4:
            st.markdown('<div class="agent-box border-curador">', unsafe_allow_html=True); st.markdown(res.mapa_mental_markdown); st.markdown('</div>', unsafe_allow_html=True)

        # --- AVALIAÇÃO FORMATIVA ---
        st.divider()
        st.subheader("🎯 Verificação de Aprendizagem")
        st.markdown('<div class="agent-box border-avaliador">', unsafe_allow_html=True)
        st.markdown(res.quiz_question)
        ans = st.text_input("Sua resposta:")
        if st.button("Avaliar"):
            # Precisamos instanciar o orchestrator com o modelo que realmente respondeu para o avaliador
            # Ou passar o modelo explicitamente para o evaluator.ask
            # Para simplificar, vamos usar o modelo selecionado na UI como fallback, mas a chave pode ser diferente
            evaluator_model_id = Config.get_model_id(st.session_state.selected_model_display_name)
            feedback = orchestrator.agents["evaluator"].ask(ans, question=res.quiz_question, model_id=evaluator_model_id) # Assumindo que a pergunta tbm vai no prompt
            st.info(f"🗨️ Feedback: {feedback}")
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
