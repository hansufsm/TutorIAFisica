import os
import google.generativeai as genai
import time
import json
from typing import List, Dict, Any
from dotenv import load_dotenv

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
        # Campos de Avaliação
        self.quiz_question = ""
        self.quiz_correct_answer = ""

    def check_ufsm_syllabus(self):
        try:
            with open('../data/ufsm_syllabus.json', 'r', encoding='utf-8') as f:
                syllabus = json.load(f)
            for disciplina in syllabus['disciplinas']:
                for tema in disciplina['temas']:
                    for conceito in self.concepts:
                        if tema.lower() in conceito.lower() or conceito.lower() in tema.lower():
                            self.ufsm_alignment = disciplina
                            return
        except Exception as e:
            print(f"Erro ao consultar ementário UFSM: {e}")

class TutorIAAgent:
    def __init__(self, name: str, system_instruction: str):
        self.name = name
        self.system_instruction = system_instruction

    def ask_gemini(self, prompt: str, teacher_notes: str = "") -> str:
        if not model:
            return "ERRO: API Key não configurada."
        try:
            context_prefix = f"CONTEXTO DO PROFESSOR: {teacher_notes}\n\n" if teacher_notes else ""
            full_prompt = f"{self.system_instruction}\n\n{context_prefix}Entrada: {prompt}"
            response = model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"Erro na API: {str(e)}"

class SocraticInterpreter(TutorIAAgent):
    def process(self, state: PhysicsState) -> PhysicsState:
        instruction = "Você é o 'Intérprete Socrático'. Identifique os conceitos principais (separados por vírgula) e crie uma pergunta reflexiva."
        self.system_instruction = instruction
        response = self.ask_gemini(state.raw_input, state.teacher_notes)
        state.pergunta_socratica = response
        if "," in response:
            state.concepts = [c.strip() for c in response.split("\n")[0].split(",")]
        else:
            state.concepts = ["Física"]
        state.check_ufsm_syllabus()
        return state

class DimensionalSolver(TutorIAAgent):
    def process(self, state: PhysicsState) -> PhysicsState:
        instruction = "Você é o 'Solucionador Matemático'. Resolva com LaTeX e rigor dimensional."
        self.system_instruction = instruction
        state.solution_steps = self.ask_gemini(state.raw_input, state.teacher_notes)
        return state

class InteractiveVisualizer(TutorIAAgent):
    def process(self, state: PhysicsState) -> PhysicsState:
        instruction = "Você é o 'Visualizador Científico'. Gere APENAS código Python (matplotlib) funcional."
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
        instruction = f"Você é o 'Curador de Contexto'. Forneça aplicações reais e um mapa mental em Markdown. {ufsm_info}"
        self.system_instruction = instruction
        state.mapa_mental_markdown = self.ask_gemini(state.raw_input, state.teacher_notes)
        return state

class Evaluator(TutorIAAgent):
    """Novo Agente: Cria e avalia desafios para o aluno."""
    def process(self, state: PhysicsState) -> PhysicsState:
        print(f"[*] {self.name}: Gerando desafio formativo...")
        instruction = (
            "Você é o 'Avaliador Pedagógico'. Com base no problema de física discutido, "
            "crie um pequeno DESAFIO (uma pergunta de múltipla escolha ou discursiva curta) "
            "para testar se o aluno entendeu a lógica. Não dê a resposta agora."
        )
        self.system_instruction = instruction
        state.quiz_question = self.ask_gemini(state.raw_input, state.teacher_notes)
        return state

    def evaluate_answer(self, question: str, student_answer: str) -> str:
        """Avalia a resposta do aluno de forma socrática."""
        instruction = (
            "Você é o 'Avaliador Pedagógico'. O aluno respondeu ao seu desafio. "
            "Se estiver certo, parabenize e aprofunde. Se estiver errado, não dê a resposta, "
            "dê uma pista socrática para ele tentar novamente."
        )
        self.system_instruction = instruction
        return self.ask_gemini(f"Desafio: {question}\nResposta do Aluno: {student_answer}")

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
        time.sleep(3)
        state = self.solver.process(state)
        time.sleep(3)
        state = self.visualizer.process(state)
        time.sleep(3)
        state = self.contextualizer.process(state)
        time.sleep(3)
        state = self.evaluator.process(state)
        return state
