from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
import random
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = Flask(__name__)
CORS(app)

# Test with lightweight model first
MODEL_NAME = "gpt2"
CACHE_DIR = "./.cache"

print("[GPT-2] Loading model and tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    cache_dir=CACHE_DIR
)
tokenizer.padding_side = 'left'
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    cache_dir=CACHE_DIR,
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
print("[GPT-2] Model loaded.")


def gpt2_generate_response(user_input, max_new_tokens=50):
    prompt = user_input.strip()
    inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True, max_length=512)
    input_ids = inputs["input_ids"]
    attention_mask = inputs["attention_mask"]
    print("[GPT-2 DEBUG] Before generate")
    with torch.no_grad():
        outputs = model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            max_new_tokens=max_new_tokens,
            pad_token_id=tokenizer.eos_token_id,
            do_sample=False,  # Greedy decoding, nhanh hơn
            num_beams=1,      # Tắt beam search
            early_stopping=True
        )
    print("[GPT-2 DEBUG] After generate")
    decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Trả về phần trả lời sau prompt
    if decoded.startswith(prompt):
        response = decoded[len(prompt):].strip()
    else:
        response = decoded.strip()
    print("[GPT-2 DEBUG] Decoded:", repr(decoded))
    print("[GPT-2 DEBUG] Response:", repr(response))
    if not response:
        response = "(GPT-2 không sinh ra câu trả lời phù hợp)"
    return response

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
    """Main chat endpoint using PhoGPT"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "Message is required"}), 400
        user_message = data['message'].strip()
        if not user_message:
            return jsonify({"error": "Message cannot be empty"}), 400
        logger.info(f"Received message: {user_message}")
        ai_response = gpt2_generate_response(user_message)
        return jsonify({
            "response": ai_response,
            "model": "PhoGPT-4B-Chat",
            "response_type": "phogpt"
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