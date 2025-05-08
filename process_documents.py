import os
from PyPDF2 import PdfReader
import logging
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def extract_text_from_txt(txt_path: str) -> str:
    """Extract text from a TXT file."""
    try:
        with open(txt_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        logger.error(f"Error processing TXT {txt_path}: {str(e)}")
        return ""

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a PDF file."""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PdfReader(file)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text
    except Exception as e:
        logger.error(f"Error processing PDF {pdf_path}: {str(e)}")
        return ""

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap

    return chunks

# Initialize Pinecone instance
pinecone_api_key = os.getenv("PINECONE_API_KEY")
if not pinecone_api_key:
    raise ValueError("Pinecone API key not found in environment variables")

pinecone_instance = Pinecone(api_key=pinecone_api_key)

# Example: Create an index if it doesn't exist
collection_name = "documents"
if collection_name not in pinecone_instance.list_indexes().names():
    pinecone_instance.create_index(
        name=collection_name,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
    logger.info(f"Created new index '{collection_name}'")
else:
    logger.info(f"Index '{collection_name}' already exists")

index = pinecone_instance.Index(collection_name)

# Initialize sentence transformer
model = SentenceTransformer('all-MiniLM-L6-v2')

def process_documents(pdf_directories: list, collection_name: str = "documents"):
    """Process PDFs from multiple directories and store them in Pinecone."""
    logger.info("Starting document processing...")

    for directory in pdf_directories:
        logger.info(f"Processing directory: {directory}")

        # Get all PDF and text files
        document_paths = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(('.pdf', '.txt')):
                    document_paths.append(os.path.join(root, file))

        logger.info(f"Found {len(document_paths)} documents in {directory}")

        # Process each document
        for path in document_paths:
            logger.info(f"Processing document: {path}")

            # Extract text
            if path.endswith('.pdf'):
                text = extract_text_from_pdf(path)
            elif path.endswith('.txt'):
                text = extract_text_from_txt(path)
            else:
                logger.warning(f"Unsupported file type: {path}")
                continue

            if not text:
                logger.warning(f"No text extracted from {path}, skipping...")
                continue

            # Chunk text
            chunks = chunk_text(text)
            logger.info(f"Created {len(chunks)} chunks from {path}")

            # Create embeddings and store in Pinecone
            for i, chunk in enumerate(chunks):
                try:
                    embedding = model.encode(chunk).tolist()

                    metadata = {
                        "source": path,
                        "chunk_index": i,
                        "chunk_text": chunk  # ✅ Added actual chunk text
                    }
                    doc_id = f"{os.path.basename(path)}_{i}"

                    index.upsert([(doc_id, embedding, metadata)])
                    logger.info(f"Upserted chunk {i} for document {path}")

                except Exception as e:
                    logger.error(f"Error storing chunk {i} from {path}: {str(e)}")

            logger.info(f"Finished processing {path}")

if __name__ == "__main__":
    # Define directories to process
    pdf_directories = [
        "docs/insurance",
        "docs/Insurance PDFs",
        "docs/angelone"
    ]
    
    process_documents(pdf_directories)
    logger.info("Document processing completed!")
