"""
GovMind AI & Intelligence Module - Main Entry Point
Production-ready API for grievance routing
WITH EMBEDDED GROQ API KEY - FIXED VERSION
"""
import base64
import tempfile
import json
import sys
import os
from typing import Dict, Optional
from pathlib import Path
from loguru import logger
import config
"""
main.py - WHISPER INTEGRATION VERSION
Add this /process-speech endpoint to your existing main.py
"""

# ===== ADD THESE IMPORTS TO YOUR main.py (top of file) =====
import base64
import tempfile
# ===== END NEW IMPORTS =====

# (Keep all your existing imports)

# ===== ADD THIS ENDPOINT TO YOUR main.py (after the /route endpoint) =====


# ===== END OF NEW ENDPOINT =====
# ============================================================================
# SET GROQ API KEY - EMBEDDED IN CODE
# ============================================================================
# Your API key is set here for the application
GROQ_API_KEY = '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'

# Set it as environment variable BEFORE importing routing_engine
os.environ['GROQ_API_KEY'] = GROQ_API_KEY
# ============================================================================

# NOW import routing_engine (which needs the API key)
from routing_engine import get_routing_engine
from vector_store import initialize_sample_policies
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
from fastapi.templating import Jinja2Templates
from fastapi import Request

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
"""
main.py - WHISPER INTEGRATION VERSION
Add this /process-speech endpoint to your existing main.py
"""

# ===== ADD THESE IMPORTS TO YOUR main.py (top of file) =====
import base64
import tempfile
# ===== END NEW IMPORTS =====

# (Keep all your existing imports)

# ===== ADD THIS ENDPOINT TO YOUR main.py (after the /route endpoint) =====

@app.post("/process-speech")
async def process_speech(request: dict):
    """
    Process audio speech using OpenAI Whisper
    
    Flow:
    1. Receive base64 audio data
    2. Decode and save to temp file
    3. Whisper: speech-to-text (Tamil or English)
    4. Route complaint through main system
    5. Generate response in detected language
    6. Return everything
    
    Input:
    {
        'audio_data': 'base64_encoded_audio',
        'language': 'ta' or 'en'
    }
    
    Output:
    {
        'status': 'success',
        'whisper_result': {
            'text': 'transcribed text',
            'language': 'ta' or 'en',
            'confidence': 0.95
        },
        'routing_result': {
            'department': '...',
            'priority': '...',
            'category': '...'
        },
        'response': 'English response',
        'response_tamil': 'Tamil response',
        'language': 'ta' or 'en'
    }
    """
    try:
        logger.info("=" * 100)
        logger.info("PROCESSING SPEECH WITH WHISPER")
        logger.info("=" * 100)
        
        # ===== STEP 1: GET AUDIO DATA =====
        audio_data = request.get('audio_data', '')
        language_hint = request.get('language', 'ta')  # 'ta' or 'en'
        
        if not audio_data:
            logger.error("No audio data provided")
            return {'error': 'No audio data provided'}
        
        logger.info(f"Step 1: Received audio ({len(audio_data) / 1024:.1f} KB)")
        logger.info(f"Language hint: {language_hint}")
        
        # ===== STEP 2: DECODE BASE64 TO AUDIO BYTES =====
        try:
            audio_bytes = base64.b64decode(audio_data)
            logger.info(f"Step 2: Decoded audio bytes ({len(audio_bytes) / 1024:.1f} KB)")
        except Exception as e:
            logger.error(f"Failed to decode audio: {e}")
            return {'error': 'Invalid audio data format'}
        
        # ===== STEP 3: SAVE TO TEMP FILE =====
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name
        
        logger.info(f"Step 3: Saved to temp file: {tmp_path}")
        
        try:
            # ===== STEP 4: WHISPER SPEECH-TO-TEXT =====
            logger.info("Step 4: Calling Whisper API for speech-to-text...")
            
            tamil_processor = get_tamil_processor(api_key=GROQ_API_KEY)
            
            # Call Whisper with specified language
            whisper_result = tamil_processor.speech_to_text(tmp_path, language=language_hint)
            
            # Check if successful
            if whisper_result['status'] != 'success':
                logger.error(f"Whisper failed: {whisper_result.get('error')}")
                return {
                    'status': 'error',
                    'error': whisper_result.get('error', 'Whisper speech-to-text failed')
                }
            
            complaint_text = whisper_result['text']
            detected_language = whisper_result['language']
            
            logger.info(f"Step 5: Transcribed: {complaint_text[:60]}...")
            logger.info(f"Step 6: Language: {detected_language}")
            
            # ===== STEP 5: ROUTE COMPLAINT THROUGH MAIN SYSTEM =====
            logger.info("Step 7: Routing complaint through main system...")
            
            ai_system = GovMindAI(initialize_db=False)
            routing_result = ai_system.route(complaint_text, use_llm=True, return_format="simple")
            
            logger.info(f"Step 8: Routed to {routing_result['department']}")
            logger.info(f"  Priority: {routing_result['priority']}")
            logger.info(f"  Category: {routing_result['category']}")
            
            # ===== STEP 6: GENERATE RESPONSE IN BOTH LANGUAGES =====
            logger.info("Step 9: Generating response...")
            
            response_dict = tamil_processor.create_full_response(routing_result, detected_language)
            
            logger.info("Step 10: Response generated")
            logger.info(f"  English: {response_dict['english'][:50]}...")
            logger.info(f"  Tamil: {response_dict['tamil'][:50]}...")
            
            # ===== STEP 7: RETURN COMPLETE RESULT =====
            logger.info("Step 11: Returning response")
            logger.info("=" * 100)
            
            return {
                'status': 'success',
                'whisper_result': {
                    'text': complaint_text,
                    'language': detected_language,
                    'confidence': whisper_result.get('confidence', 0.95),
                    'method': 'openai_whisper'
                },
                'routing_result': {
                    'department': routing_result['department'],
                    'department_id': routing_result['department_id'],
                    'priority': routing_result['priority'],
                    'category': routing_result['category'],
                    'confidence': routing_result.get('confidence', 0)
                },
                'response': response_dict['english'],
                'response_tamil': response_dict['tamil'],
                'language': detected_language
            }
            
        finally:
            # ===== CLEANUP: DELETE TEMP FILE =====
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
                logger.info("Temp file cleaned up")
        
    except Exception as e:
        logger.error(f"ERROR processing speech: {e}")
        logger.exception("Full traceback:")
        
        return {
            'status': 'error',
            'error': str(e)
        }

# ===== END OF NEW ENDPOINT =====

@app.get("/voice", response_class=HTMLResponse)
async def voice_page(request: Request):
    return templates.TemplateResponse("voice_interface.html", {"request": request})


class ComplaintRequest(BaseModel):
    complaint: str
    language: str="en-US"

# ADD THIS IMPORT (top of file)
from tamil_speech_processor import get_tamil_processor

# MODIFY /route endpoint (around line 70)
@app.post("/route")
async def route_complaint(req: ComplaintRequest):
    ai_system = GovMindAI(initialize_db=False)
    
    tamil_processor = get_tamil_processor(api_key=GROQ_API_KEY)  # ADD
    detected_lang = tamil_processor.detect_language(req.complaint)  # ADD
    
    result = ai_system.route(req.complaint, use_llm=True, return_format="simple")
    
    # ADD THIS
    response_dict = tamil_processor.create_full_response(result, detected_lang)
    
    return {
        "response": response_dict['english'],
        "response_tamil": response_dict['tamil'],  # NEW
        "language": "ta-IN" if detected_lang == 'ta' else "en-US",
        "department": result['department'],
        "priority": result['priority'],
        "category": result['category'],
        "confidence": result.get('confidence', 0),
        "full_result": result
    }

# Configure logger
logger.remove()  # Remove default handler
logger.add(
    sys.stdout,
    format=config.LOG_FORMAT,
    level=config.LOG_LEVEL,
    colorize=True
)
logger.add(
    config.LOGS_DIR / "govmind_ai_{time}.log",
    rotation="10 MB",
    retention="7 days",
    format=config.LOG_FORMAT,
    level="DEBUG"
)


class GovMindAI:
    """
    Main interface for GovMind AI Intelligence Module
    Provides simple API for complaint routing
    """
    
    def __init__(self, initialize_db: bool = True):
        """
        Initialize GovMind AI system
        
        Args:
            initialize_db: Whether to initialize vector store with sample policies
        """
        logger.info("="*100)
        logger.info("INITIALIZING GOVMIND AI & INTELLIGENCE MODULE")
        logger.info("="*100)
        
        # Verify GROQ API key is set
        if not os.getenv('GROQ_API_KEY'):
            raise ValueError("GROQ_API_KEY not set in environment or code")
        logger.success("✓ GROQ API Key is configured")
        
        # Initialize vector store if needed
        if initialize_db:
            try:
                logger.info("Checking vector store initialization...")
                initialize_sample_policies()
            except Exception as e:
                logger.warning(f"Vector store initialization skipped: {e}")
        
        # Initialize routing engine (loads all models)
        # API key is already set in environment
        self.routing_engine = get_routing_engine()
        
        logger.success("="*100)
        logger.success("GOVMIND AI SYSTEM READY")
        logger.success("="*100)
    
    def route(self, complaint_text: str, 
             use_llm: bool = True,
             return_format: str = "full") -> Dict:
        """
        Main routing function - simple interface
        
        Args:
            complaint_text: Citizen's grievance text (Tamil or English)
            use_llm: Whether to use Groq LLM for decision (default: True)
            return_format: "full" or "simple" output format
            
        Returns:
            Routing result dictionary
        """
        if not complaint_text or not complaint_text.strip():
            raise ValueError("Complaint text cannot be empty")
        
        # Process complaint
        result = self.routing_engine.route_complaint(
            complaint_text=complaint_text.strip(),
            use_llm=use_llm,
            use_enhanced_classification=True
        )
        
        # Return based on format
        if return_format == "simple":
            return self._simplify_result(result)
        else:
            return result
    
    def _simplify_result(self, full_result: Dict) -> Dict:
        """
        Convert full result to simplified format
        
        Args:
            full_result: Complete routing result
            
        Returns:
            Simplified result with essential fields
        """
        return {
            "department": full_result['routing_decision']['department'],
            "department_id": full_result['routing_decision']['department_id'],
            "category": full_result['routing_decision']['category'],
            "priority": full_result['routing_decision']['priority'],
            "confidence": full_result['classification']['primary_department']['confidence'],
            "reason": full_result['routing_decision']['reason']
        }
    
    def batch_route(self, complaints: list) -> list:
        """
        Route multiple complaints in batch
        
        Args:
            complaints: List of complaint text strings
            
        Returns:
            List of routing results
        """
        return self.routing_engine.batch_route_complaints(complaints)


def main():
    """
    Main function with CLI interface
    """
    print("\n" + "="*100)
    print(" "*35 + "GOVMIND AI MODULE")
    print(" "*25 + "AI-Powered Citizen Grievance Routing")
    print("="*100 + "\n")
    
    # Initialize system
    try:
        ai_system = GovMindAI(initialize_db=True)
    except Exception as e:
        logger.error(f"Failed to initialize system: {e}")
        print(f"\n❌ Initialization failed: {e}")
        print("\nPlease ensure:")
        print("1. Groq API key is configured (already embedded in code)")
        print("2. All dependencies are installed: pip install -r requirements.txt")
        print("3. Vector store data is available")
        sys.exit(1)
    
    # Interactive mode
    print("\nSystem initialized successfully! ✓")
    print("\nOptions:")
    print("1. Route single complaint (interactive)")
    print("2. Run demo with sample complaints")
    print("3. Load complaints from file")
    print("4. Start FastAPI Server (Voice AI)")
    print("5. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            # Interactive routing
            print("\n" + "-"*100)
            print("Enter complaint (Tamil or English):")
            complaint = input("> ").strip()
            
            if not complaint:
                print("❌ Complaint cannot be empty")
                continue
            
            print("\nProcessing...\n")
            
            try:
                result = ai_system.route(complaint, use_llm=True, return_format="simple")
                
                print("\n" + "="*100)
                print(" "*40 + "ROUTING RESULT")
                print("="*100)
                print(f"\nDepartment:  {result['department']}")
                print(f"Category:    {result['category']}")
                print(f"Priority:    {result['priority']}")
                print(f"Confidence:  {result['confidence']}")
                print(f"\nReason:\n{result['reason']}")
                print("="*100 + "\n")
                
            except Exception as e:
                logger.error(f"Routing failed: {e}")
                print(f"\n❌ Error: {e}\n")
        
        elif choice == "2":
            # Demo mode
            print("\n" + "="*100)
            print(" "*35 + "DEMO MODE")
            print("="*100)
            
            demo_complaints = [
                "Emergency power cut in our area affecting hospital nearby",
                "எங்கள் தெருவில் தண்ணீர் வருவதில்லை",
                "Garbage not collected for one week",
                "Big pothole on main road causing accidents",
                "My electricity bill is very high this month"
            ]
            
            for i, complaint in enumerate(demo_complaints, 1):
                print(f"\n{'─'*100}")
                print(f"Demo {i}/{len(demo_complaints)}: {complaint}")
                print('─'*100)
                
                try:
                    result = ai_system.route(complaint, use_llm=True, return_format="simple")
                    print(f"Department: {result['department']}")
                    print(f"Priority: {result['priority']}")
                    print(f"Confidence: {result['confidence']}")
                except Exception as e:
                    print(f"Error: {e}")
            
            print("\n" + "="*100)
            print("Demo completed!")
            print("="*100 + "\n")
        
        elif choice == "3":
            # Load from file
            file_path = input("\nEnter file path (one complaint per line): ").strip()
            
            if not Path(file_path).exists():
                print(f"❌ File not found: {file_path}")
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    complaints = [line.strip() for line in f if line.strip()]
                
                print(f"\nLoaded {len(complaints)} complaints")
                print("Processing...\n")
                
                results = ai_system.batch_route(complaints)
                
                # Save results
                output_file = "batch_routing_results.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                
                success_count = sum(1 for r in results if r['status'] == 'success')
                print(f"\n✅ Processed {success_count}/{len(complaints)} successfully")
                print(f"Results saved to: {output_file}\n")
                
            except Exception as e:
                print(f"❌ Error: {e}")
                
        elif choice == "4":
                print("\n🎤 Launching FastAPI Server (Voice AI Interface)...\n")

                import threading
                import webbrowser
                import time
                import uvicorn

    # Function to start server
                def run_server():
                    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

    # Start server in background thread
                server_thread = threading.Thread(target=run_server, daemon=True)
                server_thread.start()

    # Wait 1.5 seconds for server to start
                time.sleep(1.5)

    # Automatically open browser
                webbrowser.open("http://127.0.0.1:8000/voice")

                print("✅ Voice interface opened in browser.")
                print("Press CTRL+C to stop the server.\n")

    # Keep main thread alive
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\n🛑 Server stopped.")
                    break


# Direct function exports for programmatic use
def route_complaint(complaint_text: str, use_llm: bool = True) -> Dict:
    """
    Direct function to route a single complaint
    
    Args:
        complaint_text: The grievance text
        use_llm: Whether to use LLM
        
    Returns:
        Routing result dictionary
    """
    ai = GovMindAI(initialize_db=False)
    return ai.route(complaint_text, use_llm=use_llm, return_format="simple")


def route_complaints_batch(complaints: list) -> list:
    """
    Direct function to route multiple complaints
    
    Args:
        complaints: List of complaint texts
        
    Returns:
        List of routing results
    """
    ai = GovMindAI(initialize_db=False)
    return ai.batch_route(complaints)


if __name__ == "__main__":
    main()