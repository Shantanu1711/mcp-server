from typing import List, Dict, Optional
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import json
import os

class DocumentSearchTool:
    def __init__(self, config: Dict):
        self.top_k = config.get("top_k", 3)
        self.similarity_threshold = config.get("similarity_threshold", 0.7)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Load FAISS index
        self.index_path = "embeddings/faiss_index"
        self.index = faiss.read_index(os.path.join(self.index_path, "index.faiss"))
        
        # Load document metadata
        with open(os.path.join(self.index_path, "metadata.json"), "r") as f:
            self.metadata = json.load(f)
    
    def search(self, query: str) -> List[Dict]:
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])[0]
        
        # Search in FAISS index
        distances, indices = self.index.search(
            np.array([query_embedding]).astype('float32'),
            self.top_k
        )
        
        # Format results
        results = []
        for distance, idx in zip(distances[0], indices[0]):
            if distance < self.similarity_threshold:
                doc_metadata = self.metadata[str(idx)]
                results.append({
                    "content": doc_metadata["content"],
                    "source": doc_metadata["source"],
                    "page": doc_metadata.get("page"),
                    "similarity_score": float(1 - distance)
                })
        
        return results
    
    def __call__(self, query: str) -> List[Dict]:
        return self.search(query) 