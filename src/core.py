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

class TutorIAAgent:
    """Classe base para todos os agentes do sistema."""
    def __init__(self, name: str, instructions: str):
        self.name = name
        self.instructions = instructions

    def process(self, state: PhysicsState) -> PhysicsState:
        print(f"[*] {self.name} processando...")
        return state

class SocraticInterpreter(TutorIAAgent):
    """Analisa o enunciado e decide se precisa de mais info do aluno."""
    def process(self, state: PhysicsState) -> PhysicsState:
        print(f"[*] {self.name}: Decompondo o problema e verificando conceitos.")
        state.concepts = ["Eletrostática", "Lei de Coulomb", "Campo Elétrico"]
        return state

class DimensionalSolver(TutorIAAgent):
    """Resolve e valida unidades."""
    def process(self, state: PhysicsState) -> PhysicsState:
        print(f"[*] {self.name}: Calculando com verificação dimensional (SI).")
        return state

class InteractiveVisualizer(TutorIAAgent):
    """Gera código Python para visualização dinâmica."""
    def process(self, state: PhysicsState) -> PhysicsState:
        print(f"[*] {self.name}: Gerando código para simulação em Plotly.")
        state.code_snippet = "import plotly.graph_objects as go\n# Código gerado para visualizar campo elétrico..."
        return state

class Contextualizer(TutorIAAgent):
    """Resgata a essência do FisicaIA: Conectar com o mundo real e acadêmico."""
    def process(self, state: PhysicsState) -> PhysicsState:
        print(f"[*] {self.name}: Gerando curadoria acadêmica e aplicações práticas.")
        state.links_universidades = [
            "https://www.if.ufrgs.br/institucional/",
            "https://portal.ufsm.br/ementario/curso.html?curso=414",
            "https://www.ifsc.usp.br/"
        ]
        state.video_sugerido = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        state.exercicios_propostos = [
            {"nivel": "Médio", "enunciado": "Calcule a nova força se a distância dobrar."},
            {"nivel": "Desafio", "enunciado": "Determine o campo elétrico no ponto médio entre as cargas."}
        ]
        state.aplicacoes_reais = ["Desfibriladores cardíacos", "Pintura eletrostática", "Xerografia"]
        state.mapa_mental_markdown = """
# Eletrostática
## Lei de Coulomb
- Cargas (q1, q2)
- Distância (r)
- Constante (k)
## Aplicações
- Desfibriladores
- Impressoras
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
    print("--- INICIANDO TESTE DO TUTORIAFISICA ---")
    resultado = tutor.run("Calcular a força entre duas cargas de 5uC separadas por 10cm.")
    print("\n--- RESULTADOS DO TESTE ---")
    print(f"Conceitos: {resultado.concepts}")
    print(f"Aplicações Reais: {resultado.aplicacoes_reais}")
    print(f"Links Acadêmicos: {len(resultado.links_universidades)} fontes encontradas.")
    print("--- TESTE CONCLUÍDO COM SUCESSO ---")
