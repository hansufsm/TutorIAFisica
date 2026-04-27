import os
from supabase import create_client, Client

_client: Client | None = None

def get_supabase() -> Client:
    """Retorna cliente Supabase singleton."""
    global _client
    if _client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY")
        if not url or not key:
            raise RuntimeError(
                "SUPABASE_URL e SUPABASE_SERVICE_KEY devem estar no .env"
            )
        _client = create_client(url, key)
    return _client
