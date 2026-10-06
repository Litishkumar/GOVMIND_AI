"""
GovMind AI Module - OPTIMIZED Routing Engine
Zero-redundancy design: Each operation happens exactly once
Target: <15 seconds processing time
FULLY FIXED VERSION - Proper Groq initialization
"""

import time
import os
from typing import Dict, List, Tuple
import numpy as np
from loguru import logger
import config
from embedding_model import get_embedding_model
from department_classifier import get_classifier
from policy_retriever import get_policy_retriever


class OptimizedRoutingEngine:
    """
    High-performance routing engine with zero redundant operations.
    
    Performance improvements:
    1. Embedding computed ONCE and passed forward
    2. Classification happens ONCE
    3. Vector search happens ONCE
    4. Ambiguity check uses existing data
    5. LLM prompt optimized for speed
    """
    
    def __init__(self):
        """Initialize routing engine"""
        logger.info("Initializing Optimized Routing Engine")
        start_time = time.time()
        
        # Initialize core models
        self.embedding_model = get_embedding_model()
        self.classifier = get_classifier()
        self.policy_retriever = get_policy_retriever()
        
        # Initialize Groq LLM Engine - LAZY IMPORT AFTER API KEY IS SET
        self.llm_engine = None
        try:
            logger.info("Initializing Groq LLM Engine...")
            
            # Check if API key is in environment
            api_key = os.getenv('GROQ_API_KEY')
            if not api_key:
                logger.error("❌ GROQ_API_KEY not found in environment!")
                logger.error("API key must be set in main.py BEFORE importing routing_engine")
                raise ValueError("GROQ_API_KEY environment variable not set")
            
            logger.info(f"✓ API key found in environment")
            
            # NOW import groq_llm_decision (after API key is confirmed)
            from groq_llm_decision import get_groq_engine
            
            # Get Groq engine with API key
            self.llm_engine = get_groq_engine(api_key=api_key)
            logger.success("✓ Groq LLM Engine initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Groq LLM: {e}")
            logger.warning("⚠️  Routing will work without LLM (rule-based fallback only)")
            self.llm_engine = None
        
        init_time = time.time() - start_time
        logger.success(f"✓ Engine initialized in {init_time:.2f}s")
    
    def route_complaint(self, 
                       complaint_text: str,
                       use_llm: bool = True,
                       use_enhanced_classification: bool = True) -> Dict[str, any]:
        """
        Optimized routing with zero redundancy.
        
        Pipeline:
        1. Generate embedding ONCE
        2. Classify using embedding (no re-computation)
        3. Vector search ONCE
        4. Build compact context
        5. Fast LLM decision (or rule-based fallback)
        
        Args:
            complaint_text: Complaint text
            use_llm: Use LLM for decision
            use_enhanced_classification: Use keyword-enhanced classification (always True in optimized version)
            
        Returns:
            Complete routing result
        """
        start_time = time.time()
        logger.info("="*80)
        logger.info("PROCESSING COMPLAINT (OPTIMIZED)")
        logger.info("="*80)
        
        try:
            # ═══════════════════════════════════════════════════════════
            # STEP 1: GENERATE EMBEDDING - HAPPENS ONCE
            # ═══════════════════════════════════════════════════════════
            step_start = time.time()
            logger.info("Step 1: Generate embedding")
            
            complaint_embedding = self.embedding_model.encode_complaint(complaint_text)
            
            step_time = time.time() - step_start
            logger.info(f"✓ Embedding generated in {step_time:.3f}s")
            
            # ═══════════════════════════════════════════════════════════
            # STEP 2: CLASSIFY DEPARTMENTS - USING EXISTING EMBEDDING
            # ═══════════════════════════════════════════════════════════
            step_start = time.time()
            logger.info("Step 2: Classify departments")
            
            # Pass embedding directly - NO re-computation
            classification_results = self.classifier.classify_with_embedding(
                complaint_embedding=complaint_embedding,
                complaint_text=complaint_text,  # For keyword matching only
                return_top_k=3
            )
            
            primary_dept = classification_results[0]
            top_3_depts = classification_results[:3]
            
            # Check ambiguity using existing similarity scores - NO re-computation
            is_ambiguous = self._check_ambiguity(classification_results)
            
            step_time = time.time() - step_start
            logger.info(f"✓ Classification completed in {step_time:.3f}s")
            logger.info(f"  Primary: {primary_dept['department_name']} ({primary_dept['similarity']:.3f})")
            
            # ═══════════════════════════════════════════════════════════
            # STEP 3: RETRIEVE POLICIES - HAPPENS ONCE
            # ═══════════════════════════════════════════════════════════
            step_start = time.time()
            logger.info("Step 3: Retrieve policies")
            
            # Single vector search with all needed policies
            policies = self.policy_retriever.retrieve_policies_with_embedding(
                complaint_embedding=complaint_embedding,
                department_filter=primary_dept['department_id'],
                top_k=config.TOP_K_POLICIES
            )
            
            step_time = time.time() - step_start
            logger.info(f"✓ Retrieved {len(policies)} policies in {step_time:.3f}s")
            
            # ═══════════════════════════════════════════════════════════
            # STEP 4: ANALYZE PRIORITY - USING EXISTING DATA
            # ═══════════════════════════════════════════════════════════
            step_start = time.time()
            logger.info("Step 4: Analyze priority")
            
            priority_info = self._analyze_priority_fast(
                complaint_text=complaint_text,
                policies=policies
            )
            
            step_time = time.time() - step_start
            logger.info(f"✓ Priority analyzed in {step_time:.3f}s: {priority_info['suggested_priority']}")
            
            # ═══════════════════════════════════════════════════════════
            # STEP 5: LLM DECISION - COMPACT PROMPT (OR FALLBACK)
            # ═══════════════════════════════════════════════════════════
            if use_llm and self.llm_engine:
                step_start = time.time()
                logger.info("Step 5: Generate LLM decision")
                
                try:
                    # Build compact context
                    compact_context = self._build_compact_context(
                        policies=policies[:2],  # Only top 2 policies
                        primary_dept=primary_dept
                    )
                    
                    final_decision = self.llm_engine.generate_routing_decision_fast(
                        complaint_text=complaint_text,
                        policy_context=compact_context,
                        department_name=primary_dept['department_name'],
                        suggested_priority=priority_info['suggested_priority']
                    )
                    
                    step_time = time.time() - step_start
                    logger.info(f"✓ LLM decision in {step_time:.3f}s")
                
                except Exception as e:
                    logger.warning(f"LLM decision failed: {e}, using rule-based fallback")
                    final_decision = self._get_rule_based_decision(
                        policies, primary_dept, priority_info
                    )
            else:
                # Rule-based fallback (LLM not available or not requested)
                logger.info("Step 5: Using rule-based decision (LLM unavailable)")
                final_decision = self._get_rule_based_decision(
                    policies, primary_dept, priority_info
                )
            
            # ═══════════════════════════════════════════════════════════
            # STEP 6: COMPILE RESULTS
            # ═══════════════════════════════════════════════════════════
            processing_time = time.time() - start_time
            
            routing_result = {
                "routing_decision": {
                    "department": final_decision['department'],
                    "department_id": primary_dept['department_id'],
                    "category": final_decision['category'],
                    "priority": final_decision['priority'],
                    "reason": final_decision['reason']
                },
                "classification": {
                    "primary_department": {
                        "id": primary_dept['department_id'],
                        "name": primary_dept['department_name'],
                        "similarity": primary_dept['similarity'],
                        "confidence": primary_dept['confidence']
                    },
                    "top_3_departments": [
                        {
                            "id": d['department_id'],
                            "name": d['department_name'],
                            "similarity": d['similarity'],
                            "confidence": d['confidence']
                        }
                        for d in top_3_depts
                    ],
                    "is_ambiguous": is_ambiguous
                },
                "retrieved_policies": [
                    {
                        "text": p['text'][:200],  # Truncate for output
                        "relevance": p['relevance_score'],
                        "department": p['department'],
                        "category": p['category']
                    }
                    for p in policies
                ],
                "priority_analysis": priority_info,
                "metadata": {
                    "processing_time_seconds": processing_time,
                    "complaint_length": len(complaint_text),
                    "llm_used": use_llm and self.llm_engine is not None,
                    "enhanced_classification": use_enhanced_classification,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
            }
            
            logger.success("="*80)
            logger.success(f"COMPLETED IN {processing_time:.2f}s")
            logger.success(f"Department: {routing_result['routing_decision']['department']}")
            logger.success(f"Priority: {routing_result['routing_decision']['priority']}")
            logger.success("="*80)
            
            return routing_result
            
        except Exception as e:
            logger.error(f"Routing failed: {e}")
            logger.exception("Full traceback:")
            raise
    
    def _get_rule_based_decision(self, policies: List[Dict], 
                                  primary_dept: Dict, 
                                  priority_info: Dict) -> Dict:
        """
        Rule-based fallback decision when LLM is unavailable.
        
        Args:
            policies: Retrieved policies
            primary_dept: Primary department
            priority_info: Priority analysis
            
        Returns:
            Decision dictionary
        """
        return {
            "category": policies[0]['category'] if policies else "General",
            "department": primary_dept['department_name'],
            "priority": priority_info['suggested_priority'],
            "reason": f"Rule-based decision. Semantic similarity: {primary_dept['similarity']:.2f}"
        }
    
    def _check_ambiguity(self, classification_results: List[Dict], 
                        threshold: float = 0.15) -> bool:
        """
        Check ambiguity using existing similarity scores.
        NO re-computation needed.
        
        Args:
            classification_results: Already computed classification
            threshold: Score difference threshold
            
        Returns:
            True if ambiguous
        """
        if len(classification_results) < 2:
            return False
        
        score_diff = classification_results[0]['similarity'] - classification_results[1]['similarity']
        return score_diff < threshold
    
    def _analyze_priority_fast(self, complaint_text: str, 
                               policies: List[Dict]) -> Dict[str, any]:
        """
        Fast priority analysis using keyword matching only.
        No external calls.
        
        Args:
            complaint_text: Complaint text
            policies: Retrieved policies
            
        Returns:
            Priority analysis
        """
        complaint_lower = complaint_text.lower()
        
        # Fast keyword matching
        high_keywords = [kw for kw in config.PRIORITY_KEYWORDS['high'] 
                        if kw in complaint_lower]
        
        # Check policy priorities
        high_priority_policies = sum(1 for p in policies if p.get('priority') == 'high')
        
        # Decision logic
        if high_keywords or high_priority_policies >= 2:
            priority = "High"
            reason = "Emergency keywords or critical policy match"
        elif any(kw in complaint_lower for kw in config.PRIORITY_KEYWORDS['medium']):
            priority = "Medium"
            reason = "Significant issue"
        else:
            priority = "Medium"  # Default to Medium, not Low
            reason = "Standard priority"
        
        return {
            "suggested_priority": priority,
            "reasoning": reason,
            "high_priority_keywords": high_keywords,
            "high_priority_policies_count": high_priority_policies
        }
    
    def _build_compact_context(self, policies: List[Dict], 
                               primary_dept: Dict) -> str:
        """
        Build minimal context for LLM to reduce tokens.
        
        Args:
            policies: Top 2 policies only
            primary_dept: Primary department
            
        Returns:
            Compact context string
        """
        context_parts = [
            f"Department: {primary_dept['department_name']}",
            f"Match: {primary_dept['similarity']:.2f}",
            "\nRelevant Policies:"
        ]
        
        for i, policy in enumerate(policies, 1):
            # Only first 150 chars of policy
            context_parts.append(f"{i}. {policy['text'][:150]}...")
        
        return "\n".join(context_parts)
    
    def batch_route_complaints(self, complaints: List[str]) -> List[Dict]:
        """
        Batch processing with pre-loaded models.
        
        Args:
            complaints: List of complaint texts
            
        Returns:
            List of routing results
        """
        logger.info(f"Processing batch of {len(complaints)} complaints")
        
        results = []
        for i, complaint in enumerate(complaints, 1):
            logger.info(f"\nBatch item {i}/{len(complaints)}")
            
            try:
                result = self.route_complaint(complaint)
                results.append({
                    "status": "success",
                    "complaint": complaint,
                    "result": result
                })
            except Exception as e:
                logger.error(f"Failed: {e}")
                results.append({
                    "status": "error",
                    "complaint": complaint,
                    "error": str(e)
                })
        
        success_count = sum(1 for r in results if r['status'] == 'success')
        logger.info(f"\nBatch complete: {success_count}/{len(complaints)} successful")
        
        return results


# Global singleton
_optimized_engine_instance = None


def get_routing_engine() -> OptimizedRoutingEngine:
    """Get singleton instance"""
    global _optimized_engine_instance
    
    if _optimized_engine_instance is None:
        _optimized_engine_instance = OptimizedRoutingEngine()
    
    return _optimized_engine_instance


if __name__ == "__main__":
    from loguru import logger
    import json
    
    logger.add("logs/optimized_routing_test.log", rotation="1 MB")
    
    # Initialize
    from vector_store import initialize_sample_policies
    try:
        initialize_sample_policies()
    except:
        pass
    
    engine = get_routing_engine()
    
    # Performance test
    test_complaints = [
        "Emergency power outage affecting hospital",
        "எங்கள் பகுதியில் தண்ணீர் வருவதில்லை",
        "Garbage not collected for 5 days"
    ]
    
    print("\n" + "="*80)
    print("OPTIMIZED ROUTING ENGINE - PERFORMANCE TEST")
    print("="*80)
    
    total_time = 0
    
    for i, complaint in enumerate(test_complaints, 1):
        print(f"\n\nTest {i}: {complaint}")
        print("-"*80)
        
        result = engine.route_complaint(complaint, use_llm=True)
        
        proc_time = result['metadata']['processing_time_seconds']
        total_time += proc_time
        
        print(f"Department: {result['routing_decision']['department']}")
        print(f"Priority: {result['routing_decision']['priority']}")
        print(f"⏱️  Processing Time: {proc_time:.2f}s")
    
    avg_time = total_time / len(test_complaints)
    print("\n" + "="*80)
    print(f"AVERAGE PROCESSING TIME: {avg_time:.2f}s")
    print("="*80)