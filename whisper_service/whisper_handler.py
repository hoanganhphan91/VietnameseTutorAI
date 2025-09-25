#!/usr/bin/env python3
"""
Whisper STT Model Handler
Manages Whisper model loading and transcription using faster-whisper
"""

import os
import logging
from typing import Dict, Optional, Union
from faster_whisper import WhisperModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WhisperModelManager:
    """Manages Whisper model loading and transcription using faster-whisper"""
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize Whisper model manager
        
        Args:
            model_size: Model size (tiny, base, small, medium, large)
        """
        self.model_size = model_size
        self.model: Optional[WhisperModel] = None
        self.supported_models = ["tiny", "base", "small", "medium", "large"]
        
    def load_model(self) -> bool:
        """
        Load the Whisper model
        
        Returns:
            bool: True if model loaded successfully
        """
        try:
            if self.model_size not in self.supported_models:
                logger.warning(f"Model {self.model_size} not in supported models, using 'base'")
                self.model_size = "base"
            
            logger.info(f"Loading Whisper model: {self.model_size}")
            
            # Use CPU for compatibility
            self.model = WhisperModel(
                self.model_size, 
                device="cpu",
                compute_type="int8"
            )
            
            logger.info(f"✅ Whisper model '{self.model_size}' loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load Whisper model: {str(e)}")
            self.model = None
            return False
    
    def transcribe_file(self, audio_file_path: str, language: str = "vi") -> Dict[str, Union[str, float, bool]]:
        """
        Transcribe audio file to text
        """
        if not self.model:
            return {
                "success": False,
                "text": "",
                "confidence": 0.0,
                "error": "Model not loaded"
            }
        
        if not os.path.exists(audio_file_path):
            return {
                "success": False,
                "text": "",
                "confidence": 0.0,
                "error": "Audio file not found"
            }
        
        try:
            logger.info(f"Transcribing file: {audio_file_path}")
            
            # Transcribe the audio file
            segments, info = self.model.transcribe(
                audio_file_path,
                language=language,
                beam_size=5,
                temperature=0.0
            )
            
            # Combine all segments
            transcription_text = ""
            total_confidence = 0.0
            segment_count = 0
            
            for segment in segments:
                transcription_text += segment.text + " "
                # Use avg_logprob if available
                if hasattr(segment, 'avg_logprob'):
                    total_confidence += segment.avg_logprob
                else:
                    total_confidence += -0.5  # Default
                segment_count += 1
            
            # Calculate average confidence
            if segment_count > 0:
                avg_logprob = total_confidence / segment_count
                confidence = max(0.0, min(1.0, 1.0 + avg_logprob))  # Map [-1,0] to [0,1]
            else:
                confidence = 0.5
            
            transcription_text = transcription_text.strip()
            
            logger.info(f"✅ Transcription completed. Length: {len(transcription_text)}")
            
            return {
                "success": True,
                "text": transcription_text,
                "confidence": confidence,
                "language": info.language if hasattr(info, 'language') else 'vi',
                "error": None
            }
            
        except Exception as e:
            logger.error(f"❌ Transcription failed: {str(e)}")
            return {
                "success": False,
                "text": "",
                "confidence": 0.0,
                "error": str(e)
            }
    
    def get_model_info(self) -> Dict[str, Union[str, bool, list]]:
        """Get information about the loaded model"""
        return {
            "model_size": self.model_size,
            "model_loaded": self.model is not None,
            "supported_models": self.supported_models,
            "backend": "faster-whisper"
        }
    
    def cleanup(self):
        """Cleanup resources"""
        if self.model:
            logger.info("Cleaning up Whisper model resources")
            self.model = None