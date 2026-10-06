"""
GovMind AI Module - Embedding Model
Handles text-to-vector conversion using Sentence Transformers
Supports multilingual text (Tamil + English)
"""

from sentence_transformers import SentenceTransformer
from typing import List, Union
import numpy as np
from loguru import logger
import config


class EmbeddingModel:
    """
    Wrapper for Sentence Transformer model to generate embeddings
    Uses multilingual-e5-large for Tamil + English support
    """
    
    def __init__(self, model_name: str = config.EMBEDDING_MODEL):
        """
        Initialize the embedding model
        
        Args:
            model_name: HuggingFace model identifier
        """
        logger.info(f"Loading embedding model: {model_name}")
        try:
            self.model = SentenceTransformer(model_name)
            self.model_name = model_name
            self.embedding_dimension = config.EMBEDDING_DIMENSION
            logger.success(f"Embedding model loaded successfully (dim={self.embedding_dimension})")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    def encode_text(self, text: Union[str, List[str]], normalize: bool = True) -> np.ndarray:
        """
        Convert text to embedding vector(s)
        
        Args:
            text: Single text string or list of texts
            normalize: Whether to normalize embeddings (for cosine similarity)
            
        Returns:
            numpy array of embeddings
        """
        try:
            if isinstance(text, str):
                text = [text]
            
            # For multilingual-e5 models, add query prefix
            if "e5" in self.model_name.lower():
                text = [f"query: {t}" for t in text]
            
            logger.debug(f"Encoding {len(text)} text(s)")
            embeddings = self.model.encode(
                text,
                normalize_embeddings=normalize,
                show_progress_bar=False,
                batch_size=32
            )
            
            logger.debug(f"Generated embeddings with shape: {embeddings.shape}")
            return embeddings
            
        except Exception as e:
            logger.error(f"Encoding failed: {e}")
            raise
    
    def encode_complaint(self, complaint_text: str) -> np.ndarray:
        """
        Generate embedding for a citizen complaint
        
        Args:
            complaint_text: The grievance text
            
        Returns:
            Embedding vector as 1D numpy array
        """
        logger.info("Encoding complaint text")
        embedding = self.encode_text(complaint_text, normalize=True)
        
        # Ensure 1D array output
        if embedding.ndim > 1:
            embedding = embedding.flatten()
        
        return embedding
    
    def encode_documents(self, documents: List[str]) -> np.ndarray:
        """
        Generate embeddings for multiple documents (e.g., department descriptions)
        
        Args:
            documents: List of text documents
            
        Returns:
            Matrix of embeddings
        """
        # For multilingual-e5, use passage prefix for documents
        if "e5" in self.model_name.lower():
            documents = [f"passage: {doc}" for doc in documents]
        
        logger.info(f"Encoding {len(documents)} documents")
        embeddings = self.model.encode(
            documents,
            normalize_embeddings=True,
            show_progress_bar=False,
            batch_size=32
        )
        return embeddings
    
    def get_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score between -1 and 1
        """
        # Handle both 1D and 2D arrays
        if embedding1.ndim == 1:
            embedding1 = embedding1.reshape(1, -1)
        if embedding2.ndim == 1:
            embedding2 = embedding2.reshape(1, -1)
        
        similarity = np.dot(embedding1, embedding2.T)
        return float(similarity[0][0])
    
    def batch_similarity(self, query_embedding: np.ndarray, 
                        document_embeddings: np.ndarray) -> np.ndarray:
        """
        Calculate similarity between one query and multiple documents
        
        Args:
            query_embedding: Single query embedding
            document_embeddings: Matrix of document embeddings
            
        Returns:
            Array of similarity scores
        """
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
        
        similarities = np.dot(query_embedding, document_embeddings.T)
        return similarities.flatten()


# Global singleton instance
_embedding_model_instance = None


def get_embedding_model() -> EmbeddingModel:
    """
    Get or create the global embedding model instance
    Singleton pattern to avoid loading model multiple times
    """
    global _embedding_model_instance
    
    if _embedding_model_instance is None:
        _embedding_model_instance = EmbeddingModel()
    
    return _embedding_model_instance


if __name__ == "__main__":
    # Test the embedding model
    from loguru import logger
    logger.add("logs/embedding_test.log", rotation="1 MB")
    
    model = get_embedding_model()
    
    # Test English complaint
    english_complaint = "There is no electricity in my area for the past 3 hours"
    eng_embedding = model.encode_complaint(english_complaint)
    print(f"English embedding shape: {eng_embedding.shape}")
    
    # Test Tamil complaint
    tamil_complaint = "எங்கள் பகுதியில் தண்ணீர் வருவதில்லை"
    tamil_embedding = model.encode_complaint(tamil_complaint)
    print(f"Tamil embedding shape: {tamil_embedding.shape}")
    
    # Test similarity
    similarity = model.get_similarity(eng_embedding, tamil_embedding)
    print(f"Similarity between different topics: {similarity:.4f}")
    
    # Test similar complaints
    similar_complaint = "Power outage in our locality since morning"
    similar_embedding = model.encode_complaint(similar_complaint)
    similarity = model.get_similarity(eng_embedding, similar_embedding)
    print(f"Similarity between similar topics: {similarity:.4f}")
