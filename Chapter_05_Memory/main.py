# main.py - Interactive Memory Engine Demo
# The Senior Agent Blueprint - Chapter 05
"""
Main entry point demonstrating the Modular Memory Engine.
Run this script to ingest documents and perform semantic search.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from Chapter_05_Memory import MemoryStore, IngestionPipeline, settings


def print_header():
    """Print a nice ASCII header."""
    print("\n" + "=" * 60)
    print("   📚 MODULAR MEMORY ENGINE - Chapter 05")
    print("   The Senior Agent Blueprint")
    print("=" * 60)


def print_stats(store: MemoryStore):
    """Print memory store statistics."""
    stats = store.get_stats()
    print(f"\n📊 Store Stats:")
    print(f"   Collection: {stats['collection_name']}")
    print(f"   Documents:  {stats['document_count']}")
    print(f"   Embeddings: {stats['embedding_model']}")


def ingest_pdf(store: MemoryStore, pipeline: IngestionPipeline, pdf_path: str):
    """Ingest a PDF file into the memory store."""
    path = Path(pdf_path)
    
    if not path.exists():
        print(f"❌ File not found: {pdf_path}")
        return
    
    print(f"\n📄 Ingesting: {path.name}")
    print(f"   Size: {path.stat().st_size / 1024 / 1024:.2f} MB")
    
    # Check if already ingested
    existing = store._collection.get(where={"source": path.name})
    if existing["ids"]:
        print(f"   ⚠️  Already ingested ({len(existing['ids'])} chunks)")
        response = input("   Re-ingest? (y/n): ").strip().lower()
        if response == 'y':
            deleted = store.delete_by_source(path.name)
            print(f"   🗑️  Deleted {deleted} existing chunks")
        else:
            return
    
    # Ingest the PDF
    print("   ⏳ Processing...")
    documents = pipeline.ingest_file(path)
    store.add_documents(documents)
    
    print(f"   ✅ Ingested {len(documents)} chunks")
    
    # Show sample chunk
    if documents:
        sample = documents[0]
        print(f"\n   📝 Sample chunk (page {sample.metadata.page_number}):")
        print(f"   \"{sample.content[:150]}...\"")


def search_memory(store: MemoryStore, query: str, top_k: int = 5):
    """Perform semantic search and display results."""
    print(f"\n🔍 Searching: \"{query}\"")
    print("-" * 50)
    
    results = store.search(query, top_k=top_k)
    
    if not results:
        print("   No results found.")
        return
    
    for i, result in enumerate(results, 1):
        page_info = f"p.{result.metadata.get('page_number', '?')}" if result.metadata.get('page_number') else ""
        print(f"\n   [{i}] Score: {result.score:.3f} | Source: {result.source} {page_info}")
        print(f"   {result.content[:200]}...")


def interactive_loop(store: MemoryStore, pipeline: IngestionPipeline):
    """Main interactive loop."""
    while True:
        print("\n" + "-" * 40)
        print("Commands:")
        print("  [1] Ingest PDF")
        print("  [2] Search memory")
        print("  [3] Show stats")
        print("  [4] Clear all memory")
        print("  [q] Quit")
        
        choice = input("\nChoice: ").strip().lower()
        
        if choice == '1':
            # List available PDFs
            pdfs = list(Path(".").glob("*.pdf"))
            if not pdfs:
                print("❌ No PDF files found in current directory")
                continue
            
            print("\nAvailable PDFs:")
            for i, pdf in enumerate(pdfs, 1):
                print(f"  [{i}] {pdf.name}")
            
            # Get user selection
            selection = input("Select PDF number: ").strip()
            try:
                idx = int(selection) - 1
            except ValueError:
                print("❌ Invalid number")
                continue
            
            if not (0 <= idx < len(pdfs)):
                print("❌ Invalid selection")
                continue
            
            # Process the PDF (with its own error handling)
            try:
                ingest_pdf(store, pipeline, str(pdfs[idx]))
            except Exception as e:
                print(f"❌ Error processing PDF: {e}")
        
        elif choice == '2':
            query = input("Enter search query: ").strip()
            if query:
                search_memory(store, query)
        
        elif choice == '3':
            print_stats(store)
        
        elif choice == '4':
            confirm = input("⚠️  Delete ALL documents? (yes/no): ").strip().lower()
            if confirm == 'yes':
                count = store.clear()
                print(f"🗑️  Deleted {count} documents")
        
        elif choice == 'q':
            print("\n👋 Goodbye!")
            break


def main():
    """Main entry point."""
    print_header()
    
    # Initialize components
    print("\n⚙️  Initializing...")
    print(f"   Persist dir: {settings.CHROMA_PERSIST_DIR}")
    
    pipeline = IngestionPipeline()
    store = MemoryStore()
    
    print_stats(store)
    
    # Auto-detect PDFs in directory
    pdfs = list(Path(".").glob("*.pdf"))
    if pdfs:
        print(f"\n📁 Found {len(pdfs)} PDF(s) in directory:")
        for pdf in pdfs:
            print(f"   - {pdf.name}")
    
    # Run interactive loop
    interactive_loop(store, pipeline)


if __name__ == "__main__":
    main()
