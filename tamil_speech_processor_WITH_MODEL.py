"""
GovMind AI - Tamil Speech Processor with Trained Model Integration
Complete Tamil language processing module with ML-based predictions
"""

import os
from loguru import logger
from groq import Groq
from tamil_language_model import get_tamil_model  # ADD THIS IMPORT


class TamilSpeechProcessor:
    """
    Complete Tamil language processing module
    - Language detection (Tamil/English)
    - Tamil ↔ English translation
    - Response preparation in both languages
    - ML-based Tamil analysis with trained model
    """
    
    def __init__(self, api_key: str = None):
        """Initialize Tamil Speech Processor with Model"""
        logger.info("Initializing Tamil Speech Processor")
        
        if not api_key:
            api_key = os.getenv('GROQ_API_KEY')
        
        if not api_key:
            logger.error("❌ GROQ_API_KEY not found")
            raise ValueError("Groq API key required")
        
        self.api_key = api_key
        self.client = Groq(api_key=api_key)
        
        # Tamil Unicode characters
        self.tamil_chars = [
            'ட', 'ற', 'ண', 'ழ', 'ற்', 'ன்', 'ம்', 'ய்', 'த்',
            'உ', 'ஆ', 'ஈ', 'எ', 'ஏ', 'ஐ', 'ஒ', 'ஓ', 'ஔ', 'க்', 'ங்'
        ]
        
        # ADD THIS: Load trained Tamil model
        try:
            self.tamil_model = get_tamil_model()
            logger.success("✓ Tamil Language Model loaded")
        except Exception as e:
            logger.warning(f"Could not load Tamil model: {e}")
            self.tamil_model = None
        
        logger.success("✓ Tamil Speech Processor initialized")
    
    def detect_language(self, text: str) -> str:
        """
        Detect if text is Tamil or English
        Returns: 'ta' (Tamil) or 'en' (English)
        """
        if not text:
            return 'en'
        
        tamil_count = sum(1 for char in text if char in self.tamil_chars)
        
        if tamil_count > len(text) * 0.2:
            logger.info("✓ Language detected: TAMIL")
            return 'ta'
        
        logger.info("✓ Language detected: ENGLISH")
        return 'en'
    
    def translate_tamil_to_english(self, tamil_text: str) -> str:
        """Translate Tamil text to English"""
        try:
            logger.info("Translating Tamil → English")
            
            prompt = f"""Translate the following Tamil text to English. 
Provide ONLY the translation, no explanations.

Tamil text:
{tamil_text}

English translation:"""
            
            response = self.client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=200
            )
            
            translation = response.choices[0].message.content.strip()
            logger.success(f"✓ Translation: {translation[:50]}...")
            return translation
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return tamil_text
    
    def translate_english_to_tamil(self, english_text: str) -> str:
        """Translate English text to Tamil"""
        try:
            logger.info("Translating English → Tamil")
            
            prompt = f"""Translate the following English text to Tamil. 
Provide ONLY the translation in Tamil script, no explanations.

English text:
{english_text}

Tamil translation:"""
            
            response = self.client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=300
            )
            
            translation = response.choices[0].message.content.strip()
            logger.success(f"✓ Tamil translation: {translation[:50]}...")
            return translation
            
        except Exception as e:
            logger.error(f"Tamil translation failed: {e}")
            return english_text
    
    # ADD THIS NEW METHOD: Analyze with trained model
    def analyze_complaint_with_model(self, tamil_text: str) -> dict:
        """
        Analyze Tamil complaint using trained model
        Returns predicted category, intent, and confidence
        """
        if self.tamil_model is None:
            logger.warning("Tamil model not available")
            return {
                'category': 'unknown',
                'intent': 'complaint',
                'confidence': 0.0,
                'keywords': [],
                'method': 'none'
            }
        
        logger.info(f"Analyzing with Tamil model: {tamil_text[:50]}...")
        
        prediction = self.tamil_model.predict(tamil_text)
        
        logger.success(f"✓ Prediction: {prediction['category']} ({prediction['confidence']:.2%})")
        
        return {
            'category': prediction['category'],
            'intent': prediction['intent'],
            'confidence': prediction['confidence'],
            'keywords': prediction['keywords'],
            'method': 'tamil_language_model'
        }
    
    def process_complaint(self, complaint_text: str) -> dict:
        """
        Process complaint in any language
        Returns: Original + English + Tamil versions
        """
        logger.info("Processing complaint")
        
        language = self.detect_language(complaint_text)
        
        if language == 'ta':
            english_version = self.translate_tamil_to_english(complaint_text)
            return {
                'original': complaint_text,
                'language': 'tamil',
                'language_code': 'ta',
                'english': english_version,
                'tamil': complaint_text
            }
        else:
            tamil_version = self.translate_english_to_tamil(complaint_text)
            return {
                'original': complaint_text,
                'language': 'english',
                'language_code': 'en',
                'english': complaint_text,
                'tamil': tamil_version
            }
    
    def prepare_response(self, response_text: str, input_language: str = None) -> dict:
        """
        Prepare response in both languages
        input_language: detected language of original complaint
        """
        logger.info(f"Preparing response for input language: {input_language}")
        
        if input_language == 'ta':
            tamil_response = self.translate_english_to_tamil(response_text)
            return {
                'english': response_text,
                'tamil': tamil_response,
                'language': 'tamil',
                'language_code': 'ta',
                'display_language': 'ta',
                'speak_language': 'ta'
            }
        else:
            tamil_translation = self.translate_english_to_tamil(response_text)
            return {
                'english': response_text,
                'tamil': tamil_translation,
                'language': 'english',
                'language_code': 'en',
                'display_language': 'en',
                'speak_language': 'en'
            }
    
    def get_display_text(self, response_dict: dict) -> tuple:
        """
        Get text to display on screen
        Returns: (text, language_for_display)
        """
        display_lang = response_dict.get('display_language', 'en')
        
        if display_lang == 'ta':
            text = response_dict.get('tamil', response_dict.get('english'))
        else:
            text = response_dict.get('english', response_dict.get('tamil'))
        
        return text, display_lang
    
    def get_speak_text(self, response_dict: dict) -> tuple:
        """
        Get text for text-to-speech
        Returns: (text, language_code_for_tts)
        """
        speak_lang = response_dict.get('speak_language', 'en')
        
        if speak_lang == 'ta':
            text = response_dict.get('tamil', response_dict.get('english'))
            lang_code = 'ta'
        else:
            text = response_dict.get('english', response_dict.get('tamil'))
            lang_code = 'en'
        
        return text, lang_code
    
    def create_full_response(self, routing_result: dict, input_language: str) -> dict:
        """
        Create complete response with all languages
        Takes routing decision and creates appropriate response
        """
        logger.info(f"Creating full response for input language: {input_language}")
        
        department = routing_result.get('department', 'Department')
        priority = routing_result.get('priority', 'Medium')
        category = routing_result.get('category', 'General')
        
        if input_language == 'ta':
            english_base = (
                f"Your complaint has been routed to {department} "
                f"with {priority} priority. "
                f"Category: {category}"
            )
            tamil_response = self.translate_english_to_tamil(english_base)
            
            response_dict = {
                'english': english_base,
                'tamil': tamil_response,
                'language': 'tamil',
                'language_code': 'ta',
                'display_text': tamil_response,
                'speak_text': tamil_response,
                'speak_language': 'ta'
            }
        else:
            english_response = (
                f"Your complaint has been routed to {department} "
                f"with {priority} priority. "
                f"Category: {category}"
            )
            tamil_translation = self.translate_english_to_tamil(english_response)
            
            response_dict = {
                'english': english_response,
                'tamil': tamil_translation,
                'language': 'english',
                'language_code': 'en',
                'display_text': english_response,
                'speak_text': english_response,
                'speak_language': 'en'
            }
        
        logger.success(f"Response created - Language: {input_language}")
        return response_dict


# Global singleton
_tamil_processor_instance = None


def get_tamil_processor(api_key: str = None) -> TamilSpeechProcessor:
    """Get or create singleton instance"""
    global _tamil_processor_instance
    
    if _tamil_processor_instance is None:
        if not api_key:
            api_key = os.getenv('GROQ_API_KEY')
        
        _tamil_processor_instance = TamilSpeechProcessor(api_key=api_key)
    
    return _tamil_processor_instance
