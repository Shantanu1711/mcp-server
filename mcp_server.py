from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import requests
import yaml
import traceback
from pinecone import Pinecone, ServerlessSpec

print("Starting server initialization...")

# Load environment variables
load_dotenv()
print("Environment variables loaded")

# Load configuration
try:
    with open("mcp/mcp.yaml", "r") as f:
        config = yaml.safe_load(f)
    print("Configuration loaded successfully")
except Exception as e:
    print(f"Error loading configuration: {str(e)}")
    raise

# Initialize Hugging Face API
HF_API_KEY = os.getenv("HF_API_KEY")
if not HF_API_KEY:
    raise ValueError("Hugging Face API key not found in environment variables")

print("Hugging Face API key loaded")

# Initialize sentence transformer for embeddings
try:
    print("Initializing sentence transformer...")
    embedding_model_name = config["vector_store"]["embedding_model"]
    print(f"Embedding model: {embedding_model_name}")
    model = SentenceTransformer(embedding_model_name)
    print("Sentence transformer initialized successfully")
except Exception as e:
    print(f"Error initializing sentence transformer: {str(e)}")
    raise

# Initialize Pinecone instance
pinecone_api_key = os.getenv("PINECONE_API_KEY")
if not pinecone_api_key:
    raise ValueError("Pinecone API key not found in environment variables")

pinecone_instance = Pinecone(api_key=pinecone_api_key)

# Create an index if it doesn't exist
collection_name = "documents"
if collection_name not in pinecone_instance.list_indexes().names():
    pinecone_instance.create_index(
        name=collection_name,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
    print(f"Index '{collection_name}' created successfully.")
else:
    print(f"Index '{collection_name}' already exists.")

index = pinecone_instance.Index(collection_name)

# FastAPI app
app = FastAPI()

# Hugging Face API setup
API_URL = f"{config['model']['inference_endpoint']}{config['model']['model']}"
headers = {"Authorization": f"Bearer {HF_API_KEY}"}


class Query(BaseModel):
    text: str
    k: Optional[int] = 3


class Document(BaseModel):
    content: str
    metadata: Optional[dict] = None


class RetrieverTool:
    def __init__(self):
        self.description = "Retrieves relevant documents from the vector database"
        self.input_schema = {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "k": {"type": "integer", "default": 3}
            }
        }
        self.collection = index

    def call(self, query: str, k: int = 3) -> List[Document]:
        try:
            query_embedding = model.encode(query)
            results = self.collection.query(
                vector=query_embedding.tolist(),
                top_k=k,
                include_metadata=True
            )

            documents = []
            matches = results.get("matches", [])
            if matches:
                for match in matches:
                    metadata = match.get("metadata", {})
                    content = metadata.get("chunk_text", "No content found")
                    documents.append(Document(content=content, metadata=metadata))

            return documents

        except Exception as e:
            print(f"Error in RetrieverTool: {str(e)}")
            print(traceback.format_exc())
            raise


def check_relevance(context: str, question: str) -> bool:
    relevance_prompt = f"""
Is the following question relevant to the context below? Answer only YES or NO.

Context:
{context}

Question:
{question}
"""
    payload = {
        "inputs": relevance_prompt,
        "parameters": {
            "max_new_tokens": 10,
            "temperature": 0.0  # deterministic response
        }
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        response_data = response.json()
        print("Relevance check response:", response_data)

        if isinstance(response_data, list) and len(response_data) > 0:
            generated_text = response_data[0].get("generated_text", "").strip().lower()
        elif isinstance(response_data, dict):
            generated_text = response_data.get("generated_text", "").strip().lower()
        else:
            print("Unexpected response format for relevance check.")
            return False

        if "yes" in generated_text:
            return True
        else:
            return False

    except Exception as e:
        print(f"Error during relevance check: {str(e)}")
        return True  # fallback: allow if relevance check fails


# Initialize tools
retriever_tool = RetrieverTool()


@app.post("/chat")
async def chat(query: Query):
    try:
        # Retrieve relevant documents
        documents = retriever_tool.call(query.text, query.k)

        if not documents:
            return {"response": "I couldn't find relevant information. Please clarify your question."}

        # Prepare context from documents
        context = "\n\n".join([doc.content for doc in documents])

        # Step 1: Check relevance first
        is_relevant = check_relevance(context, query.text)

        if not is_relevant:
            return {"response": "Your question doesn't seem related to the document content. Please clarify your question."}

        # Step 2: If relevant, proceed to answer the question
        prompt = f"""Context information is below.
---------------------
{context}
---------------------
Given the context information, please answer the following question. If you cannot find the answer in the context, say "I don't know."

Question: {query.text}"""

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": config['model']['max_tokens'],
                "temperature": config['model']['temperature'],
                "top_p": 0.95,
                "do_sample": True
            }
        }

        try:
            response = requests.post(API_URL, headers=headers, json=payload, stream=False)
            response.raise_for_status()
            response_data = response.json()

            print("API Response:", response_data)

            if isinstance(response_data, list) and len(response_data) > 0:
                if "generated_text" in response_data[0]:
                    generated_text = response_data[0]["generated_text"]
                    if generated_text.startswith(prompt):
                        generated_text = generated_text.replace(prompt, "").strip()
                    return {"response": generated_text}
                else:
                    return {"response": str(response_data[0])}
            elif isinstance(response_data, dict) and "generated_text" in response_data:
                generated_text = response_data["generated_text"]
                if generated_text.startswith(prompt):
                    generated_text = generated_text.replace(prompt, "").strip()
                return {"response": generated_text}
            else:
                return {"response": str(response_data)}

        except requests.exceptions.RequestException as e:
            error_msg = f"Error calling Hugging Face API: {str(e)}"
            if hasattr(e.response, 'text'):
                error_msg += f"\nAPI Response: {e.response.text}"
            print(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)

    except Exception as e:
        error_msg = f"Error processing request: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    print("Starting FastAPI server...")
    import uvicorn
    uvicorn.run(app, host=config["server"]["host"], port=config["server"]["port"])
