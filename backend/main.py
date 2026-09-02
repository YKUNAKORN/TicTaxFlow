import logging

# Configure logging before importing app modules, so the module-level
# workflow compilation below (and every node's per-request log line) is
# actually visible instead of being dropped by the default WARNING root level.
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.api.v1.router import api_router
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
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
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