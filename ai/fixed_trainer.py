#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fixed Vietnamese Teacher Trainer - Properly working training pipeline
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
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

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
            trust_remote_code=False
        )
        
        # Configure special tokens
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        if self.tokenizer.bos_token is None:
            self.tokenizer.bos_token = self.tokenizer.eos_token
            
        # Load model
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            dtype=torch.float32,  # Use float32 for M1 Mac compatibility
            low_cpu_mem_usage=True,
            trust_remote_code=False
        )
        
        # Resize token embeddings if needed
        self.model.resize_token_embeddings(len(self.tokenizer))
        
        print(f"✅ Model loaded! Size: ~{self.get_model_size():.1f}MB")
        print(f"📝 Vocab size: {len(self.tokenizer)}")
    
    def get_model_size(self):
        """Calculate model size in MB"""
        if not self.model:
            return 0
        param_size = sum(p.numel() * p.element_size() for p in self.model.parameters())
        buffer_size = sum(b.numel() * b.element_size() for b in self.model.buffers())
        return (param_size + buffer_size) / (1024 * 1024)
    
    def prepare_training_data(self):
        """Prepare Vietnamese teacher conversation data with proper formatting"""
        try:
            with open('premium_teacher_data.txt', 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            print("❌ premium_teacher_data.txt not found!")
            return []
        
        # Parse conversations
        conversations = []
        lines = content.strip().split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if line.startswith('Học viên:'):
                student_msg = line.replace('Học viên:', '').strip()
                
                # Look for teacher response
                if i + 1 < len(lines) and lines[i + 1].strip().startswith('Giáo viên:'):
                    teacher_msg = lines[i + 1].strip().replace('Giáo viên:', '').strip()
                    
                    if student_msg and teacher_msg:
                        # Format as conversation with special tokens
                        formatted_conv = f"<|startoftext|>Học sinh: {student_msg}\nGiáo viên: {teacher_msg}<|endoftext|>"
                        conversations.append(formatted_conv)
                        print(f"✅ Added conversation: {student_msg[:50]}...")
                    
                    i += 2  # Skip both lines
                else:
                    i += 1
            else:
                i += 1
        
        print(f"📚 Prepared {len(conversations)} training conversations")
        
        # Show sample
        if conversations:
            print("Sample conversation:")
            print(f"  {conversations[0][:100]}...")
        
        return conversations
    
    def create_dataset(self, conversations):
        """Create tokenized dataset"""
        if not conversations:
            return None
            
        # Create dataset from conversations
        dataset = Dataset.from_dict({"text": conversations})
        
        def tokenize_function(examples):
            """Tokenize conversations properly"""
            # Tokenize each conversation
            tokenized = self.tokenizer(
                examples["text"],
                truncation=True,
                padding=False,  # Don't pad here
                max_length=512,  # Reasonable length
                add_special_tokens=False  # We already added them
            )
            
            # For causal language modeling, labels = input_ids
            tokenized["labels"] = [ids.copy() for ids in tokenized["input_ids"]]
            
            return tokenized
        
        # Apply tokenization
        print("🔧 Tokenizing dataset...")
        tokenized_dataset = dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=["text"]  # Remove original text column
        )
        
        print(f"✅ Dataset tokenized: {len(tokenized_dataset)} examples")
        return tokenized_dataset
    
    def train_model(self):
        """Train the Vietnamese teacher model"""
        if not self.model or not self.tokenizer:
            self.load_model()
        
        # Prepare data
        conversations = self.prepare_training_data()
        if not conversations:
            print("❌ No training data available!")
            return False
        
        # Create dataset
        train_dataset = self.create_dataset(conversations)
        if not train_dataset:
            print("❌ Failed to create dataset!")
            return False
        
        # Training arguments optimized for M1 Mac
        training_args = TrainingArguments(
            output_dir="./vietnamese_teacher_trained",
            overwrite_output_dir=True,
            num_train_epochs=5,  # More epochs for better learning
            per_device_train_batch_size=1,
            gradient_accumulation_steps=8,  # Effective batch size = 8
            warmup_steps=50,
            logging_steps=10,
            save_steps=100,
            save_total_limit=3,
            prediction_loss_only=True,
            dataloader_num_workers=0,  # Single threaded
            dataloader_pin_memory=False,
            fp16=False,  # Avoid fp16 on M1
            push_to_hub=False,
            report_to=None,  # Disable wandb
            logging_dir=None,
        )
        
        # Data collator for language modeling
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False,  # Causal language modeling
            pad_to_multiple_of=8,  # Optimize for performance
        )
        
        # Create trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            data_collator=data_collator,
            tokenizer=self.tokenizer,
        )
        
        # Start training
        print("🔥 Starting Vietnamese Teacher training...")
        print("This may take 10-20 minutes on M1 Mac...")
        
        try:
            trainer.train()
            
            # Save the trained model
            print("💾 Saving trained model...")
            trainer.save_model()
            self.tokenizer.save_pretrained("./vietnamese_teacher_trained")
            
            print("✅ Training completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Training failed: {e}")
            return False
    
    def load_trained_model(self):
        """Load the trained model"""
        try:
            if os.path.exists("./vietnamese_teacher_trained"):
                print("📦 Loading trained Vietnamese teacher model...")
                
                self.tokenizer = AutoTokenizer.from_pretrained(
                    "./vietnamese_teacher_trained",
                    use_fast=False
                )
                
                self.model = AutoModelForCausalLM.from_pretrained(
                    "./vietnamese_teacher_trained",
                    dtype=torch.float32,
                    low_cpu_mem_usage=True
                )
                
                print("✅ Trained model loaded successfully!")
                return True
            else:
                print("⚠️ No trained model found, loading base model...")
                self.load_model()
                return False
                
        except Exception as e:
            print(f"❌ Error loading trained model: {e}")
            print("🔄 Falling back to base model...")
            self.load_model()
            return False
    
    def generate_response(self, user_input, max_length=150):
        """Generate teacher response"""
        if not self.model or not self.tokenizer:
            if not self.load_trained_model():
                return "Xin lỗi, cô gặp vấn đề kỹ thuật. Em thử lại sau nhé!"
        
        # Format input like training data
        prompt = f"<|startoftext|>Học sinh: {user_input}\nGiáo viên:"
        
        # Tokenize
        inputs = self.tokenizer.encode(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=400
        )
        
        # Generate response
        try:
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=inputs.shape[1] + max_length,
                    num_return_sequences=1,
                    temperature=0.8,
                    do_sample=True,
                    top_p=0.9,
                    top_k=50,
                    repetition_penalty=1.1,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.encode("<|endoftext|>")[0] if "<|endoftext|>" in self.tokenizer.get_vocab() else self.tokenizer.eos_token_id
                )
            
            # Decode response
            generated = self.tokenizer.decode(outputs[0], skip_special_tokens=False)
            
            # Extract teacher response
            if "Giáo viên:" in generated:
                response = generated.split("Giáo viên:")[-1]
                response = response.split("<|endoftext|>")[0]  # Stop at end token
                response = response.strip()
                
                if len(response) > 10:  # Valid response
                    return response
            
            # Fallback response
            return "Em hỏi hay quá! Cô cần suy nghĩ thêm để trả lời em một cách tốt nhất."
            
        except Exception as e:
            print(f"Generation error: {e}")
            return "Xin lỗi em, cô gặp chút vấn đề kỹ thuật. Em có thể hỏi lại không?"

# Flask app
app = Flask(__name__)
CORS(app)

# Global trainer instance
vietnamese_teacher = None

def get_teacher():
    global vietnamese_teacher
    if vietnamese_teacher is None:
        vietnamese_teacher = VietnameseTeacherTrainer()
        vietnamese_teacher.load_trained_model()
    return vietnamese_teacher

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                'error': 'Empty message',
                'response': 'Em hãy nói gì đó để cô có thể giúp em!'
            }), 400
        
        # Generate response
        teacher = get_teacher()
        response = teacher.generate_response(user_message)
        
        return jsonify({
            'response': response,
            'model': 'vietnamese-teacher-trained'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'response': 'Xin lỗi em, cô gặp vấn đề kỹ thuật.'
        }), 500

@app.route('/train', methods=['POST'])
def train():
    """Endpoint to trigger training"""
    try:
        teacher = get_teacher()
        success = teacher.train_model()
        
        if success:
            # Reload the trained model
            teacher.load_trained_model()
            return jsonify({'status': 'Training completed successfully'})
        else:
            return jsonify({'error': 'Training failed'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    trained_model_exists = os.path.exists("./vietnamese_teacher_trained")
    return jsonify({
        'status': 'healthy',
        'model_loaded': vietnamese_teacher is not None,
        'trained_model_available': trained_model_exists
    })

if __name__ == '__main__':
    print("🇻🇳 Vietnamese Teacher AI - Fixed Training Version")
    print("💡 Optimized for M1 Mac with proper tokenization")
    
    # Check if we should train first
    if not os.path.exists("./vietnamese_teacher_trained") or not os.listdir("./vietnamese_teacher_trained"):
        print("\n🔥 No trained model found. Starting training...")
        
        trainer = VietnameseTeacherTrainer()
        success = trainer.train_model()
        
        if success:
            print("✅ Training completed! Starting server...")
        else:
            print("❌ Training failed! Starting with base model...")
    else:
        print("✅ Found existing trained model")
    
    # Start Flask server
    app.run(host='0.0.0.0', port=5001, debug=False)