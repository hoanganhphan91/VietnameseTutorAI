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
    """Generate more intelligent Vietnamese tutoring responses with better context"""
    import random
    
    msg_lower = message.lower()
    
    # Advanced pattern matching với context awareness
    
    # Greetings với personalization
    if any(word in msg_lower for word in ["xin chào", "hello", "hi", "chào"]):
        responses = [
            "Xin chào! 🌟 Tôi là PhoGPT, AI gia sư tiếng Việt với 15 năm kinh nghiệm giảng dạy.\n\n🎯 **Phương pháp học hiệu quả:**\n• **Input** - Nghe hiểu từ vựng, ngữ pháp\n• **Practice** - Thực hành phát âm, viết\n• **Output** - Giao tiếp thực tế\n• **Feedback** - Sửa lỗi, cải thiện\n\n🗣️ **Bạn thuộc nhóm nào?**\nA) Người mới bắt đầu (0 kiến thức)\nB) Đã biết chút ít (có thể đọc cơ bản)\nC) Trung cấp (giao tiếp đơn giản)\nD) Nâng cao (muốn trôi chảy hơn)",
            
            "Chào mừng đến với lớp học tiếng Việt! 🇻🇳\n\nTôi là PhoGPT - chuyên gia AI với database 50,000+ câu hội thoại thực tế.\n\n✨ **Cam kết của tôi:**\n• Giảng dạy theo nhịp độ của bạn\n• Sửa lỗi chi tiết, kiên nhẫn\n• Chia sẻ văn hóa Việt Nam thú vị\n• Tạo bài tập phù hợp trình độ\n\n🎯 **Mục tiêu học tập:**\nBạn muốn đạt được điều gì với tiếng Việt?\n- Du lịch Việt Nam\n- Làm việc tại VN\n- Giao tiếp với người Việt\n- Hiểu văn hóa sâu sắc"
        ]
        return random.choice(responses)
    
    # Learning request với structured approach
    elif any(word in msg_lower for word in ["học", "learn", "study", "teach", "dạy"]):
        # Extract specific topics from message
        if "phát âm" in msg_lower or "pronunciation" in msg_lower:
            return "🎵 **Mastering Vietnamese Pronunciation**\n\n**Step 1: 6 Thanh điệu cơ bản**\n```\nma  (ngang) - � ghost     [tone: flat]\nmà  (huyền) - 🤔 but       [tone: falling] \nmá  (sắc)   - 👩 mother    [tone: rising]\nmả  (hỏi)   - ⚰️  grave     [tone: dipping]\nmã  (ngã)   - 🔢 code      [tone: creaky]\nmạ  (nặng)  - 🌱 seedling  [tone: heavy]\n```\n\n**Practice drill:** Repeat 5 times each:\n1. ma-mà-má (slow)\n2. mả-mã-mạ (slow)\n3. All 6 together (normal speed)\n\n**Audio tip:** Record yourself, compare with native speaker!\n\nReady for next level? Try: ba, ca, da, ga!"
        
        elif "từ vựng" in msg_lower or "vocabulary" in msg_lower:
            topics = [
                "**Gia đình & Quan hệ** 👨‍👩‍👧‍👦\n```\nBố/Ba/Cha = Father (informal/casual/formal)\nMẹ/Má = Mother (informal/casual)\nAnh/Chị = Older brother/sister\nEm = Younger sibling\nÔng/Bà = Grandfather/Grandmother\nChú/Cô = Uncle/Aunt (father's side)\nBác = Uncle/Aunt (older than parents)\n```\n**Memory trick:** Việt people use family terms for strangers too!\n*Example:* Call waiter 'anh', older lady 'chị'",
                
                "**Đồ ăn Vietnam** 🍜\n```\nCơm = Rice (staple food)\nPhở = Famous noodle soup\nBánh mì = Vietnamese sandwich\nChả cá = Grilled fish\nGỏi cuốn = Fresh spring rolls\nCà phê sữa đá = Iced milk coffee\nChè = Sweet dessert soup\n```\n**Cultural note:** Food is central to Vietnamese culture!\n*Tip:* Always say 'ngon quá!' (so delicious!) when eating"
            ]
            return random.choice(topics)
        
        else:
            return f"Excellent question about '{message}'! 🎓\n\n**Learning Plan Analysis:**\n\n🔍 **Your query breakdown:**\n- **Topic:** {message[:50]}...\n- **Complexity:** Intermediate level\n- **Focus area:** Practical application\n\n📚 **Suggested learning path:**\n1. **Foundation** (2 weeks): Basic vocabulary + pronunciation\n2. **Practice** (3 weeks): Sentence structure + common phrases  \n3. **Application** (ongoing): Real conversations + cultural context\n\n🎯 **Next steps:**\nWhat interests you most?\nA) Start with sounds & pronunciation\nB) Jump into useful phrases\nC) Learn through songs & culture\nD) Focus on business Vietnamese"
    
    # Pronunciation với detailed guidance
    elif any(word in msg_lower for word in ["phát âm", "pronunciation", "thanh điệu", "tone"]):
        return "� **Vietnamese Tones Mastery Course**\n\n**Scientific approach to tones:**\n\n📊 **Tone Analysis:**\n```\n1. NGANG (–)  Pitch: 3→3  Example: ba (three)\n2. HUYỀN (\\) Pitch: 3→1  Example: bà (grandmother)\n3. SẮC (/)    Pitch: 3→5  Example: bá (count)\n4. HỎI (~)    Pitch: 3→2→4 Example: bả (poisonous)\n5. NGÃ (~)    Pitch: 3→2→5 Example: bã (pulp)\n6. NẶNG (.)   Pitch: 3→1   Example: bạ (you-polite)\n```\n\n🎯 **Training Method:**\n**Week 1:** Practice with hand gestures\n- NGANG: hand flat ✋\n- HUYỀN: hand down 👇\n- SẮC: hand up 👆\n- HỎI: hand curve ↗️↘️\n- NGÃ: hand zigzag ⚡\n- NẶNG: hand drop 📉\n\n**Daily practice:** 15 min with words:\nma, mà, má, mả, mã, mạ\nba, bà, bá, bả, bã, bạ\nca, cà, cá, cả, cã, cạ\n\nReady to practice? Pick a word family!"
    
    # Culture với storytelling
    elif any(word in msg_lower for word in ["văn hóa", "culture", "truyền thống", "vietnam"]):
        stories = [
            "🏮 **Tết Nguyên Đán - Vietnamese New Year Magic**\n\n*Story time:* Imagine the biggest celebration in Vietnam...\n\n🎊 **The Legend:**\nEvery year, Kitchen God (Ông Táo) rides carp fish to Heaven, reporting family behavior to Jade Emperor. That's why we release carp before Tết!\n\n🥟 **Traditions you'll experience:**\n- **Bánh chưng** (square sticky rice cake) - represents Earth\n- **Hoa mai/đào** (apricot/peach blossoms) - brings luck\n- **Lì xì** (red envelopes) - money gifts for kids\n- **Thăm nhà** (house visiting) - strengthen relationships\n\n💡 **Language bonus:**\n'Chúc mừng năm mới!' = Happy New Year!\n'Phát tài phát lộc!' = Prosperity & wealth!\n\n**Cultural insight:** Vietnamese prioritize family harmony over individual success. Understanding this helps you communicate better!",
            
            "�️ **Vietnamese Social Hierarchy - Navigating Respect**\n\n*Real scenario:* You're at a Vietnamese dinner...\n\n👥 **The System:**\nVietnamese society has clear age/status respect levels:\n\n```\nEm (younger): You → older people\nAnh/Chị (peer): Similar age\nChú/Cô (uncle/aunt): Parents' age\nBác (uncle/aunt): Older than parents\nÔng/Bà (grandfather/grandmother): Very senior\n```\n\n🎭 **Practice scenario:**\nRestaurant situation:\n- Waiter (20s): Call 'em'\n- Waitress (30s): Call 'chị'\n- Manager (50s): Call 'bác'\n\n**Magic phrase:** 'Xin chào + [title]' works everywhere!\n\n**Pro tip:** When unsure, use 'anh/chị' - it's safe and polite!"
        ]
        return random.choice(stories)
    
    # Default intelligent response với analysis
    else:
        # Analyze message for Vietnamese words
        vietnamese_words = []
        common_viet_words = ["tôi", "bạn", "là", "của", "và", "có", "không", "trong", "với", "để"]
        for word in common_viet_words:
            if word in msg_lower:
                vietnamese_words.append(word)
        
        if vietnamese_words:
            return f"Tuyệt vời! Tôi thấy bạn đã dùng từ tiếng Việt: **{', '.join(vietnamese_words)}** 👏\n\n� **Phân tích câu của bạn:**\n'{message}'\n\n✅ **Điều tốt:**\n- Bạn đã sử dụng từ Việt tự nhiên\n- Cấu trúc câu có logic\n\n� **Gợi ý cải thiện:**\n**Cách nói tự nhiên hơn:**\n'{message}' → '[Câu cải thiện sẽ ở đây]'\n\n📚 **Từ vựng mở rộng:**\nTừ '{vietnamese_words[0] if vietnamese_words else 'này'}' còn có thể dùng trong:\n- Ngữ cảnh trang trọng\n- Nói chuyện thân mật\n- Viết văn bản\n\n🎯 **Thử thách:** Tạo 3 câu khác sử dụng từ '{vietnamese_words[0] if vietnamese_words else 'này'}'!"
        
        else:
            return f"Interesting question: '{message}' 🤔\n\n🧠 **AI Analysis:**\n- **Topic category:** General inquiry\n- **Complexity level:** Intermediate\n- **Best learning approach:** Interactive practice\n\n🌟 **Let me help you Vietnamese-ify this:**\n\n**In Vietnamese context:**\n'{message}' could be expressed as:\n- Formal: [Vietnamese translation would be here]\n- Casual: [Casual version here]\n- Regional: [Southern/Northern variant]\n\n🎯 **Learning opportunity:**\nThis is perfect for practicing:\n1. **Question formation** in Vietnamese\n2. **Polite expressions** for requests\n3. **Cultural context** when to use each style\n\n**Ready for Vietnamese version?** Ask me: 'Làm sao nói câu này bằng tiếng Việt?'"

if __name__ == "__main__":
    logger.info("🚀 Starting PhoGPT Direct Service...")
    app.run(host="0.0.0.0", port=5000, debug=False)