# GovMind AI & Intelligence Module

**AI-Powered Citizen Grievance Redressal Platform**

A production-ready, fully local AI system for intelligent routing of citizen complaints to appropriate government departments using semantic understanding, RAG (Retrieval-Augmented Generation), and LLM reasoning.

---

## 🌟 Features

✅ **Multilingual Support**: Tamil + English complaint processing  
✅ **Semantic Understanding**: Context-aware classification using embeddings  
✅ **Department Auto-Classification**: 5 government departments with confidence scoring  
✅ **RAG Integration**: Policy-aware routing using ChromaDB vector store  
✅ **LLM Reasoning**: Structured decision-making using Ollama (Llama3)  
✅ **Priority Detection**: Automatic urgency classification (High/Medium/Low)  
✅ **100% Local**: No external APIs, no usage limits, complete privacy  
✅ **Production-Ready**: Error handling, logging, retry mechanisms  

---

## 🏗 Architecture

```
Complaint Text
    ↓
[Sentence Transformer Embedding]
    ↓
[Department Semantic Classification]
    ↓
[ChromaDB Policy Retrieval (RAG)]
    ↓
[Ollama LLM Reasoning]
    ↓
Structured JSON Output
```

---

## 📦 Components

### 1. **embedding_model.py**
- Loads `intfloat/multilingual-e5-large` for Tamil + English embeddings
- Converts complaints to 1024-dimensional vectors
- Supports batch processing

### 2. **vector_store.py**
- ChromaDB integration for policy document storage
- Semantic search with relevance scoring
- Pre-loaded with 16 sample government policies

### 3. **department_classifier.py**
- Classifies complaints into 5 departments:
  - Electricity Board
  - Water Supply Board
  - Municipal Sanitation
  - Police Department
  - Road & Transport Department
- Provides confidence scores and similarity rankings

### 4. **policy_retriever.py**
- RAG implementation for policy context retrieval
- Priority detection based on keywords and policy metadata
- Formatted context generation for LLM prompts

### 5. **llm_decision.py**
- Ollama integration using `llama3:8b`
- Structured JSON generation for routing decisions
- Retry mechanism with fallback logic

### 6. **routing_engine.py**
- Main orchestration layer
- Combines all components into unified pipeline
- Batch processing support

### 7. **main.py**
- Production API interface
- CLI for interactive testing
- Simple function exports for integration

---

## 🚀 Installation

### Prerequisites

1. **Python 3.8+**
2. **Ollama** (for local LLM)

### Step 1: Install Ollama

```bash
# Linux/Mac
curl https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve

# Pull Llama3 model (in another terminal)
ollama pull llama3:8b
```

### Step 2: Install Python Dependencies

```bash
cd ai_intelligence
pip install -r requirements.txt
```

**Note**: First run will download the embedding model (~1.5GB). This is one-time only.

---

## 💻 Usage

### Option 1: Interactive CLI

```bash
python main.py
```

This launches an interactive menu:
1. Route single complaint (manual input)
2. Run demo with sample complaints
3. Load complaints from file
4. Exit

### Option 2: Programmatic Use

```python
from main import route_complaint

# Route a single complaint
result = route_complaint("Power outage in my area for 6 hours", use_llm=True)

print(result)
# Output:
# {
#     "department": "Electricity Board",
#     "department_id": "electricity",
#     "category": "Power outage emergency",
#     "priority": "High",
#     "confidence": "high",
#     "reason": "Emergency power outage affecting residential area..."
# }
```

### Option 3: Batch Processing

```python
from main import route_complaints_batch

complaints = [
    "No water supply for 3 days",
    "Garbage not collected",
    "Street light not working"
]

results = route_complaints_batch(complaints)
```

### Option 4: Direct Engine Access

```python
from routing_engine import get_routing_engine

engine = get_routing_engine()

# Full detailed result
result = engine.route_complaint("Power outage emergency")

# Access detailed information
print(result['routing_decision'])
print(result['classification'])
print(result['retrieved_policies'])
print(result['priority_analysis'])
print(result['metadata'])
```

---

## 📊 Output Format

### Simple Format (default)

```json
{
  "department": "Electricity Board",
  "department_id": "electricity",
  "category": "Power outage emergency response",
  "priority": "High",
  "confidence": "high",
  "reason": "Emergency power outage affecting multiple households including hospital nearby requires immediate attention per policy guidelines"
}
```

### Full Format (detailed)

```json
{
  "routing_decision": {
    "department": "Electricity Board",
    "department_id": "electricity",
    "category": "Power outage emergency response",
    "priority": "High",
    "reason": "..."
  },
  "classification": {
    "primary_department": {
      "id": "electricity",
      "name": "Electricity Board",
      "similarity": 0.8745,
      "confidence": "high"
    },
    "top_3_departments": [...],
    "is_ambiguous": false
  },
  "retrieved_policies": [
    {
      "text": "Power outages must be reported immediately...",
      "relevance": 0.8234,
      "department": "electricity",
      "category": "emergency_response"
    }
  ],
  "priority_analysis": {
    "suggested_priority": "High",
    "reasoning": "Emergency keywords detected",
    "high_priority_keywords": ["emergency", "hospital"]
  },
  "metadata": {
    "processing_time_seconds": 2.34,
    "complaint_length": 87,
    "llm_used": true,
    "timestamp": "2024-02-16 10:30:45"
  }
}
```

---

## 🧪 Testing

### Test Individual Components

```bash
# Test embedding model
python embedding_model.py

# Test vector store
python vector_store.py

# Test department classifier
python department_classifier.py

# Test policy retriever
python policy_retriever.py

# Test LLM engine
python llm_decision.py

# Test full routing engine
python routing_engine.py
```

### Sample Test Cases

The system includes 5 test cases covering:
1. English emergency complaint (electricity)
2. Tamil complaint (water)
3. Multi-day issue (sanitation)
4. Safety hazard (transport)
5. Billing issue (electricity)

---

## 🛠 Configuration

Edit `config.py` to customize:

```python
# Models
EMBEDDING_MODEL = "intfloat/multilingual-e5-large"
OLLAMA_MODEL = "llama3:8b"

# RAG
TOP_K_POLICIES = 3
SIMILARITY_THRESHOLD = 0.65

# Departments
DEPARTMENTS = {
    "electricity": {...},
    "water": {...},
    # Add more departments
}

# Priority Keywords
PRIORITY_KEYWORDS = {
    "high": ["urgent", "emergency", ...],
    "medium": [...],
    "low": [...]
}
```

---

## 📁 Project Structure

```
ai_intelligence/
├── config.py                    # Configuration and constants
├── embedding_model.py           # Sentence Transformer wrapper
├── vector_store.py              # ChromaDB integration
├── department_classifier.py     # Semantic classification
├── policy_retriever.py          # RAG implementation
├── llm_decision.py              # Ollama LLM integration
├── routing_engine.py            # Main orchestration
├── main.py                      # Production API & CLI
├── requirements.txt             # Python dependencies
├── README.md                    # Documentation
├── data/                        # ChromaDB persistence
│   └── chromadb/
├── logs/                        # Application logs
└── models/                      # Cached models (auto-created)
```

---

## 🔧 Troubleshooting

### Issue: "Cannot connect to Ollama"

**Solution:**
```bash
# Check if Ollama is running
ps aux | grep ollama

# Start Ollama
ollama serve

# In another terminal, verify model
ollama list
```

### Issue: "Model not found"

**Solution:**
```bash
ollama pull llama3:8b
```

### Issue: Slow first run

**Cause:** Downloading embedding model (~1.5GB)  
**Solution:** Wait for initial download, subsequent runs are fast

### Issue: "ChromaDB initialization failed"

**Solution:** Check write permissions in `data/` directory

---

## 📈 Performance

- **Embedding Generation**: ~50ms per complaint
- **Department Classification**: ~20ms
- **Policy Retrieval**: ~30ms
- **LLM Decision**: ~2-5 seconds (depends on hardware)
- **Total Pipeline**: ~3-6 seconds per complaint

**Hardware Tested:**
- CPU: Intel i5 / AMD Ryzen 5
- RAM: 8GB minimum (16GB recommended)
- Storage: 5GB free space

---

## 🎯 Supported Departments

1. **Electricity Board**
   - Power outages, billing, meter issues, connections

2. **Water Supply Board**
   - Water supply, leaks, quality, drainage, sewage

3. **Municipal Sanitation**
   - Garbage collection, street cleaning, public toilets

4. **Police Department**
   - Law & order, theft, noise complaints, traffic

5. **Road & Transport**
   - Road repairs, potholes, traffic signals, streetlights

---

## 🔐 Privacy & Security

- ✅ **100% Local Processing**: No data leaves your machine
- ✅ **No API Keys Required**: Fully open-source stack
- ✅ **No Usage Limits**: Unlimited complaints
- ✅ **No Tracking**: Zero telemetry or analytics
- ✅ **Offline Capable**: Works without internet (after initial setup)

---

## 📝 Adding New Policies

```python
from vector_store import get_vector_store

vector_store = get_vector_store()

new_policies = [
    {
        "text": "Your policy text here",
        "metadata": {
            "department": "electricity",
            "category": "policy_category",
            "priority": "high"
        }
    }
]

documents = [p["text"] for p in new_policies]
metadatas = [p["metadata"] for p in new_policies]

vector_store.add_documents(documents, metadatas)
```

---

## 🚀 Integration Example

### Flask API Wrapper

```python
from flask import Flask, request, jsonify
from main import route_complaint

app = Flask(__name__)

@app.route('/api/route', methods=['POST'])
def route():
    data = request.json
    complaint = data.get('complaint', '')
    
    result = route_complaint(complaint, use_llm=True)
    return jsonify(result)

if __name__ == '__main__':
    app.run(port=5000)
```

### FastAPI Wrapper

```python
from fastapi import FastAPI
from pydantic import BaseModel
from main import route_complaint

app = FastAPI()

class Complaint(BaseModel):
    text: str
    use_llm: bool = True

@app.post("/route")
def route(complaint: Complaint):
    result = route_complaint(complaint.text, complaint.use_llm)
    return result
```

---

## 📚 Tech Stack

- **Embeddings**: Sentence Transformers (intfloat/multilingual-e5-large)
- **Vector DB**: ChromaDB
- **LLM**: Ollama (Llama3:8b)
- **Language**: Python 3.8+
- **Logging**: Loguru
- **Data Validation**: Pydantic

---

## 🤝 Contributing

This is a modular, production-ready system designed for the GovMind platform. To extend:

1. Add new departments in `config.py`
2. Add policies via `vector_store.py`
3. Customize priority logic in `policy_retriever.py`
4. Modify LLM prompt in `config.py`

---

## 📄 License

Open-source for government and civic tech use.

---

## 🎓 Citation

```
GovMind AI & Intelligence Module
AI-Powered Citizen Grievance Redressal Platform
Built with Sentence Transformers, ChromaDB, and Ollama
```

---

## 📧 Support

For issues or questions:
1. Check logs in `logs/` directory
2. Review troubleshooting section
3. Test individual components
4. Verify Ollama is running

---

**Built with ❤️ for better governance**
