#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vietnamese Teacher AI Service
Flask API server running on port 5003
"""

from transformers import AutoTokenizer, AutoModelForCausalLM, BloomTokenizerFast
import torch
from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

class VietnameseTeacherAI:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.load_model()
        
    def load_model(self):
        """Load trained model or base model"""
        trained_model_path = "./vietnamese_teacher_trained"
        
        if os.path.exists(trained_model_path) and os.listdir(trained_model_path):
            print("📦 Loading trained Vietnamese teacher model...")
            model_path = trained_model_path
        else:
            print("📦 Loading base Vietnamese model...")
            model_path = "vinai/PhoGPT-4B-Chat"
        
        try:
            # Load tokenizer
            self.tokenizer = BloomTokenizerFast.from_pretrained(
                model_path,
                use_fast=False,
                trust_remote_code=False
            )
            
            # Configure special tokens
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                dtype=torch.float32,
                low_cpu_mem_usage=True,
                trust_remote_code=False
            )
            
            print("✅ Model loaded successfully!")
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            self.model = None
            self.tokenizer = None
    
    def generate_response(self, question):
        """Generate teacher response for student question"""
        if self.model is None or self.tokenizer is None:
            return "Xin lỗi, AI giáo viên hiện tại không khả dụng."
        
        try:
            # Format input as conversation
            prompt = f"Học sinh: {question}\nGiáo viên:"
            print(f"[PROMPT] {prompt}")

            # Tokenize input
            inputs = self.tokenizer.encode(prompt, return_tensors='pt')
            print(f"[INPUT TOKENS] {inputs}")

            # Add attention_mask to avoid inf/nan errors
            attention_mask = torch.ones_like(inputs)

            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    attention_mask=attention_mask,
                    max_new_tokens=150,
                    temperature=0.5,
                    repetition_penalty=1.2,
                    pad_token_id=self.tokenizer.eos_token_id,
                    do_sample=True,
                    top_p=0.8
                )

            # Decode response
            full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            print(f"[FULL RESPONSE] {full_response}")

            # Log lại prompt và response vào file log
            with open("./ai_chat_log.txt", "a", encoding="utf-8") as logf:
                logf.write(f"PROMPT: {prompt}\nRESPONSE: {full_response}\n{'-'*40}\n")

            # Extract teacher response
            if "Giáo viên:" in full_response:
                teacher_response = full_response.split("Giáo viên:")[-1].strip()
                # Clean up response
                if "<|endoftext|>" in teacher_response:
                    teacher_response = teacher_response.split("<|endoftext|>")[0].strip()
                print(f"[TEACHER RESPONSE] {teacher_response}")
                return teacher_response
            else:
                print("[TEACHER RESPONSE] Xin lỗi, tôi không hiểu câu hỏi của em.")
                return "Xin lỗi, tôi không hiểu câu hỏi của em."
                
        except Exception as e:
            import traceback
            print(f"[ERROR] Error generating response: {e}")
            traceback.print_exc()
            return f"Xin lỗi, có lỗi xảy ra khi tạo phản hồi: {e}" 

# Initialize AI teacher
vietnamese_teacher = VietnameseTeacherAI()

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat requests"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Missing message field'}), 400
        
        user_message = data['message']
        
        # Generate AI response
        ai_response = vietnamese_teacher.generate_response(user_message)
        
        return jsonify({
            'response': ai_response,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    trained_model_exists = os.path.exists("./vietnamese_teacher_trained")
    return jsonify({
        'status': 'healthy',
        'model_loaded': vietnamese_teacher.model is not None,
        'trained_model_available': trained_model_exists
    })

@app.route('/model-info', methods=['GET'])
def model_info():
    """Get model information"""
    if vietnamese_teacher.model is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    trained_model_path = "./vietnamese_teacher_trained"
    model_type = "trained" if os.path.exists(trained_model_path) and os.listdir(trained_model_path) else "base"
    
    return jsonify({
        'model_type': model_type,
        'model_name': 'NlpHUST/gpt2-vietnamese',
        'parameters': vietnamese_teacher.model.num_parameters(),
        'vocab_size': len(vietnamese_teacher.tokenizer)
    })

if __name__ == '__main__':
    print("🇻🇳 Vietnamese Teacher AI Service")
    print("🚀 Starting server on port 5003...")
    
    if vietnamese_teacher.model is None:
        print("⚠️  Warning: Model not loaded properly")
    else:
        print("✅ AI Teacher ready to help!")
    
    app.run(host='0.0.0.0', port=5002, debug=False)