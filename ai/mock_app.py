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
    """Mock chat endpoint for testing"""
    try:
        data = request.json
        user_message = data.get('message', '')
        
        logger.info(f"Received message: {user_message}")
        
        # Mock responses based on input
        if "hello" in user_message.lower() or "hi" in user_message.lower():
            response = "Xin chào! Tôi là AI gia sư tiếng Việt. Tôi có thể giúp bạn học tiếng Việt."
        elif "vietnamese" in user_message.lower():
            response = "Tiếng Việt là một ngôn ngữ rất đẹp! Bạn muốn học về điều gì?"
        elif "thank" in user_message.lower():
            response = "Không có gì! Tôi luôn sẵn sàng giúp bạn học tiếng Việt."
        else:
            response = f"Tôi hiểu bạn nói: '{user_message}'. Đây là câu trả lời mẫu từ AI gia sư tiếng Việt."
        
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