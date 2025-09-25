#!/usr/bin/env python3
"""
Pronunciation Scorer for Vietnamese Language Learning
"""

import logging
import difflib
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class VietnamesePronunciationScorer:
    """Score Vietnamese pronunciation accuracy"""
    
    def __init__(self):
        # Vietnamese-specific pronunciation challenges
        self.difficult_sounds = {
            "ng": ["n", "g", ""],  # Common mistakes for 'ng'
            "nh": ["n", "ni", "ny"],  # 'nh' sound variations
            "tr": ["ch", "t", "r"],  # 'tr' vs 'ch' confusion
            "gi": ["z", "y", "d"],  # 'gi' sound variations
            "qu": ["k", "kw", "g"]   # 'qu' pronunciation
        }
        
        # Tone-related common mistakes
        self.tone_patterns = {
            "ngang": "no_tone",
            "huyền": "falling",
            "sắc": "rising", 
            "hỏi": "dipping",
            "ngã": "creaky",
            "nặng": "heavy"
        }
    
    def score_pronunciation(self, target_text: str, transcribed_text: str, 
                          context: Dict = None) -> Dict:
        """
        Score pronunciation based on target vs transcribed text
        
        Args:
            target_text: The text user was supposed to say
            transcribed_text: What Whisper heard
            context: Additional context (accent, difficulty level, etc.)
            
        Returns:
            Dict with score, feedback, and detailed analysis
        """
        try:
            if not target_text or not transcribed_text:
                return self._empty_result("Missing target or transcribed text")
            
            # Normalize texts
            target = self._normalize_text(target_text)
            transcribed = self._normalize_text(transcribed_text)
            
            # Calculate different types of accuracy
            word_accuracy = self._calculate_word_accuracy(target, transcribed)
            phonetic_accuracy = self._calculate_phonetic_accuracy(target, transcribed)
            length_penalty = self._calculate_length_penalty(target, transcribed)
            
            # Combined score (weighted)
            final_score = (
                word_accuracy * 0.5 +      # 50% word accuracy
                phonetic_accuracy * 0.3 +  # 30% phonetic similarity  
                length_penalty * 0.2       # 20% length appropriateness
            )
            
            # Cap between 0-100
            final_score = max(0, min(100, final_score))
            
            # Generate detailed feedback
            feedback = self._generate_detailed_feedback(
                final_score, target, transcribed, 
                word_accuracy, phonetic_accuracy
            )
            
            # Analyze specific errors
            error_analysis = self._analyze_pronunciation_errors(target, transcribed)
            
            result = {
                "overall_score": round(final_score, 1),
                "word_accuracy": round(word_accuracy, 1),
                "phonetic_accuracy": round(phonetic_accuracy, 1),
                "feedback": feedback,
                "error_analysis": error_analysis,
                "target_text": target_text,
                "transcribed_text": transcribed_text,
                "suggestions": self._get_improvement_suggestions(error_analysis)
            }
            
            logger.info(f"📊 Pronunciation score: {final_score:.1f}/100")
            return result
            
        except Exception as e:
            logger.error(f"❌ Pronunciation scoring error: {e}")
            return self._empty_result(f"Scoring failed: {str(e)}")
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison"""
        return text.lower().strip().replace(".", "").replace(",", "").replace("!", "").replace("?", "")
    
    def _calculate_word_accuracy(self, target: str, transcribed: str) -> float:
        """Calculate word-level accuracy"""
        target_words = target.split()
        transcribed_words = transcribed.split()
        
        if not target_words:
            return 0.0
        
        # Use sequence matching for better accuracy
        matcher = difflib.SequenceMatcher(None, target_words, transcribed_words)
        similarity = matcher.ratio()
        
        return similarity * 100
    
    def _calculate_phonetic_accuracy(self, target: str, transcribed: str) -> float:
        """Calculate phonetic similarity"""
        # Character-level similarity for phonetic approximation
        matcher = difflib.SequenceMatcher(None, target, transcribed)
        char_similarity = matcher.ratio()
        
        # Bonus for getting difficult Vietnamese sounds right
        bonus = self._calculate_vietnamese_sound_bonus(target, transcribed)
        
        return (char_similarity * 100) + bonus
    
    def _calculate_vietnamese_sound_bonus(self, target: str, transcribed: str) -> float:
        """Give bonus points for correctly pronouncing difficult Vietnamese sounds"""
        bonus = 0.0
        
        for sound, common_mistakes in self.difficult_sounds.items():
            if sound in target:
                if sound in transcribed:
                    bonus += 5.0  # Bonus for getting difficult sound right
                elif any(mistake in transcribed for mistake in common_mistakes):
                    bonus += 2.0  # Partial credit for close attempt
        
        return min(20.0, bonus)  # Cap bonus at 20 points
    
    def _calculate_length_penalty(self, target: str, transcribed: str) -> float:
        """Penalize for significant length differences"""
        target_len = len(target.split())
        transcribed_len = len(transcribed.split())
        
        if target_len == 0:
            return 0.0
        
        length_ratio = min(target_len, transcribed_len) / max(target_len, transcribed_len)
        return length_ratio * 100
    
    def _analyze_pronunciation_errors(self, target: str, transcribed: str) -> Dict:
        """Analyze specific pronunciation errors"""
        errors = {
            "missing_words": [],
            "extra_words": [],
            "substituted_words": [],
            "sound_confusions": []
        }
        
        target_words = target.split()
        transcribed_words = transcribed.split()
        
        # Find word-level differences
        matcher = difflib.SequenceMatcher(None, target_words, transcribed_words)
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'delete':
                errors["missing_words"].extend(target_words[i1:i2])
            elif tag == 'insert':
                errors["extra_words"].extend(transcribed_words[j1:j2])
            elif tag == 'replace':
                for k in range(min(i2-i1, j2-j1)):
                    errors["substituted_words"].append({
                        "target": target_words[i1+k],
                        "transcribed": transcribed_words[j1+k]
                    })
        
        # Analyze sound confusions
        errors["sound_confusions"] = self._find_sound_confusions(target, transcribed)
        
        return errors
    
    def _find_sound_confusions(self, target: str, transcribed: str) -> List[str]:
        """Find common Vietnamese sound confusions"""
        confusions = []
        
        common_confusions = [
            ("tr", "ch", "Confusion between 'tr' and 'ch' sounds"),
            ("gi", "z", "Confusion with 'gi' sound"),
            ("ng", "n", "Missing final 'ng' sound"),
            ("nh", "n", "Confusion between 'nh' and 'n'"),
            ("qu", "k", "Confusion with 'qu' sound")
        ]
        
        for sound1, sound2, description in common_confusions:
            if sound1 in target and sound2 in transcribed:
                confusions.append(description)
            elif sound2 in target and sound1 in transcribed:
                confusions.append(description)
        
        return confusions
    
    def _generate_detailed_feedback(self, score: float, target: str, 
                                  transcribed: str, word_acc: float, 
                                  phonetic_acc: float) -> str:
        """Generate detailed feedback message"""
        if score >= 95:
            return "🎉 Xuất sắc! Phát âm hoàn hảo, rõ ràng và chuẩn xác!"
        
        elif score >= 85:
            feedback = "👏 Rất tốt! Phát âm rõ ràng."
            if word_acc < 90:
                feedback += " Chú ý phát âm từng từ rõ hơn."
            return feedback
        
        elif score >= 75:
            feedback = "👍 Khá tốt! Có thể cải thiện: "
            issues = []
            if word_acc < 80:
                issues.append("độ chính xác từ vựng")
            if phonetic_acc < 80:
                issues.append("phát âm các âm thanh")
            feedback += ", ".join(issues) + "."
            return feedback
        
        elif score >= 60:
            return "📈 Đang tiến bộ! Hãy nói chậm hơn và rõ từng âm tiết. Thử luyện tập thêm với từng từ riêng lẻ."
        
        elif score >= 40:
            return "💪 Cố lên! Hãy nghe kỹ mẫu phát âm và luyện tập từng âm cơ bản. Nói chậm và rõ ràng."
        
        else:
            return "🎯 Bắt đầu lại! Hãy nghe mẫu phát âm nhiều lần, sau đó thử nói từng từ một cách chậm rãi."
    
    def _get_improvement_suggestions(self, error_analysis: Dict) -> List[str]:
        """Generate specific improvement suggestions"""
        suggestions = []
        
        if error_analysis["missing_words"]:
            suggestions.append(f"Hãy nhớ phát âm các từ: {', '.join(error_analysis['missing_words'])}")
        
        if error_analysis["sound_confusions"]:
            suggestions.append("Luyện tập phân biệt: " + ", ".join(error_analysis["sound_confusions"]))
        
        if len(error_analysis["substituted_words"]) > 0:
            suggestions.append("Chú ý phát âm chính xác các từ bị nhầm lẫn")
        
        # Default suggestions if no specific errors found
        if not suggestions:
            suggestions = [
                "Nói chậm và rõ từng âm tiết",
                "Chú ý thanh điệu của từng từ", 
                "Luyện tập với từng từ riêng lẻ trước"
            ]
        
        return suggestions[:3]  # Return top 3 suggestions
    
    def _empty_result(self, error_message: str) -> Dict:
        """Return empty result with error message"""
        return {
            "overall_score": 0.0,
            "word_accuracy": 0.0,
            "phonetic_accuracy": 0.0,
            "feedback": f"❌ {error_message}",
            "error_analysis": {},
            "target_text": "",
            "transcribed_text": "",
            "suggestions": ["Vui lòng thử lại với audio rõ hơn"]
        }