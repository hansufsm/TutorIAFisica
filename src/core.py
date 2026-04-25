import os
import google.generativeai as genai
import time
import json
from typing import List, Dict, Any
from src.config import Config
from src.utils.pcloud_manager import PCloudManager

# Inicialização segura
Config.validate()
genai.configure(api_key=Config.GEMINI_API_KEY)
model = genai.GenerativeModel(Config.MODEL_NAME)

class PhysicsState:
    """Objeto de Estado do Problema (Design Pattern: State)."""
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
        # Busca no pCloud via Utility
        cloud_text = PCloudManager.fetch_notes(self.pcloud_url)
        if cloud_text:
            self.teacher_notes = (self.teacher_notes + "\n\n" + cloud_text).strip()
            self.pcloud_notes_found = True
        
        # Alinhamento UFSM
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

    def ask(self, prompt: str, context: str = "", image: Any = None) -> str:
        full_prompt = f"{self.instruction}\n\nCONTEXTO: {context}\n\nENTRADA: {prompt}"
        try:
            res = model.generate_content([full_prompt, image] if image else full_prompt)
            return res.text
        except Exception as e:
            return f"Erro Agente {self.name}: {str(e)}"

class PhysicsOrchestrator:
    def __init__(self):
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
        
        # Fluxo de Execução com Delay de Compliance
        state.pergunta_socratica = self.agents["interpreter"].ask(input_data, state.teacher_notes, image)
        # Extração simples de conceitos para o alinhamento
        state.concepts = state.pergunta_socratica.split("\n")[0].split(",")[:3]
        state._check_ufsm_syllabus()
        
        time.sleep(Config.DELAY_BETWEEN_AGENTS)
        state.solution_steps = self.agents["solver"].ask(input_data, state.teacher_notes, image)
        
        time.sleep(Config.DELAY_BETWEEN_AGENTS)
        state.code_snippet = self.agents["visualizer"].ask(input_data, state.teacher_notes).replace("```python", "").replace("```", "")
        
        time.sleep(Config.DELAY_BETWEEN_AGENTS)
        state.mapa_mental_markdown = self.agents["curator"].ask(input_data, f"{state.teacher_notes} {state.ufsm_alignment}")
        
        time.sleep(Config.DELAY_BETWEEN_AGENTS)
        state.quiz_question = self.agents["evaluator"].ask(input_data, state.teacher_notes)
        
        return state
