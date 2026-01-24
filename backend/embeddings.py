"""
Local Embeddings using SentenceTransformers.
NO OpenAI dependencies.
"""
import os
from typing import List
from sentence_transformers import SentenceTransformer
import numpy as np


class LocalEmbeddings:
    """Wrapper for SentenceTransformer embeddings."""
    
    def __init__(self, model_name: str = None):
        """
        Initialize local embeddings model.
        
        Args:
            model_name: SentenceTransformer model name
        """
        self.model_name = model_name or os.getenv(
            "EMBEDDING_MODEL", 
            "sentence-transformers/all-MiniLM-L6-v2"
        )
        print(f"Loading local embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        print("Embedding model loaded successfully")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a list of documents.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        embeddings = self.model.encode(texts, show_progress_bar=False)
        return embeddings.tolist()
    
    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single query.
        
        Args:
            text: Query text to embed
            
        Returns:
            Embedding vector
        """
        embedding = self.model.encode([text], show_progress_bar=False)[0]
        return embedding.tolist()
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Compute cosine similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Cosine similarity score (0-1)
        """
        emb1 = np.array(self.embed_query(text1))
        emb2 = np.array(self.embed_query(text2))
        
        # Cosine similarity
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        return float(similarity)
