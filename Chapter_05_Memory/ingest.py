# ingest.py - ETL Ingestion Pipeline
# The Senior Agent Blueprint - Chapter 05
"""
Robust document ingestion with smart chunking and automatic metadata.
The Senior Move: Garbage In, Garbage Out - quality ingestion is critical.
"""

import re
from pathlib import Path
from datetime import datetime
from typing import Optional, Generator

from .config import settings
from .models import Document, DocumentMetadata


class RecursiveCharacterTextSplitter:
    """
    Text splitter that recursively splits on different separators.
    
    The Senior Move: Implement core functionality without heavy dependencies.
    This is a simplified but production-ready implementation.
    """
    
    # Separators in order of priority (best to worst for semantic breaks)
    DEFAULT_SEPARATORS = [
        "\n\n",      # Paragraphs
        "\n",        # Lines
        ". ",        # Sentences
        "? ",        # Questions
        "! ",        # Exclamations
        "; ",        # Semicolons
        ", ",        # Commas
        " ",         # Words
        ""           # Characters (last resort)
    ]
    
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        separators: Optional[list[str]] = None
    ):
        """
        Initialize the text splitter.
        
        Args:
            chunk_size: Target size for each chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
            separators: Custom separators (uses defaults if not provided)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or self.DEFAULT_SEPARATORS
    
    def split_text(self, text: str) -> list[str]:
        """
        Split text into chunks using recursive separation.
        
        Args:
            text: The text to split
            
        Returns:
            List of text chunks
        """
        return self._split_text_recursive(text, self.separators)
    
    def _split_text_recursive(
        self,
        text: str,
        separators: list[str]
    ) -> list[str]:
        """Recursively split text using the separator hierarchy."""
        
        # Base case: text fits in chunk
        if len(text) <= self.chunk_size:
            return [text.strip()] if text.strip() else []
        
        # Try each separator
        for i, separator in enumerate(separators):
            if separator == "":
                # Last resort: split by character count
                return self._split_by_character(text)
            
            if separator in text:
                splits = text.split(separator)
                
                # Merge small splits back together
                chunks = []
                current_chunk = ""
                
                for split in splits:
                    # Add separator back (except for first split)
                    test_chunk = current_chunk + (separator if current_chunk else "") + split
                    
                    if len(test_chunk) <= self.chunk_size:
                        current_chunk = test_chunk
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        
                        # If single split is too large, recurse with next separator
                        if len(split) > self.chunk_size:
                            sub_chunks = self._split_text_recursive(
                                split, separators[i + 1:]
                            )
                            chunks.extend(sub_chunks)
                            current_chunk = ""
                        else:
                            current_chunk = split
                
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                
                # Apply overlap
                return self._apply_overlap(chunks)
        
        return [text.strip()] if text.strip() else []
    
    def _split_by_character(self, text: str) -> list[str]:
        """Split text by character count when no separators work."""
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunks.append(text[start:end].strip())
            start = end - self.chunk_overlap
        
        return [c for c in chunks if c]
    
    def _apply_overlap(self, chunks: list[str]) -> list[str]:
        """Apply overlap between consecutive chunks."""
        if len(chunks) <= 1 or self.chunk_overlap <= 0:
            return chunks
        
        result = [chunks[0]]
        
        for i in range(1, len(chunks)):
            prev_chunk = chunks[i - 1]
            curr_chunk = chunks[i]
            
            # Get overlap from end of previous chunk
            overlap_text = prev_chunk[-self.chunk_overlap:] if len(prev_chunk) > self.chunk_overlap else prev_chunk
            
            # Only add overlap if it doesn't exceed chunk_size
            if len(overlap_text) + len(curr_chunk) <= self.chunk_size:
                result.append(overlap_text + " " + curr_chunk)
            else:
                result.append(curr_chunk)
        
        return result


class IngestionPipeline:
    """
    ETL pipeline for processing documents into the vector store.
    
    The Senior Move: Separate ingestion logic from storage logic.
    This class handles the Transform part of ETL.
    """
    
    # Supported file extensions and their handlers
    SUPPORTED_EXTENSIONS = {".txt", ".md", ".py", ".json", ".csv", ".pdf"}
    
    def __init__(
        self,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None
    ):
        """
        Initialize the ingestion pipeline.
        
        Args:
            chunk_size: Override default chunk size from config
            chunk_overlap: Override default chunk overlap from config
        """
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
        
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
    
    def ingest_text(
        self,
        text: str,
        source: str,
        extra_metadata: Optional[dict] = None
    ) -> list[Document]:
        """
        Process raw text into Document objects.
        
        Args:
            text: The text content to process
            source: Source identifier (filename, URL, etc.)
            extra_metadata: Additional metadata to include
            
        Returns:
            List of Document objects ready for storage
        """
        # Clean the text
        text = self._clean_text(text)
        
        if not text:
            return []
        
        # Split into chunks
        chunks = self.splitter.split_text(text)
        
        if not chunks:
            return []
        
        # Create documents with metadata
        documents = []
        total_chunks = len(chunks)
        
        for i, chunk in enumerate(chunks):
            metadata = DocumentMetadata(
                source=source,
                chunk_index=i,
                total_chunks=total_chunks,
                created_at=datetime.now(),
                extra=extra_metadata or {}
            )
            
            doc = Document(
                content=chunk,
                metadata=metadata
            )
            documents.append(doc)
        
        return documents
    
    def ingest_file(
        self,
        file_path: Path | str,
        extra_metadata: Optional[dict] = None
    ) -> list[Document]:
        """
        Process a file into Document objects.
        
        Args:
            file_path: Path to the file to process
            extra_metadata: Additional metadata to include
            
        Returns:
            List of Document objects ready for storage
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type: {file_path.suffix}. "
                f"Supported: {self.SUPPORTED_EXTENSIONS}"
            )
        
        # Handle PDF files specially
        if file_path.suffix.lower() == ".pdf":
            return self.ingest_pdf(file_path, extra_metadata)
        
        # Read text file content
        try:
            text = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = file_path.read_text(encoding="latin-1")
        
        # Add file-specific metadata
        file_metadata = {
            "filename": file_path.name,
            "extension": file_path.suffix,
            "file_size_bytes": file_path.stat().st_size,
            **(extra_metadata or {})
        }
        
        return self.ingest_text(
            text=text,
            source=file_path.name,
            extra_metadata=file_metadata
        )
    
    def ingest_pdf(
        self,
        file_path: Path | str,
        extra_metadata: Optional[dict] = None
    ) -> list[Document]:
        """
        Process a PDF file into Document objects with page-level metadata.
        
        The Senior Move: Extract text per page and preserve page numbers
        for precise citation and debugging.
        
        Args:
            file_path: Path to the PDF file
            extra_metadata: Additional metadata to include
            
        Returns:
            List of Document objects ready for storage
        """
        try:
            from PyPDF2 import PdfReader
        except ImportError:
            raise ImportError(
                "PyPDF2 is required for PDF processing. "
                "Install it with: pip install PyPDF2"
            )
        
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        # Read PDF
        reader = PdfReader(str(file_path))
        total_pages = len(reader.pages)
        
        # First pass: collect all chunks with their page info
        all_chunks: list[tuple[str, int, int]] = []  # (text, page_num, page_chunk_idx)
        
        for page_num, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text() or ""
            
            if not page_text.strip():
                continue  # Skip empty pages
            
            # Clean the text
            page_text = self._clean_text(page_text)
            
            # Split page into chunks
            chunks = self.splitter.split_text(page_text)
            
            for chunk_idx, chunk in enumerate(chunks):
                all_chunks.append((chunk, page_num, chunk_idx))
        
        # Now create Documents with correct total_chunks
        total_chunks = len(all_chunks)
        if total_chunks == 0:
            return []
        
        all_documents = []
        for i, (chunk_text, page_num, page_chunk_idx) in enumerate(all_chunks):
            metadata = DocumentMetadata(
                source=file_path.name,
                chunk_index=i,
                total_chunks=total_chunks,
                created_at=datetime.now(),
                page_number=page_num,
                extra={
                    "filename": file_path.name,
                    "extension": ".pdf",
                    "file_size_bytes": file_path.stat().st_size,
                    "total_pages": total_pages,
                    "page_chunk_index": page_chunk_idx,
                    **(extra_metadata or {})
                }
            )
            
            doc = Document(content=chunk_text, metadata=metadata)
            all_documents.append(doc)
        
        return all_documents
    
    def ingest_directory(
        self,
        dir_path: Path | str,
        pattern: str = "*",
        recursive: bool = True,
        extra_metadata: Optional[dict] = None
    ) -> Generator[tuple[str, list[Document]], None, None]:
        """
        Process all files in a directory.
        
        The Senior Move: Use a generator for memory efficiency
        when processing large directories.
        
        Args:
            dir_path: Path to the directory
            pattern: Glob pattern for file matching
            recursive: Whether to search subdirectories
            extra_metadata: Additional metadata to include
            
        Yields:
            Tuples of (filename, list of Documents)
        """
        dir_path = Path(dir_path)
        
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {dir_path}")
        
        if not dir_path.is_dir():
            raise ValueError(f"Not a directory: {dir_path}")
        
        # Find matching files
        glob_method = dir_path.rglob if recursive else dir_path.glob
        
        for file_path in glob_method(pattern):
            if file_path.is_file() and file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                try:
                    documents = self.ingest_file(
                        file_path,
                        extra_metadata={
                            "directory": str(dir_path),
                            **(extra_metadata or {})
                        }
                    )
                    yield file_path.name, documents
                except Exception as e:
                    # Log error but continue processing
                    print(f"Warning: Failed to process {file_path}: {e}")
                    continue
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text before chunking.
        
        Args:
            text: Raw text input
            
        Returns:
            Cleaned text
        """
        # Normalize whitespace
        text = re.sub(r'\r\n', '\n', text)  # Normalize line endings
        text = re.sub(r'\t', '    ', text)  # Convert tabs to spaces
        text = re.sub(r' +', ' ', text)     # Collapse multiple spaces
        text = re.sub(r'\n{3,}', '\n\n', text)  # Max 2 consecutive newlines
        
        return text.strip()
