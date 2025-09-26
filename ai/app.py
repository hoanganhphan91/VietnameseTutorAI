from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
import random
import torch
from transformers import MBartForConditionalGeneration, MBart50TokenizerFast

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = Flask(__name__)
CORS(app)

# mBART Vietnamese-English model
MODEL_NAME = "NghiemAbe/mbart_VietnameseToEnglish"
CACHE_DIR = "./.cache"

print("[mBART] Loading model and tokenizer...")
tokenizer = MBart50TokenizerFast.from_pretrained(
    MODEL_NAME,
    cache_dir=CACHE_DIR
)
model = MBartForConditionalGeneration.from_pretrained(
    MODEL_NAME,
    cache_dir=CACHE_DIR,
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
)
print("[mBART] Model loaded.")


def mbart_generate_response(user_input, max_new_tokens=100):
    """Generate response using mBART Vietnamese-English model"""
    # Set source language (Vietnamese) and target language (English for translation)
    tokenizer.src_lang = "vi_VN"
    tokenizer.tgt_lang = "en_XX"
    
    # For Vietnamese tutoring, we'll use the model to generate Vietnamese responses
    # by translating from Vietnamese to English then back, or use as is for translation tasks
    inputs = tokenizer(user_input, return_tensors="pt", padding=True, truncation=True, max_length=512)
    
    print("[mBART DEBUG] Before generate")
    with torch.no_grad():
        # Generate translation/response
        generated_tokens = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            num_beams=3,
            do_sample=False,
            early_stopping=True,
            forced_bos_token_id=tokenizer.lang_code_to_id["en_XX"]
        )
    
    print("[mBART DEBUG] After generate")
    response = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
    
    print("[mBART DEBUG] Response:", repr(response))
    
    if not response or response.strip() == user_input.strip():
        response = "I can help you translate Vietnamese to English. Please provide text to translate."
    
    return response.strip()

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "running",
        "service": "Vietnamese AI Tutor",
        "model": "mbart_vietnamese_english",
        "version": "2.0"
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint using PhoGPT"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "Message is required"}), 400
        user_message = data['message'].strip()
        if not user_message:
            return jsonify({"error": "Message cannot be empty"}), 400
        logger.info(f"Received message: {user_message}")
        ai_response = mbart_generate_response(user_message)
        return jsonify({
            "response": ai_response,
            "model": "mBART-Vietnamese-English",
            "response_type": "mbart_translation"
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