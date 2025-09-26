from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Vietnamese GPT model - pure AI generation, no rules
MODEL_NAME = "NlpHUST/gpt2-vietnamese"
CACHE_DIR = "./.cache"

print("[AI] Loading Vietnamese model...")
try:
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME,
        cache_dir=CACHE_DIR
    )
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        cache_dir=CACHE_DIR,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    print(f"[AI] Model {MODEL_NAME} loaded successfully!")
except Exception as e:
    print(f"[AI] Error loading Vietnamese model: {e}")
    # Fallback to standard GPT2
    MODEL_NAME = "gpt2"
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, cache_dir=CACHE_DIR)
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, cache_dir=CACHE_DIR)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    print(f"[AI] Fallback to {MODEL_NAME}")

def pure_ai_generate(user_input):
    """Pure AI generation without any rule-based logic"""
    try:
        print(f"[AI DEBUG] Input: {user_input}")
        
        # Simple and natural teacher prompt
        teacher_prompt = f"Là giáo viên dạy tiếng Việt cho người nước ngoài, tôi giải thích về '{user_input}': "
        
        inputs = tokenizer(teacher_prompt, return_tensors="pt", padding=True, truncation=True, max_length=400)
        
        print(f"[AI DEBUG] Input shape: {inputs['input_ids'].shape}")
        
        with torch.no_grad():
            outputs = model.generate(
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_new_tokens=100,
                do_sample=True,
                top_p=0.9,
                temperature=0.8,
                repetition_penalty=1.2,
                no_repeat_ngram_size=3,
                pad_token_id=tokenizer.eos_token_id
            )
        
        # Decode full response
        full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"[AI DEBUG] Full response: {repr(full_response)}")
        
        # Extract the generated explanation (after the prompt)
        if teacher_prompt in full_response:
            generated = full_response.replace(teacher_prompt, "").strip()
        else:
            generated = full_response.strip()
        
        print(f"[AI DEBUG] Generated part: {repr(generated)}")
        
        # If nothing generated or too short, return a fallback teacher response
        if not generated or len(generated) < 5:
            return f"Như một giáo viên tiếng Việt, tôi có thể giải thích rằng: {full_response}"
        
        return generated
        
    except Exception as e:
        print(f"[AI DEBUG] Generation failed: {e}")
        return f"AI Error: {str(e)}"

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "running",
        "service": "Pure AI Vietnamese Tutor",
        "model": MODEL_NAME,
        "version": "4.0-pure-ai"
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Pure AI chat endpoint - no rule-based responses"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "Message is required"}), 400
        
        user_message = data['message'].strip()
        if not user_message:
            return jsonify({"error": "Message cannot be empty"}), 400
        
        logger.info(f"User: {user_message}")
        
        # Pure AI generation
        ai_response = pure_ai_generate(user_message)
        
        logger.info(f"AI: {ai_response}")
        
        return jsonify({
            "response": ai_response,
            "model": MODEL_NAME,
            "response_type": "pure_ai_generation"
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health endpoint for service monitoring"""
    return jsonify({"status": "healthy", "service": "Pure AI Vietnamese Tutor"})

if __name__ == '__main__':
    logger.info("Starting Pure AI Vietnamese Tutor Service...")
    app.run(host='0.0.0.0', port=5002, debug=False)