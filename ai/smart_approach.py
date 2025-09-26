#!/usr/bin/env python3
"""
Simple approach: Just update the Flask app to use our data as context
No training needed - use the existing model with our conversation examples
"""

import json
import random
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

def load_teacher_examples():
    """Load our teacher examples as context"""
    examples = []
    
    with open('premium_teacher_data.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if line.startswith('Học viên:'):
            student = line.replace('Học viên:', '').strip()
            
            i += 1
            if i < len(lines) and lines[i].strip().startswith('Giáo viên:'):
                teacher = lines[i].strip().replace('Giáo viên:', '').strip()
                
                if student and teacher:
                    examples.append({
                        'student': student,
                        'teacher': teacher
                    })
        
        i += 1
    
    return examples

def find_similar_example(user_input, examples):
    """Find most relevant example based on keywords"""
    user_lower = user_input.lower()
    
    # Simple keyword matching
    keywords = {
        'xin chào': ['xin chào', 'chào', 'hello'],
        'phát âm': ['phát âm', 'thanh điệu', 'âm'],
        'từ vựng': ['từ vựng', 'vocabulary', 'từ'],
        'xưng hô': ['anh', 'chị', 'em', 'xưng hô'],
        'động từ': ['động từ', 'verb', 'chia động từ'],
        'văn hóa': ['văn hóa', 'culture', 'truyền thống'],
        'đọc sách': ['đọc', 'sách', 'reading'],
        'nói': ['nói', 'speaking', 'ngại ngùng']
    }
    
    for category, words in keywords.items():
        if any(word in user_lower for word in words):
            # Find examples related to this category
            relevant = [ex for ex in examples if any(word in ex['student'].lower() for word in words)]
            if relevant:
                return random.choice(relevant)['teacher']
    
    # If no specific match, return a general response
    return random.choice(examples)['teacher'] if examples else "Cô hiểu rồi. Hãy nói rõ hơn về điều em muốn học nhé!"

def create_smart_app():
    """Create updated app.py with context-aware responses"""
    
    app_code = '''from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import json
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Load teacher examples
TEACHER_EXAMPLES = []

def load_teacher_examples():
    """Load our teacher conversation examples"""
    global TEACHER_EXAMPLES
    
    try:
        with open('premium_teacher_data.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if line.startswith('Học viên:'):
                student = line.replace('Học viên:', '').strip()
                
                i += 1
                if i < len(lines) and lines[i].strip().startswith('Giáo viên:'):
                    teacher = lines[i].strip().replace('Giáo viên:', '').strip()
                    
                    if student and teacher:
                        TEACHER_EXAMPLES.append({
                            'student': student,
                            'teacher': teacher
                        })
            
            i += 1
        
        logger.info(f"Loaded {len(TEACHER_EXAMPLES)} teacher examples")
    except Exception as e:
        logger.error(f"Error loading teacher examples: {e}")

def find_best_response(user_input):
    """Find the best teacher response based on context"""
    user_lower = user_input.lower()
    
    # Keyword categories with responses
    if any(word in user_lower for word in ['xin chào', 'chào', 'hello']):
        responses = [ex['teacher'] for ex in TEACHER_EXAMPLES if 'chào' in ex['student'].lower()]
    elif any(word in user_lower for word in ['phát âm', 'thanh điệu', 'âm']):
        responses = [ex['teacher'] for ex in TEACHER_EXAMPLES if any(w in ex['student'].lower() for w in ['phát âm', 'thanh'])]
    elif any(word in user_lower for word in ['từ vựng', 'vocabulary', 'từ']):
        responses = [ex['teacher'] for ex in TEACHER_EXAMPLES if 'từ vựng' in ex['student'].lower()]
    elif any(word in user_lower for word in ['anh', 'chị', 'em', 'xưng hô']):
        responses = [ex['teacher'] for ex in TEACHER_EXAMPLES if any(w in ex['student'].lower() for w in ['anh', 'chị', 'em'])]
    elif any(word in user_lower for word in ['động từ', 'verb']):
        responses = [ex['teacher'] for ex in TEACHER_EXAMPLES if 'động từ' in ex['student'].lower()]
    elif any(word in user_lower for word in ['văn hóa', 'culture']):
        responses = [ex['teacher'] for ex in TEACHER_EXAMPLES if 'văn hóa' in ex['student'].lower()]
    elif any(word in user_lower for word in ['đọc', 'sách']):
        responses = [ex['teacher'] for ex in TEACHER_EXAMPLES if 'đọc' in ex['student'].lower()]
    elif any(word in user_lower for word in ['nói', 'speaking', 'ngại']):
        responses = [ex['teacher'] for ex in TEACHER_EXAMPLES if 'nói' in ex['student'].lower()]
    else:
        # Default to a random appropriate response
        responses = [ex['teacher'] for ex in TEACHER_EXAMPLES]
    
    if responses:
        return random.choice(responses)
    else:
        return "Cô hiểu rồi! Em có thể nói rõ hơn về điều em muốn học không?"

# Load examples on startup
load_teacher_examples()

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "running",
        "service": "Smart Vietnamese Tutor",
        "examples_loaded": len(TEACHER_EXAMPLES),
        "version": "smart-context-v1"
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Smart chat endpoint using context examples"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "Message is required"}), 400
        
        user_message = data['message'].strip()
        if not user_message:
            return jsonify({"error": "Message cannot be empty"}), 400
        
        logger.info(f"User: {user_message}")
        
        # Find best contextual response
        response = find_best_response(user_message)
        
        logger.info(f"Teacher: {response}")
        
        return jsonify({
            "response": response,
            "model": "context-based-teacher",
            "response_type": "contextual_match",
            "examples_available": len(TEACHER_EXAMPLES)
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health endpoint"""
    return jsonify({
        "status": "healthy", 
        "service": "Smart Vietnamese Tutor",
        "examples": len(TEACHER_EXAMPLES)
    })

if __name__ == '__main__':
    logger.info("Starting Smart Vietnamese Tutor Service...")
    app.run(host='0.0.0.0', port=5002, debug=False)
'''
    
    with open('app_smart.py', 'w', encoding='utf-8') as f:
        f.write(app_code)
    
    print("✅ Created smart app with contextual responses")

def test_smart_responses():
    """Test the smart response system"""
    examples = load_teacher_examples()
    print(f"Loaded {len(examples)} examples")
    
    test_inputs = [
        "Xin chào cô",
        "Em muốn học phát âm",
        "Làm sao để nhớ từ vựng",
        "Khi nào dùng anh chị em",
        "Tôi muốn hiểu văn hóa Việt Nam"
    ]
    
    for inp in test_inputs:
        response = find_similar_example(inp, examples)
        print(f"\\nInput: {inp}")
        print(f"Response: {response}")

if __name__ == "__main__":
    print("🎓 Creating Smart Vietnamese Teacher (No Training Required)")
    
    # Load and test examples
    examples = load_teacher_examples()
    print(f"Loaded {len(examples)} conversation examples")
    
    if examples:
        print("\\n🧪 Testing smart responses...")
        test_smart_responses()
        
        print("\\n💡 Creating smart Flask app...")
        create_smart_app()
        
        print("\\n✅ Done! Now you can:")
        print("1. Run: python3 app_smart.py")
        print("2. Test the smart responses without any training!")
    else:
        print("❌ No examples loaded")