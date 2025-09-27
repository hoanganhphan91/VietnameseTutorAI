#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vietnamese Teacher Trainer - Complete training pipeline
Optimized for M1 Mac with correct tokenization and data handling
"""

from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    Trainer, 
    TrainingArguments,
    DataCollatorForLanguageModeling
)
from datasets import Dataset
import torch
import os
import json

class VietnameseTeacherTrainer:
    def __init__(self, model_name="NlpHUST/gpt2-vietnamese"):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        
    def load_model(self):
        """Load Vietnamese model with proper configuration"""
        print(f"📦 Loading {self.model_name}...")
        
        # Load tokenizer first
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            use_fast=False,  # Use slow tokenizer for better compatibility
            trust_remote_code=True
        )
        
        # Configure special tokens
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        if self.tokenizer.bos_token is None:
            self.tokenizer.bos_token = self.tokenizer.eos_token
            
        # Load model
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float32,  # Use float32 for M1 Mac compatibility
            low_cpu_mem_usage=True,
            trust_remote_code=True
        )
        
        # Resize embeddings if needed
        self.model.resize_token_embeddings(len(self.tokenizer))
        
        print(f"✅ Model loaded: {self.model.num_parameters():,} parameters")
        print(f"✅ Tokenizer vocab size: {len(self.tokenizer):,}")
        
    def parse_conversations(self, data_file="premium_teacher_data.txt"):
        """Parse Vietnamese teacher conversations from data file"""
        print(f"📖 Parsing conversations from {data_file}...")
        
        conversations = []
        
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # Split by double newlines to get conversation pairs
            pairs = content.split('\n\n')
            
            for pair in pairs:
                if not pair.strip():
                    continue
                    
                lines = [line.strip() for line in pair.strip().split('\n') if line.strip()]
                
                # Look for student-teacher pairs
                student_line = None
                teacher_line = None
                
                for line in lines:
                    if line.startswith('Học viên:') or line.startswith('Học sinh:'):
                        student_line = line.split(':', 1)[1].strip()
                    elif line.startswith('Giáo viên:'):
                        teacher_line = line.split(':', 1)[1].strip()
                
                # If we have both student and teacher lines, add the conversation
                if student_line and teacher_line:
                    conversation_text = f"<|startoftext|>Học sinh: {student_line}\nGiáo viên: {teacher_line}<|endoftext|>"
                    conversations.append(conversation_text)
                    
                    # Debug: Print first few conversations
                    if len(conversations) <= 3:
                        print(f"Sample {len(conversations)}: {conversation_text[:100]}...")
            
            print(f"✅ Parsed {len(conversations)} conversations")
            return conversations
            
        except Exception as e:
            print(f"❌ Error parsing conversations: {e}")
            return []
    
    def prepare_dataset(self, conversations):
        """Prepare dataset with proper tokenization"""
        print("🔧 Preparing dataset...")
        
        def tokenize_function(examples):
            # Tokenize each conversation
            tokenized = self.tokenizer(
                examples['text'],
                truncation=True,
                max_length=512,
                padding='max_length',
                return_tensors='pt'
            )
            
            # For causal language modeling, labels = input_ids
            tokenized['labels'] = tokenized['input_ids'].clone()
            
            return tokenized
        
        # Create dataset from conversations
        dataset = Dataset.from_dict({'text': conversations})
        
        # Apply tokenization
        tokenized_dataset = dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=['text']
        )
        
        print(f"✅ Dataset prepared: {len(tokenized_dataset)} samples")
        return tokenized_dataset
    
    def train_model(self, output_dir="./vietnamese_teacher_trained"):
        """Train the Vietnamese teacher model"""
        print("🚀 Starting Vietnamese Teacher AI Training...")
        
        try:
            # Load model and tokenizer
            self.load_model()
            
            # Parse training data
            conversations = self.parse_conversations()
            if not conversations:
                print("❌ No conversations found!")
                return False
            
            # Prepare dataset
            train_dataset = self.prepare_dataset(conversations)
            
            # Configure training arguments (optimized for M1 Mac)
            training_args = TrainingArguments(
                output_dir=output_dir,
                overwrite_output_dir=True,
                num_train_epochs=3,
                per_device_train_batch_size=1,  # Small batch for M1 Mac
                gradient_accumulation_steps=4,  # Accumulate gradients
                warmup_steps=10,
                logging_steps=1,
                save_steps=50,
                evaluation_strategy="no",
                save_strategy="epoch",
                logging_dir=f"{output_dir}/logs",
                remove_unused_columns=False,
                dataloader_pin_memory=False,  # Better for M1 Mac
                fp16=False,  # Use float32 for M1 Mac
                report_to=None,  # No wandb logging
            )
            
            # Data collator for language modeling
            data_collator = DataCollatorForLanguageModeling(
                tokenizer=self.tokenizer,
                mlm=False,  # Not masked language modeling
                pad_to_multiple_of=None
            )
            
            # Initialize trainer
            trainer = Trainer(
                model=self.model,
                args=training_args,
                train_dataset=train_dataset,
                data_collator=data_collator,
                tokenizer=self.tokenizer,
            )
            
            print("🔥 Training started...")
            
            # Start training
            trainer.train()
            
            # Save the trained model
            print("💾 Saving trained model...")
            trainer.save_model()
            self.tokenizer.save_pretrained(output_dir)
            
            print("✅ Training completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Training error: {e}")
            return False

if __name__ == '__main__':
    print("🇻🇳 Vietnamese Teacher AI Trainer")
    print("💡 Optimized for M1 Mac with proper tokenization")
    
    trainer = VietnameseTeacherTrainer()
    success = trainer.train_model()
    
    if success:
        print("🎉 Training completed successfully!")
    else:
        print("💥 Training failed!")