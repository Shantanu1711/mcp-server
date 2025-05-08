import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec

# Load environment variables
load_dotenv()

# Initialize Pinecone
pinecone_api_key = os.getenv("PINECONE_API_KEY")
if not pinecone_api_key:
    raise ValueError("Pinecone API key not found in environment variables")

pinecone_instance = Pinecone(api_key=pinecone_api_key)

index_name = "documents"
if index_name not in pinecone_instance.list_indexes().names():
    pinecone_instance.create_index(
        name=index_name,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
    print(f"Created index '{index_name}'")
else:
    print(f"Index '{index_name}' already exists")

index = pinecone_instance.Index(index_name)

# Initialize Sentence Transformer
model = SentenceTransformer('all-MiniLM-L6-v2')

# Define a tiny test chunk
test_chunk = "This is a small test chunk to verify Pinecone is storing data correctly."

# Generate embedding
embedding = model.encode(test_chunk).tolist()

# Create metadata
metadata = {
    "source": "test_manual",
    "chunk_index": 0,
    "chunk_text": test_chunk
}

# Define a unique ID for this test
doc_id = "test_chunk_001"

# Upsert into Pinecone
print(f"Upserting test chunk with ID '{doc_id}'...")
index.upsert([(doc_id, embedding, metadata)])
print("Upsert completed.")

# Verify by querying it back
query_response = index.query(
    vector=embedding,
    top_k=1,
    include_metadata=True
)

matches = query_response.get('matches', [])
if not matches:
    print("No vectors found after upsert. Something went wrong.")
else:
    print("\n✅ Successfully retrieved the stored vector:")
    for match in matches:
        print(f"ID: {match['id']}")
        print(f"Metadata: {match.get('metadata')}")
        print(f"Score: {match.get('score')}")

do_cleanup = True  # Set to False if you want to keep it

if do_cleanup:
    print("\nCleaning up the test vector...")
    index.delete(ids=[doc_id])
    print("Test vector deleted.")
else:
    print("\nTest vector is kept in Pinecone (no cleanup).")
