import streamlit as st
from core import PhysicsOrchestrator, TutorIAAgent
from pypdf import PdfReader
import os
from PIL import Image
from config import Config

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="TutorIAFisica - Multi-Model", layout="wide", page_icon="🌌")

# --- ESTILIZAÇÃO CSS ---
# Revisado para garantir a correta delimitação da string multi-linha e clareza.
# O erro 'unterminated string literal' na linha 33 em execuções anteriores foi provavelmente devido a um detalhe de parsing.
st.markdown("""
    <style>
    /* Estilização Geral */
    .stApp { background-color: #ffffff; color: #31333f; }
    
    /* Customização das bolhas de chat */
    .stChatMessage { border-radius: 15px; padding: 15px; margin-bottom: 15px; border: 1px solid #e6e9ef; }
    
    /* Cores das equações LaTeX */
    .katex { font-size: 1.1em; color: #58a6ff; }
    
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
    .agent-solucionador { border-left: 8px solid #28a745; background-color: #e9f7ec; } /* Verde */
    .agent-visualizador { border-left: 8px solid #fd7e14; background-color: #fff9e9; } /* Laranja */
    .agent-curador { border-left: 8px solid #6f42c1; background-color: #f3f0f9; } /* Roxo */
    .agent-avaliador { border-left: 8px solid #dc3545; background-color: #fff5f5; } /* Vermelho */
    
    /* Scrollbar personalizada */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #0e1117; }
    ::-webkit-scrollbar-thumb { background: #30363d; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    return " ".join([page.extract_text() + " " for page in reader.pages])

def main():
    st.title("🌌 TutorIAFisica: Mentor Multi-Model")
    st.caption("v4.3 | Seleção Flexível de Modelos com Fallback Automático e Gerenciamento de Chaves")

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

        # Gerenciamento de Chaves API
        runtime_keys = {}
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
                        runtime_keys[key_name_to_get] = user_key
                        st.success(f"Chave '{key_name_to_get}' inserida para esta sessão.")
        
        model_is_multimodal = Config.is_model_multimodal(st.session_state.selected_model_display_name)
        if not model_is_multimodal:
            st.warning("O modelo selecionado não suporta entrada de imagem. O upload de foto será ignorado.")

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

        st.divider()
        st.header("📷 Entrada de Imagem")
        if model_is_multimodal:
            input_image = st.file_uploader("Upload de Imagem (foto do problema):", type=["png", "jpg", "jpeg", "webp"])
        else:
            input_image = None

        st.divider()
        st.header("☁️ Repositório Cloud")
        pcloud_url = st.text_input("Link Público pCloud (Pasta):", placeholder="https://u.pcloud.com/#/puplink?code=YwnXZ5JRkIVuJIKjhmWtlGzorl0jp6UeX")
        st.caption("Crie um Link Público no pCloud e cole aqui para sincronizar PDFs.")

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
            
            # Verifica se o modelo selecionado requer chave e ela está ausente
            needs_key = Config.get_provider_key_name(st.session_state.selected_model_display_name)
            if needs_key and not os.getenv(Config.get_provider_key_name(st.session_state.selected_model_display_name)) and not runtime_keys.get(Config.get_provider_key_name(st.session_state.selected_model_display_name)):
                 st.warning(f"Chave API para o modelo selecionado '{st.session_state.selected_model_display_name}' não encontrada. O sistema tentará modelos alternativos.")

            with st.status("🔄 Iniciando análise...", expanded=True) as status:
                res = orchestrator.run(enunciado, manual_notes, pcloud_url, img_obj, on_progress=st.write)
                st.session_state.last_result = res

                if res.fallback_occurred:
                    st.warning(f"Fallback ativo. Usando **{res.used_model_display_name}** para a resposta.")
                elif res.used_model_display_name:
                    st.success(f"Modelo ativo: **{res.used_model_display_name}**")
                else:
                    st.error("Não foi possível obter uma resposta de nenhum modelo disponível.")

                status.update(label="✅ Análise Concluída!", state="complete", expanded=False)

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
        if 'quiz_visible' not in st.session_state: st.session_state.quiz_visible = False
        if 'quiz_generated' not in st.session_state: st.session_state.quiz_generated = False
        if 'quiz_question' not in st.session_state: st.session_state.quiz_question = ""
        if 'quiz_feedback' not in st.session_state: st.session_state.quiz_feedback = ""
        
        # Botão para ativar o desafio
        if st.button("Desafie-me! Quero testar meu conhecimento"):
            st.session_state.quiz_visible = True
            st.session_state.quiz_question = res.quiz_question # Armazena a pergunta gerada
            st.session_state.quiz_feedback = "" # Limpa feedback anterior
            st.session_state.quiz_answer_submitted = False # Reinicia o estado de submissão
            # Não resetar last_result aqui, pois queremos manter a resposta principal visível.

        # Exibe os campos do quiz se estiverem visíveis
        if st.session_state.quiz_visible:
            st.markdown('<div class="agent-box border-avaliador">', unsafe_allow_html=True)
            st.markdown(f"**Desafio do Avaliador:**{st.session_state.quiz_question}")
            
            resposta_aluno = st.text_input("Sua resposta:", key="student_answer_input")
            
            if st.button("Enviar Resposta"):
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
                else:
                    st.warning("Por favor, digite uma resposta para o desafio.")
            
            # Exibe o feedback se houver
            if st.session_state.quiz_feedback:
                st.info(f"🗨️ **Feedback:**{st.session_state.quiz_feedback}")
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
