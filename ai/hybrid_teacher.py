#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hybrid Vietnamese Teacher - Best of both worlds
- Use cloud API for complex queries (OpenAI/Cohere/Claude)
- Use local small model for simple responses
- Smart fallback system
"""

import openai
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

# API Configuration (set your API keys)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
COHERE_API_KEY = os.getenv("COHERE_API_KEY", "")

class HybridVietnameseTeacher:
    def __init__(self):
        self.conversation_history = []
        self.local_responses = self.load_local_responses()
        
    def load_local_responses(self):
        """Load pre-defined responses for common queries"""
        try:
            with open('premium_teacher_data.txt', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse into Q&A pairs
            responses = {}
            lines = content.split('\n')
            current_question = ""
            
            for line in lines:
                line = line.strip()
                if line.startswith('Học viên:'):
                    current_question = line.replace('Học viên:', '').strip()
                elif line.startswith('Giáo viên:') and current_question:
                    answer = line.replace('Giáo viên:', '').strip()
                    responses[current_question.lower()] = answer
                    current_question = ""
            
            print(f"📚 Loaded {len(responses)} local responses")
            return responses
            
        except FileNotFoundError:
            print("⚠️ premium_teacher_data.txt not found, using basic responses")
            return {}
    
    def find_local_response(self, user_message):
        """Find matching local response using keyword matching"""
        user_lower = user_message.lower()
        
        # Direct matching
        if user_lower in self.local_responses:
            return self.local_responses[user_lower]
        
        # Keyword matching
        for question, answer in self.local_responses.items():
            # Extract key words
            user_words = set(user_lower.split())
            question_words = set(question.split())
            
            # If significant overlap, return this answer
            overlap = len(user_words.intersection(question_words))
            if overlap >= 2 and len(user_words) <= 10:  # For short questions
                return answer
        
        # Pattern matching for common topics
        keywords_responses = {
            ['phát âm', 'pronunciation']: "Phát âm là nền tảng quan trọng nhất của tiếng Việt em ạ! Tiếng Việt có 6 thanh điệu: ngang (ba), huyền (bà), sắc (bá), hỏi (bả), ngã (bã), và nặng (bạ). Chúng ta sẽ luyện từng bước một nhé!",
            ['thanh điệu', 'tones']: "6 thanh điệu trong tiếng Việt: thanh ngang (ba), thanh huyền (bà), thanh sắc (bá), thanh hỏi (bả), thanh ngã (bã), và thanh nặng (bạ). Mỗi thanh có giai điệu riêng, em cần luyện thường xuyên.",
            ['từ vựng', 'vocabulary']: "Học từ vựng hiệu quả nhất là học theo chủ đề em ạ! Ví dụ: gia đình, thức ăn, quần áo. Mỗi ngày học 5-8 từ mới và tạo câu với những từ đó.",
            ['ngại ngùng', 'shy', 'sợ']: "Đó là cảm giác bình thường em à! Đừng sợ sai, cứ thử nói. Người Việt rất hiền, họ sẽ giúp em sửa lỗi một cách tử tế. Chỉ bằng cách nói nhiều, em mới tiến bộ được.",
            ['xin chào', 'hello', 'chào']: "Xin chào em! Cô rất vui được gặp em hôm nay. Em muốn học gì về tiếng Việt?",
            ['cảm ơn', 'thank']: "Không có gì em! Học ngôn ngữ là hành trình thú vị. Cô tin rằng với sự kiên trì, em sẽ nói tiếng Việt rất tự nhiên!"
        }
        
        for keywords, response in keywords_responses.items():
            if any(keyword in user_lower for keyword in keywords):
                return response
        
        return None
    
    def call_openai_api(self, user_message):
        """Use OpenAI API for complex responses"""
        if not OPENAI_API_KEY:
            return None
        
        try:
            # System prompt for Vietnamese teacher
            system_prompt = """Bạn là một giáo viên tiếng Việt chuyên nghiệp, nhiệt tình và kiên nhẫn. 
            Hãy trả lời học sinh bằng tiếng Việt một cách tự nhiên, hữu ích và khuyến khích. 
            Giải thích rõ ràng, đưa ví dụ cụ thể, và luôn động viên học sinh."""
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return None
    
    def call_cohere_api(self, user_message):
        """Alternative: Use Cohere API"""
        if not COHERE_API_KEY:
            return None
        
        try:
            headers = {
                'Authorization': f'Bearer {COHERE_API_KEY}',
                'Content-Type': 'application/json'
            }
            
            prompt = f"""Bạn là giáo viên tiếng Việt chuyên nghiệp. Trả lời học sinh:
            
Học sinh: {user_message}
Giáo viên:"""
            
            data = {
                'model': 'command-light',  # Smaller, cheaper model
                'prompt': prompt,
                'max_tokens': 150,
                'temperature': 0.7
            }
            
            response = requests.post(
                'https://api.cohere.ai/v1/generate',
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['generations'][0]['text'].strip()
            
        except Exception as e:
            print(f"Cohere API error: {e}")
            return None
    
    def generate_response(self, user_message):
        """Smart response generation with fallback"""
        
        # Step 1: Try local response first (fast + free)
        local_response = self.find_local_response(user_message)
        if local_response:
            return local_response, "local"
        
        # Step 2: For complex queries, try cloud API
        message_length = len(user_message.split())
        if message_length > 8:  # Complex questions
            
            # Try OpenAI first
            ai_response = self.call_openai_api(user_message)
            if ai_response:
                return ai_response, "openai"
            
            # Fallback to Cohere
            ai_response = self.call_cohere_api(user_message)
            if ai_response:
                return ai_response, "cohere"
        
        # Step 3: Final fallback - generic helpful response
        fallback_response = f"""Em hỏi hay quá! Về vấn đề này, cô nghĩ em nên:
1. Luyện tập thường xuyên mỗi ngày
2. Đừng ngại hỏi khi chưa hiểu
3. Tìm hiểu thêm qua sách báo, phim ảnh

Em có thể hỏi cô cụ thể hơn được không? Ví dụ về phát âm, từ vựng, hay ngữ pháp?"""
        
        return fallback_response, "fallback"

# Global teacher instance
teacher = HybridVietnameseTeacher()

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                'error': 'Empty message',
                'response': 'Em hãy nói gì đó để cô có thể giúp em nhé!'
            }), 400
        
        # Generate response
        response, source = teacher.generate_response(user_message)
        
        # Log conversation
        teacher.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'user': user_message,
            'bot': response,
            'source': source
        })
        
        return jsonify({
            'response': response,
            'source': source,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'response': 'Xin lỗi em, cô gặp vấn đề kỹ thuật. Em thử lại sau nhé!'
        }), 500

@app.route('/history', methods=['GET'])
def get_history():
    """Get conversation history"""
    return jsonify({
        'conversations': teacher.conversation_history[-10:],  # Last 10
        'total': len(teacher.conversation_history)
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'local_responses': len(teacher.local_responses),
        'openai_available': bool(OPENAI_API_KEY),
        'cohere_available': bool(COHERE_API_KEY)
    })

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        'name': 'Hybrid Vietnamese Teacher AI',
        'description': 'Smart fallback system: Local -> Cloud API -> Fallback',
        'features': [
            'Fast local responses for common questions',
            'Cloud AI for complex queries', 
            'Always has a helpful response'
        ]
    })

if __name__ == '__main__':
    print("🇻🇳 Hybrid Vietnamese Teacher AI")
    print("💡 Local responses + Cloud AI fallback")
    print("🔑 Set OPENAI_API_KEY or COHERE_API_KEY for cloud features")
    
    app.run(host='0.0.0.0', port=5001, debug=False)