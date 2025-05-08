from sentence_transformers import SentenceTransformer
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize sentence transformer
model = SentenceTransformer('all-MiniLM-L6-v2')

def create_and_save_single_embedding(text, save_directory="pinecone_db"):
    """Create a single embedding and save it to a file."""
    # Ensure the save directory exists
    os.makedirs(save_directory, exist_ok=True)

    # Generate embedding
    embedding = model.encode(text).tolist()

    # Save embedding to a JSON file
    file_path = os.path.join(save_directory, "single_embedding.json")
    with open(file_path, "w") as f:
        json.dump({"text": text, "embedding": embedding}, f)

    print(f"Embedding saved to {file_path}")

if __name__ == "__main__":
    # Example text for testing
    sample_text = "This is a test embedding to verify the flow."

    # Generate and save a single embedding
    create_and_save_single_embedding(sample_text)