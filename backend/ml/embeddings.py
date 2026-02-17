"""
ML Embeddings Module - Completely separate from your existing parser
Add this as a new file, does not affect working code
"""
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os
from typing import List, Dict, Any
import warnings
warnings.filterwarnings('ignore')

class ResumeEmbeddingModel:
    """ML-powered semantic analysis - OPTIONAL enhancement"""
    
    def __init__(self):
        """Initialize the ML model (lazy loading)"""
        self.model = None
        self.embedding_cache = {}
        self._model_loaded = False
    
    def _load_model(self):
        """Lazy load the model only when needed"""
        if not self._model_loaded:
            print("🔄 Loading ML model (first time only)...")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self._model_loaded = True
            print("✅ ML model loaded successfully!")
    
    def get_embedding(self, text: str) -> np.ndarray:
        """Convert text to vector embedding"""
        self._load_model()
        
        # Cache to avoid recomputing
        cache_key = hash(text[:500])  # Use first 500 chars as key
        if cache_key in self.embedding_cache:
            return self.embedding_cache[cache_key]
        
        embedding = self.model.encode(text[:5000])  # Limit text length
        self.embedding_cache[cache_key] = embedding
        return embedding
    
    def calculate_semantic_similarity(self, resume_text: str, job_text: str) -> float:
        """ML-powered semantic similarity - NOT affecting your keyword matching"""
        try:
            resume_emb = self.get_embedding(resume_text)
            job_emb = self.get_embedding(job_text)
            
            similarity = cosine_similarity([resume_emb], [job_emb])[0][0]
            return float(similarity)
        except Exception as e:
            print(f"ML similarity error: {e}")
            return 0.5  # Fallback
    
    def extract_key_phrases(self, text: str, top_k: int = 5) -> List[str]:
        """Extract important phrases using ML"""
        try:
            self._load_model()
            
            # Simple sentence splitting
            sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 30]
            if not sentences:
                return []
            
            # Get embeddings
            sent_embeddings = self.model.encode(sentences[:20])  # Limit for performance
            doc_embedding = self.get_embedding(text)
            
            # Calculate similarity
            scores = cosine_similarity([doc_embedding], sent_embeddings)[0]
            
            # Get top sentences
            top_indices = np.argsort(scores)[-top_k:][::-1]
            key_phrases = [sentences[i][:100] for i in top_indices]
            
            return key_phrases
        except Exception as e:
            print(f"Key phrase extraction error: {e}")
            return []

# Singleton instance - lazy loaded
_embedding_model = None

def get_embedding_model():
    """Get or create the embedding model singleton"""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = ResumeEmbeddingModel()
    return _embedding_model