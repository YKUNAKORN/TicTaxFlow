import logging
import os

# Configure logging before importing app modules, so the module-level
# workflow compilation below (and every node's per-request log line) is
# actually visible instead of being dropped by the default WARNING root level.
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

# The RAG embedding model must already be cached locally by the time this
# app serves a request (see app/services/document_indexer.py - the
# build/deploy-time step that populates that cache and needs network).
# Force offline here, before importing the app modules below that load
# the embedding function, so a demo host with no route to Hugging Face
# fails loudly on a cold cache instead of hanging or silently depending
# on reaching it live. document_indexer.py and scripts/seed_demo.py don't
# import this file, so their deliberate first-time downloads are unaffected.
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.api.v1.router import api_router
from app.core.config import settings
from app.services.workflow import compiled_graph

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # `compiled_graph` was already compiled once at import time (module-level
    # singleton in app/services/workflow.py). Referencing it here just makes
    # that startup-time compilation explicit and confirms it's ready before
    # the app starts serving requests.
    logger.info("LangGraph workflow ready: %s", compiled_graph)
    yield


app = FastAPI(
    title="TicTaxFlow API",
    description="Tax management system with AI agents",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for receipts
receipts_dir = Path(__file__).parent / "data" / "receipts"
receipts_dir.mkdir(parents=True, exist_ok=True)
app.mount("/receipts", StaticFiles(directory=str(receipts_dir)), name="receipts")

# Include API v1 routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {
        "message": "TicTaxFlow API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/health/deep")
def health_check_deep():
    """Ping Gemini and Chroma directly. No auth — used to confirm both
    dependencies are reachable before a demo. Never include the API key."""
    from app.core.config import settings
    from app.agents.tax_expert import genai_client
    from app.services.retrieval import retrieve_context

    gemini_status = {"gemini": "ok", "detail": None}
    try:
        genai_client.models.generate_content(
            model=f"models/{settings.GEMINI_MODEL}",
            contents="ping",
        )
    except Exception as e:
        gemini_status = {"gemini": "error", "detail": f"{type(e).__name__}: {e}"}

    rag_status = {"rag": "ok", "detail": None}
    try:
        chunks = retrieve_context("test")
        if not chunks:
            rag_status = {"rag": "empty", "detail": "no chunks returned"}
    except Exception as e:
        rag_status = {"rag": "error", "detail": f"{type(e).__name__}: {e}"}

    return {**gemini_status, **rag_status}