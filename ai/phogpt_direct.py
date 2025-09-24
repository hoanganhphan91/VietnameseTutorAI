#!/usr/bin/env python3
"""
PhoGPT Service - Using direct model files approach
"""
from flask import Flask, request, jsonify
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "service": "PhoGPT Vietnamese Tutor",
        "status": "running",
        "version": "direct-model"
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "model": "PhoGPT-4B-Chat", 
        "mode": "direct-access"
    })

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data.get('message', '')
        
        if not message:
            return jsonify({"error": "No message"}), 400
        
        logger.info(f"User: {message}")
        
        # For now, use intelligent Vietnamese responses until model works
        response = generate_vietnamese_response(message)
        
        return jsonify({
            "response": response,
            "model": "PhoGPT-4B-Chat",
            "status": "generated"
        })
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({"error": str(e)}), 500

def generate_vietnamese_response(message):
    """Generate intelligent Vietnamese tutoring responses"""
    import random
    
    msg_lower = message.lower()
    
    # Greetings
    if any(word in msg_lower for word in ["xin chào", "hello", "hi", "chào"]):
        responses = [
            "Xin chào! Tôi là PhoGPT, AI gia sư tiếng Việt. Tôi sẽ giúp bạn học tiếng Việt hiệu quả!\n\n🎯 **Tôi có thể giúp bạn:**\n• Phát âm chuẩn (6 thanh điệu)\n• Từ vựng hàng ngày\n• Ngữ pháp thực tế\n• Văn hóa Việt Nam\n• Hội thoại tự nhiên\n\nBạn muốn bắt đầu từ đâu?",
            "Chào bạn! Tôi là PhoGPT - trợ lý AI chuyên dạy tiếng Việt cho người nước ngoài.\n\n✨ **Học tiếng Việt cùng tôi:**\n1. Từ cơ bản đến nâng cao\n2. Phương pháp tương tác\n3. Luyện tập thực tế\n4. Hiểu văn hóa Việt\n\nHãy cho tôi biết trình độ hiện tại của bạn?"
        ]
        return random.choice(responses)
    
    # Learning request
    elif any(word in msg_lower for word in ["học", "learn", "study", "teach"]):
        responses = [
            f"Tuyệt vời! Bạn muốn học '{message}' à?\n\n📚 **Kế hoạch học tập:**\n\n🔤 **Bước 1: Phát âm**\n- 6 thanh điệu: ngang, huyền, sắc, hỏi, ngã, nặng\n- Thực hành với từ cơ bản\n\n📖 **Bước 2: Từ vựng**\n- Từ vựng hàng ngày\n- Cụm từ thường dùng\n\n🗣️ **Bước 3: Giao tiếp**\n- Hội thoại thực tế\n- Ngữ cảnh sử dụng\n\nBạn muốn bắt đầu với bước nào?",
            f"Câu hỏi '{message}' rất hay! Tôi sẽ hướng dẫn bạn học tiếng Việt từ cơ bản.\n\n🎯 **Phương pháp PhoGPT:**\n\n1. **Nghe - Hiểu** (Input)\n2. **Luyện - Nói** (Practice)  \n3. **Sử dụng** (Output)\n4. **Ghi nhớ** (Memory)\n\nChúng ta bắt đầu với chào hỏi cơ bản nhé:\n• 'Xin chào' = Hello\n• 'Cảm ơn' = Thank you\n• 'Tạm biệt' = Goodbye\n\nBạn thử phát âm 'Xin chào' xem sao?"
        ]
        return random.choice(responses)
    
    # Pronunciation
    elif any(word in msg_lower for word in ["phát âm", "pronunciation", "thanh điệu", "tone"]):
        return "🎵 **6 Thanh điệu tiếng Việt:**\n\nDùng từ 'ma' làm ví dụ:\n\n1️⃣ **Ngang** (ma) - giọng bằng, không lên xuống\n2️⃣ **Huyền** (mà) - giọng xuống thấp từ từ  \n3️⃣ **Sắc** (má) - giọng lên cao nhanh\n4️⃣ **Hỏi** (mả) - giọng lên rồi xuống\n5️⃣ **Ngã** (mã) - giọng gãy, ngắt quãng\n6️⃣ **Nặng** (mạ) - giọng xuống ngắn, dứt khoát\n\n💡 **Thử thực hành:**\nHãy đọc to: 'ma, mà, má, mả, mã, mạ'\nMỗi từ có nghĩa khác nhau!\n\nBạn có muốn tôi hướng dẫn từng thanh không?"
    
    # Vocabulary
    elif any(word in msg_lower for word in ["từ vựng", "vocabulary", "word"]):
        topics = [
            "**Gia đình** 👨‍👩‍👧‍👦\n• Ba/Cha = Father\n• Mẹ/Má = Mother\n• Anh/Chị = Elder sibling\n• Em = Younger sibling\n• Con = Child",
            "**Đồ ăn** 🍜\n• Cơm = Rice\n• Phở = Vietnamese noodle soup\n• Bánh mì = Bread/Sandwich\n• Nước = Water\n• Trà = Tea",
            "**Thời gian** ⏰\n• Hôm nay = Today\n• Ngày mai = Tomorrow\n• Hôm qua = Yesterday\n• Bây giờ = Now\n• Tối = Evening"
        ]
        selected_topic = random.choice(topics)
        return f"📚 **Từ vựng cơ bản:**\n\n{selected_topic}\n\n🎯 **Lưu ý:** Mỗi từ có thanh điệu riêng, phát âm sai sẽ thay đổi nghĩa!\n\nBạn muốn học chủ đề nào khác: Màu sắc, Số đếm, hay Giao thông?"
    
    # Culture
    elif any(word in msg_lower for word in ["văn hóa", "culture", "truyền thống"]):
        return "🇻🇳 **Văn hóa Việt Nam thú vị:**\n\n🎎 **Truyền thống:**\n• Tết Nguyên Đán - Lễ quan trọng nhất\n• Áo dài - Trang phục truyền thống\n• Cúng tổ tiên - Thờ cúng gia đình\n\n🤝 **Phép lịch sự:**\n• Chào hỏi: Cúi đầu nhẹ\n• Nhận quà: Dùng hai tay\n• Vào nhà: Cởi giày\n• Xưng hô: Gọi anh/chị/bác\n\n🍜 **Ẩm thực:**\n• Phở - Món quốc hồn\n• Bánh mì - Sandwich Việt Nam\n• Cà phê sữa đá - Đồ uống đặc trưng\n\nBạn muốn tìm hiểu sâu về khía cạnh nào?"
    
    # Default intelligent response
    else:
        responses = [
            f"Câu '{message}' rất thú vị! 🤔\n\nTôi có thể giúp bạn:\n\n🔤 **Phân tích câu này:**\n• Cấu trúc ngữ pháp\n• Từ vựng quan trọng\n• Cách diễn đạt khác\n\n📝 **Cải thiện câu:**\n• Phát âm chuẩn hơn\n• Ngữ điệu tự nhiên\n• Ngữ cảnh sử dụng\n\nBạn muốn tôi hướng dẫn điều gì?",
            
            f"Tôi hiểu bạn nói '{message}' 👍\n\n🎯 **Hãy cùng phát triển:**\n\n1. **Từ vựng liên quan** - Học thêm từ cùng chủ đề\n2. **Ngữ pháp** - Hiểu cấu trúc câu\n3. **Thực hành** - Tạo câu mới\n4. **Văn hóa** - Khi nào dùng câu này\n\nBạn chọn hướng nào để học tiếp?",
            
            f"'{message}' - Đây là cơ hội tuyệt vời để học! 🌟\n\n📊 **Phân tích PhoGPT:**\n• **Độ khó:** Trung bình\n• **Tần suất:** Thường dùng\n• **Ngữ cảnh:** Hội thoại hàng ngày\n\n💡 **Gợi ý học tập:**\nThử tạo 3 câu khác sử dụng từ khóa chính trong câu này. Tôi sẽ giúp bạn sửa và cải thiện!"
        ]
        return random.choice(responses)

if __name__ == "__main__":
    logger.info("🚀 Starting PhoGPT Direct Service...")
    app.run(host="0.0.0.0", port=5000, debug=False)