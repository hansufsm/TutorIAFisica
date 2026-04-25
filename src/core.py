import os
import google.generativeai as genai
import time
import json
import requests
from typing import List, Dict, Any
from dotenv import load_dotenv
from pypdf import PdfReader
import io

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
    def __init__(self, raw_input: str, teacher_notes: str = "", pcloud_url: str = ""):
        self.raw_input = raw_input
        self.teacher_notes = teacher_notes
        self.pcloud_url = pcloud_url
        self.concepts = []
        self.solution_steps = ""
        self.pergunta_socratica = ""
        self.code_snippet = ""
        self.is_valid = True
        self.mapa_mental_markdown = ""
        self.ufsm_alignment = None 
        self.pcloud_notes_found = False
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
                            return
        except Exception as e:
            print(f"Erro ao consultar ementário: {e}")

    def fetch_pcloud_public_notes(self):
        """Busca arquivos PDF através de um link público do pCloud."""
        if not self.pcloud_url:
            return
        
        # Extrai o código do link (ex: https://u.pcloud.link/publink/show?code=XZ123 -> XZ123)
        try:
            code = self.pcloud_url.split("code=")[-1]
            # Tenta primeiro a API da Europa (comum para muitos usuários) e depois a Global
            api_url = "https://eapi.pcloud.com/showpublink"
            response = requests.get(api_url, params={"code": code})
            data = response.json()
            
            # Se falhar na Europa, tenta a Global
            if data.get("result") != 0:
                api_url = "https://api.pcloud.com/showpublink"
                response = requests.get(api_url, params={"code": code})
                data = response.json()

            if data.get("result") == 0:
                metadata = data.get("metadata", {})
                contents = metadata.get("contents", [])
                
                pdf_files = [item for item in contents if item.get("name", "").endswith(".pdf")]
                
                if pdf_files:
                    print(f"[*] {len(pdf_files)} PDFs encontrados no link público pCloud.")
                    self.pcloud_notes_found = True
                    all_text = ""
                    
                    for pdf_info in pdf_files:
                        # Obtém o link de download direto para o arquivo
                        dl_url_api = "https://eapi.pcloud.com/getpublinkdownload"
                        dl_res = requests.get(dl_url_api, params={"code": code, "fileid": pdf_info['fileid']})
                        dl_data = dl_res.json()
                        
                        if dl_data.get("result") == 0:
                            # Constrói a URL de download real
                            path = dl_data['path']
                            host = dl_data['hosts'][0]
                            final_dl_url = f"https://{host}{path}"
                            
                            # Baixa o PDF em memória
                            file_res = requests.get(final_dl_url)
                            f = io.BytesIO(file_res.content)
                            reader = PdfReader(f)
                            for page in reader.pages:
                                all_text += page.extract_text() + "\n"
                    
                    self.teacher_notes = (self.teacher_notes + "\n\n" + all_text).strip()
        except Exception as e:
            print(f"Erro ao processar link público pCloud: {e}")

class TutorIAAgent:
    def __init__(self, name: str, system_instruction: str):
        self.name = name
        self.system_instruction = system_instruction

    def ask_gemini(self, prompt: str, teacher_notes: str = "", image: Any = None) -> str:
        if not model:
            return "ERRO: Gemini API Key não configurada."
        try:
            context_prefix = f"CONTEXTO DO PROFESSOR (FONTE PRIMÁRIA): {teacher_notes}\n\n" if teacher_notes else ""
            full_prompt_text = f"{self.system_instruction}\n\n{context_prefix}Entrada: {prompt}"

            if image:
                # Entrada Multimodal
                response = model.generate_content([full_prompt_text, image])
            else:
                # Entrada de Texto apenas
                response = model.generate_content(full_prompt_text)

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

    def run(self, input_data: str, teacher_notes: str = "", pcloud_url: str = ""):
        state = PhysicsState(input_data, teacher_notes, pcloud_url)
        # Primeiro, buscamos as notas na nuvem antes do processamento dos agentes
        state.fetch_pcloud_public_notes()
        
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
