from flask import Flask, request, jsonify
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Model configuration
MODEL_NAME = os.getenv("MODEL_NAME", "vinai/PhoGPT-4B-Chat")
DEVICE = os.getenv("DEVICE", "cpu")
# Use local cache directory instead of /models
MODEL_PATH = os.path.join(os.path.dirname(__file__), ".cache")

# Global variables for model and tokenizer
tokenizer = None
model = None

def load_model():
    """Load PhoGPT model and tokenizer"""
    global tokenizer, model
    
    try:
        logger.info(f"Loading model: {MODEL_NAME}")
        
        # Ensure cache directory exists
        os.makedirs(MODEL_PATH, exist_ok=True)
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            MODEL_NAME, 
            trust_remote_code=True,
            cache_dir=MODEL_PATH
        )
        
        # Load model
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            trust_remote_code=True,
            torch_dtype=torch.float32 if DEVICE == "cpu" else torch.float16,
            device_map="auto" if DEVICE != "cpu" else None,
            cache_dir=MODEL_PATH
        )
        
        if DEVICE == "cpu":
            model = model.to("cpu")
        
        logger.info("Model loaded successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        return False

def generate_response(user_input: str, max_length: int = 256) -> str:
    """Generate response using PhoGPT"""
    if not model or not tokenizer:
        return "Mô hình AI chưa được tải. Vui lòng thử lại sau."
    
    try:
        # Format input for PhoGPT-Chat
        # PhoGPT expects specific format: ### Câu hỏi: {question} ### Trả lời:
        if "### Câu hỏi:" not in user_input:
            formatted_input = f"### Câu hỏi: {user_input}\n### Trả lời:"
        else:
            formatted_input = user_input
        
        # Tokenize input
        inputs = tokenizer(
            formatted_input, 
            return_tensors="pt",
            truncation=True,
            max_length=512
        )
        
        if DEVICE != "cpu":
            inputs = {k: v.to(model.device) for k, v in inputs.items()}
        
        # Generate response
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_length=max_length,
                temperature=0.7,
                do_sample=True,
                top_p=0.9,
                top_k=50,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id,
                repetition_penalty=1.1
            )
        
        # Decode response
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the answer part
        if "### Trả lời:" in response:
            response = response.split("### Trả lời:")[-1].strip()
        
        # Clean up response
        response = response.replace(formatted_input, "").strip()
        
        return response if response else "Xin lỗi, tôi không hiểu câu hỏi của bạn. Bạn có thể nói rõ hơn được không?"
        
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        return "Xin lỗi, có lỗi xảy ra khi xử lý câu hỏi của bạn."

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
        
        # Generate response
        ai_response = generate_response(user_message)
        
        return jsonify({
            "response": ai_response,
            "model": MODEL_NAME,
            "device": DEVICE
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