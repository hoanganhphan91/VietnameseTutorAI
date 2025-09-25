#!/usr/bin/env python3
"""
Simple Accent Detection Test - không cần Whisper model
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from accent_detector import VietnameseAccentDetector
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize accent detector
accent_detector = VietnameseAccentDetector()

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Vietnamese Accent Detection Service is running",
        "version": "1.0.0"
    })

@app.route('/detect-accent', methods=['POST'])
def detect_accent_text():
    """
    Detect Vietnamese accent from text
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                "success": False,
                "error": "Missing 'text' field in request"
            }), 400
        
        text = data['text']
        logger.info(f"🔍 Detecting accent for text: '{text}'")
        
        # Detect accent
        result = accent_detector.detect_region(text)
        
        logger.info(f"✅ Accent detection result: {result}")
        
        return jsonify({
            "success": True,
            "text": text,
            "accent_result": result
        })
        
    except Exception as e:
        logger.error(f"❌ Error in accent detection: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/test-samples', methods=['GET'])
def test_samples():
    """Test with sample texts from different regions"""
    samples = [
        {
            "text": "Tôi đi chợ mua rau cải",
            "expected_region": "north",
            "description": "Northern vocabulary: 'rau cải'"
        },
        {
            "text": "Mình đi chợ mua rau muống", 
            "expected_region": "south",
            "description": "Southern pronoun: 'mình' and vocabulary"
        },
        {
            "text": "Tao đi chợ mua đồ ăn",
            "expected_region": "north", 
            "description": "Northern casual pronoun: 'tao'"
        },
        {
            "text": "Tui đi chợ mua cơm",
            "expected_region": "south",
            "description": "Southern casual pronoun: 'tui'"
        }
    ]
    
    results = []
    for sample in samples:
        detection_result = accent_detector.detect_region(sample['text'])
        results.append({
            "text": sample['text'],
            "expected": sample['expected_region'], 
            "detected": detection_result['region'],
            "confidence": detection_result['confidence'],
            "match": detection_result['region'] == sample['expected_region'],
            "description": sample['description']
        })
    
    return jsonify({
        "success": True,
        "test_results": results,
        "total_tests": len(results),
        "passed": sum(1 for r in results if r['match'])
    })

if __name__ == '__main__':
    logger.info("🎤 Starting Vietnamese Accent Detection Service...")
    logger.info("🔧 Service will run on http://localhost:5001")
    logger.info("🧪 Test endpoint: http://localhost:5001/test-samples")
    
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True
    )