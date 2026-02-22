"""Application configuration and settings."""
import os
from datetime import datetime
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings and configuration."""
    
    # API Settings
    API_TITLE: str = "TicTaxFlow API"
    API_DESCRIPTION: str = "Tax management system with AI agents"
    API_VERSION: str = "1.0.0"
    
    # CORS Settings
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]
    
    # API Keys
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    
    # Database Settings
    SUPABASE_URL: Optional[str] = os.getenv("SUPABASE_URL")
    SUPABASE_KEY: Optional[str] = os.getenv("SUPABASE_KEY")
    
    # Path Settings
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    DOCUMENTS_DIR: Path = DATA_DIR / "documents"
    EMBEDDINGS_DIR: Path = DATA_DIR / "embeddings"
    RECEIPTS_DIR: Path = DATA_DIR / "receipts"
    
    # Vector Database Settings
    CHROMA_COLLECTION_NAME: str = "document_collection"
    
    # Agent Settings
    DEFAULT_TAX_YEAR: int = datetime.now().year
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    RAG_N_RESULTS: int = 5
    
    # AI Model Settings
    GEMINI_MODEL: str = "gemini-2.5-flash"
    
    def validate(self) -> None:
        """Validate required environment variables."""
        if not self.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required")
        if not self.SUPABASE_URL:
            raise ValueError("SUPABASE_URL is required")
        if not self.SUPABASE_KEY:
            raise ValueError("SUPABASE_KEY is required")


settings = Settings()
