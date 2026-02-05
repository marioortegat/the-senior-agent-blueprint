# models.py - Data Models
# The Senior Agent Blueprint - Chapter 05
"""
Pydantic models for strict typing across the memory system.
The Senior Move: Never pass loose dicts - define explicit schemas.
"""

from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field
import uuid


def generate_id() -> str:
    """Generate a unique document ID."""
    return str(uuid.uuid4())


class DocumentMetadata(BaseModel):
    """
    Structured metadata for ingested documents.
    
    The Senior Move: Storing rich metadata enables powerful filtering
    and debugging. A junior stores just text; a senior stores context.
    """
    
    source: str = Field(
        ...,
        description="Original filename or URL"
    )
    chunk_index: int = Field(
        ...,
        ge=0,
        description="Position of this chunk in the original document"
    )
    total_chunks: int = Field(
        ...,
        ge=1,
        description="Total number of chunks from the source document"
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp when the document was ingested"
    )
    page_number: Optional[int] = Field(
        default=None,
        ge=1,
        description="Page number for PDFs or paginated sources"
    )
    extra: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional custom metadata"
    )


class Document(BaseModel):
    """
    A document ready for storage in the vector database.
    
    The Senior Move: Using Pydantic ensures all documents have
    valid IDs, content, and metadata before hitting the DB.
    """
    
    id: str = Field(
        default_factory=generate_id,
        description="Unique identifier for deduplication"
    )
    content: str = Field(
        ...,
        min_length=1,
        description="The text content of the document"
    )
    metadata: DocumentMetadata = Field(
        ...,
        description="Structured metadata for the document"
    )
    
    def to_chroma_format(self) -> dict:
        """Convert to ChromaDB's expected format."""
        return {
            "id": self.id,
            "document": self.content,
            "metadata": {
                "source": self.metadata.source,
                "chunk_index": self.metadata.chunk_index,
                "total_chunks": self.metadata.total_chunks,
                "created_at": self.metadata.created_at.isoformat(),
                "page_number": self.metadata.page_number or 0,
                **self.metadata.extra
            }
        }


class SearchResult(BaseModel):
    """
    A single result from semantic search.
    
    The Senior Move: Returning typed results (not raw dicts) enables
    IDE autocomplete and catches errors at development time.
    """
    
    content: str = Field(
        ...,
        description="The retrieved text content"
    )
    score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Similarity score (0 = no match, 1 = exact match)"
    )
    source: str = Field(
        ...,
        description="Original source of the content"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Full metadata from the stored document"
    )
    
    @classmethod
    def from_chroma_result(
        cls,
        document: str,
        distance: float,
        metadata: dict
    ) -> "SearchResult":
        """
        Create SearchResult from ChromaDB query output.
        
        ChromaDB returns distances (lower = better), we convert to scores.
        """
        # Convert distance to similarity score (1 - normalized_distance)
        # ChromaDB L2 distances are typically 0-2 for normalized embeddings
        score = max(0.0, min(1.0, 1.0 - (distance / 2.0)))
        
        return cls(
            content=document,
            score=score,
            source=metadata.get("source", "unknown"),
            metadata=metadata
        )
