"""
GovMind AI Module - OPTIMIZED Policy Retriever
Key optimization: Accept pre-computed embeddings for vector search
"""

from typing import List, Dict, Optional
import numpy as np
from loguru import logger
import config
from vector_store import get_vector_store


class OptimizedPolicyRetriever:
    """
    Optimized retriever that accepts pre-computed embeddings.
    Eliminates redundant embedding generation and vector searches.
    """
    
    def __init__(self):
        """Initialize policy retriever"""
        logger.info("Initializing Optimized Policy Retriever")
        
        self.vector_store = get_vector_store()
        self.top_k = config.TOP_K_POLICIES
        
        logger.success("Policy Retriever ready")
    
    def retrieve_policies_with_embedding(self,
                                        complaint_embedding: np.ndarray,
                                        department_filter: Optional[str] = None,
                                        top_k: Optional[int] = None) -> List[Dict[str, any]]:
        """
        OPTIMIZED: Retrieve policies using pre-computed embedding.
        This eliminates redundant embedding generation!
        
        Args:
            complaint_embedding: Pre-computed embedding vector
            department_filter: Optional department filter
            top_k: Number of policies to retrieve
            
        Returns:
            List of policy documents
        """
        if top_k is None:
            top_k = self.top_k
        
        logger.info(f"Retrieving {top_k} policies with pre-computed embedding")
        
        # Prepare filter
        filter_metadata = None
        if department_filter:
            filter_metadata = {"department": department_filter}
        
        # Query vector store with pre-computed embedding
        documents, similarities, metadatas = self.vector_store.query_similar_with_embedding(
            query_embedding=complaint_embedding,
            top_k=top_k,
            filter_metadata=filter_metadata
        )
        
        # Format results
        policies = []
        for doc, sim, meta in zip(documents, similarities, metadatas):
            policy = {
                "text": doc,
                "relevance_score": sim,
                "department": meta.get("department", "unknown"),
                "category": meta.get("category", "general"),
                "priority": meta.get("priority", "medium"),
                "metadata": meta
            }
            policies.append(policy)
        
        logger.info(f"Retrieved {len(policies)} policies")
        
        return policies
    
    def retrieve_policies(self, complaint_text: str,
                         department_filter: Optional[str] = None,
                         top_k: Optional[int] = None) -> List[Dict[str, any]]:
        """
        Backward compatibility: Generate embedding if needed.
        Use retrieve_policies_with_embedding() when possible!
        
        Args:
            complaint_text: Complaint text
            department_filter: Optional department filter
            top_k: Number of policies
            
        Returns:
            List of policies
        """
        from embedding_model import get_embedding_model
        
        # Generate embedding (avoid if possible!)
        emb_model = get_embedding_model()
        complaint_embedding = emb_model.encode_complaint(complaint_text)
        
        # Use optimized method
        return self.retrieve_policies_with_embedding(
            complaint_embedding,
            department_filter,
            top_k
        )
    
    def get_policy_context(self, complaint_text: str,
                          primary_department: str,
                          include_related: bool = False) -> str:
        """
        DEPRECATED: This method causes redundant searches.
        Use routing_engine's compact context builder instead.
        
        Kept for backward compatibility only.
        """
        logger.warning("get_policy_context() is deprecated - causes redundant searches")
        
        policies = self.retrieve_policies(
            complaint_text=complaint_text,
            department_filter=primary_department,
            top_k=2
        )
        
        context_parts = [f"=== {primary_department.upper()} Policies ==="]
        
        for i, policy in enumerate(policies, 1):
            context_parts.append(f"\nPolicy {i}: {policy['text'][:150]}...")
        
        return "\n".join(context_parts)
    
    def get_priority_indicators(self, complaint_text: str,
                               retrieved_policies: List[Dict]) -> Dict[str, any]:
        """
        Fast priority analysis using keywords only.
        No external calls or heavy computation.
        
        Args:
            complaint_text: Complaint text
            retrieved_policies: Already retrieved policies
            
        Returns:
            Priority analysis
        """
        complaint_lower = complaint_text.lower()
        
        # Fast keyword matching
        high_matches = [kw for kw in config.PRIORITY_KEYWORDS['high'] 
                       if kw in complaint_lower]
        
        medium_matches = [kw for kw in config.PRIORITY_KEYWORDS['medium']
                         if kw in complaint_lower]
        
        # Check policy priorities
        high_priority_policies = sum(1 for p in retrieved_policies 
                                    if p.get('priority') == 'high')
        
        # Decide priority
        if high_matches or high_priority_policies >= 2:
            priority = "High"
            reason = "Emergency keywords or critical policies detected"
        elif medium_matches:
            priority = "Medium"
            reason = "Significant issue requiring attention"
        else:
            priority = "Medium"
            reason = "Standard priority"
        
        return {
            "suggested_priority": priority,
            "reasoning": reason,
            "high_priority_keywords": high_matches,
            "medium_priority_keywords": medium_matches,
            "high_priority_policies_count": high_priority_policies
        }
    
    def get_relevant_categories(self, complaint_text: str, 
                               top_k: int = 5) -> List[str]:
        """Get relevant categories"""
        policies = self.retrieve_policies(complaint_text, top_k=top_k)
        
        categories = []
        seen = set()
        for p in policies:
            cat = p['category']
            if cat not in seen:
                categories.append(cat)
                seen.add(cat)
        
        return categories


# Global singleton
_policy_retriever_instance = None


def get_policy_retriever() -> OptimizedPolicyRetriever:
    """Get singleton instance"""
    global _policy_retriever_instance
    
    if _policy_retriever_instance is None:
        _policy_retriever_instance = OptimizedPolicyRetriever()
    
    return _policy_retriever_instance


if __name__ == "__main__":
    from loguru import logger
    logger.add("logs/optimized_retriever_test.log", rotation="1 MB")
    
    from vector_store import initialize_sample_policies
    try:
        initialize_sample_policies()
    except:
        pass
    
    retriever = get_policy_retriever()
    
    print("\n" + "="*80)
    print("OPTIMIZED POLICY RETRIEVER TEST")
    print("="*80)
    
    complaint = "Power outage affecting hospital"
    
    # Method 1: Direct retrieval (generates embedding)
    print("\n1. Direct Retrieval (backward compatible):")
    import time
    start = time.time()
    policies1 = retriever.retrieve_policies(complaint, department_filter="electricity", top_k=3)
    time1 = time.time() - start
    print(f"   Time: {time1:.3f}s")
    print(f"   Retrieved: {len(policies1)} policies")
    
    # Method 2: With pre-computed embedding (OPTIMIZED)
    print("\n2. With Pre-computed Embedding (OPTIMIZED):")
    from embedding_model import get_embedding_model
    emb_model = get_embedding_model()
    
    start = time.time()
    embedding = emb_model.encode_complaint(complaint)
    emb_time = time.time() - start
    
    start = time.time()
    policies2 = retriever.retrieve_policies_with_embedding(
        embedding, 
        department_filter="electricity", 
        top_k=3
    )
    retrieval_time = time.time() - start
    
    print(f"   Embedding time: {emb_time:.3f}s")
    print(f"   Retrieval time: {retrieval_time:.3f}s")
    print(f"   Total: {emb_time + retrieval_time:.3f}s")
    print(f"   Retrieved: {len(policies2)} policies")
    
    print("\n" + "="*80)
    print("✓ Key Optimization: Single embedding for multiple operations")
    print("="*80)
