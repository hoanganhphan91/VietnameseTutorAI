#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run Vietnamese Teacher Training
Script to train the model separately from the service
"""

from trainer import VietnameseTeacherTrainer
import os

def main():
    print("🇻🇳 Vietnamese Teacher AI - Training Script")
    print("💡 Optimized for M1 Mac with proper tokenization")
    
    # Check if model already trained
    if os.path.exists("./vietnamese_teacher_trained") and os.listdir("./vietnamese_teacher_trained"):
        response = input("\n⚠️  Trained model already exists. Retrain? (y/N): ")
        if response.lower() != 'y':
            print("🚫 Training cancelled")
            return
    
    # Initialize trainer
    print("\n🔥 Initializing trainer...")
    trainer = VietnameseTeacherTrainer()
    
    # Start training
    success = trainer.train_model()
    
    if success:
        print("\n🎉 Training completed successfully!")
        print("✅ Model saved to ./vietnamese_teacher_trained")
        print("🚀 You can now start the AI service with: python app.py")
    else:
        print("\n💥 Training failed!")
        print("❌ Please check the error messages above")

if __name__ == '__main__':
    main()