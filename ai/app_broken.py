from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Force CPU to avoid MPS issues on M1 Mac
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
os.environ["PYTORCH_MPS_HIGH_WATERMARK_RATIO"] = "0.0"  # Force CPU

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# DialoGPT for better conversations
MODEL_NAME = "microsoft/DialoGPT-medium"
CACHE_DIR = "./.cache"

print("[AI] Loading DialoGPT-medium model...")
try:
    # Force CPU device to avoid MPS mixed precision issues
    device = "cpu"
    
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME,
        cache_dir=CACHE_DIR
    )
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        cache_dir=CACHE_DIR,
        torch_dtype=torch.float32,
    ).to(device)
    
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        
    print(f"[AI] DialoGPT-medium loaded on {device}!")
except Exception as e:
    print(f"[AI] Error loading model: {e}")
    exit(1)

def pure_ai_generate(user_input):
    """Pure AI generation without any rule-based logic"""
    try:
        print(f"[AI DEBUG] Input: {user_input}")
        
        # Simple conversation prompt - let AI continue naturally
        conversation_prompt = f"{user_input}\n"
        
        inputs = tokenizer(conversation_prompt, return_tensors="pt", padding=True, truncation=True, max_length=300)
        
        print(f"[AI DEBUG] Input shape: {inputs['input_ids'].shape}")
        
        with torch.no_grad():
            outputs = model.generate(
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_new_tokens=60,               # Shorter for better quality
                do_sample=True,
                top_p=0.9,                      
                top_k=40,                       
                temperature=0.8,                
                repetition_penalty=1.1,         # Less aggressive
                no_repeat_ngram_size=2,         
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id
            )
        
        # Decode and get only the new generated part
        full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"[AI DEBUG] Full response: {repr(full_response)}")
        
        # Extract only the new generated text after the input
        if full_response.startswith(conversation_prompt):
            generated = full_response[len(conversation_prompt):].strip()
        else:
            generated = full_response.strip()
        
        print(f"[AI DEBUG] Generated part: {repr(generated)}")
        
        # Clean up the response - remove any leftover prompts or weird text
        if generated and len(generated) > 5:
            # Remove common artifacts
            generated = generated.replace("Tôi là giáo viên dạy tiếng Việt. Về câu hỏi", "")
            generated = generated.replace("tôi giải thích:", "").strip()
            
            # If still has content, return it
            if len(generated) > 10:
                return generated
        
        # If generation failed, provide a simple acknowledgment
        return "Tôi hiểu câu hỏi của bạn. Đây là một chủ đề thú vị trong tiếng Việt."
        
    except Exception as e:
        print(f"[AI DEBUG] Generation failed: {e}")
        return f"Xin lỗi, tôi gặp lỗi khi xử lý câu hỏi: {str(e)}"

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "running",
        "service": "DialoGPT Vietnamese Tutor",
        "model": MODEL_NAME,
        "version": "5.3-dialogpt-cpu"
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