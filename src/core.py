import os
import google.generativeai as genai
import time
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
from pypdf import PdfReader

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-flash-latest')
else:
    model = None

class PhysicsState:
    """Maintains the rich state of the conversation and physical context."""
    def __init__(self, raw_input: str, teacher_notes: str = ""):
        self.raw_input = raw_input
        self.teacher_notes = teacher_notes
        self.concepts = []
        self.solution_steps = ""
        self.pergunta_socratica = ""
        self.code_snippet = ""
        self.is_valid = True
        self.mapa_mental_markdown = ""
        self.ufsm_alignment = None 
        self.pcloud_notes_found = False
        # Campos de Avaliação
        self.quiz_question = ""

    def check_ufsm_syllabus(self):
        try:
            with open('../data/ufsm_syllabus.json', 'r', encoding='utf-8') as f:
                syllabus = json.load(f)
            for disciplina in syllabus['disciplinas']:
                for tema in disciplina['temas']:
                    for conceito in self.concepts:
                        if tema.lower() in conceito.lower() or conceito.lower() in tema.lower():
                            self.ufsm_alignment = disciplina
                            # Tenta buscar notas no pCloud se houver match institucional
                            self.fetch_pcloud_notes()
                            return
        except Exception as e:
            print(f"Erro ao consultar ementário: {e}")

    def fetch_pcloud_notes(self):
        """Busca arquivos PDF na pasta correspondente do pCloud Drive."""
        if not self.ufsm_alignment:
            return
        
        code = self.ufsm_alignment['codigo']
        pcloud_path = os.path.expanduser(f"~/pCloudDrive/TutorIA_Notes/{code}")
        
        if os.path.exists(pcloud_path):
            files = [f for f in os.listdir(pcloud_path) if f.endswith('.pdf')]
            if files:
                print(f"[*] Notas encontradas no pCloud para {code}: {files}")
                self.pcloud_notes_found = True
                content = ""
                for file in files:
                    try:
                        reader = PdfReader(os.path.join(pcloud_path, file))
                        for page in reader.pages:
                            content += page.extract_text() + "\n"
                    except Exception as e:
                        print(f"Erro ao ler PDF do pCloud: {e}")
                
                # Concatena com notas manuais se existirem
                self.teacher_notes = (self.teacher_notes + "\n\n" + content).strip()

class TutorIAAgent:
    def __init__(self, name: str, system_instruction: str):
        self.name = name
        self.system_instruction = system_instruction

    def ask_gemini(self, prompt: str, teacher_notes: str = "") -> str:
        if not model:
            return "ERRO: API Key não configurada."
        try:
            context_prefix = f"CONTEXTO DO PROFESSOR (PRIORIDADE): {teacher_notes}\n\n" if teacher_notes else ""
            full_prompt = f"{self.system_instruction}\n\n{context_prefix}Entrada: {prompt}"
            response = model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"Erro na API: {str(e)}"

class SocraticInterpreter(TutorIAAgent):
    def process(self, state: PhysicsState) -> PhysicsState:
        instruction = "Você é o 'Intérprete Socrático'. Identifique conceitos e crie perguntas reflexivas."
        self.system_instruction = instruction
        response = self.ask_gemini(state.raw_input, state.teacher_notes)
        state.pergunta_socratica = response
        if "," in response:
            state.concepts = [c.strip() for c in response.split("\n")[0].split(",")]
        else:
            state.concepts = ["Física"]
        # Aciona o check institucional e a busca no pCloud
        state.check_ufsm_syllabus()
        return state

class DimensionalSolver(TutorIAAgent):
    def process(self, state: PhysicsState) -> PhysicsState:
        instruction = "Você é o 'Solucionador Matemático'. Resolva com LaTeX."
        self.system_instruction = instruction
        state.solution_steps = self.ask_gemini(state.raw_input, state.teacher_notes)
        return state

class InteractiveVisualizer(TutorIAAgent):
    def process(self, state: PhysicsState) -> PhysicsState:
        instruction = "Você é o 'Visualizador Científico'. Gere apenas código Python."
        self.system_instruction = instruction
        code = self.ask_gemini(state.raw_input, state.teacher_notes)
        state.code_snippet = code.replace("```python", "").replace("```", "").strip()
        return state

class Contextualizer(TutorIAAgent):
    def process(self, state: PhysicsState) -> PhysicsState:
        ufsm_info = ""
        if state.ufsm_alignment:
            d = state.ufsm_alignment
            ufsm_info = f"\nALINHAMENTO UFSM: Disciplina {d['codigo']}. Bibliografia: {', '.join(d['bibliografia_basica'])}."
        instruction = f"Você é o 'Curador de Contexto'. Forneça aplicações e mapa mental. {ufsm_info}"
        self.system_instruction = instruction
        state.mapa_mental_markdown = self.ask_gemini(state.raw_input, state.teacher_notes)
        return state

class Evaluator(TutorIAAgent):
    def process(self, state: PhysicsState) -> PhysicsState:
        instruction = "Você é o 'Avaliador Pedagógico'. Crie um desafio curto."
        self.system_instruction = instruction
        state.quiz_question = self.ask_gemini(state.raw_input, state.teacher_notes)
        return state

    def evaluate_answer(self, question: str, student_answer: str) -> str:
        instruction = "Você é o 'Avaliador Pedagógico'. Dê feedback socrático."
        self.system_instruction = instruction
        return self.ask_gemini(f"Desafio: {question}\nResposta: {student_answer}")

class PhysicsOrchestrator:
    def __init__(self):
        self.interpreter = SocraticInterpreter("Intérprete", "")
        self.solver = DimensionalSolver("Matemático", "")
        self.visualizer = InteractiveVisualizer("Visualizador", "")
        self.contextualizer = Contextualizer("Curador", "")
        self.evaluator = Evaluator("Avaliador", "")

    def run(self, input_data: str, teacher_notes: str = ""):
        state = PhysicsState(input_data, teacher_notes)
        state = self.interpreter.process(state)
        time.sleep(2)
        state = self.solver.process(state)
        time.sleep(2)
        state = self.visualizer.process(state)
        time.sleep(2)
        state = self.contextualizer.process(state)
        time.sleep(2)
        state = self.evaluator.process(state)
        return state
