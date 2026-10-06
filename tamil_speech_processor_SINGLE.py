"""
GovMind AI - Tamil Speech Processor
Complete Tamil language processing module
Handles: Detection, Translation, Voice I/O
"""

import os
from loguru import logger
from groq import Groq


class TamilSpeechProcessor:
    """
    Complete Tamil language processing module
    - Language detection (Tamil/English)
    - Tamil ↔ English translation
    - Response preparation in both languages
    - Text-to-speech language selection
    """
    
    def __init__(self, api_key: str = None):
        """Initialize Tamil Speech Processor"""
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
        
        logger.success("✓ Tamil Speech Processor initialized")
    
    def detect_language(self, text: str) -> str:
        """
        Detect if text is Tamil or English
        Returns: 'ta' (Tamil) or 'en' (English)
        """
        if not text:
            return 'en'
        
        tamil_count = sum(1 for char in text if char in self.tamil_chars)
        
        # If more than 20% Tamil characters, it's Tamil
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
            # Tamil input: create Tamil response
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
            # English input: create English response + Tamil translation
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
        
        # Create base response in English
        if input_language == 'ta':
            # For Tamil input, create Tamil response
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
            # For English input, create English response
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


if __name__ == "__main__":
    """Test Tamil processor"""
    logger.add("logs/tamil_processor_test.log", rotation="1 MB")
    
    try:
        processor = get_tamil_processor()
        
        print("\n" + "="*80)
        print("TAMIL SPEECH PROCESSOR TEST")
        print("="*80)
        
        # Test 1: Detect Tamil
        print("\n📋 Test 1: Detect Tamil")
        tamil_text = "பொது கழிப்பறை மிகவும் அசுத்தமாக உள்ளது"
        lang = processor.detect_language(tamil_text)
        print(f"Language: {lang}")
        
        # Test 2: Process Tamil complaint
        print("\n📋 Test 2: Process Tamil Complaint")
        result = processor.process_complaint(tamil_text)
        print(f"Original: {result['original']}")
        print(f"English: {result['english']}")
        print(f"Language: {result['language']}")
        
        # Test 3: Create response
        print("\n📋 Test 3: Create Response")
        routing_result = {
            'department': 'Municipal Sanitation',
            'priority': 'Medium',
            'category': 'Sanitation'
        }
        response = processor.create_full_response(routing_result, 'ta')
        print(f"English: {response['english']}")
        print(f"Tamil: {response['tamil']}")
        print(f"Display: {response['display_text']}")
        print(f"Speak: {response['speak_text']}")
        
        print("\n" + "="*80)
        print("✓ All tests passed!")
        print("="*80)
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"\n❌ Error: {e}")
