#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vietnamese Teacher Trainer - Complete training pipeline
Optimized for M1 Mac with correct tokenization and data handling
"""

from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    BloomTokenizerFast,
    Trainer, 
    TrainingArguments,
    DataCollatorForLanguageModeling
)
from datasets import Dataset
import torch
import os
import json

class VietnameseTeacherTrainer:
    def __init__(self, model_name="vinai/PhoGPT-4B-Chat"):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        
    def load_model(self):
        """Load Vietnamese model with proper configuration"""
        print(f"📦 Loading {self.model_name}...")
        
        # Load tokenizer first
        self.tokenizer = BloomTokenizerFast.from_pretrained(
            self.model_name,
            use_fast=False,  # Use slow tokenizer for better compatibility
            trust_remote_code=True,
            use_flash_attention_2=False  # Disable flash attention for M1 Mac compatibility
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
        """FIXED: Parse Vietnamese teacher conversations with better format"""
        print(f"📖 Parsing conversations from {data_file}...")
        
        conversations = []
        
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # Parse line by line để chính xác hơn
            lines = content.split('\n')
            i = 0
            
            while i < len(lines):
                line = lines[i].strip()
                
                # Tìm câu hỏi của học sinh
                if line.startswith('Học viên:') or line.startswith('Học sinh:'):
                    student_question = line.split(':', 1)[1].strip()
                    
                    # Tìm câu trả lời của giáo viên ở dòng tiếp theo
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if next_line.startswith('Giáo viên:'):
                            teacher_answer = next_line.split(':', 1)[1].strip()
                            
                            if student_question and teacher_answer:
                                # Format conversation ĐÚNG cho GPT-2 Vietnamese
                                conversation_text = f"Học sinh: {student_question}\\nGiáo viên: {teacher_answer}"
                                conversations.append(conversation_text)
                                
                                # Debug: Show sample
                                if len(conversations) <= 3:
                                    print(f"✅ Conversation {len(conversations)}: {student_question[:50]}... → {teacher_answer[:50]}...")
                            
                            i += 2  # Skip cả 2 dòng
                        else:
                            i += 1
                    else:
                        i += 1
                else:
                    i += 1
            
            print(f"✅ Successfully parsed {len(conversations)} high-quality conversations")
            
            # Show final sample
            if conversations:
                print(f"Final format sample: {conversations[0][:100]}...")
            
            return conversations
            
        except Exception as e:
            print(f"❌ Error parsing conversations: {e}")
            return []
    
    def prepare_dataset(self, conversations):
        """Prepare dataset with FIXED tokenization"""
        print("🔧 Preparing dataset with PROPER tokenization...")
        
        def tokenize_function(examples):
            # Tokenize với attention mask và padding đúng
            tokenized = self.tokenizer(
                examples['text'],
                truncation=True,
                max_length=256,
                padding='max_length',  # QUAN TRỌNG: padding để mọi sample cùng chiều dài
                return_attention_mask=True,
                add_special_tokens=False
            )
            # labels phải là tensor cùng chiều dài với input_ids
            tokenized['labels'] = tokenized['input_ids']
            return tokenized
        
        # Create dataset from conversations
        dataset = Dataset.from_dict({'text': conversations})
        
        print(f"Sample conversation format: {conversations[0][:100]}...")
        
        # Apply tokenization
        tokenized_dataset = dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=['text'],
            desc="Tokenizing conversations"
        )
        
        print(f"✅ Dataset prepared: {len(tokenized_dataset)} samples")
        print(f"Sample tokenized length: {len(tokenized_dataset[0]['input_ids'])}")
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
            
            # Log 5 mẫu hội thoại đã convert để kiểm tra format
            print("🔎 Kiểm tra 5 mẫu hội thoại đã convert:")
            for idx, conv in enumerate(conversations[:5]):
                print(f"Mẫu {idx+1}: {conv}")

            # Prepare dataset
            train_dataset = self.prepare_dataset(conversations)
            
            # FIXED training arguments - loại bỏ conflicting params
            training_args = TrainingArguments(
                output_dir=output_dir,
                overwrite_output_dir=True,
                num_train_epochs=20,  # Giảm số epoch để tránh overfit dữ liệu nhỏ
                per_device_train_batch_size=2,  # Tăng batch size nếu RAM đủ
                gradient_accumulation_steps=4,  # Giảm tích lũy gradient cho batch lớn hơn
                learning_rate=1e-5,  # Giữ learning rate ổn định
                warmup_steps=20,
                logging_steps=1,
                save_steps=25,
                save_strategy="steps",
                logging_dir=f"{output_dir}/logs",
                remove_unused_columns=False,
                dataloader_pin_memory=False,
                dataloader_num_workers=0,
                fp16=False,
                report_to=None,
            )
            
            # FIXED Data collator với padding đúng
            data_collator = DataCollatorForLanguageModeling(
                tokenizer=self.tokenizer,
                mlm=False,  # Causal LM (not masked)
                pad_to_multiple_of=8,  # Pad to multiple của 8 để tối ưu
                return_tensors="pt"  # Return PyTorch tensors
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