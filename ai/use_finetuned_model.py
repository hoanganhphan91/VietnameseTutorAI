#!/usr/bin/env python3
"""
Load và sử dụng PhoGPT đã fine-tuned
"""
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import torch

def load_finetuned_model(base_model_path, adapter_path=None):
    """Load fine-tuned PhoGPT"""
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        base_model_path,
        trust_remote_code=True
    )
    
    # Load base model
    model = AutoModelForCausalLM.from_pretrained(
        base_model_path,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True
    )
    
    # Load LoRA adapter nếu có
    if adapter_path:
        model = PeftModel.from_pretrained(model, adapter_path)
        print("✅ Loaded LoRA adapter")
    
    return model, tokenizer

def generate_response(model, tokenizer, prompt):
    """Generate response with fine-tuned model"""
    
    # Format prompt
    formatted_prompt = f"### Câu hỏi: {prompt}\n\n### Trả lời:"
    
    # Tokenize
    inputs = tokenizer(formatted_prompt, return_tensors="pt")
    
    # Generate
    with torch.no_grad():
        outputs = model.generate(
            inputs.input_ids,
            max_new_tokens=300,
            temperature=0.7,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
            repetition_penalty=1.1
        )
    
    # Decode
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    response = response.replace(formatted_prompt, "").strip()
    
    return response

# Example usage
if __name__ == "__main__":
    BASE_MODEL = "vinai/PhoGPT-4B-Chat"
    ADAPTER_PATH = "./phogpt-lora-vietnamese-tutor"  # LoRA adapter path
    
    # Load model
    model, tokenizer = load_finetuned_model(BASE_MODEL, ADAPTER_PATH)
    
    # Test
    questions = [
        "Cách phát âm thanh hỏi như thế nào?",
        "Giải thích văn hóa chào hỏi Việt Nam",
        "Làm sao học từ vựng hiệu quả?"
    ]
    
    for q in questions:
        print(f"❓ {q}")
        response = generate_response(model, tokenizer, q)
        print(f"🤖 {response}\n")