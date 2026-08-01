from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from .routes import upload, extraction, score, graph

app = FastAPI(
    title="CurricuAlign AI — Backend Intelligence Engine",
    description="FastAPI backend for Stage 1 (PDF Ingestion), Stage 2 (Skill Extraction & Normalization), Stage 4 (Alignment Score Engine), and Knowledge Graph API.",
    version="1.0.0"
)

# Enable CORS for local React frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Member 1 Route Handlers
app.include_router(upload.router)
app.include_router(extraction.router)
app.include_router(score.router)
app.include_router(graph.router)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "CurricuAlign Backend Engine",
        "member": "Member 1 (Pranav)",
        "pipeline_stages": ["Stage 1: PDF Ingestion", "Stage 2: Extraction & Normalization", "Stage 4: Alignment Score"]
    }

@app.get("/")
def root():
    return {
        "message": "CurricuAlign AI Backend Engine is Running",
        "docs_url": "/docs",
        "health_url": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
