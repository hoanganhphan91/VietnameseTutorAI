from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Force CPU to avoid issues
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Simple reliable model
MODEL_NAME = "microsoft/DialoGPT-small"  # Smaller, more stable
CACHE_DIR = "./.cache"

print("[AI] Loading DialoGPT-small...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, cache_dir=CACHE_DIR)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, cache_dir=CACHE_DIR)

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

print("[AI] Model loaded!")

def simple_generate(user_input):
    """Simple AI generation - no tricks, just let the model talk"""
    try:
        print(f"[DEBUG] Input: '{user_input}'")
        
        # Encode user input
        inputs = tokenizer.encode(user_input + tokenizer.eos_token, return_tensors="pt")
        
        # Generate response 
        with torch.no_grad():
            outputs = model.generate(
                inputs,
                max_length=inputs.shape[1] + 50,  # Add 50 tokens max
                do_sample=True,
                top_p=0.9,
                temperature=0.8,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id
            )
        
        # Decode and extract new part
        full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Get only the new generated part
        if full_response.startswith(user_input):
            response = full_response[len(user_input):].strip()
        else:
            response = full_response
            
        print(f"[DEBUG] Generated: '{response}'")
        
        if not response or len(response) < 3:
            return f"Tôi hiểu bạn nói về '{user_input}'. Đây là chủ đề thú vị!"
            
        return response
        
    except Exception as e:
        print(f"[ERROR] Generation failed: {e}")
        return f"Về '{user_input}': Xin lỗi, tôi gặp lỗi khi xử lý câu hỏi này."

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({
        "status": "running", 
        "service": "Simple AI Tutor",
        "model": MODEL_NAME
    })

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "Message is required"}), 400
        
        user_message = data['message'].strip()
        if not user_message:
            return jsonify({"error": "Message cannot be empty"}), 400
        
        logger.info(f"User: {user_message}")
        
        # Simple AI generation
        ai_response = simple_generate(user_message)
        
        logger.info(f"AI: {ai_response}")
        
        return jsonify({
            "response": ai_response,
            "model": MODEL_NAME,
            "response_type": "simple_ai"
        })
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    logger.info("Starting Simple AI Service...")
    app.run(host='0.0.0.0', port=5002, debug=False)