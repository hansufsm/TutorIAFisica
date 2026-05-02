"""
Geração de embeddings via OpenAI text-embedding-3-small.
Usado pelo Long-term RAG para busca semântica em sessões passadas.
"""
import os


async def generate_embedding(text: str) -> list[float] | None:
    """Gera embedding 1536-dim para o texto. Retorna None se falhar."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=api_key)
        resp = await client.embeddings.create(
            model="text-embedding-3-small",
            input=text[:8000],
        )
        return resp.data[0].embedding
    except Exception as e:
        print(f"[RAG] Embedding generation failed: {e}")
        return None
