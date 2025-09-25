#!/usr/bin/env python3
"""
Simple Whisper STT Service for Testing Accent Detection
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
from whisper_handler import WhisperModelManager
from accent_detector import VietnameseAccentDetector
from pronunciation_scorer import VietnamesePronunciationScorer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Global instances
whisper_manager = None
accent_detector = VietnameseAccentDetector()
pronunciation_scorer = VietnamesePronunciationScorer()

@app.route('/', methods=['GET'])
def home():
    """Service information"""
    return jsonify({
        "service": "Vietnamese Whisper STT Service",
        "version": "1.0.0",
        "status": "running",
        "endpoints": [
            "/health",
            "/transcribe",
            "/detect-accent",
            "/pronunciation",
            "/model/info"
        ]
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    global whisper_manager
    
    model_status = "loaded" if whisper_manager and whisper_manager.model else "not_loaded"
    
    return jsonify({
        "status": "healthy",
        "whisper_model": model_status,
        "accent_detector": "ready",
        "pronunciation_scorer": "ready"
    })

@app.route('/detect-accent', methods=['POST'])
def detect_accent():
    """Test accent detection with text input"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({"error": "Missing 'text' field"}), 400
        
        text = data['text']
        logger.info(f"Detecting accent for text: {text}")
        
        # Detect regional accent
        result = accent_detector.detect_region(text)
        
        logger.info(f"✅ Accent detection result: {result}")
        
        return jsonify({
            "success": True,
            "text": text,
            "accent_analysis": result
        })
        
    except Exception as e:
        logger.error(f"❌ Accent detection failed: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/model/info', methods=['GET'])
def model_info():
    """Get model information"""
    global whisper_manager
    
    if not whisper_manager:
        return jsonify({
            "whisper_model": "not_initialized",
            "accent_detector": "ready",
            "pronunciation_scorer": "ready"
        })
    
    return jsonify({
        "whisper_model": whisper_manager.get_model_info(),
        "accent_detector": "ready", 
        "pronunciation_scorer": "ready"
    })

def initialize_whisper():
    """Initialize Whisper model"""
    global whisper_manager
    try:
        logger.info("🔄 Initializing Whisper model...")
        whisper_manager = WhisperModelManager("base")
        
        # Load model
        if whisper_manager.load_model():
            logger.info("✅ Whisper model loaded successfully")
            return True
        else:
            logger.error("❌ Failed to load Whisper model")
            return False
            
    except Exception as e:
        logger.error(f"❌ Whisper initialization failed: {str(e)}")
        return False

if __name__ == '__main__':
    logger.info("🚀 Starting Vietnamese Whisper STT Service...")
    
    # Initialize Whisper model (optional for testing accent detection)
    initialize_whisper()
    
    # Start Flask server
    logger.info("🎤 Whisper STT Service running on http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=False)