"""
Performance Diagnostic Script
Identifies which operation is causing the slowdown
"""

import time
from loguru import logger

# Suppress logs for clean output
logger.remove()

print("\n" + "="*80)
print("GOVMIND AI - PERFORMANCE DIAGNOSTIC")
print("="*80)

# Test 1: Embedding Model Loading
print("\n[1/6] Testing Embedding Model Loading...")
start = time.time()
from embedding_model import get_embedding_model
emb_model = get_embedding_model()
load_time = time.time() - start
print(f"✓ Embedding model loaded in {load_time:.2f}s")
if load_time > 5:
    print("⚠️  WARNING: Model loading is slow (first time is normal)")

# Test 2: Embedding Generation
print("\n[2/6] Testing Embedding Generation...")
test_text = "no power in my area"
start = time.time()
embedding = emb_model.encode_complaint(test_text)
embed_time = time.time() - start
print(f"✓ Embedding generated in {embed_time:.2f}s")
print(f"  Embedding shape: {embedding.shape}")
if embed_time > 2:
    print("❌ PROBLEM: Embedding generation is TOO SLOW")
    print("   Expected: <1s, Actual: {:.2f}s".format(embed_time))

# Test 3: Department Classification
print("\n[3/6] Testing Department Classification...")
start = time.time()
from department_classifier import get_classifier
classifier = get_classifier()
class_load_time = time.time() - start
print(f"✓ Classifier loaded in {class_load_time:.2f}s")

start = time.time()
results = classifier.classify_with_embedding(embedding, test_text, return_top_k=3)
class_time = time.time() - start
print(f"✓ Classification in {class_time:.2f}s")
print(f"  Result: {results[0]['department_name']}")
if class_time > 1:
    print("❌ PROBLEM: Classification is TOO SLOW")

# Test 4: Vector Store
print("\n[4/6] Testing Vector Store...")
start = time.time()
from vector_store import get_vector_store
store = get_vector_store()
store_load_time = time.time() - start
print(f"✓ Vector store loaded in {store_load_time:.2f}s")

start = time.time()
docs, sims, metas = store.query_similar_with_embedding(embedding, top_k=3)
search_time = time.time() - start
print(f"✓ Vector search in {search_time:.2f}s")
print(f"  Retrieved {len(docs)} documents")
if search_time > 2:
    print("❌ PROBLEM: Vector search is TOO SLOW")

# Test 5: Policy Retrieval
print("\n[5/6] Testing Policy Retrieval...")
start = time.time()
from policy_retriever import get_policy_retriever
retriever = get_policy_retriever()
policies = retriever.retrieve_policies_with_embedding(
    embedding,
    department_filter=results[0]['department_id'],
    top_k=3
)
retrieval_time = time.time() - start
print(f"✓ Policy retrieval in {retrieval_time:.2f}s")
if retrieval_time > 2:
    print("❌ PROBLEM: Policy retrieval is TOO SLOW")

# Test 6: LLM
print("\n[6/6] Testing LLM (Ollama)...")
print("Checking Ollama connection...")
start = time.time()
from groq_llm_decision import get_llm_engine
try:
    llm = get_llm_engine()
    llm_load_time = time.time() - start
    print(f"✓ LLM engine loaded in {llm_load_time:.2f}s")
    
    # Test LLM generation
    print("Testing LLM generation (this takes longest)...")
    start = time.time()
    decision = llm.generate_routing_decision_fast(
        complaint_text=test_text,
        policy_context="Emergency power outage policy",
        department_name=results[0]['department_name'],
        suggested_priority="High"
    )
    llm_time = time.time() - start
    print(f"✓ LLM generation in {llm_time:.2f}s")
    print(f"  Result: {decision['department']}")
    
    if llm_time > 10:
        print("❌ PROBLEM: LLM is TOO SLOW")
        print("   Expected: 5-8s, Actual: {:.2f}s".format(llm_time))
        print("   Check: Are you using phi3 model?")
        
except Exception as e:
    print(f"❌ LLM ERROR: {e}")
    llm_time = 0

# Summary
print("\n" + "="*80)
print("PERFORMANCE SUMMARY")
print("="*80)

total_time = (load_time + embed_time + class_load_time + class_time + 
              store_load_time + search_time + retrieval_time + llm_time)

print(f"\nComponent Breakdown:")
print(f"1. Model Loading:       {load_time:.2f}s")
print(f"2. Embedding:           {embed_time:.2f}s")
print(f"3. Classifier Load:     {class_load_time:.2f}s")
print(f"4. Classification:      {class_time:.2f}s")
print(f"5. Vector Store Load:   {store_load_time:.2f}s")
print(f"6. Vector Search:       {search_time:.2f}s")
print(f"7. Policy Retrieval:    {retrieval_time:.2f}s")
print(f"8. LLM Generation:      {llm_time:.2f}s")
print(f"{'-'*40}")
print(f"TOTAL:                  {total_time:.2f}s")

print("\n" + "="*80)

# Analysis
if total_time < 15:
    print("✅ PERFORMANCE: GOOD - Within target (<15s)")
elif total_time < 25:
    print("⚠️  PERFORMANCE: OK - Slightly slow (15-25s)")
else:
    print("❌ PERFORMANCE: POOR - Too slow (>25s)")

print("\nBottleneck Analysis:")
components = [
    ("LLM Generation", llm_time),
    ("Model Loading", load_time),
    ("Embedding", embed_time),
    ("Vector Search", search_time),
    ("Policy Retrieval", retrieval_time),
    ("Classification", class_time),
]

sorted_components = sorted(components, key=lambda x: x[1], reverse=True)
print("\nSlowest Operations:")
for i, (name, t) in enumerate(sorted_components[:3], 1):
    percent = (t / total_time * 100) if total_time > 0 else 0
    print(f"{i}. {name}: {t:.2f}s ({percent:.1f}%)")

# Recommendations
print("\n" + "="*80)
print("RECOMMENDATIONS")
print("="*80)

if llm_time > 15:
    print("\n🔧 LLM is very slow:")
    print("   1. Check model: ollama list")
    print("   2. Should be using: phi3 (not llama3:8b)")
    print("   3. Run: ollama pull phi3")
    print("   4. Restart your script")

if embed_time > 2:
    print("\n🔧 Embedding is slow:")
    print("   1. First run loads model (normal)")
    print("   2. CPU-only inference is slower")
    print("   3. Consider using smaller model if persistent")

if search_time > 2:
    print("\n🔧 Vector search is slow:")
    print("   1. Check ChromaDB database size")
    print("   2. May need to rebuild index")

if total_time > 20 and llm_time < 10:
    print("\n🔧 Multiple components slow:")
    print("   1. Check if you're using OPTIMIZED files")
    print("   2. Verify files from ai_intelligence_optimized folder")
    print("   3. Check for redundant embedding generations in logs")

print("\n" + "="*80)
print("Run this again after fixes to verify improvements")
print("="*80 + "\n")
