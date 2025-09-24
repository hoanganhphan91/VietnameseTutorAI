from flask import Flask, request, jsonify
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "Mock AI Service"})

@app.route('/chat', methods=['POST'])
def chat():
    """Smart mock chat endpoint with varied responses"""
    try:
        data = request.json
        user_message = data.get('message', '')
        
        logger.info(f"Received message: {user_message}")
        
        # Smart responses based on Vietnamese learning context
        user_lower = user_message.lower()
        
        if any(word in user_lower for word in ["xin chào", "hello", "hi", "chào bạn"]):
            response = "Xin chào! Tôi là AI gia sư tiếng Việt. Tôi có thể giúp bạn:\n• Luyện phát âm\n• Học từ vựng mới\n• Hiểu văn hóa Việt Nam\n• Thực hành hội thoại\n\nBạn muốn bắt đầu từ đâu?"
            
        elif any(word in user_lower for word in ["học", "learning", "study", "muốn học"]):
            response = "Tuyệt vời! Bạn muốn học tiếng Việt à? Hãy bắt đầu với:\n\n1. **Chào hỏi cơ bản:**\n   - Xin chào (Sin chow) = Hello\n   - Cảm ơn (Gahm uhn) = Thank you\n   - Tạm biệt (Dahm bee-ut) = Goodbye\n\n2. **Giới thiệu bản thân:**\n   - Tôi tên là... = My name is...\n   - Tôi đến từ... = I come from...\n\nBạn thử nói 'Xin chào' xem sao?"
            
        elif any(word in user_lower for word in ["cảm ơn", "thank", "thanks", "cám ơn"]):
            response = "Không có gì! 😊\n\n**Các cách nói 'cảm ơn' trong tiếng Việt:**\n- Cảm ơn (formal)\n- Cám ơn (informal)\n- Cảm ơn bạn nhiều (Thank you very much)\n- Cảm ơn anh/chị (Thank you sir/miss)\n\nBạn có muốn học thêm về cách xưng hô không?"
            
        elif any(word in user_lower for word in ["phát âm", "pronunciation", "nói", "speak"]):
            response = "Phát âm tiếng Việt có 6 thanh điệu:\n\n1. **Ngang** (a) - giọng bằng\n2. **Huyền** (à) - giọng xuống\n3. **Sắc** (á) - giọng lên\n4. **Hỏi** (ả) - giọng lên xuống\n5. **Ngã** (ã) - giọng gãy\n6. **Nặng** (ạ) - giọng ngắt\n\nThử phát âm từ 'ma, mà, má, mả, mã, mạ' - 6 từ khác nhau!"
            
        elif any(word in user_lower for word in ["từ vựng", "vocabulary", "word", "words"]):
            response = "Hãy học một số từ vựng cơ bản:\n\n**Gia đình:**\n- Cha/Ba = Father\n- Mẹ/Má = Mother  \n- Anh/Chị = Older brother/sister\n- Em = Younger sibling\n\n**Đồ ăn:**\n- Cơm = Rice\n- Phở = Pho noodle soup\n- Bánh mì = Bread/sandwich\n- Nước = Water\n\nBạn muốn học chủ đề nào khác?"
            
        elif any(word in user_lower for word in ["văn hóa", "culture", "cultural", "tradition"]):
            response = "Văn hóa Việt Nam rất phong phú! 🇻🇳\n\n**Điều thú vị:**\n- Người Việt chào hỏi bằng cách cúi đầu nhẹ\n- Ăn cơm bằng đũa và thìa\n- Tết Nguyên Đán là lễ quan trọng nhất\n- Áo dài là trang phục truyền thống\n\n**Phép lịch sự:**\n- Luôn dùng hai tay khi nhận quà\n- Gọi người lớn tuổi là anh/chị/bác\n- Cởi giày khi vào nhà\n\nBạn có muốn biết thêm về phong tục nào không?"
            
        elif any(word in user_lower for word in ["numbers", "số", "đếm"]):
            response = "Học đếm số trong tiếng Việt:\n\n**1-10:**\n1. Một (mohdt)\n2. Hai (high)\n3. Ba (bah)\n4. Bốn (bohn)\n5. Năm (nahm)\n6. Sáu (shah-oo)\n7. Bảy (by)\n8. Tám (tahm)\n9. Chín (cheen)\n10. Mười (moo-uhr-ee)\n\nThử đếm từ 1 đến 10 xem sao!"
            
        else:
            # More dynamic response based on message content
            import random
            
            responses = [
                f"Thú vị! Bạn vừa nói '{user_message}'. Tôi có thể giúp bạn:\n• Sửa phát âm\n• Giải thích ngữ pháp\n• Dạy từ mới\n• Chia sẻ văn hóa\n\nBạn muốn tập trung vào điều gì?",
                
                f"Câu '{user_message}' của bạn rất hay! Trong tiếng Việt, chúng ta có thể nói theo nhiều cách khác nhau tùy theo ngữ cảnh. Bạn có muốn học cách diễn đạt trang trọng hơn không?",
                
                f"Tôi hiểu bạn muốn nói '{user_message}'. Hãy thử phân tích câu này:\n• Chủ ngữ là gì?\n• Động từ là gì?\n• Có tính từ nào không?\n\nTôi sẽ giúp bạn cải thiện câu này!",
                
                f"Hay quá! '{user_message}' - đây là cơ hội tốt để học:\n🔤 Phát âm chuẩn\n📚 Từ vựng liên quan  \n🎭 Ngữ cảnh sử dụng\n🌏 Khác biệt văn hóa\n\nBạn muốn bắt đầu từ đâu?"
            ]
            
            response = random.choice(responses)
        
        return jsonify({
            "response": response,
            "corrections": [],
            "cultural_context": "Đây là phản hồi từ mock AI service để test hệ thống."
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        "message": "Mock Vietnamese AI Tutor Service",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "chat": "/chat"
        }
    })

if __name__ == '__main__':
    logger.info("Starting Mock Vietnamese AI Tutor Service...")
    app.run(host='0.0.0.0', port=5000, debug=True)