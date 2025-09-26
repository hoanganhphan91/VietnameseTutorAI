from flask import Flask, request, jsonify
import os
import logging
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Simplified Vietnamese Tutor AI without heavy dependencies
# We'll use rule-based responses until model dependencies are resolved

def generate_intelligent_response(user_input):
    """Generate intelligent Vietnamese tutoring responses"""
    user_lower = user_input.lower().strip()
    
    # Vietnamese greetings
    if any(word in user_lower for word in ['xin chào', 'hello', 'hi', 'chào', 'chào bạn']):
        responses = [
            "Xin chào! Tôi là AI gia sư tiếng Việt của bạn. Tôi có thể giúp bạn học:\n• Từ vựng và ngữ pháp\n• Phát âm chuẩn\n• Văn hóa Việt Nam\n• Giao tiếp hàng ngày\n\nBạn muốn bắt đầu học gì?",
            "Chào bạn! Rất vui được gặp bạn. Hôm nay chúng ta sẽ cùng khám phá tiếng Việt nhé! Bạn đã biết những từ tiếng Việt nào chưa?"
        ]
        return random.choice(responses)
    
    # Thanks responses
    elif any(word in user_lower for word in ['cảm ơn', 'cám ơn', 'thank you', 'thanks']):
        responses = [
            "Rất vui được giúp bạn! 😊 Học tiếng Việt cần kiên nhẫn, nhưng tôi tin bạn sẽ thành công. Còn gì khác tôi có thể giúp không?",
            "Không có gì! Đó là niềm vui của tôi. Bạn có muốn học thêm cách nói 'cảm ơn' trong các tình huống khác nhau không?"
        ]
        return random.choice(responses)
    
    # Handle complaints/negative feedback
    elif any(word in user_lower for word in ['ngu ngốc', 'stupid', 'tệ', 'xấu', 'không tốt', 'bad', 'phản hồi']):
        return "Xin lỗi bạn rất nhiều! 🙏 Tôi thực sự muốn cải thiện để giúp bạn học tốt hơn.\n\nHãy cho tôi biết:\n• Bạn muốn học chủ đề gì?\n• Tôi có thể giải thích rõ hơn điều gì?\n• Bạn cần hỗ trợ gì cụ thể?\n\nTôi sẽ cố gắng phản hồi chính xác và hữu ích hơn!"
    
    # Learning topics
    elif any(word in user_lower for word in ['học', 'learn', 'study', 'dạy', 'teach']):
        return "Tuyệt vời! Bạn muốn học tiếng Việt. Chúng ta có thể bắt đầu với:\n\n🗣️ **Phát âm cơ bản:**\n- 6 thanh điệu tiếng Việt\n- Cách phát âm đúng\n\n📚 **Từ vựng thiết yếu:**\n- Chào hỏi và giới thiệu\n- Số đếm và thời gian\n- Gia đình và công việc\n\n🎭 **Văn hóa và giao tiếp:**\n- Phép lịch sự Việt Nam\n- Cách xưng hô phù hợp\n\nBạn muốn bắt đầu từ đâu?"
    
    # Pronunciation
    elif any(word in user_lower for word in ['phát âm', 'pronunciation', 'thanh điệu', 'tone']):
        return "Tiếng Việt có 6 thanh điệu quan trọng:\n\n1. **Thanh ngang** (không dấu): ma\n2. **Thanh huyền** (dấu `): mà  \n3. **Thanh sắc** (dấu ´): má\n4. **Thanh hỏi** (dấu ?): mả\n5. **Thanh ngã** (dấu ~): mã\n6. **Thanh nặng** (dấu .): mạ\n\n💡 **Mẹo nhớ:** Hãy thử phát âm 6 từ này - chúng có nghĩa hoàn toàn khác nhau:\n- ma (ghost) - mà (but) - má (cheek) - mả (grave) - mã (code) - mạ (rice seedling)\n\nBạn thử phát âm xem sao?"
    
    # Vocabulary
    elif any(word in user_lower for word in ['từ vựng', 'vocabulary', 'từ', 'word']):
        return "Hãy học từ vựng cơ bản theo chủ đề:\n\n👨‍👩‍👧‍👦 **Gia đình:**\n- Bố/Cha = Father\n- Mẹ/Má = Mother\n- Anh = Older brother\n- Chị = Older sister\n- Em = Younger sibling\n\n🍜 **Đồ ăn phổ biến:**\n- Cơm = Rice\n- Phở = Pho soup\n- Bánh mì = Vietnamese sandwich\n- Chả cá = Grilled fish\n- Cà phê = Coffee\n\nBạn muốn học chủ đề nào khác?"
    
    # Numbers
    elif any(word in user_lower for word in ['số', 'number', 'đếm', 'count']):
        return "Học đếm số tiếng Việt:\n\n**Số cơ bản 1-10:**\n1️⃣ Một (mohdt)\n2️⃣ Hai (high)\n3️⃣ Ba (bah)\n4️⃣ Bốn (bohn)\n5️⃣ Năm (nahm)\n6️⃣ Sáu (shah-oo)\n7️⃣ Bảy (by)\n8️⃣ Tám (tahm)\n9️⃣ Chín (cheen)\n🔟 Mười (moo-uhr-ee)\n\n**Số lớn:**\n- 100 = Một trăm\n- 1000 = Một ngàn\n- 10000 = Một vạn\n\nBạn thử đếm từ 1-10 xem!"
    
    # Culture
    elif any(word in user_lower for word in ['văn hóa', 'culture', 'truyền thống', 'tradition']):
        return "Văn hóa Việt Nam thật phong phú! 🇻🇳\n\n🎭 **Đặc trưng văn hóa:**\n- Tôn trọng người lớn tuổi\n- Gia đình là trung tâm\n- Hiếu khách và thân thiện\n- Trọng nghĩa tình\n\n🎊 **Lễ hội truyền thống:**\n- Tết Nguyên Đán (Lunar New Year)\n- Tết Trung Thu (Mid-Autumn Festival)\n- Lễ Vu Lan (Ghost Festival)\n\n🍜 **Ẩm thực đặc sắc:**\n- Phở, Bún Bò Huế, Cơm Tấm\n- Bánh Mì, Chả Cá, Nem Nướng\n\nBạn muốn tìm hiểu về khía cạnh nào?"
    
    # Default intelligent response
    else:
        responses = [
            f"Bạn vừa nói '{user_input}'. Đây là cơ hội tốt để cải thiện tiếng Việt!\n\n🔍 **Tôi có thể giúp bạn:**\n• Sửa ngữ pháp nếu cần\n• Giải thích từ khó\n• Gợi ý cách diễn đạt hay hơn\n• Dạy thêm từ vựng liên quan\n\nBạn muốn tôi tập trung vào điều gì?",
            
            f"Thú vị! Câu '{user_input}' của bạn có thể được cải thiện.\n\n📝 **Hãy thử phân tích:**\n• Ý chính bạn muốn truyền đạt?\n• Có từ nào khó phát âm không?\n• Ngữ cảnh sử dụng là gì?\n\n💡 Tôi sẽ giúp bạn diễn đạt tự nhiên hơn!",
            
            f"Hay lắm! '{user_input}' - tôi hiểu bạn đang luyện tập.\n\n🎯 **Cùng cải thiện:**\n• Phát âm chuẩn hơn\n• Từ vựng phong phú hơn\n• Ngữ pháp chính xác hơn\n• Giao tiếp tự nhiên hơn\n\nBạn muốn bắt đầu từ đâu?"
        ]
        return random.choice(responses)

def load_model():
    """Placeholder for model loading - using intelligent rule-based system"""
    logger.info("Using intelligent rule-based Vietnamese tutoring system")
    return True
        
        logger.info("Model loaded successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        return False

def generate_response(user_input, max_length=512):
    """Generate AI response using PhoGPT"""
    if not tokenizer or not model:
        return "Xin lỗi, hệ thống AI chưa sẵn sàng."
    
    try:
        # Improved Vietnamese tutoring prompt
        system_prompt = """Bạn là một giáo viên tiếng Việt thân thiện và chuyên nghiệp, dạy tiếng Việt cho người nước ngoài. Hãy:

1. Trả lời một cách tự nhiên, thân thiện và hữu ích
2. Giải thích rõ ràng, dễ hiểu
3. Đưa ra ví dụ cụ thể khi cần
4. Khuyến khích học viên
5. Sửa lỗi một cách tích cực

"""
        
        # Create contextual prompt based on user input
        if any(greeting in user_input.lower() for greeting in ['xin chào', 'hello', 'hi', 'chào']):
            context = "Đây là lời chào. Hãy phản hồi thân thiện và có thể dạy thêm về cách chào hỏi trong tiếng Việt."
        elif any(word in user_input.lower() for word in ['cảm ơn', 'thank you', 'thanks', 'cám ơn']):
            context = "Đây là lời cảm ơn. Hãy phản hồi lịch sự và có thể dạy về cách cảm ơn trong tiếng Việt."
        elif any(word in user_input.lower() for word in ['phản hồi', 'response', 'reply']):
            context = "Học viên đang thắc mắc về phản hồi. Hãy giải thích và tương tác tích cực."
        elif any(word in user_input.lower() for word in ['ngu ngốc', 'stupid', 'bad', 'tệ']):
            context = "Học viên có vẻ không hài lòng. Hãy xin lỗi, giải thích và cải thiện cách phản hồi."
        else:
            context = "Hãy phản hồi như một giáo viên tiếng Việt chuyên nghiệp và hỗ trợ học viên tốt nhất."
        
        # Format the prompt properly
        formatted_input = f"""<s>[INST] {system_prompt}

{context}

Câu nói của học viên: "{user_input}"

Hãy phản hồi một cách thông minh, hữu ích và phù hợp: [/INST]"""
        
        # Tokenize input
        inputs = tokenizer.encode(formatted_input, return_tensors="pt")
        
        if DEVICE != "cpu":
            inputs = inputs.to(model.device)
        
        # Generate response with better parameters
        with torch.no_grad():
            outputs = model.generate(
                inputs,
                max_length=len(inputs[0]) + 256,
                temperature=0.8,
                do_sample=True,
                top_p=0.9,
                top_k=40,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id,
                repetition_penalty=1.2,
                no_repeat_ngram_size=3
            )
        
        # Decode response
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the response part after [/INST]
        if "[/INST]" in response:
            response = response.split("[/INST]")[-1].strip()
        
        # Clean up response
        response = response.strip()
        
        # Ensure response is appropriate
        if not response or len(response) < 10:
            return "Xin chào! Tôi là AI giáo viên tiếng Việt của bạn. Tôi ở đây để giúp bạn học tiếng Việt một cách hiệu quả. Bạn có câu hỏi gì về tiếng Việt không?"
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        return "Xin lỗi, tôi đang gặp một chút trục trặc kỹ thuật. Tôi sẽ cố gắng phản hồi tốt hơn. Bạn có thể thử hỏi lại không?"

# Smart fallback responses for Vietnamese tutoring
SMART_RESPONSES = {
    'greeting': [
        "Xin chào! Tôi là AI giáo viên tiếng Việt của bạn. Tôi rất vui được giúp bạn học tiếng Việt! 👋",
        "Chào bạn! Hôm nay chúng ta sẽ học gì về tiếng Việt nhỉ? 😊",
        "Hello! Tôi có thể giúp bạn luyện tập tiếng Việt. Bạn muốn học về chủ đề gì?"
    ],
    'thanks': [
        "Không có chi! Tôi rất vui được giúp bạn học tiếng Việt. 😊",
        "Rất vinh dự được hỗ trợ bạn! Còn câu hỏi nào khác không?",
        "Cảm ơn bạn! Hãy tiếp tục luyện tập nhé!"
    ],
    'complaint': [
        "Xin lỗi bạn! Tôi sẽ cố gắng phản hồi tốt hơn. Tôi đang học cách trở thành giáo viên giỏi hơn từ feedback của bạn. 🙏",
        "Tôi xin lỗi vì phản hồi chưa tốt. Bạn có thể cho tôi biết bạn mong muốn tôi giải thích như thế nào không?",
        "Cảm ơn góp ý của bạn! Tôi sẽ cải thiện. Bạn có muốn tôi giải thích lại một cách khác không?"
    ],
    'encouragement': [
        "Bạn đang học rất tốt! Tiếp tục cố gắng nhé! 💪",
        "Tuyệt vời! Việc luyện tập tiếng Việt đòi hỏi kiên nhẫn, nhưng bạn làm rất tốt!",
        "Đừng nản lòng! Mỗi câu nói đều giúp bạn tiến bộ trong việc học tiếng Việt!"
    ],
    'default': [
        "Tôi hiểu bạn đang muốn học tiếng Việt. Bạn có thể hỏi tôi về từ vựng, ngữ pháp, phát âm, hay văn hóa Việt Nam! 📚",
        "Rất thú vị! Hãy cùng khám phá tiếng Việt nhé. Bạn muốn tôi giải thích gì?",
        "Tiếng Việt là ngôn ngữ tuyệt vời! Tôi có thể giúp bạn với phát âm, từ vựng, hoặc giao tiếp hàng ngày."
    ]
}

def get_smart_response(user_input):
    """Get contextual smart response based on user input"""
    import random
    
    user_lower = user_input.lower()
    
    # Detect greeting
    if any(word in user_lower for word in ['xin chào', 'chào', 'hello', 'hi', 'hey']):
        return random.choice(SMART_RESPONSES['greeting'])
    
    # Detect thanks
    elif any(word in user_lower for word in ['cảm ơn', 'cám ơn', 'thank you', 'thanks']):
        return random.choice(SMART_RESPONSES['thanks'])
    
    # Detect complaint
    elif any(word in user_lower for word in ['ngu ngốc', 'stupid', 'tệ', 'xấu', 'không tốt', 'bad']):
        return random.choice(SMART_RESPONSES['complaint'])
    
    # Detect need for encouragement
    elif any(word in user_lower for word in ['khó', 'difficult', 'không hiểu', 'confused', 'help']):
        return random.choice(SMART_RESPONSES['encouragement'])
    
    # Default educational response
    else:
        return random.choice(SMART_RESPONSES['default'])

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    model_status = "loaded" if model and tokenizer else "not loaded"
    return jsonify({
        "status": "running",
        "model": MODEL_NAME,
        "device": DEVICE,
        "model_status": model_status
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({"error": "Message is required"}), 400
        
        user_message = data['message'].strip()
        
        if not user_message:
            return jsonify({"error": "Message cannot be empty"}), 400
        
        # Try PhoGPT first, fallback to smart responses
        try:
            ai_response = generate_response(user_message)
            
            # If PhoGPT response is too generic or empty, use smart response
            if not ai_response or len(ai_response.strip()) < 20 or "xin lỗi" in ai_response.lower():
                ai_response = get_smart_response(user_message)
                logger.info("Used smart fallback response")
            
        except Exception as model_error:
            logger.warning(f"PhoGPT failed: {model_error}, using smart response")
            ai_response = get_smart_response(user_message)
        
        return jsonify({
            "response": ai_response,
            "model": MODEL_NAME,
            "device": DEVICE,
            "response_type": "smart_ai"
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/model/reload', methods=['POST'])
def reload_model():
    """Reload model endpoint"""
    success = load_model()
    if success:
        return jsonify({"message": "Model reloaded successfully"})
    else:
        return jsonify({"error": "Failed to reload model"}), 500

# Educational prompts for Vietnamese learning
VIETNAMESE_LEARNING_PROMPTS = {
    "greeting": "### Câu hỏi: Hãy dạy tôi cách chào hỏi bằng tiếng Việt trong các tình huống khác nhau\n### Trả lời:",
    "pronunciation": "### Câu hỏi: Hãy giải thích cách phát âm tiếng Việt cho người nước ngoài\n### Trả lời:",
    "culture": "### Câu hỏi: Hãy giải thích về văn hóa Việt Nam một cách đơn giản\n### Trả lời:",
}

@app.route('/learn/<topic>', methods=['GET'])
def learn_topic(topic):
    """Get learning content for specific topics"""
    if topic not in VIETNAMESE_LEARNING_PROMPTS:
        return jsonify({"error": "Topic not found"}), 404
    
    prompt = VIETNAMESE_LEARNING_PROMPTS[topic]
    response = generate_response(prompt)
    
    return jsonify({
        "topic": topic,
        "content": response
    })

if __name__ == '__main__':
    logger.info("Starting PhoGPT AI Service...")
    
    # Load model on startup
    if load_model():
        logger.info("Model loaded successfully. Starting Flask app...")
        app.run(host='0.0.0.0', port=5000, debug=False)
    else:
        logger.error("Failed to load model. Exiting...")
        exit(1)