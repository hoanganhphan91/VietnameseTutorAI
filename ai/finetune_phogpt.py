#!/usr/bin/env python3
"""
Fine-tune PhoGPT-4B for Vietnamese Language Tutoring
"""
import json
from datasets import Dataset
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer
)
import torch

# Training data for Vietnamese tutoring
TRAINING_DATA = [
    {
        "prompt": "Học viên: Xin chào, tôi muốn học tiếng Việt",
        "response": "Xin chào! Tôi rất vui được giúp bạn học tiếng Việt. Hãy bắt đầu với những câu chào hỏi cơ bản: 'Xin chào' (sin chow) = Hello, 'Cảm ơn' (gahm uhn) = Thank you. Bạn đã biết tiếng Việt đến mức nào rồi?"
    },
    {
        "prompt": "Học viên: Dạy tôi thanh điệu tiếng Việt",
        "response": "Tiếng Việt có 6 thanh điệu quan trọng:\n1. Ngang (a) - không dấu\n2. Huyền (à) - dấu huyền\n3. Sắc (á) - dấu sắc\n4. Hỏi (ả) - dấu hỏi\n5. Ngã (ã) - dấu ngã\n6. Nặng (ạ) - dấu nặng\n\nVí dụ với từ 'ma': ma (ma quỷ), mà (but), má (mother), mả (grave), mã (code), mạ (rice seedling). Mỗi thanh có nghĩa khác nhau!"
    },
    {
        "prompt": "Học viên: Tôi không phát âm được",
        "response": "Đừng lo lắng! Phát âm tiếng Việt cần thời gian luyện tập. Mẹo hay:\n1. Nghe và nhắc lại từng thanh điệu\n2. Bắt đầu với từ đơn giản: má, ba, cơm\n3. Luyện tập hàng ngày 10-15 phút\n4. Ghi âm giọng mình để so sánh\n\nHãy thử phát âm 'má' (mother) với giọng lên cao nhé!"
    }
]

def create_training_dataset():
    """Create training dataset"""
    formatted_data = []
    for item in TRAINING_DATA:
        text = f"### {item['prompt']}\n### Gia sư: {item['response']}"
        formatted_data.append({"text": text})
    
    return Dataset.from_list(formatted_data)

def fine_tune_phogpt():
    """Fine-tune PhoGPT for Vietnamese tutoring"""
    print("🚀 Starting PhoGPT Fine-tuning for Vietnamese Tutoring...")
    
    # Load model and tokenizer
    model_name = "vinai/PhoGPT-4B-Chat"
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_name, 
        trust_remote_code=True,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
    )
    
    # Prepare dataset
    dataset = create_training_dataset()
    
    def tokenize_function(examples):
        return tokenizer(examples["text"], truncation=True, padding="max_length", max_length=512)
    
    tokenized_dataset = dataset.map(tokenize_function, batched=True)
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir="./phogpt_finetuned",
        num_train_epochs=3,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        learning_rate=2e-5,
        warmup_steps=100,
        logging_steps=10,
        save_strategy="epoch",
        evaluation_strategy="no",
        fp16=torch.cuda.is_available(),
        push_to_hub=False,
    )
    
    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        tokenizer=tokenizer,
    )
    
    # Start training
    print("📚 Training started...")
    trainer.train()
    
    # Save model
    trainer.save_model()
    tokenizer.save_pretrained("./phogpt_finetuned")
    
    print("✅ Fine-tuning completed!")
    print("📁 Model saved to: ./phogpt_finetuned")

if __name__ == "__main__":
    fine_tune_phogpt()