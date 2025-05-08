from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Pinecone instance
pinecone_api_key = os.getenv("PINECONE_API_KEY")
if not pinecone_api_key:
    raise ValueError("Pinecone API key not found in environment variables")

pinecone_instance = Pinecone(api_key=pinecone_api_key)

# Example: Create an index if it doesn't exist
collection_name = "test_documents"
if collection_name not in pinecone_instance.list_indexes().names():
    pinecone_instance.create_index(
        name=collection_name,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

index = pinecone_instance.Index(collection_name)

# Initialize sentence transformer
model = SentenceTransformer('all-MiniLM-L6-v2')

def test_upsert_single_embedding():
    """Test upserting a single embedding into Pinecone."""
    # Example text
    sample_text = "This is a test embedding to verify the upsert functionality."

    # Generate embedding
    embedding = model.encode(sample_text).tolist()

    # Metadata for the embedding
    metadata = {"source": "test_script", "description": "Test embedding"}

    # Upsert the embedding into Pinecone
    try:
        index.upsert([("test_id_1", embedding, metadata)])
        print("Upsert successful! Check your Pinecone dashboard for the test index.")
    except Exception as e:
        print(f"Error during upsert: {str(e)}")

if __name__ == "__main__":
    test_upsert_single_embedding()