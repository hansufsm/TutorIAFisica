import os
from dotenv import load_dotenv
from typing import Dict

load_dotenv()

class Config:
    # Chaves de API - Lidas do .env
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
    XAI_API_KEY = os.getenv("XAI_API_KEY")
    MANUS_API_KEY = os.getenv("MANUS_API_KEY")

    # Endpoints pCloud (mantidos para referência)
    PCLOUD_API_URL = "https://eapi.pcloud.com"
    PCLOUD_GLOBAL_URL = "https://api.pcloud.com"
    
    # Modelos Disponíveis via LiteLLM
    # Mapeamento de nomes amigáveis para IDs de modelo LiteLLM e suas capacidades
    AVAILABLE_MODELS = {
        "DeepSeek Chat": {"id": "deepseek/deepseek-chat", "multimodal": False},
        "Gemini 2.0 Flash": {"id": "gemini/gemini-2.0-flash", "multimodal": True},
        "Manus": {"id": "manus/manus-1.6", "multimodal": False},

        # Modelos para implementação futura:
        # "Grok 2 Vision": {"id": "xai/grok-2-vision-1212", "multimodal": True},
        # "Gemini 1.5 Flash": {"id": "gemini/gemini-1.5-flash", "multimodal": True},
        # "OpenAI GPT-3.5 Turbo": {"id": "openai/gpt-3.5-turbo", "multimodal": False},
        # "Gemini 2.5 Pro": {"id": "gemini/gemini-2.5-pro-preview-05-06", "multimodal": True},
        # "Grok 3": {"id": "xai/grok-3", "multimodal": False},
        # "Claude 3.5 Sonnet": {"id": "anthropic/claude-3-5-sonnet-20241022", "multimodal": False},
        # "Claude 3 Haiku": {"id": "anthropic/claude-3-haiku-20240307", "multimodal": False},
        # "Perplexity Sonar": {"id": "perplexity/llama-3.1-sonar-small-128k-online", "multimodal": False},
    }

    # Ordem de preferência para fallback automático
    MODEL_PREFERENCE_ORDER = [
        "DeepSeek Chat",
        "Gemini 2.0 Flash",
        "Manus",
    ]

    DEFAULT_MODEL_DISPLAY_NAME = "Gemini 2.0 Flash"
    
    # Configurações Pedagógicas
    SYLLABUS_PATH = os.path.join(os.path.dirname(__file__), "../data/ufsm_syllabus.json")
    DELAY_BETWEEN_AGENTS = 0
    
    @staticmethod
    def get_provider_key_name(model_display_name: str) -> str | None:
        """Mapeia o nome amigável do modelo para o nome da variável de ambiente da chave API."""
        model_info = Config.AVAILABLE_MODELS.get(model_display_name, {})
        model_id = model_info.get("id")
        if not model_id: return None
        
        provider = model_id.split('/')[0]
        if provider == "gemini": return "GEMINI_API_KEY"
        if provider == "deepseek": return "DEEPSEEK_API_KEY"
        if provider == "openai": return "OPENAI_API_KEY"
        if provider == "anthropic": return "ANTHROPIC_API_KEY"
        if provider == "perplexity": return "PERPLEXITY_API_KEY"
        if provider == "xai": return "XAI_API_KEY"
        if provider == "manus": return "MANUS_API_KEY"
        if provider == "local": return None
        return f"{provider.upper()}_API_KEY"

    @staticmethod
    def check_key_availability_for_model(model_display_name: str, runtime_keys: Dict[str, str]) -> bool:
        """Verifica se a chave API para um modelo específico está disponível (env var ou runtime)."""
        key_name = Config.get_provider_key_name(model_display_name)
        if not key_name: return True # Assume disponível se não requer chave externa (ex: local)
        
        # Verifica primeiro no ambiente (dotenv)
        if os.getenv(key_name): return True
        # Verifica se foi fornecida runtime
        if key_name in runtime_keys: return True
        
        return False # Chave não encontrada nem em .env nem em runtime

    @staticmethod
    def get_model_id(display_name: str) -> str:
        default_id = Config.AVAILABLE_MODELS[Config.DEFAULT_MODEL_DISPLAY_NAME]["id"]
        return Config.AVAILABLE_MODELS.get(display_name, {}).get("id", default_id)

    @staticmethod
    def is_model_multimodal(display_name: str) -> bool:
        return Config.AVAILABLE_MODELS.get(display_name, {}).get("multimodal", False)

    @staticmethod
    def get_model_display_name_by_id(model_id: str) -> str | None:
        """Mapeia o ID do modelo para o nome amigável."""
        for name, info in Config.AVAILABLE_MODELS.items():
            if info["id"] == model_id:
                return name
        return None
