"""
GovMind AI Module - OPTIMIZED Department Classifier
Key optimization: Accept pre-computed embeddings to avoid re-computation
"""

from typing import Dict, List
import numpy as np
from loguru import logger
import config
from embedding_model import get_embedding_model


class OptimizedDepartmentClassifier:
    """
    Optimized classifier that can work with pre-computed embeddings.
    Eliminates redundant embedding generation.
    """
    
    def __init__(self):
        """Initialize classifier"""
        logger.info("Initializing Optimized Department Classifier")
        
        self.departments = config.DEPARTMENTS
        self.embedding_model = get_embedding_model()
        self.similarity_threshold = config.SIMILARITY_THRESHOLD
        
        # Pre-compute department embeddings ONCE
        self._initialize_department_embeddings()
        
        logger.success(f"Classifier ready with {len(self.departments)} departments")
    
    def _initialize_department_embeddings(self):
        """Pre-compute department embeddings once during initialization"""
        logger.info("Pre-computing department embeddings")
        
        self.department_ids = list(self.departments.keys())
        
        descriptions = []
        for dept_id in self.department_ids:
            dept = self.departments[dept_id]
            full_desc = f"{dept['name']}. {dept['description']}. {', '.join(dept['keywords'])}"
            descriptions.append(full_desc)
        
        self.department_embeddings = self.embedding_model.encode_documents(descriptions)
        logger.debug(f"Department embeddings shape: {self.department_embeddings.shape}")
    
    def classify_with_embedding(self, 
                               complaint_embedding: np.ndarray,
                               complaint_text: str = None,
                               return_top_k: int = 3) -> List[Dict[str, any]]:
        """
        OPTIMIZED: Classify using pre-computed embedding.
        This is the key optimization - no re-computation!
        
        Args:
            complaint_embedding: Pre-computed embedding vector
            complaint_text: Optional text for keyword matching
            return_top_k: Number of results
            
        Returns:
            List of department matches
        """
        logger.info("Classifying with pre-computed embedding")
        
        # Calculate similarities using existing embedding
        similarities = self.embedding_model.batch_similarity(
            complaint_embedding,
            self.department_embeddings
        )
        
        # Keyword boost if text provided
        if complaint_text:
            similarities = self._apply_keyword_boost(
                similarities,
                complaint_text.lower()
            )
        
        # Sort and format results
        sorted_indices = np.argsort(similarities)[::-1]
        
        results = []
        for idx in sorted_indices[:return_top_k]:
            dept_id = self.department_ids[idx]
            dept_name = self.departments[dept_id]['name']
            similarity = float(similarities[idx])
            
            # Confidence level
            if similarity >= 0.75:
                confidence = "high"
            elif similarity >= 0.60:
                confidence = "medium"
            else:
                confidence = "low"
            
            results.append({
                "department_id": dept_id,
                "department_name": dept_name,
                "similarity": similarity,
                "confidence": confidence,
                "description": self.departments[dept_id]['description']
            })
        
        logger.info(f"Top match: {results[0]['department_name']} ({results[0]['similarity']:.3f})")
        
        return results
    
    def _apply_keyword_boost(self, similarities: np.ndarray, 
                            complaint_lower: str) -> np.ndarray:
        """
        Apply keyword matching boost to similarity scores.
        Lightweight operation, no heavy computation.
        
        Args:
            similarities: Base similarity scores
            complaint_lower: Lowercase complaint text
            
        Returns:
            Boosted similarity scores
        """
        boosted = similarities.copy()
        
        for i, dept_id in enumerate(self.department_ids):
            keywords = self.departments[dept_id]['keywords']
            
            # Count keyword matches
            matches = sum(1 for kw in keywords if kw in complaint_lower)
            
            if matches > 0:
                # Boost: 5% per keyword match, max 30%
                boost = min(0.05 * matches, 0.30)
                boosted[i] = min(boosted[i] * (1 + boost), 1.0)
        
        return boosted
    
    def classify(self, complaint_text: str, 
                 return_top_k: int = 3) -> List[Dict[str, any]]:
        """
        Backward compatibility: Generate embedding if not provided.
        Use classify_with_embedding() when possible to avoid this.
        
        Args:
            complaint_text: Complaint text
            return_top_k: Number of results
            
        Returns:
            List of department matches
        """
        # Generate embedding
        complaint_embedding = self.embedding_model.encode_complaint(complaint_text)
        
        # Use optimized method
        return self.classify_with_embedding(
            complaint_embedding,
            complaint_text,
            return_top_k
        )
    
    def get_primary_department(self, complaint_text: str) -> Dict[str, any]:
        """Get single best match"""
        results = self.classify(complaint_text, return_top_k=1)
        return results[0]
    
    def classify_with_keywords(self, complaint_text: str) -> Dict[str, any]:
        """
        DEPRECATED: Use classify_with_embedding() instead.
        Kept for backward compatibility.
        """
        return self.classify(complaint_text, return_top_k=1)[0]


# Global singleton
_classifier_instance = None


def get_classifier() -> OptimizedDepartmentClassifier:
    """Get singleton instance"""
    global _classifier_instance
    
    if _classifier_instance is None:
        _classifier_instance = OptimizedDepartmentClassifier()
    
    return _classifier_instance


if __name__ == "__main__":
    from loguru import logger
    logger.add("logs/optimized_classifier_test.log", rotation="1 MB")
    
    classifier = get_classifier()
    
    # Test with pre-computed embedding (FAST)
    print("\n" + "="*80)
    print("OPTIMIZED CLASSIFIER TEST")
    print("="*80)
    
    complaint = "Power outage in my area"
    
    # Method 1: Direct classification (generates embedding)
    print("\n1. Direct Classification (backward compatible):")
    import time
    start = time.time()
    result1 = classifier.classify(complaint, return_top_k=3)
    time1 = time.time() - start
    print(f"   Time: {time1:.3f}s")
    print(f"   Top: {result1[0]['department_name']} ({result1[0]['similarity']:.3f})")
    
    # Method 2: With pre-computed embedding (OPTIMIZED)
    print("\n2. With Pre-computed Embedding (OPTIMIZED):")
    from embedding_model import get_embedding_model
    emb_model = get_embedding_model()
    
    start = time.time()
    embedding = emb_model.encode_complaint(complaint)
    emb_time = time.time() - start
    
    start = time.time()
    result2 = classifier.classify_with_embedding(embedding, complaint, return_top_k=3)
    class_time = time.time() - start
    
    print(f"   Embedding time: {emb_time:.3f}s")
    print(f"   Classification time: {class_time:.3f}s")
    print(f"   Total: {emb_time + class_time:.3f}s")
    print(f"   Top: {result2[0]['department_name']} ({result2[0]['similarity']:.3f})")
    
    print("\n" + "="*80)
    print("✓ Key Optimization: Reuse embedding instead of regenerating")
    print("="*80)
