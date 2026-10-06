"""
GovMind AI Module - OPTIMIZED Vector Store
Added method to query with pre-computed embeddings
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional, Tuple
import numpy as np
from loguru import logger
import config
from embedding_model import get_embedding_model


class OptimizedVectorStore:
    """
    ChromaDB wrapper with optimized query methods.
    Supports pre-computed embeddings to avoid redundant generation.
    """
    
    def __init__(self, persist_directory: str = config.CHROMA_PERSIST_DIR,
                 collection_name: str = config.CHROMA_COLLECTION_NAME):
        """Initialize ChromaDB"""
        logger.info(f"Initializing ChromaDB at: {persist_directory}")
        
        try:
            self.client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            self.collection_name = collection_name
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"description": "GovMind policy documents"}
            )
            
            self.embedding_model = get_embedding_model()
            
            logger.success(f"ChromaDB ready: {self.collection.count()} documents")
            
        except Exception as e:
            logger.error(f"ChromaDB init failed: {e}")
            raise
    
    def query_similar_with_embedding(self,
                                    query_embedding: np.ndarray,
                                    top_k: int = config.TOP_K_POLICIES,
                                    filter_metadata: Optional[Dict] = None) -> Tuple[List[str], List[float], List[Dict]]:
        """
        OPTIMIZED: Query using pre-computed embedding.
        This is the key optimization - no embedding regeneration!
        
        Args:
            query_embedding: Pre-computed embedding vector
            top_k: Number of results
            filter_metadata: Optional filters
            
        Returns:
            Tuple of (documents, similarities, metadatas)
        """
        try:
            logger.info(f"Querying with pre-computed embedding (top_k={top_k})")
            
            # Ensure embedding is 1D array
            if query_embedding.ndim > 1:
                query_embedding = query_embedding.flatten()
            
            # Convert to list - ChromaDB expects a list of embeddings
            embedding_list = query_embedding.tolist()
            
            # Query ChromaDB with pre-computed embedding
            results = self.collection.query(
                query_embeddings=[embedding_list],  # Wrap in list as ChromaDB expects batch format
                n_results=top_k,
                where=filter_metadata
            )
            
            documents = results['documents'][0] if results['documents'] else []
            distances = results['distances'][0] if results['distances'] else []
            metadatas = results['metadatas'][0] if results['metadatas'] else []
            
            # Convert distances to similarities
            similarities = [1 - d for d in distances]
            
            logger.info(f"Retrieved {len(documents)} documents")
            
            return documents, similarities, metadatas
            
        except Exception as e:
            logger.error(f"Query failed: {e}")
            raise
    
    def query_similar(self, query_text: str, 
                     top_k: int = config.TOP_K_POLICIES,
                     filter_metadata: Optional[Dict] = None) -> Tuple[List[str], List[float], List[Dict]]:
        """
        Backward compatibility: Generate embedding if needed.
        Use query_similar_with_embedding() when possible!
        
        Args:
            query_text: Query text
            top_k: Number of results
            filter_metadata: Optional filters
            
        Returns:
            Tuple of (documents, similarities, metadatas)
        """
        logger.warning("query_similar() generates embedding - use query_similar_with_embedding() when possible")
        
        # Generate embedding
        query_embedding = self.embedding_model.encode_complaint(query_text)
        
        # Use optimized method
        return self.query_similar_with_embedding(
            query_embedding,
            top_k,
            filter_metadata
        )
    
    def add_documents(self, documents: List[str], 
                     metadatas: Optional[List[Dict]] = None,
                     ids: Optional[List[str]] = None) -> None:
        """Add documents to vector store"""
        try:
            logger.info(f"Adding {len(documents)} documents")
            
            # Generate embeddings
            embeddings = self.embedding_model.encode_documents(documents)
            
            # Generate IDs if not provided
            if ids is None:
                existing_count = self.collection.count()
                ids = [f"policy_{existing_count + i}" for i in range(len(documents))]
            
            # Default metadata
            if metadatas is None:
                metadatas = [{"source": "policy_document"} for _ in documents]
            
            # Add to ChromaDB
            self.collection.add(
                documents=documents,
                embeddings=embeddings.tolist(),
                metadatas=metadatas,
                ids=ids
            )
            
            logger.success(f"Added {len(documents)} documents")
            
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise
    
    def get_all_documents(self) -> List[Dict]:
        """Get all documents"""
        try:
            results = self.collection.get()
            
            documents = []
            for i in range(len(results['ids'])):
                documents.append({
                    'id': results['ids'][i],
                    'document': results['documents'][i] if results['documents'] else None,
                    'metadata': results['metadatas'][i] if results['metadatas'] else {}
                })
            
            logger.info(f"Retrieved {len(documents)} documents")
            return documents
            
        except Exception as e:
            logger.error(f"Failed to get documents: {e}")
            raise
    
    def delete_collection(self) -> None:
        """Delete collection"""
        try:
            logger.warning(f"Deleting collection: {self.collection_name}")
            self.client.delete_collection(self.collection_name)
            logger.success("Collection deleted")
        except Exception as e:
            logger.error(f"Delete failed: {e}")
            raise
    
    def reset_collection(self) -> None:
        """Reset collection"""
        try:
            logger.warning("Resetting collection")
            self.delete_collection()
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "GovMind policy documents"}
            )
            logger.success("Collection reset")
        except Exception as e:
            logger.error(f"Reset failed: {e}")
            raise


# Global singleton
_vector_store_instance = None


def get_vector_store() -> OptimizedVectorStore:
    """Get singleton instance"""
    global _vector_store_instance
    
    if _vector_store_instance is None:
        _vector_store_instance = OptimizedVectorStore()
    
    return _vector_store_instance


# Sample policies (same as before)
SAMPLE_POLICIES = [
    {
        "text": "Power outages must be reported immediately to the Electricity Board. Emergency repairs will be prioritized within 2 hours for critical areas including hospitals, emergency services, and densely populated residential zones.",
        "metadata": {"department": "electricity", "category": "emergency_response", "priority": "high"}
    },
    {
        "text": "Electricity billing disputes should be raised within 30 days of bill receipt. Consumers can request meter reading verification and billing history. Incorrect bills will be rectified within 15 working days.",
        "metadata": {"department": "electricity", "category": "billing", "priority": "medium"}
    },
    {
        "text": "New electricity connection requests require property ownership documents, ID proof, and site plan. Connections in urban areas are processed within 7 working days, rural areas within 15 days.",
        "metadata": {"department": "electricity", "category": "connection", "priority": "low"}
    },
    {
        "text": "Water pipeline leaks causing flooding or property damage require immediate attention. Emergency response team will be deployed within 1 hour for major leaks affecting multiple households.",
        "metadata": {"department": "water", "category": "emergency_leak", "priority": "high"}
    },
    {
        "text": "Water quality complaints regarding contamination, odor, or color must be investigated immediately. Water samples will be collected and tested within 24 hours. Alternative water supply will be arranged if contamination is confirmed.",
        "metadata": {"department": "water", "category": "quality", "priority": "high"}
    },
    {
        "text": "Water supply timings and schedules are managed by zone. Residents can report irregular supply patterns. Supply improvements require infrastructure assessment and may take 30-60 days to implement.",
        "metadata": {"department": "water", "category": "supply_schedule", "priority": "medium"}
    },
    {
        "text": "Garbage collection is scheduled per zone weekly schedule. Missed collections should be reported within 24 hours. Special waste collection for large items requires prior booking 3 days in advance.",
        "metadata": {"department": "sanitation", "category": "waste_collection", "priority": "medium"}
    },
    {
        "text": "Public toilet maintenance complaints including cleanliness, broken facilities, or lack of water will be addressed within 48 hours. Regular maintenance is conducted weekly.",
        "metadata": {"department": "sanitation", "category": "public_facilities", "priority": "medium"}
    },
    {
        "text": "Illegal dumping and littering complaints can be reported with photo evidence. Violators will be identified and fined as per municipal bylaws. Regular areas affected by dumping will receive increased monitoring.",
        "metadata": {"department": "sanitation", "category": "illegal_dumping", "priority": "medium"}
    },
    {
        "text": "Emergency law and order situations including violence, theft, or immediate danger should be reported to emergency hotline 100. Police response time for emergencies is targeted at 10-15 minutes in urban areas.",
        "metadata": {"department": "police", "category": "emergency", "priority": "high"}
    },
    {
        "text": "Noise pollution complaints during night hours (10 PM - 6 AM) will be investigated immediately. Repeated violations may result in legal action against the source of disturbance.",
        "metadata": {"department": "police", "category": "noise", "priority": "medium"}
    },
    {
        "text": "Traffic violations and parking issues can be reported with vehicle details and location. Traffic police will issue citations based on evidence. Repeat offenders face increased penalties.",
        "metadata": {"department": "police", "category": "traffic", "priority": "low"}
    },
    {
        "text": "Dangerous potholes and road damage affecting vehicle safety or causing accidents require immediate repair. Emergency road repairs are prioritized within 24-48 hours based on severity and traffic volume.",
        "metadata": {"department": "transport", "category": "road_damage", "priority": "high"}
    },
    {
        "text": "Non-functional traffic signals create safety hazards and traffic congestion. Signal repairs are completed within 12 hours. Alternative traffic management is arranged during repair period.",
        "metadata": {"department": "transport", "category": "traffic_signals", "priority": "high"}
    },
    {
        "text": "Streetlight outages affecting public safety should be reported with location details. Repairs are scheduled within 3-5 days based on area priority. Multiple outages in same area are expedited.",
        "metadata": {"department": "transport", "category": "streetlights", "priority": "medium"}
    },
    {
        "text": "Public bus service complaints including route delays, driver behavior, or vehicle condition are reviewed monthly. Serious safety issues are addressed immediately. Service improvements are implemented quarterly.",
        "metadata": {"department": "transport", "category": "public_transport", "priority": "medium"}
    }
]


def initialize_sample_policies():
    """Initialize vector store with sample policies"""
    logger.info("Initializing sample policies")
    
    vector_store = get_vector_store()
    
    if vector_store.collection.count() > 0:
        logger.info(f"Collection has {vector_store.collection.count()} docs - skipping init")
        return
    
    documents = [p["text"] for p in SAMPLE_POLICIES]
    metadatas = [p["metadata"] for p in SAMPLE_POLICIES]
    
    vector_store.add_documents(documents, metadatas)
    logger.success(f"Initialized with {len(documents)} policies")


if __name__ == "__main__":
    from loguru import logger
    logger.add("logs/optimized_vector_store_test.log", rotation="1 MB")
    
    initialize_sample_policies()
    
    store = get_vector_store()
    
    print("\n" + "="*80)
    print("OPTIMIZED VECTOR STORE TEST")
    print("="*80)
    
    query = "Power outage emergency"
    
    # Method 1: Direct query (generates embedding)
    print("\n1. Direct Query (backward compatible):")
    import time
    start = time.time()
    docs1, sims1, metas1 = store.query_similar(query, top_k=3)
    time1 = time.time() - start
    print(f"   Time: {time1:.3f}s")
    print(f"   Results: {len(docs1)}")
    
    # Method 2: With pre-computed embedding (OPTIMIZED)
    print("\n2. With Pre-computed Embedding (OPTIMIZED):")
    from embedding_model import get_embedding_model
    emb_model = get_embedding_model()
    
    start = time.time()
    embedding = emb_model.encode_complaint(query)
    emb_time = time.time() - start
    
    start = time.time()
    docs2, sims2, metas2 = store.query_similar_with_embedding(embedding, top_k=3)
    query_time = time.time() - start
    
    print(f"   Embedding time: {emb_time:.3f}s")
    print(f"   Query time: {query_time:.3f}s")
    print(f"   Total: {emb_time + query_time:.3f}s")
    print(f"   Results: {len(docs2)}")
    
    print("\n" + "="*80)
    print("✓ Key Optimization: Reuse embedding across multiple queries")
    print("="*80)
