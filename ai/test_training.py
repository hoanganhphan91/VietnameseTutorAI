#!/usr/bin/env python3
"""
Simple test to actually train and verify the Vietnamese Teacher model
"""

import os
import sys
sys.path.append('/Users/Shared/PearBit/VietnameseTutorAI/ai')

from lightweight_trainer import LightweightVietnameseTrainer

def test_training():
    print("🧪 Testing Vietnamese Teacher Training")
    print("=" * 50)
    
    # Remove existing model if any
    if os.path.exists("./vietnamese_teacher_light"):
        import shutil
        shutil.rmtree("./vietnamese_teacher_light")
        print("🗑️ Removed existing empty model folder")
    
    # Create trainer
    trainer = LightweightVietnameseTrainer()
    
    # Test data preparation first
    print("📚 Testing data preparation...")
    training_texts = trainer.prepare_data()
    
    if not training_texts:
        print("❌ FAILED: No training data found!")
        return False
    
    print(f"✅ Found {len(training_texts)} training examples")
    print("Sample training text:")
    print(f"  {training_texts[0][:100]}...")
    
    # Test actual training
    print("\n🔥 Starting REAL training...")
    success = trainer.train_lightweight()
    
    if success:
        print("✅ Training completed!")
        
        # Verify model was saved
        if os.path.exists("./vietnamese_teacher_light") and os.listdir("./vietnamese_teacher_light"):
            print("✅ Model files saved successfully")
            
            # Test generation
            print("\n🧪 Testing generation...")
            response = trainer.generate_response("Em muốn học phát âm")
            print(f"Generated: {response}")
            
            return True
        else:
            print("❌ Model folder empty after training!")
            return False
    else:
        print("❌ Training failed!")
        return False

if __name__ == "__main__":
    os.chdir('/Users/Shared/PearBit/VietnameseTutorAI/ai')
    success = test_training()
    
    if success:
        print("\n🎉 Vietnamese Teacher AI training SUCCESSFUL!")
    else:
        print("\n💥 Vietnamese Teacher AI training FAILED!")