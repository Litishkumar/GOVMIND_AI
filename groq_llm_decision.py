"""
GovMind AI Module - GROQ LLM Decision Engine with Multi-Language Support
Supports Tamil, English, and other languages for input and output
FULLY FIXED VERSION - Updated model + Proper Tamil response
"""

import json
import re
import os
from typing import Dict, Optional, Tuple
import requests
from loguru import logger
from groq import Groq
from enum import Enum


class Language(Enum):
    """Supported languages"""
    ENGLISH = "en"
    TAMIL = "ta"
    TELUGU = "te"
    KANNADA = "kn"
    MALAYALAM = "ml"
    HINDI = "hi"


class GroqLLMDecisionEngine:
    """
    Groq LLM interface with multi-language support.
    Handles input in any language and responds in the same language.
    
    Supports:
    - Tamil (தமிழ்)
    - English
    - Telugu
    - Kannada
    - Malayalam
    - Hindi
    """
    
    def __init__(self, 
                 api_key: str = None,
                 model_name: str = "llama-3.1-70b-versatile",  # UPDATED MODEL
                 default_language: Language = Language.ENGLISH):
        """
        Initialize Multi-Language Groq LLM engine
        
        Args:
            api_key: Groq API key (optional if in environment)
            model_name: Model to use (default: llama-3.1-70b-versatile - active model)
            default_language: Default language for responses
        """
        logger.info(f"Initializing Multi-Language LLM Engine: {model_name}")
        
        # Get API key from parameter or environment
        if not api_key:
            api_key = os.getenv('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')
        
        if not api_key:
            logger.error("❌ GROQ_API_KEY not found!")
            logger.error("Set it with: export GROQ_API_KEY='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'")
            raise ValueError("Groq API key is required")
        
        self.api_key = api_key
        self.model_name = model_name
        self.default_language = default_language
        
        # Initialize Groq client
        try:
            self.client = Groq(api_key=api_key)
            logger.success(f"✓ Groq client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Groq: {e}")
            raise
        
        # Language detection mapping
        self.language_indicators = {
            Language.TAMIL: ['ட', 'ற', 'ண', 'ழ', 'ற்', 'ன்', 'ம்', 'ய்', 'த்', 'உ', 'ஆ', 'ஈ', 'எ', 'ஏ', 'ஐ', 'ஒ', 'ஓ'],
            Language.TELUGU: ['ఆ', 'ఇ', 'ఉ', 'ఎ', 'ఏ', 'ఐ', 'ఒ', 'ఓ'],
            Language.KANNADA: ['ಅ', 'ಆ', 'ಇ', 'ಈ', 'ಉ', 'ಊ', 'ಋ'],
            Language.MALAYALAM: ['അ', 'ആ', 'ഇ', 'ഈ', 'ഉ', 'ൂ'],
            Language.HINDI: ['अ', 'आ', 'इ', 'ई', 'उ', 'ऊ'],
        }
        
        self._verify_connection()
        
        logger.success("Multi-Language LLM Engine ready")
    
    def _verify_connection(self) -> bool:
        """Verify Groq API connection"""
        try:
            logger.info("Verifying Groq API connection...")
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": "Test"}
                ],
                max_tokens=10,
                temperature=0.1
            )
            
            if response.choices[0].message.content:
                logger.success(f"✓ Groq API connected. Model: {self.model_name}")
                return True
            
        except Exception as e:
            logger.error(f"Cannot connect to Groq API: {e}")
            raise ConnectionError(f"Groq API unavailable: {e}")
    
    def detect_language(self, text: str) -> Language:
        """
        Detect the language of input text.
        
        Args:
            text: Input text
            
        Returns:
            Detected Language enum
        """
        if not text:
            return self.default_language
        
        # Check for language indicators
        for language, indicators in self.language_indicators.items():
            count = sum(1 for char in text if char in indicators)
            # If more than 20% of text contains language indicators
            if count > len(text) * 0.2:
                logger.info(f"✓ Detected language: {language.name}")
                return language
        
        # Default to English if no indicators found
        logger.info("No language indicators found, using default language: ENGLISH")
        return self.default_language
    
    def translate_to_english(self, text: str, source_language: Language) -> str:
        """
        Translate text to English using Groq.
        
        Args:
            text: Text to translate
            source_language: Source language
            
        Returns:
            Translated text in English
        """
        if source_language == Language.ENGLISH:
            return text
        
        try:
            logger.info(f"Translating from {source_language.name} to English")
            
            prompt = f"""Translate the following {source_language.name} text to English. 
Provide ONLY the translation, no explanations or extra text.

{source_language.name} text:
{text}

English translation only:"""
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=200
            )
            
            translated = response.choices[0].message.content.strip()
            logger.success(f"✓ Translation complete: {translated[:50]}...")
            return translated
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return text  # Return original if translation fails
    
    def translate_to_language(self, text: str, target_language: Language) -> str:
        """
        Translate English text to target language using Groq.
        
        Args:
            text: English text to translate
            target_language: Target language
            
        Returns:
            Translated text
        """
        if target_language == Language.ENGLISH:
            return text
        
        try:
            logger.info(f"Translating from English to {target_language.name}")
            
            prompt = f"""Translate the following English text to {target_language.name}. 
Provide ONLY the translation in {target_language.name} script, no explanations or extra text.

English text:
{text}

{target_language.name} translation only:"""
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=300
            )
            
            translated = response.choices[0].message.content.strip()
            logger.success(f"✓ Translation to {target_language.name} complete: {translated[:50]}...")
            return translated
            
        except Exception as e:
            logger.error(f"Translation to {target_language.name} failed: {e}")
            return text  # Return original if translation fails
    
    def _extract_json(self, text: str) -> Optional[Dict]:
        """Extract JSON from response"""
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    pass
            
            code_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
            if code_match:
                try:
                    return json.loads(code_match.group(1))
                except json.JSONDecodeError:
                    pass
            
            logger.warning("Could not extract JSON from response")
            return None
    
    def generate_routing_decision_fast(self,
                                      complaint_text: str,
                                      policy_context: str,
                                      department_name: str,
                                      suggested_priority: str,
                                      temperature: float = 0.3,
                                      max_tokens: int = 500) -> Dict[str, any]:
        """
        Fast LLM decision generation using Groq API.
        
        Args:
            complaint_text: Complaint description
            policy_context: Compact policy context
            department_name: Pre-identified department
            suggested_priority: Pre-analyzed priority level
            temperature: Sampling temperature (lower = more deterministic)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Routing decision JSON with category, department, priority, reason
        """
        try:
            logger.info("Generating LLM decision using Groq")
            
            # COMPACT PROMPT - Optimized for Groq
            prompt = f"""Route this complaint to the appropriate department.

Complaint: {complaint_text}

Department: {department_name}
Suggested Priority: {suggested_priority}

Policy Guidelines: {policy_context}

Respond with ONLY valid JSON (no markdown, no extra text):
{{
  "category": "brief category name",
  "department": "{department_name}",
  "priority": "{suggested_priority}",
  "reason": "1-2 sentence justification"
}}"""

            logger.debug(f"Prompt length: {len(prompt)} chars")
            
            # Call Groq API
            logger.info("Calling Groq API...")
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=0.9,
                stop=None
            )
            
            generated_text = response.choices[0].message.content
            
            logger.debug(f"Generated response: {generated_text[:150]}...")
            
            # Extract JSON
            decision_json = self._extract_json(generated_text)
            
            if decision_json and all(k in decision_json for k in ['category', 'department', 'priority', 'reason']):
                logger.success("✓ LLM decision generated successfully")
                return decision_json
            
            # Fallback if JSON extraction fails
            logger.warning("Using fallback decision - JSON extraction failed")
            return self._construct_fallback(
                complaint_text,
                department_name,
                suggested_priority,
                "LLM response incomplete"
            )
            
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            return self._construct_fallback(
                complaint_text,
                department_name,
                suggested_priority,
                str(e)
            )
    
    def generate_routing_decision_multilingual(self,
                                              complaint_text: str,
                                              policy_context: str,
                                              department_name: str,
                                              suggested_priority: str,
                                              response_language: Optional[Language] = None,
                                              temperature: float = 0.3,
                                              max_tokens: int = 500) -> Dict[str, any]:
        """
        Generate routing decision with automatic language detection and translation.
        FIXED: Properly detects and responds in Tamil
        
        Args:
            complaint_text: Complaint in any supported language
            policy_context: Policy context
            department_name: Department name
            suggested_priority: Priority level
            response_language: Language for response (auto-detected if None)
            temperature: Sampling temperature
            max_tokens: Max tokens to generate
            
        Returns:
            Routing decision with Tamil/English response
        """
        try:
            logger.info("Generating multilingual routing decision")
            
            # Detect input language
            input_language = self.detect_language(complaint_text)
            logger.info(f"✓ Input language detected: {input_language.name}")
            
            # Determine response language
            if response_language is None:
                response_language = input_language
                logger.info(f"✓ Response language auto-set to: {response_language.name}")
            else:
                logger.info(f"✓ Response language forced to: {response_language.name}")
            
            # Translate complaint to English for processing
            if input_language != Language.ENGLISH:
                complaint_english = self.translate_to_english(complaint_text, input_language)
                logger.info(f"✓ Translated to English: {complaint_english[:50]}...")
            else:
                complaint_english = complaint_text
            
            # Generate decision in English using LLM
            logger.info("Generating decision in English using LLM...")
            
            decision_json = self.generate_routing_decision_fast(
                complaint_text=complaint_english,
                policy_context=policy_context,
                department_name=department_name,
                suggested_priority=suggested_priority,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Translate response to target language if needed
            if response_language != Language.ENGLISH:
                logger.info(f"✓ Translating response to {response_language.name}...")
                
                # Translate category
                original_category = decision_json['category']
                translated_category = self.translate_to_language(original_category, response_language)
                decision_json['category'] = translated_category
                logger.info(f"  Category: {original_category} → {translated_category}")
                
                # Translate reason
                original_reason = decision_json['reason']
                translated_reason = self.translate_to_language(original_reason, response_language)
                decision_json['reason'] = translated_reason
                logger.info(f"  Reason: {original_reason[:40]}... → {translated_reason[:40]}...")
                
                logger.success(f"✓ Response translated to {response_language.name}")
            
            # Add language metadata
            decision_json['input_language'] = input_language.name
            decision_json['response_language'] = response_language.name
            
            logger.success("✓ Multilingual decision generated successfully")
            return decision_json
            
        except Exception as e:
            logger.error(f"Multilingual decision generation failed: {e}")
            logger.exception("Full traceback:")
            return self._construct_fallback(
                complaint_text,
                department_name,
                suggested_priority,
                str(e)
            )
    
    def _construct_fallback(self,
                           complaint_text: str,
                           department_name: str,
                           suggested_priority: str,
                           error_info: str) -> Dict[str, any]:
        """Construct fallback decision"""
        logger.warning("Constructing fallback decision")
        
        complaint_lower = complaint_text.lower()
        
        # Simple categorization
        if any(word in complaint_lower for word in ['bill', 'payment', 'charge', 'கட்டணம்', 'பணம்']):
            category = "Billing Issue"
        elif any(word in complaint_lower for word in ['emergency', 'urgent', 'critical', 'அவசர']):
            category = "Emergency Response"
        elif any(word in complaint_lower for word in ['not working', 'broken', 'outage', 'வேலை', 'உடைந்த']):
            category = "Service Outage"
        else:
            category = "Service Request"
        
        return {
            "category": category,
            "department": department_name,
            "priority": suggested_priority,
            "reason": f"Routed based on analysis. Error: {error_info}",
            "input_language": "unknown",
            "response_language": "unknown"
        }
    
    def generate_with_retry(self,
                           complaint_text: str,
                           policy_context: str,
                           department_name: str,
                           suggested_priority: str,
                           max_retries: int = 2) -> Dict[str, any]:
        """
        Generate with retry mechanism.
        
        Args:
            complaint_text: Complaint description
            policy_context: Policy context
            department_name: Department
            suggested_priority: Priority level
            max_retries: Maximum retry attempts
            
        Returns:
            Decision JSON
        """
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    logger.info(f"Retry attempt {attempt}/{max_retries}")
                
                decision = self.generate_routing_decision_fast(
                    complaint_text,
                    policy_context,
                    department_name,
                    suggested_priority,
                    temperature=0.3 + (attempt * 0.1)
                )
                
                if all(k in decision for k in ['category', 'department', 'priority', 'reason']):
                    return decision
                    
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt == max_retries:
                    return self._construct_fallback(
                        complaint_text,
                        department_name,
                        suggested_priority,
                        "Max retries exceeded"
                    )
        
        return self._construct_fallback(
            complaint_text,
            department_name,
            suggested_priority,
            "Unknown error"
        )
    
    def batch_generate_decisions(self,
                                complaints: list,
                                policy_context: str,
                                max_retries: int = 2) -> list:
        """
        Generate decisions for multiple complaints.
        
        Args:
            complaints: List of dicts with 'text', 'department', 'priority'
            policy_context: Shared policy context
            max_retries: Max retries per complaint
            
        Returns:
            List of decision JSONs
        """
        logger.info(f"Processing batch of {len(complaints)} complaints")
        
        decisions = []
        for idx, complaint in enumerate(complaints, 1):
            try:
                logger.info(f"Processing complaint {idx}/{len(complaints)}")
                
                decision = self.generate_with_retry(
                    complaint_text=complaint.get('text', ''),
                    policy_context=policy_context,
                    department_name=complaint.get('department', 'Unknown'),
                    suggested_priority=complaint.get('priority', 'Medium'),
                    max_retries=max_retries
                )
                decisions.append(decision)
                
            except Exception as e:
                logger.error(f"Failed to process complaint {idx}: {e}")
                decisions.append(self._construct_fallback(
                    complaint.get('text', ''),
                    complaint.get('department', 'Unknown'),
                    complaint.get('priority', 'Medium'),
                    f"Batch processing error: {e}"
                ))
        
        logger.success(f"Batch processing complete. Processed {len(decisions)} complaints")
        return decisions
    
    def get_supported_languages(self) -> list:
        """Get list of supported languages"""
        return [lang.name for lang in Language]


# Global singleton
_groq_engine_instance = None


def get_groq_engine(api_key: str = None) -> GroqLLMDecisionEngine:
    """
    Get or create singleton instance of Groq LLM Engine.
    
    Args:
        api_key: Groq API key (optional if in environment)
        
    Returns:
        GroqLLMDecisionEngine instance
    """
    global _groq_engine_instance
    
    if _groq_engine_instance is None:
        if not api_key:
            api_key = os.getenv('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')
            if not api_key:
                logger.error("❌ GROQ_API_KEY not found in environment")
                raise ValueError("Groq API key not provided and GROQ_API_KEY env var not set")
        
        logger.info(f"Creating Groq LLM Engine instance")
        _groq_engine_instance = GroqLLMDecisionEngine(api_key=api_key)
    
    return _groq_engine_instance


if __name__ == "__main__":
    import time
    
    logger.add("logs/groq_llm_test.log", rotation="1 MB")
    
    try:
        api_key = os.getenv('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')
        if not api_key:
            raise ValueError("Please set GROQ_API_KEY environment variable")
        
        # Initialize engine
        engine = get_groq_engine(api_key=api_key)
        
        print("\n" + "="*80)
        print("GROQ LLM ENGINE TEST")
        print("="*80)
        
        # Test case 1: Emergency complaint (English)
        complaint1 = "Emergency power outage affecting hospital operations"
        context1 = "Department: Electricity Board\nPolicy: Emergency repairs prioritized within 30 minutes"
        
        print(f"\n📋 Test 1 - Emergency Complaint (English)")
        print(f"Complaint: {complaint1}")
        
        start = time.time()
        decision1 = engine.generate_routing_decision_fast(
            complaint_text=complaint1,
            policy_context=context1,
            department_name="Electricity Board",
            suggested_priority="High"
        )
        duration1 = time.time() - start
        
        print(f"✓ Decision generated in {duration1:.2f}s")
        print(f"Category: {decision1['category']}")
        print(f"Priority: {decision1['priority']}")
        
        # Test case 2: Tamil complaint with Tamil response
        print(f"\n" + "-"*80)
        complaint2 = "பொது கழிப்பறை மிகவும் அசுத்தமாக உள்ளது"
        context2 = "Municipal Sanitation: Public facility complaints priority medium"
        
        print(f"\n📋 Test 2 - Tamil Complaint (Tamil Response)")
        print(f"Complaint: {complaint2}")
        
        start = time.time()
        decision2 = engine.generate_routing_decision_multilingual(
            complaint_text=complaint2,
            policy_context=context2,
            department_name="Municipal Sanitation",
            suggested_priority="Medium",
            response_language=Language.TAMIL
        )
        duration2 = time.time() - start
        
        print(f"✓ Decision generated in {duration2:.2f}s")
        print(f"Input Language: {decision2['input_language']}")
        print(f"Response Language: {decision2['response_language']}")
        print(f"Category (Tamil): {decision2['category']}")
        print(f"Reason (Tamil): {decision2['reason']}")
        
        # Summary
        print(f"\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        print(f"Test 1 (English): {duration1:.2f}s")
        print(f"Test 2 (Tamil): {duration2:.2f}s")
        print(f"Average: {(duration1 + duration2)/2:.2f}s")
        print("✓ All tests passed!")
        
    except ValueError as e:
        print(f"\n❌ Error: {e}")
    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"\n❌ Error: {e}")