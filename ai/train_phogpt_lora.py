#!/usr/bin/env python3
"""
PhoGPT LoRA Fine-tuning - Memory Efficient
"""
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer
)
from peft import (
    get_peft_model, 
    LoraConfig, 
    TaskType,
    prepare_model_for_kbit_training
)
from datasets import Dataset
import json

MODEL_NAME = "vinai/PhoGPT-4B-Chat"
OUTPUT_DIR = "./phogpt-lora-vietnamese-tutor"

def setup_lora_model():
    """Setup LoRA configuration"""
    
    # Load base model
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
        cache_dir="./.cache"
    )
    
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME,
        trust_remote_code=True,
        cache_dir="./.cache"
    )
    
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # LoRA configuration
    lora_config = LoraConfig(
        r=16,  # Rank of adaptation
        lora_alpha=32,  # LoRA scaling parameter
        target_modules=[
            "q_proj",
            "k_proj", 
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],
        lora_dropout=0.1,
        bias="none",
        task_type=TaskType.CAUSAL_LM,
    )
    
    # Prepare model for k-bit training
    model = prepare_model_for_kbit_training(model)
    
    # Get PEFT model
    model = get_peft_model(model, lora_config)
    
    # Print trainable parameters
    model.print_trainable_parameters()
    
    return model, tokenizer

def create_vietnamese_tutor_dataset():
    """Tạo dataset chuyên sâu cho Vietnamese tutoring"""
    
    # Extended training data
    training_conversations = [
        # Pronunciation training
        {
            "input": "Làm sao phân biệt thanh sắc và thanh hỏi?",
            "output": "Đây là câu hỏi rất hay! 🎯\n\n**Thanh Sắc (á):**\n- Giọng lên cao một cách nhanh và dứt khoát ↗️\n- Ví dụ: 'má' (mother/cheek)\n- Cảm giác: Như hỏi câu nghi vấn ngắn\n\n**Thanh Hỏi (ả):**\n- Giọng lên rồi xuống, như dấu hỏi ↗️↘️\n- Ví dụ: 'mả' (tomb)\n- Cảm giác: Như nghi ngờ, do dự\n\n**Thực hành:**\nHãy nói 'má - mả' liên tiếp 10 lần để cảm nhận sự khác biệt!"
        },
        
        # Grammar explanation
        {
            "input": "Giải thích cách dùng 'đang', 'đã', 'sẽ' trong tiếng Việt",
            "output": "Tuyệt! Đây là 3 từ chỉ thời gian quan trọng: ⏰\n\n**🔄 ĐANG (Present Continuous):**\n- Hành động đang xảy ra\n- 'Tôi đang học tiếng Việt' = I am learning Vietnamese\n- 'Em đang làm bài' = She is doing homework\n\n**✅ ĐÃ (Past Perfect):**\n- Hành động đã hoàn thành\n- 'Tôi đã ăn cơm' = I have eaten rice\n- 'Anh ấy đã về nhà' = He has gone home\n\n**🔮 SẼ (Future):**\n- Hành động sẽ xảy ra\n- 'Mai tôi sẽ đi Hà Nội' = Tomorrow I will go to Hanoi\n- 'Chúng ta sẽ gặp lại' = We will meet again\n\n**Bài tập:** Tạo 3 câu với 3 từ này về hoạt động hôm nay!"
        },
        
        # Cultural context
        {
            "input": "Tại sao người Việt hay nói 'ăn cơm chưa?'",
            "output": "Câu hỏi văn hóa rất thú vị! 🍚\n\n**'Ăn cơm chưa?' - Ý nghĩa sâu sắc:**\n\n🤝 **Không chỉ hỏi về bữa ăn:**\n- Cách chào hỏi thân thiết\n- Thể hiện sự quan tâm\n- Như 'How are you?' trong tiếng Anh\n\n🏠 **Gốc rễ văn hóa:**\n- Cơm = nguồn sống của người Việt\n- Xưa kia, có cơm ăn = sung túc\n- Hỏi thăm = chia sẻ, lo lắng cho nhau\n\n💬 **Cách trả lời:**\n- 'Rồi, cảm ơn anh/chị' = Yes, thank you\n- 'Chưa, sắp ăn' = Not yet, will eat soon\n- 'Anh/chị ăn chưa?' = Ask back\n\n**Tương tự:** 'Đi đâu vậy?', 'Khỏe không?' - đều là cách quan tâm!"
        }
    ]
    
    formatted_data = []
    for item in training_conversations:
        text = f"### Câu hỏi: {item['input']}\n\n### Trả lời: {item['output']}\n\n"
        formatted_data.append({"text": text})
    
    return Dataset.from_list(formatted_data)

def train_lora_model():
    """Train PhoGPT với LoRA"""
    
    print("🚀 Bắt đầu LoRA fine-tuning...")
    
    # Setup model và tokenizer
    model, tokenizer = setup_lora_model()
    
    # Create dataset
    dataset = create_vietnamese_tutor_dataset()
    
    def tokenize_function(examples):
        return tokenizer(
            examples["text"],
            truncation=True,
            padding=True,
            max_length=1024
        )
    
    tokenized_dataset = dataset.map(tokenize_function, batched=True)
    
    # Training arguments - optimized for LoRA
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        overwrite_output_dir=True,
        num_train_epochs=5,  # More epochs for LoRA
        per_device_train_batch_size=2,
        gradient_accumulation_steps=2,
        warmup_steps=100,
        learning_rate=2e-4,  # Higher LR for LoRA
        logging_steps=10,
        save_steps=50,
        eval_steps=50,
        save_total_limit=3,
        remove_unused_columns=False,
        dataloader_pin_memory=False,
        fp16=True,
        optim="adamw_torch",
        weight_decay=0.01,
        lr_scheduler_type="cosine",
    )
    
    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        tokenizer=tokenizer,
    )
    
    # Start training
    print("📚 Bắt đầu LoRA training...")
    trainer.train()
    
    # Save LoRA adapter
    print("💾 Lưu LoRA adapter...")
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    
    print(f"✅ LoRA fine-tuning hoàn tất!")
    print(f"📁 LoRA adapter: {OUTPUT_DIR}")

if __name__ == "__main__":
    train_lora_model()