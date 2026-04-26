import os
import time
import json
import litellm
from typing import List, Dict, Any
from src.config import Config
from src.utils.pcloud_manager import PCloudManager

# Configuração de chaves para LiteLLM
os.environ["GEMINI_API_KEY"] = Config.GEMINI_API_KEY or ""
os.environ["DEEPSEEK_API_KEY"] = Config.DEEPSEEK_API_KEY or ""

class PhysicsState:
    def __init__(self, raw_input: str, teacher_notes: str = "", pcloud_url: str = ""):
        self.raw_input = raw_input
        self.teacher_notes = teacher_notes
        self.pcloud_url = pcloud_url
        self.concepts = []
        self.solution_steps = ""
        self.pergunta_socratica = ""
        self.code_snippet = ""
        self.mapa_mental_markdown = ""
        self.ufsm_alignment = None 
        self.pcloud_notes_found = False
        self.quiz_question = ""

    def sync_external_data(self):
        cloud_text = PCloudManager.fetch_notes(self.pcloud_url)
        if cloud_text:
            self.teacher_notes = (self.teacher_notes + "\n\n" + cloud_text).strip()
            self.pcloud_notes_found = True
        self._check_ufsm_syllabus()

    def _check_ufsm_syllabus(self):
        if not os.path.exists(Config.SYLLABUS_PATH): return
        with open(Config.SYLLABUS_PATH, 'r', encoding='utf-8') as f:
            syllabus = json.load(f)
            for d in syllabus['disciplinas']:
                for t in d['temas']:
                    if any(t.lower() in c.lower() for c in self.concepts):
                        self.ufsm_alignment = d
                        return

class TutorIAAgent:
    def __init__(self, name: str, instruction: str):
        self.name = name
        self.instruction = instruction

    def ask(self, prompt: str, context: str = "", image: Any = None, model: str = None) -> str:
        target_model = model or Config.ACTIVE_MODEL
        
        # Preparação das mensagens (Formato OpenAI/LiteLLM)
        messages = [
            {"role": "system", "content": f"{self.instruction}\nCONTEXTO: {context}"},
            {"role": "user", "content": prompt}
        ]

        # Tratamento de Imagem para modelos que suportam (Gemini)
        if image and "gemini" in target_model:
            # LiteLLM lida com imagens passando a PIL Image ou URL
            messages[1]["content"] = [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": image}
            ]
        elif image and "deepseek" in target_model:
            return f"Erro Agente {self.name}: O modelo DeepSeek selecionado não suporta análise de imagens (Visão). Por favor, use o Gemini para esta tarefa."

        try:
            res = litellm.completion(model=target_model, messages=messages)
            return res.choices[0].message.content
        except Exception as e:
            return f"Erro Agente {self.name} ({target_model}): {str(e)}"

class PhysicsOrchestrator:
    def __init__(self, model_override: str = None):
        self.active_model = model_override or Config.ACTIVE_MODEL
        self.agents = {
            "interpreter": TutorIAAgent("Intérprete", "Você é um professor socrático. Identifique conceitos e crie perguntas reflexivas."),
            "solver": TutorIAAgent("Matemático", "Resolva com LaTeX e rigor dimensional."),
            "visualizer": TutorIAAgent("Visualizador", "Gere apenas código Python (matplotlib) funcional."),
            "curator": TutorIAAgent("Curador", "Forneça aplicações reais e mapa mental."),
            "evaluator": TutorIAAgent("Avaliador", "Crie desafios pedagógicos curtos.")
        }

    def run(self, input_data: str, notes: str = "", pcloud_url: str = "", image: Any = None):
        state = PhysicsState(input_data, notes, pcloud_url)
        state.sync_external_data()
        
        # Execução com o modelo ativo
        state.pergunta_socratica = self.agents["interpreter"].ask(input_data, state.teacher_notes, image, model=self.active_model)
        state.concepts = state.pergunta_socratica.split("\n")[0].split(",")[:3]
        state._check_ufsm_syllabus()
        
        time.sleep(Config.DELAY_BETWEEN_AGENTS)
        state.solution_steps = self.agents["solver"].ask(input_data, state.teacher_notes, image, model=self.active_model)
        
        time.sleep(Config.DELAY_BETWEEN_AGENTS)
        state.code_snippet = self.agents["visualizer"].ask(input_data, state.teacher_notes, model=self.active_model).replace("```python", "").replace("```", "")
        
        time.sleep(Config.DELAY_BETWEEN_AGENTS)
        state.mapa_mental_markdown = self.agents["curator"].ask(input_data, f"{state.teacher_notes} {state.ufsm_alignment}", model=self.active_model)
        
        time.sleep(Config.DELAY_BETWEEN_AGENTS)
        state.quiz_question = self.agents["evaluator"].ask(input_data, state.teacher_notes, model=self.active_model)
        
        return state
