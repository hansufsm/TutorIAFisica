import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    PCLOUD_API_URL = "https://eapi.pcloud.com"
    PCLOUD_GLOBAL_URL = "https://api.pcloud.com"
    MODEL_NAME = "gemini-flash-latest"
    
    # Configurações Pedagógicas
    SYLLABUS_PATH = os.path.join(os.path.dirname(__file__), "../data/ufsm_syllabus.json")
    DELAY_BETWEEN_AGENTS = 2
    
    @staticmethod
    def validate():
        if not Config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY não encontrada no ambiente ou arquivo .env")
