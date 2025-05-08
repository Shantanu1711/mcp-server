import chromadb
from chromadb.config import Settings
import json
import os
from pathlib import Path

def inspect_chromadb():
    """Inspect ChromaDB's internal structure and data."""
    print("ChromaDB Inspector")
    print("=" * 50)
    
    # Initialize ChromaDB client
    client = chromadb.Client(Settings(
        persist_directory="pinecone_db",
        anonymized_telemetry=False
    ))
    
    try:
        # Get the collection
        collection = client.get_collection("documents")
        
        # Get collection info
        print("\nCollection Information:")
        print("-" * 30)
        print(f"Collection Name: {collection.name}")
        print(f"Collection Count: {collection.count()}")
        
        # Get all items
        results = collection.get()
        
        if not results['ids']:
            print("\nNo documents found in the collection.")
            return
        
        # Print document structure
        print("\nDocument Structure:")
        print("-" * 30)
        print(f"Number of documents: {len(results['ids'])}")
        print(f"Number of unique sources: {len(set(metadata.get('source', 'N/A') for metadata in results['metadatas']))}")
        
        # Print sample document
        print("\nSample Document:")
        print("-" * 30)
        sample_idx = 0
        print(f"ID: {results['ids'][sample_idx]}")
        print(f"Source: {results['metadatas'][sample_idx].get('source', 'N/A')}")
        print(f"Chunk Index: {results['metadatas'][sample_idx].get('chunk_index', 'N/A')}")
        print("\nContent Preview:")
        content = results['documents'][sample_idx]
        print(content[:200] + "..." if len(content) > 200 else content)
        
        # Print storage location
        print("\nStorage Information:")
        print("-" * 30)
        chroma_dir = Path("pinecone_db")
        if chroma_dir.exists():
            print(f"ChromaDB Directory: {chroma_dir.absolute()}")
            print("\nDirectory Contents:")
            for item in chroma_dir.iterdir():
                if item.is_file():
                    print(f"File: {item.name} ({item.stat().st_size / 1024:.2f} KB)")
                else:
                    print(f"Directory: {item.name}")
        
        # Print collection statistics
        print("\nCollection Statistics:")
        print("-" * 30)
        sources = {}
        for metadata in results['metadatas']:
            source = metadata.get('source', 'N/A')
            sources[source] = sources.get(source, 0) + 1
        
        print("\nDocuments per source:")
        for source, count in sources.items():
            print(f"{Path(source).name}: {count} documents")
        
    except Exception as e:
        print(f"Error accessing ChromaDB: {str(e)}")
        print("Make sure you have processed documents using process_documents.py first.")

if __name__ == "__main__":
    inspect_chromadb()