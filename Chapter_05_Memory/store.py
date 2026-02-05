# store.py - Memory Store Abstraction
# The Senior Agent Blueprint - Chapter 05
"""
ChromaDB wrapper providing a clean abstraction layer.
The Senior Move: If you need to swap ChromaDB for Qdrant/Pinecone,
only this file changes - not your entire codebase.
"""

from typing import Optional
import chromadb
from chromadb.config import Settings as ChromaSettings

from .config import settings
from .models import Document, SearchResult


class MemoryStore:
    """
    Abstraction layer over ChromaDB for vector memory operations.
    
    The Senior Move: Dependency inversion - business logic depends on
    this interface, not on ChromaDB directly. Enables easy testing
    and future provider migrations.
    """
    
    def __init__(
        self,
        collection_name: Optional[str] = None,
        persist_directory: Optional[str] = None
    ):
        """
        Initialize the memory store.
        
        Args:
            collection_name: Name of the collection (default from config)
            persist_directory: Path for persistent storage (default from config)
        """
        self._collection_name = collection_name or settings.COLLECTION_NAME
        self._persist_dir = persist_directory or str(settings.CHROMA_PERSIST_DIR)
        
        # Ensure persist directory exists
        settings.CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client with persistence
        self._client = chromadb.PersistentClient(
            path=self._persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # Get or create collection with embedding function
        self._embedding_function = self._get_embedding_function()
        self._collection = self._client.get_or_create_collection(
            name=self._collection_name,
            embedding_function=self._embedding_function,
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )
    
    def _get_embedding_function(self):
        """
        Get the appropriate embedding function based on config.
        
        The Senior Move: Support both local (sentence-transformers) and
        cloud (OpenAI) embeddings via configuration.
        """
        if settings.OPENAI_API_KEY:
            # Use OpenAI embeddings if API key is provided
            from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
            return OpenAIEmbeddingFunction(
                api_key=settings.OPENAI_API_KEY,
                model_name=settings.OPENAI_EMBEDDING_MODEL
            )
        else:
            # Default to local sentence-transformers
            from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
            return SentenceTransformerEmbeddingFunction(
                model_name=settings.EMBEDDING_MODEL
            )
    
    def add_documents(self, documents: list[Document]) -> int:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of Document objects to add
            
        Returns:
            Number of documents successfully added
        """
        if not documents:
            return 0
        
        # Convert to ChromaDB format
        ids = []
        texts = []
        metadatas = []
        
        for doc in documents:
            chroma_format = doc.to_chroma_format()
            ids.append(chroma_format["id"])
            texts.append(chroma_format["document"])
            metadatas.append(chroma_format["metadata"])
        
        # Upsert to handle duplicates gracefully
        self._collection.upsert(
            ids=ids,
            documents=texts,
            metadatas=metadatas
        )
        
        return len(documents)
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        where: Optional[dict] = None,
        where_document: Optional[dict] = None
    ) -> list[SearchResult]:
        """
        Perform semantic search over stored documents.
        
        Args:
            query: The search query text
            top_k: Number of results to return
            where: Optional metadata filter (e.g., {"source": "file.txt"})
            where_document: Optional document content filter
            
        Returns:
            List of SearchResult objects, ranked by relevance
        """
        results = self._collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where,
            where_document=where_document,
            include=["documents", "metadatas", "distances"]
        )
        
        # Convert to SearchResult objects
        search_results = []
        
        if results["documents"] and results["documents"][0]:
            documents = results["documents"][0]
            distances = results["distances"][0]
            metadatas = results["metadatas"][0]
            
            for doc, dist, meta in zip(documents, distances, metadatas):
                search_results.append(
                    SearchResult.from_chroma_result(
                        document=doc,
                        distance=dist,
                        metadata=meta
                    )
                )
        
        return search_results
    
    def delete(self, document_ids: list[str]) -> int:
        """
        Delete documents by their IDs.
        
        Args:
            document_ids: List of document IDs to delete
            
        Returns:
            Number of documents deleted
        """
        if not document_ids:
            return 0
        
        # ChromaDB delete doesn't return count, so we track it
        existing = self._collection.get(ids=document_ids)
        count = len(existing["ids"]) if existing["ids"] else 0
        
        if count > 0:
            self._collection.delete(ids=document_ids)
        
        return count
    
    def delete_by_source(self, source: str) -> int:
        """
        Delete all documents from a specific source.
        
        The Senior Move: Enables clean re-ingestion of updated files.
        
        Args:
            source: The source filename/URL to delete
            
        Returns:
            Number of documents deleted
        """
        # Get all documents with this source
        results = self._collection.get(
            where={"source": source},
            include=["metadatas"]
        )
        
        if not results["ids"]:
            return 0
        
        self._collection.delete(ids=results["ids"])
        return len(results["ids"])
    
    def get_stats(self) -> dict:
        """
        Get statistics about the memory store.
        
        Returns:
            Dictionary with collection statistics
        """
        count = self._collection.count()
        
        return {
            "collection_name": self._collection_name,
            "persist_directory": self._persist_dir,
            "document_count": count,
            "embedding_model": (
                settings.OPENAI_EMBEDDING_MODEL 
                if settings.OPENAI_API_KEY 
                else settings.EMBEDDING_MODEL
            )
        }
    
    def clear(self) -> int:
        """
        Clear all documents from the collection.
        
        Returns:
            Number of documents deleted
        """
        count = self._collection.count()
        
        if count > 0:
            # Delete and recreate collection
            self._client.delete_collection(self._collection_name)
            self._collection = self._client.get_or_create_collection(
                name=self._collection_name,
                embedding_function=self._embedding_function,
                metadata={"hnsw:space": "cosine"}
            )
        
        return count
