import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from backend.routers import tutor, student

load_dotenv()

app = FastAPI(
    title="TutorIAFisica API",
    version="2026.2.0",
    description="Backend dos 5 agentes + Student Model (Supabase)"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tutor.router)
app.include_router(student.router)

@app.options("/{full_path:path}")
async def preflight_handler(full_path: str):
    return {"message": "OK"}

@app.get("/health")
def health():
    return {"status": "ok", "version": "2026.2.0"}

@app.get("/models")
def list_models():
    from config import Config
    return {name: {"multimodal": info["multimodal"]}
            for name, info in Config.AVAILABLE_MODELS.items()}
