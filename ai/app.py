from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

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

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "running",
        "service": "Vietnamese AI Tutor",
        "model": "intelligent_rule_based",
        "version": "2.0"
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
        
        logger.info(f"Received message: {user_message}")
        
        # Generate intelligent response
        ai_response = generate_intelligent_response(user_message)
        
        return jsonify({
            "response": ai_response,
            "model": "vietnamese_tutor_ai",
            "response_type": "intelligent_rule_based"
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health endpoint for service monitoring"""
    return jsonify({"status": "healthy", "service": "Vietnamese AI Tutor"})

if __name__ == '__main__':
    logger.info("Starting Vietnamese AI Tutor Service...")
    app.run(host='0.0.0.0', port=5002, debug=False)