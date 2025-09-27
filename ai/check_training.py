#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Vietnamese Teacher Model - Kiểm tra model đã train chưa
"""

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import os

def test_trained_model():
    print("🔍 KIỂM TRA MODEL ĐÃ TRAIN")
    print("=" * 50)
    
    trained_path = "./vietnamese_teacher_trained"
    
    # Kiểm tra thư mục model
    if not os.path.exists(trained_path):
        print("❌ CHƯA CÓ MODEL TRAIN - Thư mục không tồn tại")
        return False
    
    files = os.listdir(trained_path)
    print(f"📁 Files trong thư mục: {len(files)} files")
    
    required_files = ['model.safetensors', 'config.json', 'tokenizer_config.json']
    missing_files = [f for f in required_files if f not in files]
    
    if missing_files:
        print(f"❌ THIẾU FILES QUAN TRỌNG: {missing_files}")
        return False
    
    print("✅ Tất cả files cần thiết đều có")
    
    # Load và test model
    try:
        print("\n📦 Loading model...")
        tokenizer = AutoTokenizer.from_pretrained(trained_path, use_fast=False)
        model = AutoModelForCausalLM.from_pretrained(trained_path, torch_dtype=torch.float32)
        
        print("✅ Model load thành công!")
        
        # Test generation với câu hỏi từ training data
        test_question = "6 thanh điệu là những thanh nào ạ?"
        print(f"\n🧪 TEST CÂU HỎI: {test_question}")
        
        prompt = f"<|startoftext|>Học sinh: {test_question}\nGiáo viên:"
        inputs = tokenizer.encode(prompt, return_tensors='pt')
        
        with torch.no_grad():
            outputs = model.generate(
                inputs,
                max_length=inputs.size(1) + 100,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        if "Giáo viên:" in response:
            teacher_response = response.split("Giáo viên:")[-1].strip()
            print(f"🤖 AI PHẢN HỒI: {teacher_response}")
            
            # Kiểm tra xem có học được từ training data không
            keywords = ["thanh ngang", "thanh huyền", "thanh sắc", "6 thanh", "bà", "ba"]
            learned = any(keyword in teacher_response.lower() for keyword in keywords)
            
            if learned:
                print("✅ MODEL ĐÃ HỌC TỪ TRAINING DATA!")
                return True
            else:
                print("⚠️  Model chưa học tốt từ training data")
                return False
        else:
            print("❌ Model không tạo được response đúng format")
            return False
            
    except Exception as e:
        print(f"❌ LỖI KHI TEST MODEL: {e}")
        return False

if __name__ == '__main__':
    result = test_trained_model()
    print("\n" + "=" * 50)
    if result:
        print("🎉 KẾT LUẬN: MODEL ĐÃ ĐƯỢC TRAIN THÀNH CÔNG!")
    else:
        print("💥 KẾT LUẬN: MODEL CHƯA TRAIN HOẶC TRAIN THẤT BẠI!")