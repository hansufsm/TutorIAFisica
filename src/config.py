import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    
    # Endpoints pCloud
    PCLOUD_API_URL = "https://eapi.pcloud.com"
    PCLOUD_GLOBAL_URL = "https://api.pcloud.com"
    
    # Configurações de IA
    PRIMARY_MODEL = "gemini/gemini-2.0-flash"
    FALLBACK_MODEL = "deepseek/deepseek-chat"
    
    # Modelo Ativo (Pode ser alterado dinamicamente no app.py)
    ACTIVE_MODEL = PRIMARY_MODEL
    
    # Configurações Pedagógicas
    SYLLABUS_PATH = os.path.join(os.path.dirname(__file__), "../data/ufsm_syllabus.json")
    DELAY_BETWEEN_AGENTS = 2
    
    @staticmethod
    def validate():
        if not Config.GEMINI_API_KEY and not Config.DEEPSEEK_API_KEY:
            raise ValueError("Nenhuma chave de API (Gemini ou DeepSeek) encontrada.")
