"""
GovMind AI - Tamil Language Model
Trainable Tamil speech-to-text and text processing module
Understands Tamil complaints and generates Tamil responses
"""

import os
import json
import pickle
import numpy as np
from pathlib import Path
from loguru import logger
from typing import Dict, Tuple, List
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import LabelEncoder
except ImportError:
    logger.warning("scikit-learn not installed. Install with: pip install scikit-learn")


class TamilLanguageModel:
    """
    Trainable Tamil Language Model
    - Understands Tamil text and speech
    - Classifies complaints in Tamil
    - Detects intent and entities
    - Generates Tamil responses
    """
    
    def __init__(self, model_dir: str = "./tamil_models"):
        """Initialize Tamil Language Model"""
        logger.info("Initializing Tamil Language Model")
        
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
        
        # Tamil-specific vocabularies
        self.tamil_vocabulary = {
            'sanitation': ['கழிப்பறை', 'கழிவு', 'சுத்தம்', 'அசுத்தம்', 'தெருவு', 'சுத்தம்'],
            'electricity': ['மின்சாரம்', 'மின்', 'மின்விசிறி', 'மின்விளக்கு', 'மின்கம்பி', 'ட்ரான்ஸ்ஃபார்மர்'],
            'water': ['நீர்', 'தண்ணீர்', 'குழாய்', 'வெள்ள', 'நீர்வழங்கல்', 'வடிகால்'],
            'transport': ['சாலை', 'பொதியல்', 'போக்குவரவு', 'பேருந்து', 'ஓட்டம்', 'சாலை'],
            'police': ['பாதுகாப்பு', 'தீப்பொறி', 'குற்றம்', 'கடவுளோ', 'கொள்ளை', 'பாதுகாப்பு']
        }
        
        # Intent keywords in Tamil
        self.intent_keywords = {
            'emergency': ['அவசர', 'உடனடி', 'அவசரம்', 'உடனடியாக', 'இப்பொழுது'],
            'complaint': ['பிரச்சனை', 'குறை', 'புகை', 'அதிருப்தி', 'பிரச்சனை'],
            'request': ['கோரிக்கை', 'வேண்டிக்கொள்ளுதல்', 'வேண்டுதல்', 'கோள்', 'வேண்டுதல்'],
            'query': ['கேள்வி', 'கேட்ட', 'அறிய', 'தெரிய', 'தகவல்']
        }
        
        # Initialize models
        self.classifier = None
        self.label_encoder = LabelEncoder()
        self.vectorizer = TfidfVectorizer(max_features=100, lowercase=False)
        
        # Training data storage
        self.training_data = []
        self.training_labels = []
        
        # Load existing model if available
        self.load_model()
        
        logger.success("✓ Tamil Language Model initialized")
    
    def add_training_data(self, tamil_text: str, intent: str, category: str) -> None:
        """
        Add training data for the model
        
        Args:
            tamil_text: Tamil complaint text
            intent: Intent (emergency, complaint, request, query)
            category: Category (sanitation, electricity, water, transport, police)
        """
        logger.info(f"Adding training data: {tamil_text[:50]}...")
        
        self.training_data.append({
            'text': tamil_text,
            'intent': intent,
            'category': category,
            'timestamp': datetime.now().isoformat()
        })
    
    def load_training_data_from_file(self, filepath: str) -> None:
        """
        Load training data from JSON file
        Format: [{"text": "Tamil text", "intent": "...", "category": "..."}, ...]
        """
        try:
            logger.info(f"Loading training data from {filepath}")
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.training_data.extend(data)
            logger.success(f"✓ Loaded {len(data)} training examples")
            
        except Exception as e:
            logger.error(f"Failed to load training data: {e}")
    
    def train(self) -> None:
        """Train the Tamil Language Model"""
        if not self.training_data:
            logger.warning("No training data available")
            return
        
        logger.info(f"Training Tamil Language Model with {len(self.training_data)} examples")
        
        try:
            # Extract texts and labels
            texts = [item['text'] for item in self.training_data]
            categories = [item['category'] for item in self.training_data]
            
            # Encode labels
            self.label_encoder.fit(categories)
            y = self.label_encoder.transform(categories)
            
            # Vectorize texts
            X = self.vectorizer.fit_transform(texts)
            
            # Train classifier
            self.classifier = MultinomialNB()
            self.classifier.fit(X, y)
            
            logger.success("✓ Model trained successfully")
            self.save_model()
            
        except Exception as e:
            logger.error(f"Training failed: {e}")
    
    def predict(self, tamil_text: str) -> Dict:
        """
        Predict category and intent from Tamil text
        
        Args:
            tamil_text: Tamil complaint text
            
        Returns:
            {category, intent, confidence, keywords}
        """
        logger.info(f"Predicting for: {tamil_text[:50]}...")
        
        if self.classifier is None:
            logger.warning("Model not trained yet, using keyword matching")
            return self._keyword_predict(tamil_text)
        
        try:
            # Vectorize input
            X = self.vectorizer.transform([tamil_text])
            
            # Predict category
            category_idx = self.classifier.predict(X)[0]
            category = self.label_encoder.inverse_transform([category_idx])[0]
            
            # Get confidence
            probabilities = self.classifier.predict_proba(X)[0]
            confidence = float(max(probabilities))
            
            # Detect intent
            intent = self._detect_intent(tamil_text)
            
            # Extract keywords
            keywords = self._extract_keywords(tamil_text, category)
            
            result = {
                'category': category,
                'intent': intent,
                'confidence': confidence,
                'keywords': keywords,
                'method': 'trained_model'
            }
            
            logger.success(f"✓ Prediction: {category} ({confidence:.2%})")
            return result
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return self._keyword_predict(tamil_text)
    
    def _keyword_predict(self, tamil_text: str) -> Dict:
        """Fallback keyword-based prediction"""
        logger.info("Using keyword-based prediction")
        
        tamil_lower = tamil_text.lower()
        
        # Find matching category
        category = 'general'
        max_matches = 0
        
        for cat, keywords in self.tamil_vocabulary.items():
            matches = sum(1 for kw in keywords if kw in tamil_lower)
            if matches > max_matches:
                max_matches = matches
                category = cat
        
        intent = self._detect_intent(tamil_text)
        keywords = self._extract_keywords(tamil_text, category)
        
        confidence = (max_matches / 5) if max_matches > 0 else 0.3
        
        return {
            'category': category,
            'intent': intent,
            'confidence': min(confidence, 0.95),
            'keywords': keywords,
            'method': 'keyword_matching'
        }
    
    def _detect_intent(self, tamil_text: str) -> str:
        """Detect intent from Tamil text"""
        tamil_lower = tamil_text.lower()
        
        for intent, keywords in self.intent_keywords.items():
            if any(kw in tamil_lower for kw in keywords):
                return intent
        
        return 'complaint'  # Default intent
    
    def _extract_keywords(self, tamil_text: str, category: str) -> List[str]:
        """Extract relevant keywords"""
        tamil_lower = tamil_text.lower()
        keywords = []
        
        # Extract from vocabulary
        if category in self.tamil_vocabulary:
            for kw in self.tamil_vocabulary[category]:
                if kw.lower() in tamil_lower:
                    keywords.append(kw)
        
        # Extract common words
        words = tamil_text.split()
        for word in words:
            if len(word) > 3 and word not in keywords:
                keywords.append(word)
        
        return keywords[:5]  # Return top 5
    
    def save_model(self) -> None:
        """Save trained model to disk"""
        try:
            logger.info("Saving model...")
            
            model_file = self.model_dir / 'tamil_model.pkl'
            
            model_data = {
                'classifier': self.classifier,
                'vectorizer': self.vectorizer,
                'label_encoder': self.label_encoder,
                'training_data': self.training_data,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(model_file, 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.success(f"✓ Model saved to {model_file}")
            
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
    
    def load_model(self) -> None:
        """Load trained model from disk"""
        try:
            model_file = self.model_dir / 'tamil_model.pkl'
            
            if not model_file.exists():
                logger.info("No existing model found")
                return
            
            logger.info(f"Loading model from {model_file}...")
            
            with open(model_file, 'rb') as f:
                model_data = pickle.load(f)
            
            self.classifier = model_data.get('classifier')
            self.vectorizer = model_data.get('vectorizer')
            self.label_encoder = model_data.get('label_encoder')
            self.training_data = model_data.get('training_data', [])
            
            logger.success(f"✓ Model loaded (trained: {model_data['timestamp']})")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
    
    def generate_tamil_response(self, prediction: Dict, routing_result: Dict) -> str:
        """
        Generate Tamil response based on prediction and routing
        
        Args:
            prediction: Prediction dictionary from predict()
            routing_result: Routing decision from main system
            
        Returns:
            Tamil response text
        """
        logger.info("Generating Tamil response")
        
        # Tamil response templates
        response_templates = {
            'emergency': "உங்கள் அவசர புகைர் {department} துறைக்கு உடனடியாக அனுப்பப்பட்டுள்ளது.",
            'complaint': "உங்கள் புகைர் {department} துறைக்கு {priority} முன்னுரிமையுடன் அனுப்பப்பட்டுள்ளது.",
            'request': "உங்கள் கோரிக்கை {department} துறைக்கு {priority} முன்னுரிமையுடன் பதிவு செய்யப்பட்டுள்ளது.",
            'query': "உங்கள் கேள்விக்கான விசாரணை {department} துறைக்கு அனுப்பப்பட்டுள்ளது."
        }
        
        intent = prediction.get('intent', 'complaint')
        template = response_templates.get(intent, response_templates['complaint'])
        
        response = template.format(
            department=routing_result.get('department', 'தகுந்த'),
            priority=self._get_tamil_priority(routing_result.get('priority', 'Medium'))
        )
        
        logger.success(f"✓ Tamil response generated: {response[:50]}...")
        return response
    
    def _get_tamil_priority(self, english_priority: str) -> str:
        """Convert English priority to Tamil"""
        priority_map = {
            'Critical': 'அவசரம்',
            'High': 'உயர்',
            'Medium': 'நடுத்தர',
            'Low': 'குறைந்த'
        }
        return priority_map.get(english_priority, 'நடுத்தர')
    
    def get_statistics(self) -> Dict:
        """Get model statistics"""
        return {
            'training_examples': len(self.training_data),
            'categories': len(set(item['category'] for item in self.training_data)),
            'intents': len(set(item['intent'] for item in self.training_data)),
            'model_trained': self.classifier is not None,
            'model_dir': str(self.model_dir)
        }


# Global singleton
_tamil_model_instance = None


def get_tamil_model(model_dir: str = "./tamil_models") -> TamilLanguageModel:
    """Get or create singleton instance of Tamil Language Model"""
    global _tamil_model_instance
    
    if _tamil_model_instance is None:
        _tamil_model_instance = TamilLanguageModel(model_dir=model_dir)
    
    return _tamil_model_instance


if __name__ == "__main__":
    """Test and train Tamil Language Model"""
    logger.add("logs/tamil_model_test.log", rotation="1 MB")
    
    # Initialize model
    model = get_tamil_model()
    
    # Add sample training data
    training_samples = [
        {
            'text': 'பொது கழிப்பறை மிகவும் அசுத்தமாக உள்ளது',
            'intent': 'complaint',
            'category': 'sanitation'
        },
        {
            'text': 'எங்கள் தெருவில் சுத்தம் செய்ய வேண்டும்',
            'intent': 'request',
            'category': 'sanitation'
        },
        {
            'text': 'மின்சாரம் வரவில்லை, அவசரம்',
            'intent': 'emergency',
            'category': 'electricity'
        },
        {
            'text': 'தண்ணீர் வருவதில்லை பல நாட்களாக',
            'intent': 'complaint',
            'category': 'water'
        },
        {
            'text': 'சாலையில் பெரிய பொதியல் உள்ளது',
            'intent': 'complaint',
            'category': 'transport'
        }
    ]
    
    print("\n" + "="*80)
    print("TAMIL LANGUAGE MODEL - TEST & TRAIN")
    print("="*80)
    
    # Add training data
    print("\n📚 Adding training data...")
    for sample in training_samples:
        model.add_training_data(sample['text'], sample['intent'], sample['category'])
    print(f"✓ Added {len(training_samples)} samples")
    
    # Train model
    print("\n🤖 Training model...")
    model.train()
    
    # Test predictions
    print("\n🧪 Testing predictions...")
    test_texts = [
        'கழிப்பறை சுத்தம் செய்ய வேண்டும்',
        'மின்விளக்கு வேலை செய்யவில்லை',
        'நீர் பிரச்சனை உண்டு'
    ]
    
    for text in test_texts:
        print(f"\nTest: {text}")
        prediction = model.predict(text)
        print(f"Category: {prediction['category']}")
        print(f"Intent: {prediction['intent']}")
        print(f"Confidence: {prediction['confidence']:.2%}")
    
    # Show statistics
    print("\n📊 Model Statistics:")
    stats = model.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n" + "="*80)
    print("✓ Tamil Language Model ready!")
    print("="*80)