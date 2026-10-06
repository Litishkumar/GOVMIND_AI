"""
Test Tamil Language Model
Verify predictions are working correctly
"""

from tamil_language_model import get_tamil_model
from loguru import logger
import sys

logger.add("logs/testing.log", rotation="10 MB")

def test_model():
    """Test trained model with sample Tamil texts"""
    
    print("\n" + "="*80)
    print("🧪 TESTING TAMIL LANGUAGE MODEL")
    print("="*80)
    
    try:
        # Load trained model
        print("\n📦 Loading trained model...")
        model = get_tamil_model(model_dir="./tamil_models")
        
        if not model.get_statistics()['model_trained']:
            print("❌ Model not trained!")
            print("   Run: python train_tamil_model.py")
            return False
        
        print("✓ Model loaded successfully")
        
        # Test samples
        test_samples = [
            ("பொது கழிப்பறை அசுத்தம்", "sanitation", "complaint"),
            ("மின்சாரம் வரவில்லை உடனே", "electricity", "emergency"),
            ("தண்ணீர் வருவதில்லை", "water", "complaint"),
            ("சாலையில் பெரிய பொதியல்", "transport", "complaint"),
            ("பாதுகாப்பு சிக்கல் உண்டு", "police", "emergency"),
        ]
        
        print("\n🎯 Testing Predictions:")
        print("="*80)
        
        correct = 0
        intent_correct = 0
        
        for tamil_text, expected_category, expected_intent in test_samples:
            prediction = model.predict(tamil_text)
            
            category_match = prediction['category'].lower() == expected_category.lower()
            intent_match = prediction['intent'].lower() == expected_intent.lower()
            
            is_correct = category_match
            status = "✓" if is_correct else "⚠"
            
            print(f"\n{status} Input: {tamil_text}")
            print(f"   Expected Category: {expected_category}")
            print(f"   Predicted Category: {prediction['category']}")
            print(f"   Expected Intent: {expected_intent}")
            print(f"   Predicted Intent: {prediction['intent']}")
            print(f"   Confidence: {prediction['confidence']:.2%}")
            print(f"   Keywords: {', '.join(prediction['keywords'][:3])}")
            
            if is_correct:
                correct += 1
            if intent_match:
                intent_correct += 1
        
        # Summary
        category_accuracy = (correct / len(test_samples)) * 100
        intent_accuracy = (intent_correct / len(test_samples)) * 100
        
        print("\n" + "="*80)
        print("📊 Test Results")
        print("="*80)
        print(f"✓ Category Accuracy: {correct}/{len(test_samples)} ({category_accuracy:.1f}%)")
        print(f"✓ Intent Accuracy: {intent_correct}/{len(test_samples)} ({intent_accuracy:.1f}%)")
        
        if category_accuracy >= 80:
            print("\n✅ Model Performance: EXCELLENT (≥80%)")
            success = True
        elif category_accuracy >= 60:
            print("\n✅ Model Performance: GOOD (≥60%)")
            success = True
        else:
            print("\n⚠️  Model Performance: NEEDS IMPROVEMENT (<60%)")
            success = False
        
        print("="*80)
        
        if success:
            print("\n✅ Model is ready for integration!")
            print("Next step: Run python main.py to start the system\n")
        else:
            print("\n⚠️  Model needs more training data or tuning")
            print("Add more samples to tamil_training_data.json and retrain\n")
        
        return success
        
    except Exception as e:
        logger.error(f"Testing error: {e}")
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_model()
    sys.exit(0 if success else 1)
