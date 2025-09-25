#!/usr/bin/env python3
"""
Accent Detector for Vietnamese Regional Variations
"""

import logging
import re

logger = logging.getLogger(__name__)

class VietnameseAccentDetector:
    """Detect Vietnamese regional accents from transcribed text"""
    
    def __init__(self):
        self.regional_indicators = {
            "north": {
                "vocabulary": [
                    "cơm trưa", "xe đạp", "áo phông", "nhà vệ sinh",
                    "hà nội", "miền bắc", "thủ đô"
                ],
                "phonetic_patterns": [
                    "tr", "ch", "gi", "r"  # Northern consonant patterns
                ],
                "expressions": [
                    "ừm", "ờm", "chắc chắn", "chuẩn luôn"
                ]
            },
            
            "central": {
                "vocabulary": [
                    "chào đỏ", "nghệ an", "huế", "quảng", "đà nẵng",
                    "miền trung", "cố đô"
                ],
                "phonetic_patterns": [
                    "tr", "s", "th"  # Central patterns
                ],
                "expressions": [
                    "chào đỏ", "cưng ơi", "mình ơi"
                ]
            },
            
            "south": {
                "vocabulary": [
                    "cơm chiều", "xe đạp", "áo thun", "toa lét",
                    "sài gòn", "miền nam", "tphcm", "thành phố"
                ],
                "phonetic_patterns": [
                    "ch", "j", "z"  # Southern patterns (ch -> j sound)
                ],
                "expressions": [
                    "dạ", "ơi", "nhé", "à", "ừa"
                ]
            }
        }
    
    def detect_region(self, text, context=None):
        """
        Detect Vietnamese regional accent from text
        
        Args:
            text (str): Transcribed Vietnamese text
            context (dict): Optional context info
            
        Returns:
            dict: Detection result with region, confidence, scores
        """
        try:
            text_lower = text.lower().strip()
            
            if not text_lower:
                return self._default_result()
            
            # Calculate scores for each region
            scores = {
                "north": self._calculate_north_score(text_lower),
                "central": self._calculate_central_score(text_lower),
                "south": self._calculate_south_score(text_lower)
            }
            
            # Find best match
            detected_region = max(scores, key=scores.get)
            confidence = scores[detected_region]
            
            # If confidence is too low, default to standard (north)
            if confidence < 0.3:
                detected_region = "north"
                confidence = 0.5
            
            result = {
                "region": detected_region,
                "confidence": round(confidence, 3),
                "scores": {k: round(v, 3) for k, v in scores.items()},
                "indicators": self._get_found_indicators(text_lower, detected_region),
                "text_analyzed": text[:100] + "..." if len(text) > 100 else text
            }
            
            logger.info(f"🎯 Accent detected: {detected_region} (conf: {confidence:.3f})")
            return result
            
        except Exception as e:
            logger.error(f"❌ Accent detection error: {e}")
            return self._default_result()
    
    def _calculate_north_score(self, text):
        """Calculate score for Northern accent"""
        score = 0.0
        indicators = self.regional_indicators["north"]
        
        # Check vocabulary
        for vocab in indicators["vocabulary"]:
            if vocab in text:
                score += 0.3
        
        # Check expressions
        for expr in indicators["expressions"]:
            if expr in text:
                score += 0.2
        
        # Default base score for standard Vietnamese
        score += 0.4
        
        return min(1.0, score)
    
    def _calculate_central_score(self, text):
        """Calculate score for Central accent"""
        score = 0.0
        indicators = self.regional_indicators["central"]
        
        # Strong indicators for Central
        if "chào đỏ" in text:
            score += 0.8
        if any(place in text for place in ["nghệ an", "huế", "đà nẵng", "quảng"]):
            score += 0.6
        
        # Check vocabulary
        for vocab in indicators["vocabulary"]:
            if vocab in text:
                score += 0.3
        
        # Check expressions
        for expr in indicators["expressions"]:
            if expr in text:
                score += 0.25
        
        return min(1.0, score)
    
    def _calculate_south_score(self, text):
        """Calculate score for Southern accent"""
        score = 0.0
        indicators = self.regional_indicators["south"]
        
        # Strong indicators for Southern
        if "cơm chiều" in text:
            score += 0.7
        if any(place in text for place in ["sài gòn", "tphcm", "miền nam"]):
            score += 0.6
        
        # Check vocabulary
        for vocab in indicators["vocabulary"]:
            if vocab in text:
                score += 0.3
        
        # Check expressions (Southern people use more "dạ", "ạ", "nhé")
        southern_particles = text.count("dạ") + text.count(" ạ") + text.count("nhé")
        if southern_particles > 0:
            score += min(0.4, southern_particles * 0.1)
        
        return min(1.0, score)
    
    def _get_found_indicators(self, text, region):
        """Get list of indicators found for detected region"""
        indicators = self.regional_indicators.get(region, {})
        found = []
        
        # Check vocabulary
        for vocab in indicators.get("vocabulary", []):
            if vocab in text:
                found.append(f"vocabulary: {vocab}")
        
        # Check expressions
        for expr in indicators.get("expressions", []):
            if expr in text:
                found.append(f"expression: {expr}")
        
        return found[:5]  # Return top 5 indicators
    
    def _default_result(self):
        """Return default result when detection fails"""
        return {
            "region": "north",
            "confidence": 0.5,
            "scores": {
                "north": 0.5,
                "central": 0.25,
                "south": 0.25
            },
            "indicators": ["default: standard Vietnamese"],
            "text_analyzed": ""
        }
    
    def get_region_info(self, region):
        """Get information about a specific region"""
        region_info = {
            "north": {
                "name": "Miền Bắc",
                "description": "Giọng chuẩn, rõ ràng, thanh điệu rõ nét",
                "characteristics": [
                    "Phát âm 'tr' và 'ch' phân biệt rõ",
                    "Thanh điệu đầy đủ 6 thanh",
                    "Từ vựng: cơm trưa, xe đạp, áo phông"
                ]
            },
            "central": {
                "name": "Miền Trung", 
                "description": "Giọng du dương, nhịp độ chậm",
                "characteristics": [
                    "Đặc trưng: 'chào đỏ' thay vì 'xin chào'",
                    "Nói chậm rãi, rõ từng âm",
                    "Có những từ độc đáo riêng vùng"
                ]
            },
            "south": {
                "name": "Miền Nam",
                "description": "Giọng mềm mại, thân thiện",
                "characteristics": [
                    "'ch' thành 'j', 'tr' thành 'ch'", 
                    "Nhiều trợ từ: dạ, ạ, nhé",
                    "Từ vựng: cơm chiều, áo thun"
                ]
            }
        }
        
        return region_info.get(region, {
            "name": "Unknown",
            "description": "Không xác định được vùng miền",
            "characteristics": []
        })