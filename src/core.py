import os
import json
import time
import base64
import io
import requests as http_requests
import litellm
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from config import Config
from utils.pcloud_manager import PCloudManager
from utils.web_searcher import WebSearcher

load_dotenv()

class PhysicsState:
    """Objeto de Estado do Problema (Design Pattern: State)."""
    def __init__(self, raw_input: str, teacher_notes: str = "", pcloud_url: str = "", image: Any = None):
        self.raw_input = raw_input
        # Nível 1: Materiais do Professor
        self.professor_notes_text = teacher_notes
        self.pcloud_repo_text = ""
        # Nível 2: Documentos Adotados
        self.adopted_docs_text = ""
        # Nível 3: UFSM
        self.ufsm_context = ""
        # Nível 4: Portais .edu.br
        self.web_edu_br_text = ""
        # Nível 5: Referências Internacionais
        self.intl_refs_text = ""
        # Fora da hierarquia: Material do aluno (pCloud sessão)
        self.pcloud_url = pcloud_url
        self.pcloud_session_text = ""
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

        # Informações de fallback e modelo utilizado
        self.used_model_display_name: Optional[str] = None
        self.fallback_occurred: bool = False

    @property
    def teacher_notes(self) -> str:
        """Compatibilidade: retorna a concatenação de todas as notas."""
        parts = [self.professor_notes_text, self.pcloud_session_text, self.pcloud_repo_text]
        return "\n\n".join([p for p in parts if p.strip()])

    def sync_external_data(self, on_progress=None, repo_url: str = "", adopted_url: str = ""):
        """Sincroniza dados de fontes externas (pCloud, notas do professor)."""
        if on_progress: on_progress("📚 Verificando materiais...")
        # Sessão: Material do aluno
        if self.pcloud_url:
            cloud_text = PCloudManager.fetch_notes(self.pcloud_url)
            if cloud_text:
                self.pcloud_session_text = cloud_text
                self.pcloud_notes_found = True
                if on_progress: on_progress(f"☁️ Material do aluno carregado ({len(cloud_text)} caracteres)")
            elif on_progress:
                on_progress("ℹ️ Material do aluno: nenhum PDF encontrado")
        # Repositório: Nível 1 do professor
        if repo_url:
            repo_text = PCloudManager.fetch_notes(repo_url)
            if repo_text:
                self.pcloud_repo_text = repo_text
                if on_progress: on_progress(f"📦 Repositório do professor carregado ({len(repo_text)} caracteres)")
        # Documentos Adotados: Nível 2
        if adopted_url:
            adopted_text = PCloudManager.fetch_notes(adopted_url)
            if adopted_text:
                self.adopted_docs_text = adopted_text
                if on_progress: on_progress(f"📗 Documentos adotados carregados ({len(adopted_text)} caracteres)")

    def _check_ufsm_syllabus(self):
        """Busca match no ementário da UFSM baseado nos conceitos identificados."""
        if not os.path.exists(Config.SYLLABUS_PATH): return
        try:
            with open(Config.SYLLABUS_PATH, 'r', encoding='utf-8') as f:
                syllabus = json.load(f)
            for d in syllabus['disciplinas']:
                for t in d['temas']:
                    for conceito in self.concepts:
                        if conceito.lower() in t.lower():
                            self.ufsm_alignment = d
                            self.ufsm_context = (
                                f"Disciplina: {d['nome']} ({d['codigo']})\n"
                                f"Temas do ementário: {', '.join(d['temas'])}\n"
                                f"Bibliografia básica: {'; '.join(d['bibliografia_basica'][:3]) if d.get('bibliografia_basica') else 'N/A'}"
                            )
                            return
        except Exception as e:
            print(f"Erro ao consultar ementário UFSM: {e}")

    def build_context(self) -> str:
        """Monta contexto priorizado em 5 níveis com truncação por fonte."""
        MAX_CHARS = {
            1: 4000,   # Professor (notes + repo combined)
            2: 2000,   # Documentos adotados
            3: 600,    # UFSM
            4: 1500,   # .edu.br
            5: 1200,   # Internacional
            "aluno": 2000,   # Material do aluno
        }

        parts = []

        # Nível 1 — Materiais do Professor (notas + repositório juntos)
        prof_combined = []
        if self.professor_notes_text.strip():
            prof_combined.append(self.professor_notes_text.strip())
        if self.pcloud_repo_text.strip():
            prof_combined.append(self.pcloud_repo_text.strip())
        if prof_combined:
            prof_text = "\n\n".join(prof_combined)[:MAX_CHARS[1]]
            parts.append(f"### [NOTAS DO PROFESSOR]\n{prof_text}")

        # Nível 2 — Documentos Adotados
        if self.adopted_docs_text.strip():
            adopted_text = self.adopted_docs_text.strip()[:MAX_CHARS[2]]
            parts.append(f"### [DOCUMENTOS ADOTADOS]\n{adopted_text}")

        # Nível 3 — UFSM Ementário
        if self.ufsm_context:
            ufsm_text = self.ufsm_context[:MAX_CHARS[3]]
            parts.append(f"### [EMENTA UFSM]\n{ufsm_text}")

        # Nível 4 — Portais Acadêmicos .edu.br
        if self.web_edu_br_text.strip():
            edu_br_text = self.web_edu_br_text.strip()[:MAX_CHARS[4]]
            parts.append(f"### [PORTAIS ACADÊMICOS .edu.br]\n{edu_br_text}")

        # Nível 5 — Referências Internacionais
        if self.intl_refs_text.strip():
            intl_text = self.intl_refs_text.strip()[:MAX_CHARS[5]]
            parts.append(f"### [REFERÊNCIAS INTERNACIONAIS]\n{intl_text}")

        # Extra — Material do Aluno (pCloud sessão, fora da hierarquia)
        if self.pcloud_session_text.strip():
            aluno_text = self.pcloud_session_text.strip()[:MAX_CHARS["aluno"]]
            parts.append(f"### [MATERIAL DO ALUNO]\n{aluno_text}")

        return "\n\n".join(parts)

    def sync_web_sources(self, on_progress=None) -> bool:
        """Busca fontes web com base nos conceitos identificados pelo Intérprete."""
        if not self.concepts:
            return False

        topic = " ".join(self.concepts[:3])  # Usar primeiros 3 conceitos

        if on_progress:
            on_progress("🌐 Buscando em portais acadêmicos .edu.br...")
        self.web_edu_br_text = WebSearcher.search_edu_br(topic, max_results=3)

        if on_progress:
            on_progress("🔬 Consultando arXiv e Semantic Scholar...")
        arxiv_results = WebSearcher.search_arxiv(topic, max_results=3)
        scholar_results = WebSearcher.search_semantic_scholar(topic, max_results=3)

        # Combinar resultados das duas APIs internacionais
        intl_results = []
        if arxiv_results:
            intl_results.append(f"**arXiv:**\n{arxiv_results}")
        if scholar_results:
            intl_results.append(f"**Semantic Scholar:**\n{scholar_results}")

        if intl_results:
            self.intl_refs_text = "\n\n".join(intl_results)
            if on_progress:
                on_progress(f"✅ {len(intl_results)} fontes internacionais encontradas")
            return True

        return False

class TutorIAAgent:
    """Classe base para todos os agentes de IA."""
    def __init__(self, name: str, system_instruction: str):
        self.name = name
        self.system_instruction = system_instruction

    def _ask_manus(self, prompt: str, context: str = "", api_key: str = None) -> str:
        """Bypass route para o Manus: envia task assíncrona e faz polling até completar."""
        _MANUS_BASE = "https://api.manus.im"
        _MANUS_HEADERS = {"API_KEY": api_key or os.getenv("MANUS_API_KEY", "")}
        _POLL_INTERVAL = 5   # segundos entre polls
        _MAX_POLLS = 60      # timeout de 5 min

        full_prompt = f"{self.system_instruction}\n\n{context}\n\n{prompt}".strip() if context.strip() else f"{self.system_instruction}\n\n{prompt}".strip()

        resp = litellm.responses(
            model="manus/manus-1.6",
            api_key=api_key or os.getenv("MANUS_API_KEY", ""),
            input=full_prompt,
        )
        task_id = resp.metadata.get("task_id", "")
        if not task_id:
            raise RuntimeError("Manus: task_id não encontrado na resposta inicial")

        for _ in range(_MAX_POLLS):
            time.sleep(_POLL_INTERVAL)
            r = http_requests.get(
                f"{_MANUS_BASE}/v1/responses/{task_id}",
                headers=_MANUS_HEADERS,
                timeout=15,
            )
            if r.status_code != 200:
                raise RuntimeError(f"Manus polling error HTTP {r.status_code}: {r.text[:200]}")
            data = r.json()
            status = data.get("status")
            if status == "completed":
                # Extrai o texto do último output de assistente
                for item in reversed(data.get("output", [])):
                    if item.get("role") == "assistant":
                        for c in reversed(item.get("content", [])):
                            if c.get("type") == "output_text" and c.get("text"):
                                return c["text"]
                raise RuntimeError("Manus: resposta completed mas sem texto de assistente")
            if status == "failed":
                raise RuntimeError(f"Manus: task falhou — {data.get('error', 'sem detalhes')}")

        raise RuntimeError("Manus: timeout após 5 minutos de polling")

    def ask(self, prompt: str, context: str = "", image: Any = None, model_id: str = None, api_key: str = None) -> str:
        """Realiza a chamada para o LLM usando LiteLLM com o modelo especificado."""
        if not model_id:
            model_id = Config.get_model_id(Config.DEFAULT_MODEL_DISPLAY_NAME)
            print(f"Aviso: Nenhum model_id especificado, usando padrão {model_id}")

        if model_id and model_id.startswith("manus/"):
            return self._ask_manus(prompt, context=context, api_key=api_key)

        context_block = f"\n\n### MATERIAL DE REFERÊNCIA (use prioritariamente):\n{context}" if context.strip() else ""
        messages = [
            {"role": "system", "content": f"{self.system_instruction}{context_block}"},
            {"role": "user", "content": prompt}
        ]

        if image and Config.is_model_multimodal(Config.get_model_display_name_by_id(model_id)):
            buf = io.BytesIO()
            image.save(buf, format="JPEG")
            b64 = base64.b64encode(buf.getvalue()).decode()
            messages[1]["content"] = [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
            ]
        elif image and not Config.is_model_multimodal(Config.get_model_display_name_by_id(model_id)):
            print(f"[!] Aviso: Imagem fornecida, mas modelo '{model_id}' não é multimodal.")

        try:
            response = litellm.completion(model=model_id, messages=messages, api_key=api_key)
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
    def __init__(self, selected_model_display_name: str = None, runtime_keys: Dict[str, str] = None):
        self.selected_model_display_name = selected_model_display_name or "Gemini 3.0 Preview"
        self.runtime_keys = runtime_keys or {}
        self.model_id = Config.get_model_id(self.selected_model_display_name)
        self.is_multimodal = Config.is_model_multimodal(self.selected_model_display_name)
        
        self.used_model_display_name: Optional[str] = None
        self.fallback_occurred: bool = False

        source_attribution = "Ao usar informações do MATERIAL DE REFERÊNCIA, cite a fonte: **[Notas do Professor]**, **[Documentos Adotados]**, **[Ementa UFSM]**, **[Portais .edu.br]**, **[Referências Internacionais]**, **[Material do Aluno]** ou **[Modelo de IA]**."
        self.agents = {
            "interpreter": TutorIAAgent("Intérprete", f"Você é um professor socrático. Identifique conceitos e crie perguntas reflexivas. {source_attribution}"),
            "solver": TutorIAAgent("Matemático", f"Resolva com LaTeX e rigor. {source_attribution}"),
            "visualizer": TutorIAAgent("Visualizador", f"Gere apenas código Python (matplotlib/plotly) funcional. {source_attribution}"),
            "curator": TutorIAAgent("Curador", f"Forneça aplicações reais, links acadêmicos e mapa mental. {source_attribution}"),
            "evaluator": TutorIAAgent("Avaliador", f"Crie desafios pedagógicos curtos e dê feedback socrático. {source_attribution}")
        }

    def _attempt_model_call(self, agent_name: str, prompt: str, context: str, image: Any = None) -> tuple[str, Optional[str], bool]:
        """Tenta chamar modelos na ordem de preferência, implementando fallback automático.
        Exceção: quando o modelo selecionado é Manus, executa bypass direto sem fallback.
        """
        # Bypass route: Manus é assíncrono e não entra no loop de fallback
        if self.selected_model_display_name == "Manus":
            api_key = os.getenv("MANUS_API_KEY", "")
            try:
                agent = self.agents[agent_name]
                result = agent._ask_manus(prompt, context=context, api_key=api_key)
                return result, "Manus", False
            except Exception as e:
                return f"Erro no Manus: {str(e)}", None, True

        models_to_try_display_names = Config.MODEL_PREFERENCE_ORDER
        last_error_message = "Nenhum modelo testado com sucesso."

        # Determina a ordem de modelos a tentar, priorizando o selecionado pelo usuário
        preferred_order = []
        if self.selected_model_display_name and self.selected_model_display_name in Config.AVAILABLE_MODELS:
            preferred_order.append(self.selected_model_display_name)

        for model_name in models_to_try_display_names:
            if model_name not in preferred_order and model_name != "Manus":
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

                api_key = self.runtime_keys.get(key_name) or os.getenv(key_name) if key_name else None

                response_text = agent.ask(prompt, context=context, image=image, model_id=current_model_id, api_key=api_key)

                if response_text and "ERRO" not in response_text and "Erro na API" not in response_text:
                    is_fallback = (model_display_name != self.selected_model_display_name)
                    return response_text, model_display_name, is_fallback
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

    def run(self, input_data: str, teacher_notes: str = "", pcloud_url: str = "", repo_url: str = "", adopted_url: str = "", enable_web_search: bool = True, image: Any = None, on_progress=None):
        """Executa o pipeline de agentes com fallback automático e busca web opcional."""

        state = PhysicsState(input_data, teacher_notes, pcloud_url, image)

        # Debug: Log material sources
        if on_progress:
            on_progress(f"📚 Fontes fornecidas:")
            if teacher_notes.strip():
                on_progress(f"  📄 Notas do professor: {len(teacher_notes)} caracteres")
            if repo_url:
                on_progress(f"  📦 Repositório do professor fornecido")
            if adopted_url:
                on_progress(f"  📗 Documentos adotados fornecidos")
            if pcloud_url:
                on_progress(f"  ☁️ Material do aluno fornecido")
            if enable_web_search:
                on_progress(f"  🌐 Busca web habilitada")

        state.sync_external_data(on_progress=on_progress, repo_url=repo_url, adopted_url=adopted_url)

        # --- Execução sequencial dos agentes com fallback ---

        # Intérprete
        if on_progress: on_progress("🧩 Intérprete: analisando o problema...")
        context = state.build_context() or ""
        response, model_name_used_int, fb_int = self._attempt_model_call("interpreter", input_data, context, image)
        state.pergunta_socratica = response
        if "," in response:
            state.concepts = [c.strip() for c in response.split("\n")[0].split(",")]
        else:
            state.concepts = ["Física Geral"]
        state._check_ufsm_syllabus()

        if fb_int: state.fallback_occurred = True
        state.used_model_display_name = model_name_used_int
        if on_progress: on_progress(f"✅ Intérprete concluído — modelo: {model_name_used_int or 'desconhecido'}")

        time.sleep(Config.DELAY_BETWEEN_AGENTS)

        # Busca web baseada nos conceitos identificados (opcional, pode ser lento)
        if enable_web_search:
            if on_progress: on_progress("🌐 Consultando fontes web (portais .edu.br, arXiv, Semantic Scholar)...")
            state.sync_web_sources(on_progress=on_progress)

        # Atualizar contexto após identificar disciplina UFSM e buscar web sources
        context = state.build_context() or ""
        if on_progress and context:
            on_progress(f"✅ Contexto montado: {len(context)} caracteres com {context.count('[') // 2} fontes")

        # Solucionador
        if on_progress: on_progress("📐 Solucionador: calculando...")
        response, model_name_solver, fb_solver = self._attempt_model_call("solver", input_data, context, image)
        state.solution_steps = response
        if fb_solver: state.fallback_occurred = True
        if model_name_solver: state.used_model_display_name = model_name_solver
        if on_progress: on_progress("✅ Solucionador concluído")

        time.sleep(Config.DELAY_BETWEEN_AGENTS)

        # Visualizador
        if on_progress: on_progress("🖼️ Visualizador: gerando código Python...")
        response, model_name_vis, fb_vis = self._attempt_model_call("visualizer", input_data, context, image)
        state.code_snippet = response.replace("```python", "").replace("```", "").strip()
        if fb_vis: state.fallback_occurred = True
        if model_name_vis: state.used_model_display_name = model_name_vis
        if on_progress: on_progress("✅ Visualizador concluído")

        time.sleep(Config.DELAY_BETWEEN_AGENTS)

        # Curador
        if on_progress: on_progress("📚 Curador: mapeando contexto UFSM...")
        response, model_name_curator, fb_curator = self._attempt_model_call("curator", input_data, context, image)
        state.mapa_mental_markdown = response
        if fb_curator: state.fallback_occurred = True
        if model_name_curator: state.used_model_display_name = model_name_curator
        if on_progress: on_progress("✅ Curador concluído")

        time.sleep(Config.DELAY_BETWEEN_AGENTS)

        # Avaliador
        if on_progress: on_progress("🎯 Avaliador: criando desafio...")
        response, model_name_eval, fb_eval = self._attempt_model_call("evaluator", input_data, context, image)
        state.quiz_question = response
        if fb_eval: state.fallback_occurred = True
        if model_name_eval: state.used_model_display_name = model_name_eval
        if on_progress: on_progress("✅ Avaliador concluído")

        return state

    def process(self, state: PhysicsState, model_id: str = None, api_key: str = None) -> PhysicsState:
        """
        Interface simplificada para backend FastAPI.
        Usa model_id e api_key passados diretamente.
        """
        if model_id:
            # Obter nome de exibição do model_id
            model_name = Config.get_model_display_name_by_id(model_id)
            self.selected_model_display_name = model_name or "Unknown"
            self.model_id = model_id

        if api_key:
            # Adicionar chave ao runtime_keys
            key_name = Config.get_provider_key_name(self.selected_model_display_name)
            if key_name:
                self.runtime_keys[key_name] = api_key

        # Usar o state fornecido ou criar novo
        if not isinstance(state, PhysicsState):
            state = PhysicsState(str(state))

        input_data = state.raw_input

        # Executar pipeline
        state.sync_external_data()

        # Intérprete
        context = state.build_context() or ""
        response, model_name_used, fb = self._attempt_model_call("interpreter", input_data, context, state.image_input)
        state.pergunta_socratica = response
        if "," in response:
            state.concepts = [c.strip() for c in response.split("\n")[0].split(",")]
        else:
            state.concepts = ["Física Geral"]
        state._check_ufsm_syllabus()
        if fb: state.fallback_occurred = True
        state.used_model_display_name = model_name_used

        time.sleep(Config.DELAY_BETWEEN_AGENTS)

        # Solucionador
        context = state.build_context() or ""
        response, model_name_used, fb = self._attempt_model_call("solver", input_data, context, state.image_input)
        state.solution_steps = response
        if fb: state.fallback_occurred = True
        if model_name_used: state.used_model_display_name = model_name_used

        time.sleep(Config.DELAY_BETWEEN_AGENTS)

        # Visualizador
        response, model_name_used, fb = self._attempt_model_call("visualizer", input_data, context, state.image_input)
        state.code_snippet = response.replace("```python", "").replace("```", "").strip()
        if fb: state.fallback_occurred = True
        if model_name_used: state.used_model_display_name = model_name_used

        time.sleep(Config.DELAY_BETWEEN_AGENTS)

        # Curador
        response, model_name_used, fb = self._attempt_model_call("curator", input_data, context, state.image_input)
        state.mapa_mental_markdown = response
        if fb: state.fallback_occurred = True
        if model_name_used: state.used_model_display_name = model_name_used

        time.sleep(Config.DELAY_BETWEEN_AGENTS)

        # Avaliador
        response, model_name_used, fb = self._attempt_model_call("evaluator", input_data, context, state.image_input)
        state.quiz_question = response
        if fb: state.fallback_occurred = True
        if model_name_used: state.used_model_display_name = model_name_used

        return state

    def process_streaming(self, state: PhysicsState, model_id: str = None, api_key: str = None):
        """
        Versão generator (streaming) para SSE.
        Faz yield (agent_name, content) após cada agente.
        """
        if model_id:
            model_name = Config.get_model_display_name_by_id(model_id)
            self.selected_model_display_name = model_name or "Unknown"
            self.model_id = model_id

        if api_key:
            key_name = Config.get_provider_key_name(self.selected_model_display_name)
            if key_name:
                self.runtime_keys[key_name] = api_key

        if not isinstance(state, PhysicsState):
            state = PhysicsState(str(state))

        input_data = state.raw_input
        state.sync_external_data()

        # Intérprete
        context = state.build_context() or ""
        response, model_name_used, fb = self._attempt_model_call("interpreter", input_data, context, state.image_input)
        state.pergunta_socratica = response
        if "," in response:
            state.concepts = [c.strip() for c in response.split("\n")[0].split(",")]
        else:
            state.concepts = ["Física Geral"]
        state._check_ufsm_syllabus()
        if fb: state.fallback_occurred = True
        state.used_model_display_name = model_name_used
        yield ("Intérprete", response)
        time.sleep(Config.DELAY_BETWEEN_AGENTS)

        # Solucionador
        context = state.build_context() or ""
        response, model_name_used, fb = self._attempt_model_call("solver", input_data, context, state.image_input)
        state.solution_steps = response
        if fb: state.fallback_occurred = True
        if model_name_used: state.used_model_display_name = model_name_used
        yield ("Solucionador", response)
        time.sleep(Config.DELAY_BETWEEN_AGENTS)

        # Visualizador
        response, model_name_used, fb = self._attempt_model_call("visualizer", input_data, context, state.image_input)
        state.code_snippet = response.replace("```python", "").replace("```", "").strip()
        if fb: state.fallback_occurred = True
        if model_name_used: state.used_model_display_name = model_name_used
        yield ("Visualizador", response)
        time.sleep(Config.DELAY_BETWEEN_AGENTS)

        # Curador
        response, model_name_used, fb = self._attempt_model_call("curator", input_data, context, state.image_input)
        state.mapa_mental_markdown = response
        if fb: state.fallback_occurred = True
        if model_name_used: state.used_model_display_name = model_name_used
        yield ("Curador", response)
        time.sleep(Config.DELAY_BETWEEN_AGENTS)

        # Avaliador
        response, model_name_used, fb = self._attempt_model_call("evaluator", input_data, context, state.image_input)
        state.quiz_question = response
        if fb: state.fallback_occurred = True
        if model_name_used: state.used_model_display_name = model_name_used
        yield ("Avaliador", response)

if __name__ == "__main__":
    # --- Teste Básico de Fallback ---
    print("--- TESTE CORE: Seleção de Modelo e Fallback ---")
    
    # Teste 1: Simular seleção manual de um modelo que pode ter chave ausente (ex: Gemini 3.0 Preview se GEMINI_API_KEY não estiver no .env)
    print("\nTentando modelo selecionado (Gemini 3.0 Preview) com fallback automático...")
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

        print(f"\n--- RESULTADO DO TESTE ---")
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

    print("\n--- TESTE CORE FINALIZADO ---")
