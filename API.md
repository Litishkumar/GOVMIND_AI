# GovMind AI Module - API Documentation

Complete API reference for integrating the AI routing system into your application.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Core Functions](#core-functions)
3. [Class APIs](#class-apis)
4. [Data Structures](#data-structures)
5. [Configuration](#configuration)
6. [Error Handling](#error-handling)
7. [Integration Examples](#integration-examples)

---

## Quick Start

### Simple Integration

```python
from main import route_complaint

# Route a single complaint
result = route_complaint(
    complaint_text="Power outage in my area",
    use_llm=True
)

print(result['department'])  # "Electricity Board"
print(result['priority'])    # "High"
```

---

## Core Functions

### `route_complaint()`

Route a single citizen complaint to the appropriate department.

**Signature:**
```python
def route_complaint(
    complaint_text: str,
    use_llm: bool = True
) -> Dict[str, any]
```

**Parameters:**
- `complaint_text` (str, required): The citizen's grievance text in Tamil or English
- `use_llm` (bool, optional): Whether to use Ollama LLM for reasoning (default: True)

**Returns:**
- Dictionary with routing decision (simplified format)

**Return Schema:**
```python
{
    "department": str,        # Department name
    "department_id": str,     # Department identifier
    "category": str,          # Grievance category
    "priority": str,          # "High" | "Medium" | "Low"
    "confidence": str,        # "high" | "medium" | "low"
    "reason": str            # Routing justification
}
```

**Example:**
```python
result = route_complaint("Water pipe leaking badly")

# Output:
# {
#     "department": "Water Supply Board",
#     "department_id": "water",
#     "category": "Emergency leak response",
#     "priority": "High",
#     "confidence": "high",
#     "reason": "Emergency water leak requires immediate attention..."
# }
```

**Raises:**
- `ValueError`: If complaint_text is empty
- `ConnectionError`: If Ollama is not accessible
- `Exception`: For other processing errors

---

### `route_complaints_batch()`

Route multiple complaints in batch mode.

**Signature:**
```python
def route_complaints_batch(
    complaints: List[str]
) -> List[Dict[str, any]]
```

**Parameters:**
- `complaints` (List[str], required): List of complaint texts

**Returns:**
- List of result dictionaries with status information

**Return Schema:**
```python
[
    {
        "status": "success" | "error",
        "complaint": str,
        "result": {...} | None,
        "error": str | None
    },
    ...
]
```

**Example:**
```python
complaints = [
    "No electricity for 6 hours",
    "Garbage not collected",
    "Road has big pothole"
]

results = route_complaints_batch(complaints)

for item in results:
    if item['status'] == 'success':
        print(f"{item['result']['department']} - {item['result']['priority']}")
    else:
        print(f"Error: {item['error']}")
```

---

## Class APIs

### `GovMindAI`

Main interface class for the AI system.

**Initialization:**
```python
from main import GovMindAI

ai_system = GovMindAI(initialize_db=True)
```

**Parameters:**
- `initialize_db` (bool, optional): Initialize vector store with sample policies (default: True)

---

#### `GovMindAI.route()`

Route a single complaint with format options.

**Signature:**
```python
def route(
    self,
    complaint_text: str,
    use_llm: bool = True,
    return_format: str = "full"
) -> Dict[str, any]
```

**Parameters:**
- `complaint_text` (str, required): Complaint text
- `use_llm` (bool, optional): Use LLM reasoning (default: True)
- `return_format` (str, optional): "full" or "simple" (default: "full")

**Returns:**
- Dictionary with routing information (format depends on return_format)

**Example:**
```python
ai = GovMindAI()

# Simple format
result = ai.route("Power outage", return_format="simple")
print(result['department'])

# Full format with detailed info
result = ai.route("Power outage", return_format="full")
print(result['routing_decision'])
print(result['classification'])
print(result['retrieved_policies'])
print(result['metadata'])
```

---

#### `GovMindAI.batch_route()`

Route multiple complaints.

**Signature:**
```python
def batch_route(
    self,
    complaints: List[str]
) -> List[Dict[str, any]]
```

Same as `route_complaints_batch()` but as a class method.

---

### `RoutingEngine`

Core routing engine with full pipeline control.

**Initialization:**
```python
from routing_engine import get_routing_engine

engine = get_routing_engine()  # Singleton instance
```

---

#### `RoutingEngine.route_complaint()`

Full routing with all AI components.

**Signature:**
```python
def route_complaint(
    self,
    complaint_text: str,
    use_llm: bool = True,
    use_enhanced_classification: bool = True
) -> Dict[str, any]
```

**Parameters:**
- `complaint_text` (str, required): Complaint text
- `use_llm` (bool, optional): Use LLM for decision (default: True)
- `use_enhanced_classification` (bool, optional): Use keyword-enhanced classification (default: True)

**Returns:**
- Complete routing result with all metadata (full format)

**Full Return Schema:**
```python
{
    "routing_decision": {
        "department": str,
        "department_id": str,
        "category": str,
        "priority": str,
        "reason": str
    },
    "classification": {
        "primary_department": {
            "id": str,
            "name": str,
            "similarity": float,
            "confidence": str
        },
        "top_3_departments": [...],
        "is_ambiguous": bool
    },
    "retrieved_policies": [
        {
            "text": str,
            "relevance": float,
            "department": str,
            "category": str
        },
        ...
    ],
    "priority_analysis": {
        "suggested_priority": str,
        "reasoning": str,
        "high_priority_keywords": [str, ...],
        "medium_priority_keywords": [str, ...],
        "low_priority_keywords": [str, ...],
        "high_priority_policies_count": int
    },
    "metadata": {
        "processing_time_seconds": float,
        "complaint_length": int,
        "llm_used": bool,
        "enhanced_classification": bool,
        "timestamp": str
    }
}
```

**Example:**
```python
engine = get_routing_engine()

result = engine.route_complaint(
    "Emergency power outage affecting hospital",
    use_llm=True
)

# Access different components
decision = result['routing_decision']
classification = result['classification']
policies = result['retrieved_policies']
priority_info = result['priority_analysis']
```

---

### Component-Level APIs

#### `DepartmentClassifier`

Classify complaints to departments.

```python
from department_classifier import get_classifier

classifier = get_classifier()

# Get top 3 departments
results = classifier.classify("Power outage", return_top_k=3)

# Get primary department only
primary = classifier.get_primary_department("Power outage")

# Enhanced classification with keywords
enhanced = classifier.classify_with_keywords("Power outage")
```

---

#### `PolicyRetriever`

Retrieve relevant policies (RAG).

```python
from policy_retriever import get_policy_retriever

retriever = get_policy_retriever()

# Retrieve policies
policies = retriever.retrieve_policies(
    complaint_text="Power outage",
    department_filter="electricity",
    top_k=3
)

# Get formatted context for LLM
context = retriever.get_policy_context(
    complaint_text="Power outage",
    primary_department="electricity",
    include_related=True
)
```

---

#### `VectorStore`

ChromaDB vector store operations.

```python
from vector_store import get_vector_store

store = get_vector_store()

# Add new policies
store.add_documents(
    documents=["Policy text here"],
    metadatas=[{"department": "electricity", "category": "billing"}]
)

# Query similar documents
docs, similarities, metadatas = store.query_similar(
    query_text="Power bill issue",
    top_k=5
)
```

---

#### `LLMDecisionEngine`

Ollama LLM integration.

```python
from llm_decision import get_llm_engine

llm = get_llm_engine()

decision = llm.generate_routing_decision(
    complaint_text="Power outage emergency",
    policy_context="Policy text...",
    department_match={"department_name": "Electricity Board", ...}
)
```

---

## Data Structures

### Department Configuration

```python
DEPARTMENTS = {
    "department_id": {
        "name": str,           # Display name
        "description": str,    # Department responsibilities
        "keywords": [str, ...]  # Related keywords
    },
    ...
}
```

### Priority Keywords

```python
PRIORITY_KEYWORDS = {
    "high": [str, ...],    # Emergency keywords
    "medium": [str, ...],  # Important keywords
    "low": [str, ...]      # Minor issue keywords
}
```

---

## Configuration

### Modify Settings

Edit `config.py`:

```python
# Change models
EMBEDDING_MODEL = "intfloat/multilingual-e5-large"
OLLAMA_MODEL = "llama3:8b"

# Adjust RAG settings
TOP_K_POLICIES = 3
SIMILARITY_THRESHOLD = 0.65

# Customize prompt
LLM_ROUTING_PROMPT = """
Your custom prompt here...
"""
```

### Add Department

```python
# In config.py
DEPARTMENTS["new_dept"] = {
    "name": "New Department Name",
    "description": "Handles X, Y, and Z",
    "keywords": ["keyword1", "keyword2", ...]
}
```

### Add Policies

```python
from vector_store import get_vector_store

store = get_vector_store()

new_policies = [
    {
        "text": "Policy content here...",
        "metadata": {
            "department": "electricity",
            "category": "new_category",
            "priority": "high"
        }
    }
]

documents = [p["text"] for p in new_policies]
metadatas = [p["metadata"] for p in new_policies]

store.add_documents(documents, metadatas)
```

---

## Error Handling

### Common Exceptions

```python
try:
    result = route_complaint("Power outage")
except ValueError as e:
    # Empty or invalid input
    print(f"Invalid input: {e}")
except ConnectionError as e:
    # Ollama not running
    print(f"Service unavailable: {e}")
except Exception as e:
    # Other errors
    print(f"Processing error: {e}")
```

### Graceful Degradation

```python
# If LLM fails, use rule-based routing
try:
    result = route_complaint("Power outage", use_llm=True)
except Exception:
    result = route_complaint("Power outage", use_llm=False)
```

---

## Integration Examples

### Flask API

```python
from flask import Flask, request, jsonify
from main import route_complaint

app = Flask(__name__)

@app.route('/api/v1/route', methods=['POST'])
def route_api():
    try:
        data = request.json
        complaint = data.get('complaint', '')
        
        if not complaint:
            return jsonify({"error": "Complaint text required"}), 400
        
        result = route_complaint(complaint, use_llm=True)
        
        return jsonify({
            "success": True,
            "data": result
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

**Usage:**
```bash
curl -X POST http://localhost:5000/api/v1/route \
  -H "Content-Type: application/json" \
  -d '{"complaint": "Power outage in my area"}'
```

---

### FastAPI

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from main import route_complaint

app = FastAPI(title="GovMind Routing API")

class ComplaintRequest(BaseModel):
    complaint: str
    use_llm: bool = True

class RoutingResponse(BaseModel):
    department: str
    category: str
    priority: str
    confidence: str
    reason: str

@app.post("/route", response_model=RoutingResponse)
async def route(request: ComplaintRequest):
    try:
        result = route_complaint(
            request.complaint,
            use_llm=request.use_llm
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run: uvicorn api:app --reload
```

---

### Django View

```python
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from main import route_complaint

@csrf_exempt
def route_complaint_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            complaint = data.get('complaint', '')
            
            result = route_complaint(complaint, use_llm=True)
            
            return JsonResponse({
                'success': True,
                'data': result
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)
```

---

### Async Processing

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
from main import route_complaint

executor = ThreadPoolExecutor(max_workers=4)

async def async_route_complaint(complaint: str):
    """Async wrapper for complaint routing"""
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        executor,
        route_complaint,
        complaint,
        True  # use_llm
    )
    return result

# Usage
async def main():
    complaints = ["Power outage", "Water leak", "Garbage issue"]
    tasks = [async_route_complaint(c) for c in complaints]
    results = await asyncio.gather(*tasks)
    return results

# Run
results = asyncio.run(main())
```

---

### Webhook Integration

```python
import requests
from main import route_complaint

def route_with_webhook(complaint: str, webhook_url: str):
    """Route complaint and send result to webhook"""
    try:
        # Route complaint
        result = route_complaint(complaint, use_llm=True)
        
        # Send to webhook
        response = requests.post(
            webhook_url,
            json={
                "complaint": complaint,
                "routing": result
            },
            timeout=10
        )
        
        return result
        
    except Exception as e:
        # Send error to webhook
        requests.post(
            webhook_url,
            json={"error": str(e), "complaint": complaint}
        )
        raise
```

---

## Performance Considerations

### Caching

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_route(complaint: str) -> str:
    """Cache routing results for identical complaints"""
    result = route_complaint(complaint, use_llm=True)
    return json.dumps(result)

# Usage
result = json.loads(cached_route("Power outage"))
```

### Pre-warming

```python
from main import GovMindAI

# Initialize once at application startup
ai_system = GovMindAI(initialize_db=False)

# Models are now loaded, subsequent calls are fast
def fast_route(complaint: str):
    return ai_system.route(complaint, return_format="simple")
```

---

## Monitoring and Logging

### Custom Logging

```python
from loguru import logger

# Configure custom log file
logger.add(
    "my_app_routing.log",
    rotation="100 MB",
    retention="30 days",
    level="INFO",
    format="{time} | {level} | {message}"
)

# Log routing events
result = route_complaint("Power outage")
logger.info(f"Routed to: {result['department']}")
```

### Metrics Collection

```python
import time

def route_with_metrics(complaint: str):
    start_time = time.time()
    
    try:
        result = route_complaint(complaint)
        
        metrics = {
            "status": "success",
            "department": result['department'],
            "priority": result['priority'],
            "processing_time": time.time() - start_time
        }
        
        return result, metrics
        
    except Exception as e:
        metrics = {
            "status": "error",
            "error": str(e),
            "processing_time": time.time() - start_time
        }
        
        return None, metrics
```

---

## Testing

### Unit Tests

```python
import unittest
from main import route_complaint

class TestRouting(unittest.TestCase):
    
    def test_electricity_complaint(self):
        result = route_complaint("Power outage")
        self.assertEqual(result['department_id'], 'electricity')
    
    def test_tamil_complaint(self):
        result = route_complaint("தண்ணீர் வருவதில்லை")
        self.assertEqual(result['department_id'], 'water')
    
    def test_priority_detection(self):
        result = route_complaint("Emergency power cut")
        self.assertEqual(result['priority'], 'High')

if __name__ == '__main__':
    unittest.main()
```

---

**For more details, see README.md**
