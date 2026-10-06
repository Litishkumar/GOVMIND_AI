# GovMind AI Module - Quick Start Guide

## 🚀 5-Minute Setup

### 1. Install Ollama

**Linux/Mac:**
```bash
curl https://ollama.ai/install.sh | sh
```

**Start Ollama:**
```bash
ollama serve
```

### 2. Install Llama3 Model

In a new terminal:
```bash
ollama pull llama3:8b
```

This downloads ~4.7GB. Wait for completion.

### 3. Run Setup Script

```bash
cd ai_intelligence
chmod +x setup.sh
./setup.sh
```

This will:
- Check dependencies
- Create virtual environment
- Install Python packages
- Initialize vector database
- Run system test

### 4. Start Using

**Option A: Interactive CLI**
```bash
source venv/bin/activate
python main.py
```

**Option B: Python Code**
```python
from main import route_complaint

result = route_complaint("Power outage emergency")
print(result)
```

---

## 📋 Manual Setup (Alternative)

If setup script doesn't work:

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Initialize database
python vector_store.py

# 4. Test system
python main.py
```

---

## 🎯 First Test

After setup, try this:

```python
from main import route_complaint

# English complaint
result = route_complaint("No electricity in my area for 8 hours")
print(f"Department: {result['department']}")
print(f"Priority: {result['priority']}")

# Tamil complaint  
result = route_complaint("எங்கள் தெருவில் தண்ணீர் வருவதில்லை")
print(f"Department: {result['department']}")
```

---

## 🔧 Troubleshooting

### "Cannot connect to Ollama"
```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Verify
curl http://localhost:11434/api/tags
```

### "Model not found"
```bash
ollama pull llama3:8b
ollama list  # Verify installation
```

### "Module not found"
```bash
source venv/bin/activate  # Activate venv first
pip install -r requirements.txt
```

---

## 📊 Expected Output

```json
{
  "department": "Electricity Board",
  "department_id": "electricity",
  "category": "Power outage emergency response",
  "priority": "High",
  "confidence": "high",
  "reason": "Emergency power outage affecting residential area requires immediate attention per emergency response policy"
}
```

---

## 📁 What Gets Created

After setup:
```
ai_intelligence/
├── venv/                    # Python virtual environment
├── data/
│   └── chromadb/           # Vector database (policies)
├── logs/                   # Application logs
└── models/                 # Cached models (~1.5GB)
```

---

## ⚡ System Requirements

- **Python**: 3.8 or higher
- **RAM**: 8GB minimum (16GB recommended)
- **Storage**: 5GB free space
- **Internet**: Only for initial setup

---

## 🎓 Next Steps

1. ✅ Complete setup
2. 📖 Read full README.md
3. 🧪 Try test cases in main.py
4. 🔧 Customize config.py
5. 📚 Add your own policies
6. 🚀 Integrate with your app

---

## 💡 Pro Tips

1. **First run is slow** (~5-10 seconds) due to model loading. Subsequent runs are fast.

2. **Keep Ollama running** in background for best performance.

3. **Test individual components** before integrating:
   ```bash
   python embedding_model.py
   python department_classifier.py
   python routing_engine.py
   ```

4. **Check logs** if something fails:
   ```bash
   cat logs/govmind_ai_*.log
   ```

---

## 📧 Need Help?

1. Check logs in `logs/` directory
2. Review README.md
3. Test individual components
4. Ensure Ollama is running

---

**You're ready to go! 🎉**
