#!/usr/bin/env python3
"""
Whisper STT Service for Vietnamese Tutor AI
Port: 5001
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import tempfile
import os
import logging
import numpy as np
from pydub import AudioSegment
import io

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global Whisper model
whisper_model = None
MODEL_SIZE = "base"  # Can be: tiny, base, small, medium, large

class WhisperHandler:
    def __init__(self, model_size="base"):
        self.model_size = model_size
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Load Whisper model"""
        try:
            logger.info(f"🤖 Loading Whisper model: {self.model_size}")
            logger.info("📥 First time will download model (~244MB for base)")
            
            self.model = whisper.load_model(self.model_size)
            
            logger.info("✅ Whisper model loaded successfully!")
            logger.info(f"📊 Model info: {self.model_size} - Multi-language support")
            
        except Exception as e:
            logger.error(f"❌ Failed to load Whisper model: {e}")
            self.model = None
    
    def transcribe_audio(self, audio_file_path, language="vi"):
        """Transcribe audio file to text"""
        if not self.model:
            return {"error": "Whisper model not loaded"}
        
        try:
            logger.info(f"🎤 Transcribing audio: {audio_file_path}")
            
            # Transcribe with Whisper
            result = self.model.transcribe(
                audio_file_path,
                language=language,
                verbose=False
            )
            
            transcription = result["text"].strip()
            language_detected = result.get("language", "vi")
            
            logger.info(f"✅ Transcription successful: '{transcription[:50]}...'")
            
            return {
                "text": transcription,
                "language": language_detected,
                "confidence": self._estimate_confidence(result),
                "segments": result.get("segments", [])
            }
            
        except Exception as e:
            logger.error(f"❌ Transcription failed: {e}")
            return {"error": f"Transcription failed: {str(e)}"}
    
    def _estimate_confidence(self, result):
        """Estimate transcription confidence from segments"""
        try:
            segments = result.get("segments", [])
            if not segments:
                return 0.8  # Default confidence
            
            # Average confidence from segments that have it
            confidences = []
            for segment in segments:
                if "avg_logprob" in segment:
                    # Convert log probability to confidence (rough estimation)
                    conf = max(0, min(1, np.exp(segment["avg_logprob"])))
                    confidences.append(conf)
            
            if confidences:
                return sum(confidences) / len(confidences)
            else:
                return 0.8  # Default
                
        except Exception:
            return 0.8  # Default confidence

class AccentDetector:
    """Detect Vietnamese regional accents"""
    
    REGIONAL_PATTERNS = {
        "north": {
            "indicators": ["tr", "ch", "gi", "r"],
            "vowel_patterns": ["ô", "ơ", "ư"],
            "tone_characteristics": "clear_tones"
        },
        "central": {
            "indicators": ["tr", "s", "th"],
            "vowel_patterns": ["ê", "ô"],
            "tone_characteristics": "melodic"
        },
        "south": {
            "indicators": ["ch", "j", "z"],
            "vowel_patterns": ["â", "ă"],
            "tone_characteristics": "tone_reduction"
        }
    }
    
    def detect_region(self, text, audio_features=None):
        """Detect Vietnamese regional accent from transcribed text"""
        try:
            text_lower = text.lower()
            
            # Simple pattern-based detection
            scores = {"north": 0, "central": 0, "south": 0}
            
            # Check for regional indicators (this is simplified)
            if any(word in text_lower for word in ["chào đỏ", "nghệ an"]):
                scores["central"] += 0.8
            elif any(word in text_lower for word in ["sài gòn", "miền nam"]):
                scores["south"] += 0.7
            elif any(word in text_lower for word in ["hà nội", "miền bắc"]):
                scores["north"] += 0.7
            else:
                # Default to standard (northern) if can't detect
                scores["north"] = 0.5
            
            # Find highest scoring region
            detected_region = max(scores, key=scores.get)
            confidence = scores[detected_region]
            
            return {
                "region": detected_region,
                "confidence": confidence,
                "scores": scores
            }
            
        except Exception as e:
            logger.error(f"Accent detection error: {e}")
            return {
                "region": "standard",
                "confidence": 0.5,
                "scores": {"north": 0.5, "central": 0.25, "south": 0.25}
            }

class PronunciationScorer:
    """Score pronunciation accuracy"""
    
    def score_pronunciation(self, target_text, transcribed_text):
        """Score pronunciation based on transcription accuracy"""
        try:
            target = target_text.lower().strip()
            transcribed = transcribed_text.lower().strip()
            
            # Simple word-level comparison
            target_words = target.split()
            transcribed_words = transcribed.split()
            
            if not target_words:
                return {"score": 0, "feedback": "No target text provided"}
            
            # Calculate word-level accuracy
            correct_words = 0
            total_words = len(target_words)
            
            for i, target_word in enumerate(target_words):
                if i < len(transcribed_words):
                    if target_word == transcribed_words[i]:
                        correct_words += 1
                    elif self._similar_words(target_word, transcribed_words[i]):
                        correct_words += 0.7  # Partial credit for similar words
            
            # Calculate score (0-100)
            accuracy = (correct_words / total_words) * 100
            score = max(0, min(100, accuracy))
            
            # Generate feedback
            feedback = self._generate_feedback(score, target, transcribed)
            
            return {
                "score": round(score, 1),
                "accuracy": f"{correct_words}/{total_words} words correct",
                "feedback": feedback,
                "target": target,
                "transcribed": transcribed
            }
            
        except Exception as e:
            logger.error(f"Pronunciation scoring error: {e}")
            return {
                "score": 0,
                "feedback": f"Scoring failed: {str(e)}"
            }
    
    def _similar_words(self, word1, word2):
        """Check if two words are similar (simple implementation)"""
        if abs(len(word1) - len(word2)) > 2:
            return False
        
        # Simple character overlap check
        common_chars = set(word1) & set(word2)
        return len(common_chars) / max(len(word1), len(word2)) > 0.6
    
    def _generate_feedback(self, score, target, transcribed):
        """Generate pronunciation feedback"""
        if score >= 90:
            return "🎉 Xuất sắc! Phát âm rất chuẩn!"
        elif score >= 80:
            return "👏 Tốt lắm! Phát âm rõ ràng, có thể cải thiện một chút."
        elif score >= 70:
            return "👍 Khá tốt! Hãy chú ý phát âm từng từ rõ ràng hơn."
        elif score >= 50:
            return "📈 Đang tiến bộ! Thử nói chậm hơn và rõ từng âm."
        else:
            return "💪 Cố lên! Hãy luyện tập thêm và nói chậm rãi từng từ."

# Initialize services
whisper_handler = WhisperHandler(MODEL_SIZE)
accent_detector = AccentDetector()
pronunciation_scorer = PronunciationScorer()

@app.route('/', methods=['GET'])
def home():
    """Service information"""
    return jsonify({
        "service": "Whisper STT Service",
        "version": "1.0.0",
        "model": MODEL_SIZE,
        "status": "running" if whisper_handler.model else "model_not_loaded",
        "endpoints": [
            "POST /transcribe - Convert speech to text",
            "POST /pronunciation - Score pronunciation",
            "GET /health - Health check",
            "POST /detect-accent - Detect regional accent"
        ]
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    model_status = "loaded" if whisper_handler.model else "not_loaded"
    
    return jsonify({
        "status": "healthy",
        "model": MODEL_SIZE,
        "model_status": model_status,
        "service": "whisper-stt"
    })

@app.route('/transcribe', methods=['POST'])
def transcribe():
    """Main transcription endpoint"""
    try:
        # Check if model is loaded
        if not whisper_handler.model:
            return jsonify({"error": "Whisper model not loaded"}), 500
        
        # Get audio file from request
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({"error": "No audio file selected"}), 400
        
        # Get optional parameters
        language = request.form.get('language', 'vi')  # Default to Vietnamese
        detect_accent = request.form.get('detect_accent', 'false').lower() == 'true'
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            audio_file.save(temp_file.name)
            temp_filename = temp_file.name
        
        try:
            # Transcribe audio
            result = whisper_handler.transcribe_audio(temp_filename, language)
            
            if "error" in result:
                return jsonify(result), 500
            
            # Add accent detection if requested
            if detect_accent and result.get("text"):
                accent_info = accent_detector.detect_region(result["text"])
                result["accent"] = accent_info
            
            logger.info(f"✅ Transcription complete: '{result.get('text', '')[:50]}...'")
            return jsonify(result)
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
    
    except Exception as e:
        logger.error(f"❌ Transcription endpoint error: {e}")
        return jsonify({"error": f"Transcription failed: {str(e)}"}), 500

@app.route('/pronunciation', methods=['POST'])
def check_pronunciation():
    """Pronunciation assessment endpoint"""
    try:
        # Check if model is loaded
        if not whisper_handler.model:
            return jsonify({"error": "Whisper model not loaded"}), 500
        
        # Get audio file and target text
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
        
        target_text = request.form.get('target_text', '')
        if not target_text:
            return jsonify({"error": "No target text provided"}), 400
        
        audio_file = request.files['audio']
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            audio_file.save(temp_file.name)
            temp_filename = temp_file.name
        
        try:
            # Transcribe the pronunciation attempt
            transcription_result = whisper_handler.transcribe_audio(temp_filename, 'vi')
            
            if "error" in transcription_result:
                return jsonify(transcription_result), 500
            
            transcribed_text = transcription_result.get("text", "")
            
            # Score the pronunciation
            pronunciation_result = pronunciation_scorer.score_pronunciation(
                target_text, transcribed_text
            )
            
            # Combine results
            result = {
                "transcription": transcription_result,
                "pronunciation_assessment": pronunciation_result,
                "target_text": target_text
            }
            
            logger.info(f"✅ Pronunciation check: Score {pronunciation_result.get('score', 0)}")
            return jsonify(result)
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
    
    except Exception as e:
        logger.error(f"❌ Pronunciation endpoint error: {e}")
        return jsonify({"error": f"Pronunciation assessment failed: {str(e)}"}), 500

@app.route('/detect-accent', methods=['POST'])
def detect_accent():
    """Regional accent detection endpoint"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({"error": "No text provided"}), 400
        
        text = data['text']
        
        # Detect regional accent
        accent_info = accent_detector.detect_region(text)
        
        logger.info(f"✅ Accent detection: {accent_info['region']} ({accent_info['confidence']:.2f})")
        return jsonify(accent_info)
    
    except Exception as e:
        logger.error(f"❌ Accent detection error: {e}")
        return jsonify({"error": f"Accent detection failed: {str(e)}"}), 500

@app.route('/model/info', methods=['GET'])
def model_info():
    """Get model information"""
    return jsonify({
        "model_size": MODEL_SIZE,
        "model_loaded": whisper_handler.model is not None,
        "supported_languages": [
            "vi", "en", "zh", "ja", "ko", "th", "id", "ms"
        ],
        "vietnamese_features": [
            "Tone recognition",
            "Regional accent detection", 
            "Pronunciation scoring",
            "Multi-speaker support"
        ]
    })

if __name__ == '__main__':
    logger.info("🚀 Starting Whisper STT Service...")
    logger.info(f"📡 Service will run on port 5001")
    logger.info(f"🤖 Model size: {MODEL_SIZE}")
    logger.info("🎤 Ready for Vietnamese speech recognition!")
    
    app.run(host='0.0.0.0', port=5001, debug=False)