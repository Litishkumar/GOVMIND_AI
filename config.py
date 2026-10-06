"""
GovMind AI Module - Configuration
Centralized configuration for all AI components
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
LOGS_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Embedding Model Configuration
EMBEDDING_MODEL = "intfloat/multilingual-e5-base"  # Supports Tamil + English
EMBEDDING_DIMENSION = 1024

# ChromaDB Configuration
CHROMA_PERSIST_DIR = str(DATA_DIR / "chromadb")
CHROMA_COLLECTION_NAME = "govmind_policies"

# Ollama Configuration
# Default Ollama endpoint

# Department Definitions
DEPARTMENTS = {
    "electricity": {
        "name": "Electricity Board",
        "description": "Handles power outages, electricity billing issues, meter problems, line faults, transformer issues, and electrical connection requests",
        "keywords": ["power", "electricity", "current", "outage", "bill", "meter", "transformer", "connection", "wire", "pole"]
    },
    "water": {
        "name": "Water Supply Board",
        "description": "Manages water supply problems, pipeline leaks, water quality issues, drainage problems, sewage overflow, and water connection requests",
        "keywords": ["water", "supply", "leak", "pipe", "drainage", "sewage", "tap", "tank", "quality", "contamination"]
    },
    "sanitation": {
        "name": "Municipal Sanitation",
        "description": "Handles garbage collection, street cleaning, waste management, public toilet maintenance, and sanitation workers",
        "keywords": ["garbage", "waste", "trash", "cleaning", "sanitation", "toilet", "dump", "sweeping", "hygiene"]
    },
    "police": {
        "name": "Police Department",
        "description": "Addresses law and order issues, theft, harassment, noise complaints, traffic violations, and public safety concerns",
        "keywords": ["theft", "crime", "harassment", "noise", "traffic", "safety", "police", "violation", "security", "stolen"]
    },
    "transport": {
        "name": "Road & Transport Department",
        "description": "Manages road repairs, potholes, traffic signals, streetlights, public transport issues, and road maintenance",
        "keywords": ["road", "pothole", "transport", "bus", "traffic", "signal", "street", "light", "highway", "bridge"]
    }
}

# Priority Keywords
PRIORITY_KEYWORDS = {
    "high": ["urgent", "emergency", "critical", "danger", "severe", "immediate", "life-threatening"],
    "medium": ["important", "significant", "affecting", "multiple", "recurring", "weeks"],
    "low": ["minor", "small", "cosmetic", "future", "enhancement"]
}

# RAG Configuration
TOP_K_POLICIES = 2  # Number of policy chunks to retrieve
SIMILARITY_THRESHOLD = 0.65  # Minimum similarity score for department matching

# LLM Prompt Template
LLM_ROUTING_PROMPT = """You are a grievance routing AI.

Based on the complaint and policy context, return JSON with:
category, department, priority, reason.

Departments:
- Electricity Board
- Water Supply Board
- Municipal Sanitation
- Police Department
- Road & Transport Department

Complaint:
{complaint_text}

Policy Context:
{policy_context}

Respond ONLY in valid JSON:
{{
    "category": "",
    "department": "",
    "priority": "",
    "reason": ""
}}
"""

"""Respond with ONLY the JSON object, no additional text."""

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> | <level>{message}</level>"
