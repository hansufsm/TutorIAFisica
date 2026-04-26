import os
from dotenv import load_dotenv
import litellm
import streamlit as st
from typing import List, Dict, Any, Optional

load_dotenv()

class Config:
    # Chaves de API - Lidas do .env
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY") # Para Claude
    PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
    # Chave para modelo Manusc (se for um serviço externo, senão pode ser configurado de outra forma)
    MANUSC_API_KEY = os.getenv("MANUSC_API_KEY") 

    # Endpoints pCloud (mantidos para referência)
    PCLOUD_API_URL = "https://eapi.pcloud.com"
    PCLOUD_GLOBAL_URL = "https://api.pcloud.com"
    
    # Modelos Disponíveis via LiteLLM
    # Mapeamento de nomes amigáveis para IDs de modelo LiteLLM e suas capacidades
    AVAILABLE_MODELS = {
        "Gemini 3.0 Preview": {"id": "gemini/gemini-3-pro-preview", "multimodal": True}, 
        "Gemini 2.0 Flash": {"id": "gemini/gemini-2.0-flash", "multimodal": True},
        "Gemini 1.5 Flash": {"id": "gemini/gemini-1.5-flash", "multimodal": True},
        "OpenAI GPT-3.5 Turbo": {"id": "openai/gpt-3.5-turbo", "multimodal": False},
        "Claude 3 Sonnet": {"id": "claude/claude-3-sonnet", "multimodal": False},
        "Claude 3 Haiku": {"id": "claude/claude-3-haiku", "multimodal": False},
        "Claude 3 Opus": {"id": "claude/claude-3-opus", "multimodal": False},
        "Perplexity Online": {"id": "perplexity/online", "multimodal": False},
        "DeepSeek Chat": {"id": "deepseek/deepseek-chat", "multimodal": False},
        "Manusc Model": {"id": "local/manusc-model", "multimodal": False} # Placeholder para modelo local/customizado
    }
    
    # Ordem de preferência para fallback automático
    MODEL_PREFERENCE_ORDER = [
        "Gemini 3.0 Preview", 
        "Gemini 1.5 Flash", 
        "OpenAI GPT-3.5 Turbo", 
        "Claude 3 Sonnet", 
        "Claude 3 Haiku", 
        "Claude 3 Opus", 
        "Perplexity Online", 
        "DeepSeek Chat",
        "Manusc Model" 
    ]
    
    DEFAULT_MODEL_DISPLAY_NAME = "Gemini 3.0 Preview" # Modelo inicial selecionado no UI
    
    # Configurações Pedagógicas
    SYLLABUS_PATH = os.path.join(os.path.dirname(__file__), "../data/ufsm_syllabus.json")
    DELAY_BETWEEN_AGENTS = 2
    
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
        if provider == "claude": return "ANTHROPIC_API_KEY"
        if provider == "perplexity": return "PERPLEXITY_API_KEY"
        if provider == "local": return None # Modelos locais não usam chave API externa
        return f"{provider.upper()}_API_KEY" # Fallback genérico para outros provedores

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
        return Config.AVAILABLE_MODELS.get(display_name, {}).get("id", Config.DEFAULT_MODEL_DISPLAY_NAME)

    @staticmethod
    def is_model_multimodal(display_name: str) -> bool:
        return Config.AVAILABLE_MODELS.get(display_name, {}).get("multimodal", False)
