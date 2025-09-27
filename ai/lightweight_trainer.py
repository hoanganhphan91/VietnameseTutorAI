#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lightweight Vietnamese Teacher using smaller, smarter models
Optimized for M1 Mac with limited memory
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

# Best lightweight models for Vietnamese
VIETNAMESE_MODELS = {
    "vinai_bartpho": "vinai/bartpho-syllable",  # 400MB - Vietnamese BART
    "phobert_base": "vinai/phobert-base",       # 1.3GB - Vietnamese BERT (for understanding)
    "vietnamese_gpt2": "NlpHUST/gpt2-vietnamese", # 500MB - Vietnamese GPT-2 small
    "bloom_560m": "bigscience/bloom-560m"       # 1.1GB - Multilingual including Vietnamese
}

class LightweightVietnameseTrainer:
    def __init__(self, model_name="NlpHUST/gpt2-vietnamese"):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        
    def load_model(self):
        """Load lightweight Vietnamese model"""
        print(f"📦 Loading {self.model_name}...")
        
        # Load with memory optimization
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            use_fast=True
        )
        
        # Add padding token if not exists
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None,
            low_cpu_mem_usage=True
        )
        
        print(f"✅ Model loaded! Size: ~{self.get_model_size():.1f}MB")
    
    def get_model_size(self):
        """Calculate model size in MB"""
        param_size = sum(p.numel() * p.element_size() for p in self.model.parameters())
        buffer_size = sum(b.numel() * b.element_size() for b in self.model.buffers())
        return (param_size + buffer_size) / (1024 * 1024)
    
    def prepare_data(self):
        """Prepare Vietnamese teacher conversation data"""
        try:
            with open('premium_teacher_data.txt', 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            print("❌ premium_teacher_data.txt not found!")
            return None
        
        # Load tokenizer if not already loaded
        if not self.tokenizer:
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                use_fast=True
            )
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Split into conversations
        conversations = []
        lines = content.strip().split('\n')
        
        current_pair = []
        for line in lines:
            line = line.strip()
            if line.startswith('Học viên:'):
                if current_pair:
                    conversations.append(' '.join(current_pair))
                current_pair = [line]
            elif line.startswith('Giáo viên:') and current_pair:
                current_pair.append(line)
                conversations.append(' '.join(current_pair))
                current_pair = []
        
        # Format for training
        training_texts = []
        for conv in conversations:
            if 'Học viên:' in conv and 'Giáo viên:' in conv:
                # Simple format for small models
                formatted = conv.replace('Học viên:', 'Học sinh:').replace('Giáo viên:', 'Cô giáo:')
                training_texts.append(formatted + self.tokenizer.eos_token)
        
        print(f"📚 Prepared {len(training_texts)} training examples")
        return training_texts
    
    def train_lightweight(self):
        """Train with minimal resource usage"""
        if not self.model or not self.tokenizer:
            self.load_model()
            
        training_texts = self.prepare_data()
        if not training_texts:
            return False
        
        # Create dataset
        dataset = Dataset.from_dict({"text": training_texts})
        
        def tokenize_function(examples):
            # Tokenize the text properly
            tokenized = self.tokenizer(
                examples["text"],
                truncation=True,
                padding=False,  # Don't pad here, let data collator handle it
                max_length=256,
                return_tensors=None  # Return lists, not tensors
            )
            # For causal language modeling, labels are the same as input_ids
            tokenized["labels"] = tokenized["input_ids"].copy()
            return tokenized
        
        tokenized_dataset = dataset.map(tokenize_function, batched=True)
        
        # Lightweight training arguments
        training_args = TrainingArguments(
            output_dir="./vietnamese_teacher_light",
            overwrite_output_dir=True,
            num_train_epochs=3,
            per_device_train_batch_size=1,  # Very small batch
            gradient_accumulation_steps=4,
            warmup_steps=10,
            logging_steps=5,
            save_steps=50,
            eval_steps=50,
            save_total_limit=2,
            prediction_loss_only=True,
            remove_unused_columns=False,
            dataloader_pin_memory=False,  # Save memory
            fp16=False,  # Avoid fp16 issues on M1
            dataloader_num_workers=0,  # Single threaded
        )
        
        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False,  # Causal LM, not masked LM
        )
        
        # Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            data_collator=data_collator,
            train_dataset=tokenized_dataset,
        )
        
        print("🔥 Starting lightweight training...")
        trainer.train()
        
        # Save model
        trainer.save_model()
        self.tokenizer.save_pretrained("./vietnamese_teacher_light")
        
        print("✅ Training completed!")
        return True
    
    def generate_response(self, user_input, max_length=100):
        """Generate response with small model"""
        if not self.model:
            self.load_model()
            
        # Format input
        prompt = f"Học sinh: {user_input} Cô giáo:"
        
        # Tokenize
        inputs = self.tokenizer.encode(
            prompt, 
            return_tensors="pt", 
            truncation=True, 
            max_length=200
        )
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_length=inputs.shape[1] + max_length,
                num_return_sequences=1,
                temperature=0.8,
                do_sample=True,
                top_p=0.9,
                repetition_penalty=1.2,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        # Decode response
        generated = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract teacher response
        if "Cô giáo:" in generated:
            response = generated.split("Cô giáo:")[-1].strip()
        else:
            response = "Em hỏi gì cô không hiểu rõ. Em có thể nói lại không?"
            
        return response

# Flask app
app = Flask(__name__)
CORS(app)

# Global trainer instance
trainer = None

def get_trainer():
    global trainer
    if trainer is None:
        trainer = LightweightVietnameseTrainer()
        try:
            # Try to load trained model first
            import os
            if os.path.exists("./vietnamese_teacher_light"):
                trainer.model = AutoModelForCausalLM.from_pretrained("./vietnamese_teacher_light")
                trainer.tokenizer = AutoTokenizer.from_pretrained("./vietnamese_teacher_light")
                print("✅ Loaded trained model")
            else:
                # Load base model if no trained model exists
                trainer.load_model()
                print("📦 Loaded base model - consider training first!")
        except Exception as e:
            print(f"⚠️ Error loading model: {e}")
            # Fallback to base model
            trainer.load_model()
            print("📦 Loaded base model as fallback")
    return trainer

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
        teacher = get_trainer()
        response = teacher.generate_response(user_message)
        
        return jsonify({
            'response': response,
            'model': teacher.model_name
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
        teacher = get_trainer()
        success = teacher.train_lightweight()
        
        if success:
            return jsonify({'status': 'Training completed successfully'})
        else:
            return jsonify({'error': 'Training failed'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'model_loaded': trainer is not None
    })

if __name__ == '__main__':
    print("🇻🇳 Starting Lightweight Vietnamese Teacher AI")
    print("💡 Optimized for M1 Mac with small models")
    
    # Check if we should train first
    import os
    if not os.path.exists("./vietnamese_teacher_light"):
        print("\n🔥 No trained model found. Starting training...")
        
        # Create trainer and train
        trainer_instance = LightweightVietnameseTrainer()
        success = trainer_instance.train_lightweight()
        
        if success:
            print("✅ Training completed! Starting server...")
        else:
            print("❌ Training failed! Using base model...")
    else:
        print("✅ Found existing trained model")
    
    # Start Flask server
    app.run(host='0.0.0.0', port=5002, debug=False)