import os
from typing import List, Dict, Any

class PhysicsState:
    """Mantém o estado rico da conversa e do contexto físico."""
    def __init__(self, raw_input: str):
        self.raw_input = raw_input
        self.concepts = []
        self.variables = {}
        self.solution_steps = []
        self.code_snippet = ""
        self.is_valid = True
        # Novos campos de Contexto (Herança do FisicaIA original)
        self.links_universidades = []
        self.video_sugerido = ""
        self.exercicios_propostos = []
        self.mapa_mental_markdown = ""
        self.aplicacoes_reais = []

class Contextualizer(TutorIAAgent):
    """Resgata a essência do FisicaIA: Conectar com o mundo real e acadêmico."""
    def process(self, state: PhysicsState) -> PhysicsState:
        print(f"[*] {self.name}: Gerando curadoria acadêmica...")
        state.links_universidades = [
            "https://www.if.ufrgs.br/institucional/",
            "https://portal.ufsm.br/ementario/curso.html?curso=414",
            "https://www.ifsc.usp.br/"
        ]
        state.video_sugerido = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" # Exemplo
        state.exercicios_propostos = [
            {"nivel": "Médio", "enunciado": "Calcule a nova força se a distância dobrar."},
            {"nivel": "Desafio", "enunciado": "Determine o campo elétrico no ponto médio entre as cargas."}
        ]
        state.aplicacoes_reais = ["Desfibriladores cardíacos", "Impressoras a jato de tinta", "Pintura eletrostática"]
        state.mapa_mental_markdown = """
        # Eletrostática
        ## Lei de Coulomb
        ### Cargas
        ### Distância
        ## Campo Elétrico
        """
        return state

class PhysicsOrchestrator:
    """Coordena o fluxo de agentes com lógica de feedback."""
    def __init__(self):
        self.interpreter = SocraticInterpreter("Intérprete Socrático", "Analise e questione.")
        self.solver = DimensionalSolver("Solucionador Dimensional", "Calcule e valide.")
        self.visualizer = InteractiveVisualizer("Visualizador Dinâmico", "Codifique e ilustre.")
        self.contextualizer = Contextualizer("Curador de Contexto", "Conecte e aprofunde.")

    def run(self, input_data: str):
        state = PhysicsState(input_data)
        state = self.interpreter.process(state)
        state = self.solver.process(state)
        state = self.visualizer.process(state)
        state = self.contextualizer.process(state)
        return state

if __name__ == "__main__":
    tutor = PhysicsOrchestrator()
    tutor.run("Calcular a força entre duas cargas de 2C a 3m de distância.")
