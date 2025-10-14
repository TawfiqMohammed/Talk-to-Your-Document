"""
Embedding Service using FAISS
"""
from sentence_transformers import SentenceTransformer
from typing import List, Dict
import faiss
import numpy as np
import pickle
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import CHROMA_DIR, EMBEDDING_MODEL, TOP_K_RESULTS
from utils.chunking import chunk_text

class EmbeddingService:
    """Service for creating and managing embeddings with FAISS"""
    
    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        self.indexes = {}  # Store FAISS indexes per document
        self.metadata_store = {}  # Store metadata
        
        # Create directory for storing indexes
        os.makedirs(CHROMA_DIR, exist_ok=True)
    
    def create_embeddings(self, doc_id: str, text_chunks: List[Dict]) -> bool:
        """
        Create and store embeddings for document chunks
        """
        try:
            documents = []
            metadatas = []
            
            for idx, chunk in enumerate(text_chunks):
                # Further chunk large content
                sub_chunks = chunk_text(chunk['content'])
                
                for sub_idx, sub_chunk in enumerate(sub_chunks):
                    documents.append(sub_chunk)
                    metadatas.append({
                        "page": chunk['page'],
                        "chunk_id": idx,
                        "sub_chunk_id": sub_idx,
                        "content": sub_chunk
                    })
            
            # Create embeddings
            embeddings = self.model.encode(documents)
            embeddings = np.array(embeddings).astype('float32')
            
            # Create FAISS index
            dimension = embeddings.shape[1]
            index = faiss.IndexFlatL2(dimension)
            index.add(embeddings)
            
            # Store index and metadata
            self.indexes[doc_id] = index
            self.metadata_store[doc_id] = metadatas
            
            # Save to disk
            index_path = os.path.join(CHROMA_DIR, f"{doc_id}.index")
            metadata_path = os.path.join(CHROMA_DIR, f"{doc_id}.meta")
            
            faiss.write_index(index, index_path)
            with open(metadata_path, 'wb') as f:
                pickle.dump(metadatas, f)
            
            print(f"✅ Created {len(documents)} embeddings for {doc_id}")
            return True
            
        except Exception as e:
            print(f"❌ Embedding creation failed: {str(e)}")
            return False
    
    def retrieve_relevant_chunks(self, doc_id: str, query: str, top_k: int = TOP_K_RESULTS) -> List[Dict]:
        """
        Retrieve relevant chunks using semantic search
        """
        try:
            # Load index if not in memory
            if doc_id not in self.indexes:
                index_path = os.path.join(CHROMA_DIR, f"{doc_id}.index")
                metadata_path = os.path.join(CHROMA_DIR, f"{doc_id}.meta")
                
                if not os.path.exists(index_path):
                    print(f"❌ Index not found for {doc_id}")
                    return []
                
                self.indexes[doc_id] = faiss.read_index(index_path)
                with open(metadata_path, 'rb') as f:
                    self.metadata_store[doc_id] = pickle.load(f)
            
            # Encode query
            query_embedding = self.model.encode([query])
            query_embedding = np.array(query_embedding).astype('float32')
            
            # Search
            distances, indices = self.indexes[doc_id].search(query_embedding, top_k)
            
            # Build results
            relevant_chunks = []
            for idx, distance in zip(indices[0], distances[0]):
                if idx < len(self.metadata_store[doc_id]):
                    metadata = self.metadata_store[doc_id][idx]
                    relevant_chunks.append({
                        "content": metadata['content'],
                        "metadata": {
                            "page": metadata['page'],
                            "chunk_id": metadata['chunk_id']
                        },
                        "distance": float(distance),
                        "relevance": 1.0 / (1.0 + float(distance))  # Convert distance to relevance score
                    })
            
            return relevant_chunks
            
        except Exception as e:
            print(f"❌ Retrieval error: {str(e)}")
            return []
    
    def delete_collection(self, doc_id: str) -> bool:
        """
        Delete document embeddings
        """
        try:
            # Remove from memory
            if doc_id in self.indexes:
                del self.indexes[doc_id]
            if doc_id in self.metadata_store:
                del self.metadata_store[doc_id]
            
            # Delete files
            index_path = os.path.join(CHROMA_DIR, f"{doc_id}.index")
            metadata_path = os.path.join(CHROMA_DIR, f"{doc_id}.meta")
            
            if os.path.exists(index_path):
                os.remove(index_path)
            if os.path.exists(metadata_path):
                os.remove(metadata_path)
            
            return True
        except Exception as e:
            print(f"❌ Deletion failed: {str(e)}")
            return False