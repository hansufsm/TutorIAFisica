import os
import google.generativeai as genai
import time
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
    # Usando o modelo flash estável com limites mais amplos
    model = genai.GenerativeModel('gemini-flash-latest')
else:
    model = None

class PhysicsState:
    """Maintains the rich state of the conversation and physical context."""
    def __init__(self, raw_input: str):
        self.raw_input = raw_input
        self.concepts = []
        self.solution_steps = ""
        self.pergunta_socratica = ""
        self.code_snippet = ""
        self.is_valid = True
        self.links_universidades = []
        self.video_sugerido = ""
        self.exercicios_propostos = []
        self.mapa_mental_markdown = ""
        self.aplicacoes_reais = []

class TutorIAAgent:
    """Base class for all system agents."""
    def __init__(self, name: str, system_instruction: str):
        self.name = name
        self.system_instruction = system_instruction

    def ask_gemini(self, prompt: str) -> str:
        if not model:
            return "ERRO: Gemini API Key não configurada no arquivo .env."
        try:
            full_prompt = f"{self.system_instruction}\n\nEntrada do Aluno: {prompt}"
            response = model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"Erro na chamada da API: {str(e)}"

class SocraticInterpreter(TutorIAAgent):
    """Analyzes the problem and generates socratic questions."""
    def process(self, state: PhysicsState) -> PhysicsState:
        print(f"[*] {self.name}: Analisando enunciado...")
        instruction = (
            "Você é o 'Intérprete Socrático'. Sua tarefa é analisar o enunciado de física, "
            "identificar os conceitos principais e criar uma pergunta reflexiva que ajude o aluno "
            "a pensar na base teórica antes de ver a conta. Retorne primeiro os conceitos "
            "separados por vírgula e depois a pergunta socrática."
        )
        self.system_instruction = instruction
        response = self.ask_gemini(state.raw_input)
        
        # Simple parsing for the UI
        state.pergunta_socratica = response
        # Extract concepts (heuristic)
        if "," in response:
            state.concepts = response.split("\n")[0].split(",")[:3]
        else:
            state.concepts = ["Física Geral"]
        return state

class DimensionalSolver(TutorIAAgent):
    """Solves the problem with mathematical rigor and LaTeX."""
    def process(self, state: PhysicsState) -> PhysicsState:
        print(f"[*] {self.name}: Resolvendo...")
        instruction = (
            "Você é o 'Solucionador Matemático'. Resolva o problema de física fornecido "
            "passo a passo. Use LaTeX para todas as fórmulas. Verifique a consistência "
            "das unidades no SI. Seja rigoroso e didático."
        )
        self.system_instruction = instruction
        state.solution_steps = self.ask_gemini(state.raw_input)
        return state

class InteractiveVisualizer(TutorIAAgent):
    """Generates Python code for visualization."""
    def process(self, state: PhysicsState) -> PhysicsState:
        print(f"[*] {self.name}: Gerando visualização...")
        instruction = (
            "Você é o 'Visualizador Científico'. Gere APENAS o código Python usando Matplotlib "
            "ou Plotly para criar um gráfico ou diagrama que ilustre o problema. "
            "Não forneça explicações em texto, apenas o bloco de código funcional."
        )
        self.system_instruction = instruction
        code = self.ask_gemini(state.raw_input)
        # Clean markdown code blocks if present
        state.code_snippet = code.replace("```python", "").replace("```", "").strip()
        return state

class Contextualizer(TutorIAAgent):
    """Provides real-world context and academic curation."""
    def process(self, state: PhysicsState) -> PhysicsState:
        print(f"[*] {self.name}: Contextualizando...")
        instruction = (
            "Você é o 'Curador de Contexto'. Para o problema fornecido, apresente: "
            "1. Três aplicações reais (ex: engenharia, medicina). "
            "2. Três links de domínios .edu.br ou .gov.br sobre o tema. "
            "3. Um mapa mental estruturado em Markdown. "
            "Nunca use blogs ou fontes não confiáveis."
        )
        self.system_instruction = instruction
        state.mapa_mental_markdown = self.ask_gemini(state.raw_input)
        return state

class PhysicsOrchestrator:
    """Coordinates the agent flow with state management."""
    def __init__(self):
        self.interpreter = SocraticInterpreter("Intérprete", "")
        self.solver = DimensionalSolver("Matemático", "")
        self.visualizer = InteractiveVisualizer("Visualizador", "")
        self.contextualizer = Contextualizer("Curador", "")

    def run(self, input_data: str):
        state = PhysicsState(input_data)
        state = self.interpreter.process(state)
        time.sleep(3) # Delay para evitar estouro de quota (429)
        state = self.solver.process(state)
        time.sleep(3)
        state = self.visualizer.process(state)
        time.sleep(3)
        state = self.contextualizer.process(state)
        return state

if __name__ == "__main__":
    tutor = PhysicsOrchestrator()
    print("--- TESTE COM GEMINI API ---")
    # Agora o teste será dinâmico!
    res = tutor.run("Qual o período de um pêndulo de 2 metros na Terra?")
    print(f"\nResposta Socrática:\n{res.pergunta_socratica}")
