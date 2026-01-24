"""
Pinecone Vector Store for Silver Narratives.
Cloud-native persistent storage for Global RAG.
"""
import os
import time
from typing import List, Dict, Any
from pinecone import Pinecone, ServerlessSpec
from embeddings import LocalEmbeddings

class SilverVectorStore:
    """Pinecone-based vector store for silver narrative evidence."""
    
    def __init__(self, persist_directory: str = None):
        """Initialize Pinecone client."""
        self.api_key = os.getenv("PINECONE_API_KEY")
        if not self.api_key:
            print("⚠️ PINECONE_API_KEY missing. Vector store usage will fail.")
            self.pc = None
            return

        print("🔄 Connecting to Pinecone...")
        self.pc = Pinecone(api_key=self.api_key)
        self.index_name = "silver-sentinel"
        
        # Check/Create Index
        try:
            existing_indexes = [i.name for i in self.pc.list_indexes()]
            if self.index_name not in existing_indexes:
                print(f"Creating Pinecone Index: {self.index_name} (Dim: 384)...")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=384, # sentence-transformers/all-MiniLM-L6-v2
                    metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region="us-east-1")
                )
                time.sleep(15) # Allow initialization
        except Exception as e:
            print(f"⚠️ Index Check Failed (Likely Exists): {e}")

        self.index = self.pc.Index(self.index_name)
        self.embeddings = LocalEmbeddings()
        print("✅ Pinecone Vector Store Initialized.")
    
    def add_documents(
        self, 
        texts: List[str], 
        metadatas: List[Dict[str, Any]], 
        ids: List[str]
    ):
        """Add documents to Pinecone."""
        if not self.pc: return
        
        # Generate Embeddings
        embeddings = self.embeddings.embed_documents(texts)
        
        vectors = []
        for i, text in enumerate(texts):
            # Pinecone metadata values must be strings, numbers, booleans, or list of strings
            # Ensure text is stored in metadata for retrieval
            clean_meta = {k: v for k, v in metadatas[i].items() if v is not None}
            clean_meta['text'] = text  # Critical for RAG retrieval
            
            vectors.append({
                "id": ids[i],
                "values": embeddings[i],
                "metadata": clean_meta
            })
        
        # Batch Upsert
        batch_size = 50
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i+batch_size]
            try:
                self.index.upsert(vectors=batch)
            except Exception as e:
                print(f"Batch Upsert Error: {e}")
                
        print(f"✅ Uploaded {len(texts)} documents to Pinecone.")
    
    def search(
        self, 
        query: str, 
        n_results: int = 5,
        filter_dict: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Search Pinecone."""
        if not self.pc: return []
        
        query_vec = self.embeddings.embed_query(query)
        
        try:
            res = self.index.query(
                vector=query_vec,
                top_k=n_results,
                include_metadata=True,
                filter=filter_dict
            )
            
            formatted = []
            for match in res['matches']:
                if match and match.get('metadata'):
                    formatted.append({
                        'id': match['id'],
                        'text': match['metadata'].get('text', ''),
                        'metadata': match['metadata'],
                        'distance': match['score'] # Pinecone returns score (cosine similarity)
                    })
            return formatted
        except Exception as e:
            print(f"Search Error: {e}")
            return []
    
    def get_by_narrative_id(self, narrative_id: str) -> List[Dict[str, Any]]:
        """Retrieve context by narrative_id (using filtered query)."""
        # Since Pinecone isn't a relational DB, we assume 'silver' is relevant to all docs
        # and filter strictly by narrative_id.
        return self.search("silver market context", n_results=50, filter_dict={"narrative_id": narrative_id})
    
    def reset(self):
        """Wipe index."""
        if self.pc:
            try:
                self.index.delete(delete_all=True)
                print("⚠️ Pinecone Index Wiped.")
            except Exception as e:
                print(f"Reset Error: {e}")
