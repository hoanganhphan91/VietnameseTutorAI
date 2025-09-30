#!/usr/bin/env python3
"""
Professional Vietnamese Teacher Training Script
- Uses NlpHUST/gpt2-vietnamese as base model
- High-quality conversational data
- Proper learning rate and epochs
- Saves training info and metrics
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer, DataCollatorForLanguageModeling
from datasets import Dataset
import os
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VietnameseTeacherTrainer:
    def __init__(self):
        self.base_model = "vinai/PhoGPT-4B-Chat"
        self.output_dir = "./vietnamese-teacher-professional"
        self.device = torch.device("cpu")  # Use CPU for stability
        self.training_info = {}
        
    def load_base_model(self):
        """Load the Vietnamese GPT-2 base model"""
        logger.info(f"📦 Loading base model: {self.base_model}")
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.base_model)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
        self.model = AutoModelForCausalLM.from_pretrained(
            self.base_model,
            dtype=torch.float32
        )
        
        # Resize token embeddings if needed
        self.model.resize_token_embeddings(len(self.tokenizer))
        logger.info("✅ Base model loaded successfully!")
        
    def prepare_dataset(self, data_file="premium_teacher_data.txt"):
        """Prepare training dataset from conversation file"""
        logger.info(f"📚 Loading training data from {data_file}")
        
        with open(data_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        conversations = []
        lines = content.split('\n')
        current_conversation = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_conversation:
                    conversations.append(current_conversation.strip())
                    current_conversation = ""
                continue
                
            if line.startswith("Học viên:"):
                # Start new conversation pair
                current_conversation = line + "\n"
            elif line.startswith("Giáo viên:") and current_conversation:
                # Complete conversation pair
                current_conversation += line + self.tokenizer.eos_token
                conversations.append(current_conversation.strip())
                current_conversation = ""
        
        logger.info(f"📊 Prepared {len(conversations)} conversation pairs")
        self.training_info['total_conversations'] = len(conversations)
        
        # Create dataset
        dataset = Dataset.from_dict({"text": conversations})
        
        def tokenize_function(examples):
            return self.tokenizer(
                examples["text"],
                truncation=True,
                padding="max_length",
                max_length=512,
                return_tensors="pt"
            )
        
        tokenized_dataset = dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=dataset.column_names
        )
        
        return tokenized_dataset
    
    def train(self, dataset):
        """Train the Vietnamese teacher model"""
        logger.info("🔥 Starting training...")
        
        # Training arguments optimized for Vietnamese teacher
        training_args = TrainingArguments(
            output_dir=self.output_dir,
            overwrite_output_dir=True,
            num_train_epochs=3,              # Balanced training
            per_device_train_batch_size=2,   # Small batch for memory
            gradient_accumulation_steps=4,   # Effective batch size = 8
            warmup_steps=50,
            logging_steps=10,
            save_steps=100,
            save_total_limit=2,
            learning_rate=3e-5,              # Conservative learning rate
            weight_decay=0.01,
            fp16=False,                      # Avoid mixed precision issues
            dataloader_pin_memory=False,     # M1 Mac compatibility
            remove_unused_columns=False,
        )
        
        # Data collator for language modeling
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False,  # GPT-2 is autoregressive, not masked LM
        )
        
        # Initialize trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            data_collator=data_collator,
            train_dataset=dataset,
            tokenizer=self.tokenizer,
        )
        
        # Start training
        train_result = trainer.train()
        
        # Save training info
        self.training_info.update({
            'training_loss': train_result.training_loss,
            'epochs': training_args.num_train_epochs,
            'learning_rate': training_args.learning_rate,
            'batch_size': training_args.per_device_train_batch_size,
            'trained_at': datetime.now().isoformat(),
            'base_model': self.base_model
        })
        
        logger.info(f"✅ Training completed! Final loss: {train_result.training_loss:.4f}")
        
    def save_model(self):
        """Save the trained model and info"""
        logger.info(f"💾 Saving model to {self.output_dir}")
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Save model and tokenizer
        self.model.save_pretrained(self.output_dir)
        self.tokenizer.save_pretrained(self.output_dir)
        
        # Save training info
        info_path = f"{self.output_dir}/training_info.json"
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(self.training_info, f, indent=2, ensure_ascii=False)
        
        logger.info("💾 Model and training info saved successfully!")
        
    def test_model(self):
        """Test the trained model"""
        logger.info("🧪 Testing trained model...")
        
        self.model.eval()
        test_prompts = [
            "Học viên: Xin chào cô!\nGiáo viên:",
            "Học viên: Làm sao để học phát âm tốt?\nGiáo viên:",
            "Học viên: Em muốn học từ vựng.\nGiáo viên:"
        ]
        
        for prompt in test_prompts:
            inputs = self.tokenizer.encode(prompt, return_tensors="pt")
            
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=inputs.shape[1] + 80,
                    temperature=0.7,
                    do_sample=True,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            logger.info(f"Test - Input: {prompt}")
            logger.info(f"Test - Output: {response}")
            logger.info("-" * 50)

def main():
    """Main training function"""
    logger.info("🚀 Starting Professional Vietnamese Teacher Training")
    
    trainer = VietnameseTeacherTrainer()
    
    # Step 1: Load base model
    trainer.load_base_model()
    
    # Step 2: Prepare dataset
    dataset = trainer.prepare_dataset()
    
    # Step 3: Train model
    trainer.train(dataset)
    
    # Step 4: Save model
    trainer.save_model()
    
    # Step 5: Test model
    trainer.test_model()
    
    logger.info("🎉 Training pipeline completed successfully!")
    logger.info(f"📁 Model saved at: {trainer.output_dir}")
    logger.info(f"📊 Training info: {trainer.training_info}")

if __name__ == "__main__":
    main()