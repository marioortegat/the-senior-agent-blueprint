# __init__.py - Package Exports
# The Senior Agent Blueprint - Chapter 05
"""
Modular Memory Engine - A production-ready vector memory system.

The Senior Move: Clean public API - users import what they need,
internal implementation details stay hidden.
"""

from .models import Document, DocumentMetadata, SearchResult
from .store import MemoryStore
from .ingest import IngestionPipeline, RecursiveCharacterTextSplitter
from .config import settings

__all__ = [
    # Core classes
    "MemoryStore",
    "IngestionPipeline",
    "RecursiveCharacterTextSplitter",
    
    # Data models
    "Document",
    "DocumentMetadata", 
    "SearchResult",
    
    # Configuration
    "settings",
]

__version__ = "1.0.0"
