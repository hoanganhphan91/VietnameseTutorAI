#!/usr/bin/env python3
"""
PhoGPT Fine-tuning Script for Vietnamese Tutoring
"""
import json
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from datasets import Dataset
import os

# Training configuration
MODEL_NAME = "vinai/PhoGPT-4B-Chat"
OUTPUT_DIR = "./phogpt-vietnamese-tutor"
CACHE_DIR = "./.cache"

# Sample training data for Vietnamese tutoring
TRAINING_DATA = [
    {
        "conversation": [
            {"role": "student", "content": "Xin chào, tôi muốn học tiếng Việt"},
            {"role": "tutor", "content": "Xin chào! Tôi rất vui được dạy bạn tiếng Việt. Chúng ta sẽ bắt đầu từ những điều cơ bản nhất. Trước tiên, hãy học cách chào hỏi:\n\n• 'Xin chào' - Hello (formal)\n• 'Chào bạn' - Hi friend\n• 'Chúc buổi sáng tốt lành' - Good morning\n\nBạn có muốn thực hành phát âm không?"}
        ]
    },
    {
        "conversation": [
            {"role": "student", "content": "Làm sao phát âm 'xin chào' cho đúng?"},
            {"role": "tutor", "content": "Tuyệt! Hãy phân tích từng từ:\n\n🔤 **'Xin' [sin]:**\n- X = 's' sound\n- i = 'ee' sound  \n- n = 'n' sound\n- Thanh ngang (không lên xuống)\n\n🔤 **'Chào' [chow]:**\n- Ch = 'ch' sound\n- ào = 'ow' sound\n- Thanh huyền (giọng xuống nhẹ)\n\n💡 **Thử nói chậm:** 'Sin... chow'\n\nHãy luyện tập 5 lần và cho tôi biết cảm nhận!"}
        ]
    },
    {
        "conversation": [
            {"role": "student", "content": "Tôi muốn học từ vựng về gia đình"},
            {"role": "tutor", "content": "Gia đình là chủ đề quan trọng! 👨‍👩‍👧‍👦\n\n**Thành viên gia đình:**\n• Ba/Cha = Father\n• Mẹ/Má = Mother\n• Anh = Older brother\n• Chị = Older sister  \n• Em = Younger sibling\n• Con = Child\n• Ông = Grandfather\n• Bà = Grandmother\n\n**Câu mẫu:**\n- 'Gia đình tôi có 4 người' = My family has 4 people\n- 'Ba mẹ tôi rất tốt' = My parents are very good\n\nBạn thử tạo câu về gia đình mình xem?"}
        ]
    },
    {
        "conversation": [
            {"role": "student", "content": "6 thanh điệu tiếng Việt là gì?"},
            {"role": "tutor", "content": "Đây là điều quan trọng nhất trong tiếng Việt! 🎵\n\n**6 Thanh điệu với từ 'ma':**\n\n1️⃣ **Ngang** (ma) - Ghost 👻\n   - Giọng bằng, không lên xuống\n   \n2️⃣ **Huyền** (mà) - Which/That\n   - Giọng xuống từ từ ↘️\n   \n3️⃣ **Sắc** (má) - Mother/Cheek\n   - Giọng lên cao ↗️\n   \n4️⃣ **Hỏi** (mả) - Tomb\n   - Giọng lên rồi xuống ↗️↘️\n   \n5️⃣ **Ngã** (mã) - Code/Horse\n   - Giọng gãy, ngắt quãng ↗️↘️↗️\n   \n6️⃣ **Nặng** (mạ) - Rice seedling\n   - Giọng xuống ngắn, dứt khoát ⬇️\n\n🎯 **Thực hành:** Hãy đọc to 6 từ này liên tục!"}
        ]
    },
    {
        "conversation": [
            {"role": "student", "content": "Kể cho tôi về văn hóa Việt Nam"},
            {"role": "tutor", "content": "Văn hóa Việt Nam rất phong phú và độc đáo! 🇻🇳\n\n**🎎 Truyền thống quan trọng:**\n\n• **Tết Nguyên Đán** - Năm mới Âm lịch\n  - Lễ quan trọng nhất trong năm\n  - Ăn bánh chưng, mứt Tết\n  - Lì xì đỏ cho trẻ em\n\n• **Áo dài** - Trang phục truyền thống\n  - Thanh lịch, duyên dáng\n  - Mặc trong dịp đặc biệt\n\n• **Cúng tổ tiên** - Thờ cúng gia đình\n  - Bàn thờ trong nhà\n  - Tôn kính người có công\n\n**🍜 Ẩm thực đặc sắc:**\n• Phở - Món quốc hồn\n• Bánh mì - Sandwich Việt\n• Cà phê sữa đá - Đồ uống truyền thống\n\nBạn muốn tìm hiểu sâu về khía cạnh nào?"}
        ]
    }
]

def create_training_dataset():
    """Tạo dataset cho fine-tuning"""
    formatted_data = []
    
    for item in TRAINING_DATA:
        conversation = item["conversation"]
        
        # Format theo style PhoGPT
        text = ""
        for turn in conversation:
            if turn["role"] == "student":
                text += f"### Học viên: {turn['content']}\n\n"
            else:
                text += f"### Gia sư: {turn['content']}\n\n"
        
        formatted_data.append({"text": text})
    
    return Dataset.from_list(formatted_data)

def fine_tune_phogpt():
    """Fine-tune PhoGPT cho Vietnamese tutoring"""
    
    print("🚀 Bắt đầu fine-tuning PhoGPT...")
    
    # Load tokenizer và model
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME,
        cache_dir=CACHE_DIR,
        trust_remote_code=True
    )
    
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        cache_dir=CACHE_DIR,
        trust_remote_code=True,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
    )
    
    # Thêm pad token nếu chưa có
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Tạo dataset
    dataset = create_training_dataset()
    
    def tokenize_function(examples):
        texts = examples["text"]
        # Flatten nếu có list lồng nhau (phòng trường hợp lỗi dataset)
        flat_texts = []
        for t in texts:
            if isinstance(t, list):
                flat_texts.extend([str(x) for x in t])
            else:
                flat_texts.append(str(t))
        print("DEBUG - Sample texts:", flat_texts[:2])
        return tokenizer(
            flat_texts,
            truncation=True,
            padding=True,
            max_length=1024
        )
    
    tokenized_dataset = dataset.map(tokenize_function, batched=True)
    
    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,  # Causal LM, not masked LM
    )
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        overwrite_output_dir=True,
        num_train_epochs=3,
        per_device_train_batch_size=1,  # Small batch for memory
        gradient_accumulation_steps=4,
        warmup_steps=50,
        logging_steps=10,
        save_steps=100,
        evaluation_strategy="no",
        save_total_limit=2,
        prediction_loss_only=True,
        remove_unused_columns=False,
        dataloader_pin_memory=False,
        learning_rate=5e-5,
        weight_decay=0.01,
        fp16=torch.cuda.is_available(),  # Use fp16 if GPU available
    )
    
    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        data_collator=data_collator,
        train_dataset=tokenized_dataset,
        tokenizer=tokenizer,
    )
    
    # Start training
    print("📚 Bắt đầu training...")
    trainer.train()
    
    # Save model
    print("💾 Lưu model...")
    trainer.save_model()
    tokenizer.save_pretrained(OUTPUT_DIR)
    
    print(f"✅ Fine-tuning hoàn tất! Model được lưu tại: {OUTPUT_DIR}")

if __name__ == "__main__":
    fine_tune_phogpt()