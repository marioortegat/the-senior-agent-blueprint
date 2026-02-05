# config.py - Centralized Configuration
# The Senior Agent Blueprint - Chapter 05
"""
Configuration management using pydantic-settings.
The Senior Move: All settings from environment variables, zero hardcoded paths.
"""

from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    The Senior Move: Using pydantic-settings ensures type validation,
    default values, and seamless .env file support.
    """
    
    # Storage Configuration
    CHROMA_PERSIST_DIR: Path = Field(
        default=Path("./data/chromadb"),
        description="Directory for persistent ChromaDB storage"
    )
    COLLECTION_NAME: str = Field(
        default="memory",
        description="Default collection name in ChromaDB"
    )
    
    # Embedding Configuration
    EMBEDDING_MODEL: str = Field(
        default="all-MiniLM-L6-v2",
        description="Sentence-transformers model for local embeddings"
    )
    OPENAI_API_KEY: Optional[str] = Field(
        default=None,
        description="OpenAI API key for cloud embeddings (optional)"
    )
    OPENAI_EMBEDDING_MODEL: str = Field(
        default="text-embedding-3-small",
        description="OpenAI embedding model to use if API key is provided"
    )
    
    # Chunking Configuration
    CHUNK_SIZE: int = Field(
        default=500,
        ge=100,
        le=2000,
        description="Target size for text chunks in characters"
    )
    CHUNK_OVERLAP: int = Field(
        default=50,
        ge=0,
        le=200,
        description="Overlap between consecutive chunks"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# Singleton instance
settings = Settings()
