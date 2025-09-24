#!/usr/bin/env python3
"""
Download PhoGPT-4B model offline - Simple version
"""
import os
import sys
from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import snapshot_download
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_NAME = "vinai/PhoGPT-4B-Chat"
CACHE_DIR = os.path.join(os.path.dirname(__file__), ".cache")

def download_model_simple():
    """Download PhoGPT-4B model using snapshot_download (no model loading)"""
    try:
        logger.info(f"Downloading model: {MODEL_NAME}")
        logger.info(f"Cache directory: {CACHE_DIR}")
        
        # Ensure cache directory exists
        os.makedirs(CACHE_DIR, exist_ok=True)
        
        # Download entire model repository without loading into memory
        logger.info("Downloading model files (this may take 10-20 minutes)...")
        snapshot_download(
            repo_id=MODEL_NAME,
            cache_dir=CACHE_DIR,
            ignore_patterns=["*.msgpack", "*.h5"],  # Skip unnecessary formats
            resume_download=True
        )
        
        logger.info("Model downloaded successfully!")
        
        # Try to load tokenizer to verify download
        logger.info("Verifying download by loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            MODEL_NAME, 
            trust_remote_code=True,
            cache_dir=CACHE_DIR
        )
        logger.info(f"✅ Tokenizer loaded successfully! Vocab size: {len(tokenizer)}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to download model: {e}")
        return False

if __name__ == "__main__":
    success = download_model_simple()
    if success:
        print("✅ PhoGPT-4B model downloaded successfully!")
        print(f"📁 Location: {CACHE_DIR}")
        print("🚀 Ready to start AI service!")
    else:
        print("❌ Failed to download model")
        print("💡 Try running: pip install triton_pre_mlir")
        sys.exit(1)