"""
Train Tamil Language Model
Run this script to train the model with provided dataset
"""

from tamil_language_model import get_tamil_model
from loguru import logger
import sys

# Setup logging
logger.add("logs/training.log", rotation="10 MB")

def train_model():
    """Train Tamil Language Model"""
    
    print("\n" + "="*80)
    print("🤖 TRAINING TAMIL LANGUAGE MODEL")
    print("="*80)
    
    try:
        # Initialize model
        print("\n📦 Initializing model...")
        model = get_tamil_model(model_dir="./tamil_models")
        print("✓ Model initialized")
        
        # Load training data
        print("\n📚 Loading training data from tamil_training_data.json...")
        try:
            model.load_training_data_from_file("tamil_training_data.json")
            stats = model.get_statistics()
            print(f"✓ Loaded {stats['training_examples']} training examples")
            print(f"  Categories: {stats['categories']}")
            print(f"  Intents: {stats['intents']}")
        except FileNotFoundError:
            print("❌ Error: tamil_training_data.json not found!")
            print("   Make sure tamil_training_data.json is in the same directory")
            return False
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
        
        # Train model
        print("\n🔧 Training model...")
        print("   (This may take a moment...)")
        try:
            model.train()
            print("✓ Model trained successfully!")
        except Exception as e:
            print(f"❌ Training failed: {e}")
            return False
        
        # Show final statistics
        print("\n📊 Training Complete!")
        final_stats = model.get_statistics()
        print(f"  ✓ Training Examples: {final_stats['training_examples']}")
        print(f"  ✓ Categories: {final_stats['categories']}")
        print(f"  ✓ Intents: {final_stats['intents']}")
        print(f"  ✓ Model Trained: {final_stats['model_trained']}")
        print(f"  ✓ Model Location: {final_stats['model_dir']}")
        
        print("\n" + "="*80)
        print("✅ SUCCESS! Model saved to tamil_models/tamil_model.pkl")
        print("="*80)
        print("\nNext step: Run test_tamil_model.py to test the trained model\n")
        
        return True
        
    except Exception as e:
        logger.error(f"Training error: {e}")
        print(f"\n❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = train_model()
    sys.exit(0 if success else 1)
