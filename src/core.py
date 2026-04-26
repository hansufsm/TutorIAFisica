import os
import time
import json
import litellm
import streamlit as st
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from pypdf import PdfReader
from PIL import Image
from src.config import Config

load_dotenv()

class PhysicsState:
    """Objeto de Estado do Problema (Design Pattern: State)."""
    def __init__(self, raw_input: str, teacher_notes: str = "", pcloud_url: str = "", image: Any = None):
        self.raw_input = raw_input
        self.teacher_notes = teacher_notes
        self.pcloud_url = pcloud_url
        self.image_input = image
        
        self.concepts = []
        self.solution_steps = ""
        self.pergunta_socratica = ""
        self.code_snippet = ""
        self.mapa_mental_markdown = ""
        self.ufsm_alignment = None 
        self.pcloud_notes_found = False
        
        # Campos de Avaliação Formativa
        self.quiz_question: str = ""
        self.quiz_answer_submitted: bool = False
        self.quiz_feedback: str = ""

        # Informações de fallback e modelo utilizado
        self.used_model_display_name: Optional[str] = None
        self.fallback_occurred: bool = False

    def sync_external_data(self):
        """Sincroniza dados de fontes externas (pCloud, Ementário UFSM)."""
        cloud_text = PCloudManager.fetch_notes(self.pcloud_url)
        if cloud_text:
            self.teacher_notes = (self.teacher_notes + "

" + cloud_text).strip()
            self.pcloud_notes_found = True
        self._check_ufsm_syllabus()

    def _check_ufsm_syllabus(self):
        """Busca match no ementário da UFSM baseado nos conceitos identificados."""
        if not os.path.exists(Config.SYLLABUS_PATH): return
        try:
            with open(Config.SYLLABUS_PATH, 'r', encoding='utf-8') as f:
                syllabus = json.load(f)
            for d in syllabus['disciplinas']:
                for t in d['temas']:
                    for conceito in self.concepts:
                        if conceito.lower() in t.lower(): # Simples busca por substring
                            self.ufsm_alignment = d
                            return
        except Exception as e:
            print(f"Erro ao consultar ementário UFSM: {e}")

class TutorIAAgent:
    """Classe base para todos os agentes de IA."""
    def __init__(self, name: str, system_instruction: str):
        self.name = name
        self.system_instruction = system_instruction

    def ask(self, prompt: str, context: str = "", image: Any = None, model_id: str = None) -> str:
        """Realiza a chamada para o LLM usando LiteLLM com o modelo especificado."""
        if not model_id:
            model_id = Config.get_model_id(Config.DEFAULT_MODEL_DISPLAY_NAME) 
            print(f"Aviso: Nenhum model_id especificado, usando padrão {model_id}")

        messages = [
            {"role": "system", "content": f"{self.system_instruction}
CONTEXTO: {context}"},
            {"role": "user", "content": prompt}
        ]

        # Tratamento de entrada multimodal
        if image and Config.is_model_multimodal(Config.get_model_display_name_by_id(model_id)):
            messages[1]["content"] = [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": image}]
        elif image and not Config.is_model_multimodal(Config.get_model_display_name_by_id(model_id)):
            print(f"[!] Aviso: Imagem fornecida, mas modelo '{model_id}' não é multimodal.")
            # O modelo de texto puro simplesmente ignorará a imagem.

        try:
            response = litellm.completion(model=model_id, messages=messages)
            return response.choices[0].message.content
        except litellm.RateLimitError as e:
            raise RuntimeError(f"Rate limit exceeded for {model_id}: {e}") from e
        except litellm.AuthenticationError as e:
            raise RuntimeError(f"Authentication error for {model_id}: {str(e)}") from e
        except litellm.APIError as e:
            raise RuntimeError(f"API Error for {model_id}: {str(e)}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected error with {model_id}: {str(e)}") from e

class PhysicsOrchestrator:
    def __init__(self, selected_model_display_name: str, runtime_keys: Dict[str, str]):
        self.selected_model_display_name = selected_model_display_name
        self.runtime_keys = runtime_keys
        self.model_id = Config.get_model_id(selected_model_display_name)
        self.is_multimodal = Config.is_model_multimodal(selected_model_display_name)
        
        self.used_model_display_name: Optional[str] = None
        self.fallback_occurred: bool = False

        self.agents = {
            "interpreter": TutorIAAgent("Intérprete", "Você é um professor socrático. Identifique conceitos e crie perguntas reflexivas."),
            "solver": TutorIAAgent("Matemático", "Resolva com LaTeX e rigor."),
            "visualizer": TutorIAAgent("Visualizador", "Gere apenas código Python (matplotlib/plotly) funcional."),
            "curator": TutorIAAgent("Curador", "Forneça aplicações reais, links acadêmicos e mapa mental."),
            "evaluator": TutorIAAgent("Avaliador", "Crie desafios pedagógicos curtos e dê feedback socrático.")
        }

    def _attempt_model_call(self, agent_name: str, prompt: str, context: str, image: Any = None) -> tuple[str, Optional[str], bool]:
        """Tenta chamar modelos na ordem de preferência, implementando fallback automático."""
        models_to_try_display_names = Config.MODEL_PREFERENCE_ORDER
        last_error_message = "Nenhum modelo testado com sucesso."
        
        # Determina a ordem de modelos a tentar, priorizando o selecionado pelo usuário
        preferred_order = []
        if self.selected_model_display_name and self.selected_model_display_name in Config.AVAILABLE_MODELS:
            preferred_order.append(self.selected_model_display_name)
        
        for model_name in models_to_try_display_names:
            if model_name not in preferred_order:
                preferred_order.append(model_name)

        for model_display_name in preferred_order:
            model_info = Config.AVAILABLE_MODELS.get(model_display_name)
            if not model_info: continue 
            
            current_model_id = model_info["id"]
            
            # Verificar capacidade multimodal
            if image and not model_info.get("multimodal", False):
                print(f"[*] Skipped {model_display_name}: Não suporta imagem.")
                continue 

            # Verificar disponibilidade da chave API
            key_name = Config.get_provider_key_name(model_display_name)
            api_key_present = Config.check_key_availability_for_model(model_display_name, self.runtime_keys)

            if key_name and not api_key_present:
                print(f"[*] Skipping {model_display_name}: API key '{key_name}' missing.")
                continue 

            try:
                agent = self.agents[agent_name]
                
                # Configura variáveis de ambiente para LiteLLM, se chave foi fornecida runtime
                litellm_env = {}
                if key_name and key_name in self.runtime_keys:
                    litellm_env[key_name] = self.runtime_keys[key_name]
                
                # Chama o agente com o modelo específico
                response_text = agent.ask(prompt, context=context, image=image, model_id=current_model_id)
                
                if response_text and "ERRO" not in response_text and "Erro na API" not in response_text:
                    # Sucesso! Retorna a resposta, nome do modelo e indica que não houve fallback (ainda)
                    return response_text, model_display_name, False
                else:
                    last_error_message = f"Model {model_display_name} ({current_model_id}) returned an error: {response_text}"
                    print(f"[*] {last_error_message}")

            except (litellm.RateLimitError, litellm.AuthenticationError, litellm.APIError) as e:
                last_error_message = f"{type(e).__name__} for {model_display_name} ({current_model_id}). Trying next model. Error: {str(e)}"
                print(f"[*] {last_error_message}")
            except Exception as e:
                last_error_message = f"Unexpected error with {model_display_name} ({current_model_id}): {str(e)}"
                print(f"[*] {last_error_message}")
            
            time.sleep(Config.DELAY_BETWEEN_AGENTS) # Espera antes de tentar o próximo

        return f"Erro: Todos os modelos falharam. Último erro: {last_error_message}", None, True

    def run(self, input_data: str, teacher_notes: str = "", pcloud_url: str = "", image: Any = None, selected_model_display_name: str = Config.DEFAULT_MODEL_DISPLAY_NAME, runtime_keys: Dict[str, str] = {}):
        """Executa o pipeline de agentes com fallback automático."""
        
        state = PhysicsState(input_data, teacher_notes, pcloud_url, image)
        state.sync_external_data()
        
        used_model_name = None
        fallback_occurred = False
        
        # --- Execução sequencial dos agentes com fallback ---
        
        # Intérprete
        response, model_name_used_int, fb_int = self._attempt_model_call("interpreter", input_data, state.teacher_notes, image)
        state.pergunta_socratica = response
        if "," in response:
            state.concepts = [c.strip() for c in response.split("
")[0].split(",")]
        else:
            state.concepts = ["Física Geral"]
        state._check_ufsm_syllabus()
        
        if fb_int: state.fallback_occurred = True
        state.used_model_display_name = model_name_used_int

        time.sleep(Config.DELAY_BETWEEN_AGENTS)

        # Solucionador
        response, model_name_solver, fb_solver = self._attempt_model_call("solver", input_data, state.teacher_notes, image)
        state.solution_steps = response
        if fb_solver: state.fallback_occurred = True
        if model_name_solver: state.used_model_display_name = model_name_solver # Atualiza modelo usado se fallback ocorreu

        time.sleep(Config.DELAY_BETWEEN_AGENTS)
        
        # Visualizador
        response, model_name_vis, fb_vis = self._attempt_model_call("visualizer", input_data, state.teacher_notes, image)
        state.code_snippet = response.replace("```python", "").replace("```", "").strip()
        if fb_vis: state.fallback_occurred = True
        if model_name_vis: state.used_model_display_name = model_name_vis

        time.sleep(Config.DELAY_BETWEEN_AGENTS)

        # Curador
        combined_context = f"{state.teacher_notes}
        
ALINHAMENTO UFSM: {state.ufsm_alignment['nome'] if state.ufsm_alignment else 'N/A'}"
        response, model_name_curator, fb_curator = self._attempt_model_call("curator", input_data, combined_context, image)
        state.mapa_mental_markdown = response
        if fb_curator: state.fallback_occurred = True
        if model_name_curator: state.used_model_display_name = model_name_curator
        
        time.sleep(Config.DELAY_BETWEEN_AGENTS)

        # Avaliador
        response, model_name_eval, fb_eval = self._attempt_model_call("evaluator", input_data, state.teacher_notes, image)
        state.quiz_question = response
        if fb_eval: state.fallback_occurred = True
        if model_name_eval: state.used_model_display_name = model_name_eval
        
        return state

if __name__ == "__main__":
    # --- Teste Básico de Fallback ---
    print("--- TESTE CORE: Seleção de Modelo e Fallback ---")
    
    # Teste 1: Simular seleção manual de um modelo que pode ter chave ausente (ex: Gemini 3.0 Preview se GEMINI_API_KEY não estiver no .env)
    print("
Tentando modelo selecionado (Gemini 3.0 Preview) com fallback automático...")
    try:
        # Simula que GEMINI_API_KEY está ausente, mas OPENAI_API_KEY está presente.
        # Em um teste real, você ajustaria as variáveis de ambiente ou passaria runtime_keys.
        
        # Mocking os.getenv para simular chave ausente para Gemini
        original_gemini_key = os.environ.pop("GEMINI_API_KEY", None)
        # Preserva outras chaves que podem estar setadas para o teste de fallback
        original_openai_key = os.getenv("OPENAI_API_KEY")
        original_deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        
        # Chaves fornecidas runtime para o teste (simulando a entrada do usuário)
        simulated_runtime_keys = {}
        if not os.getenv("OPENAI_API_KEY") and original_openai_key: # Se OpenAI não está em .env, mas foi lida antes
             simulated_runtime_keys["OPENAI_API_KEY"] = original_openai_key
        elif not os.getenv("OPENAI_API_KEY") and not original_openai_key: # Se não está em .env e não foi lida antes
             print("NOTA: OpenAI API Key não encontrada no .env. Teste de fallback para OpenAI pode falhar se não for fornecida.")
             # simulated_runtime_keys["OPENAI_API_KEY"] = "sk-test-openai-key" # Exemplo de chave runtime

        selected_model_display_for_test = "Gemini 3.0 Preview"
        orchestrator_test = PhysicsOrchestrator(
            selected_model_display_name=selected_model_display_for_test,
            runtime_keys=simulated_runtime_keys
        )
        test_prompt = "Explique a conservação de energia."
        
        result = orchestrator_test.run(test_prompt, selected_model_display_name=selected_model_display_for_test, runtime_keys=simulated_runtime_keys)
        
        print(f"
--- RESULTADO DO TESTE ---")
        print(f"Modelo utilizado: {result.used_model_display_name}")
        print(f"Fallback ocorreu: {result.fallback_occurred}")
        print(f"Resposta Socrática: {result.pergunta_socratica[:150]}...")
        
    except Exception as e:
        print(f"Erro durante o teste do orchestrator: {e}")
    finally:
        # Restaurar chaves originais no ambiente, se foram removidas/modificadas
        if original_gemini_key: os.environ["GEMINI_API_KEY"] = original_gemini_key
        if original_openai_key: os.environ["OPENAI_API_KEY"] = original_openai_key
        if original_deepseek_key: os.environ["DEEPSEEK_API_KEY"] = original_deepseek_key # Se também foi manipulada


    print("
--- TESTE CORE FINALIZADO ---")
