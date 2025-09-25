# 🎤 Whisper STT Service

Vietnamese Speech-to-Text service using OpenAI Whisper, specifically optimized for Vietnamese language learning.

## 🌟 Features

- **Multi-language STT** with excellent Vietnamese support
- **Regional accent detection** (North, Central, South Vietnam)  
- **Pronunciation scoring** for language learning
- **Real-time transcription** with confidence scoring
- **Educational feedback** for pronunciation improvement

## 🚀 Quick Start

### 1. Setup Service
```bash
# Install dependencies and setup
./setup.sh

# Start the service  
./start.sh
```

### 2. Test Service
```bash
# Test all endpoints
python test_service.py
```

The service will be available at `http://localhost:5001`

## 📡 API Endpoints

### Health Check
```bash
GET /health
```

### Speech-to-Text
```bash
POST /transcribe
Content-Type: multipart/form-data

Parameters:
- audio: Audio file (wav, mp3, mp4, m4a, webm)
- language: Language code (default: 'vi')
- detect_accent: Boolean (default: false)
```

**Example:**
```bash
curl -X POST http://localhost:5001/transcribe \
  -F "audio=@vietnamese_audio.wav" \
  -F "language=vi" \
  -F "detect_accent=true"
```

**Response:**
```json
{
  "text": "Xin chào, tôi tên là Nam",
  "language": "vi", 
  "confidence": 0.95,
  "segments": [...],
  "accent": {
    "region": "south",
    "confidence": 0.87,
    "indicators": ["vocabulary: sài gòn"]
  }
}
```

### Pronunciation Assessment  
```bash
POST /pronunciation
Content-Type: multipart/form-data

Parameters:
- audio: Audio file 
- target_text: Text user was supposed to say
```

**Example:**
```bash
curl -X POST http://localhost:5001/pronunciation \
  -F "audio=@pronunciation_attempt.wav" \
  -F "target_text=Xin chào"
```

**Response:**
```json
{
  "transcription": {
    "text": "Xin chào",
    "confidence": 0.92
  },
  "pronunciation_assessment": {
    "overall_score": 89.5,
    "word_accuracy": 95.0,
    "phonetic_accuracy": 87.3,
    "feedback": "👏 Rất tốt! Phát âm rõ ràng.",
    "suggestions": [
      "Nói chậm và rõ từng âm tiết",
      "Chú ý thanh điệu của từng từ"
    ]
  }
}
```

### Accent Detection
```bash
POST /detect-accent
Content-Type: application/json

{
  "text": "Chào đỏ, tôi là người Nghệ An"
}
```

**Response:**
```json
{
  "region": "central",
  "confidence": 0.92,
  "scores": {
    "north": 0.15,
    "central": 0.92, 
    "south": 0.23
  },
  "indicators": [
    "expression: chào đỏ",
    "vocabulary: nghệ an"
  ]
}
```

## 🏗️ Architecture

```
whisper_service/
├── app.py                    # Main Flask application
├── whisper_handler.py        # Whisper model management
├── accent_detector.py        # Vietnamese accent detection
├── pronunciation_scorer.py   # Pronunciation assessment
├── requirements.txt          # Python dependencies
├── setup.sh                 # Setup script
├── start.sh                 # Start script
├── test_service.py          # Test script
├── Dockerfile               # Docker container
└── .env.example             # Environment configuration
```

## 🎯 Vietnamese Language Features

### Regional Accent Detection
- **Northern (Miền Bắc)**: Standard pronunciation, clear tones
- **Central (Miền Trung)**: Distinctive patterns like "chào đỏ"
- **Southern (Miền Nam)**: Softer tones, different vocabulary

### Pronunciation Scoring
- **Word-level accuracy**: Exact word matching
- **Phonetic similarity**: Character-level comparison  
- **Vietnamese sound bonus**: Extra points for difficult sounds
- **Educational feedback**: Specific improvement suggestions

### Common Vietnamese Challenges
- **tr vs ch** sound confusion
- **gi sound** variations  
- **ng final** consonant pronunciation
- **Tone accuracy** across 6 tones

## ⚙️ Configuration

Edit `.env` file for customization:

```bash
# Model size (tiny, base, small, medium, large)
WHISPER_MODEL_SIZE=base

# Service configuration
WHISPER_PORT=5001
WHISPER_HOST=0.0.0.0

# Vietnamese features
DEFAULT_LANGUAGE=vi
SUPPORT_ACCENT_DETECTION=true
SUPPORT_PRONUNCIATION_SCORING=true
```

## 🔧 Integration

### With Backend Service
The backend automatically integrates with Whisper:

```python
# Voice chat endpoint
POST /api/voice-chat
- Uploads audio to Whisper
- Gets transcription  
- Sends to PhoGPT for response

# Pronunciation check
POST /api/pronunciation  
- Compares user audio with target text
- Returns detailed assessment
```

### With Frontend  
Frontend can record audio and send to backend:

```javascript
// Record audio
const mediaRecorder = new MediaRecorder(stream);

// Send to backend
const formData = new FormData();
formData.append('audio', audioBlob);
formData.append('target_text', 'Xin chào');

fetch('/api/pronunciation', {
  method: 'POST',
  body: formData
});
```

## 📊 Performance

| Model | Size | Speed | Accuracy | Recommendation |
|-------|------|-------|----------|----------------|
| tiny | 39MB | Fastest | Good | Development testing |
| base | 74MB | Fast | Very good | **Recommended** |
| small | 244MB | Medium | Excellent | High accuracy needs |
| medium | 769MB | Slow | Outstanding | Production quality |
| large | 1550MB | Slowest | Perfect | Maximum accuracy |

## 🐛 Troubleshooting

### Common Issues

**1. Model download fails:**
```bash
# Check internet connection
# Retry setup
./setup.sh
```

**2. Audio format not supported:**
```bash
# Convert audio to WAV
ffmpeg -i input.mp3 output.wav
```

**3. Low pronunciation scores:**
```bash
# Check audio quality
# Ensure clear pronunciation
# Verify target text accuracy
```

**4. Service won't start:**
```bash
# Check port availability
lsof -i:5001

# Check logs
tail -f whisper.log
```

### Memory Issues
If running out of memory with larger models:
```bash
# Use smaller model
export WHISPER_MODEL_SIZE=tiny

# Or increase system RAM
# Or use model on GPU if available
```

## 🧪 Testing

```bash
# Test all endpoints
python test_service.py

# Manual testing
curl http://localhost:5001/health

# Test with actual audio file
curl -X POST http://localhost:5001/transcribe \
  -F "audio=@test_vietnamese.wav"
```

## 🚀 Production Deployment

### Docker
```bash
# Build image
docker build -t whisper-service .

# Run container
docker run -p 5001:5001 whisper-service
```

### Performance Optimization
```bash
# Use GPU if available
export TORCH_DEVICE=cuda

# Optimize CPU threads
export TORCH_THREADS=4

# Use smaller model for speed
export WHISPER_MODEL_SIZE=base
```

## 🤝 Integration with PhoGPT

Perfect combination for Vietnamese learning:

1. **User speaks** → Whisper transcribes
2. **Transcription** → PhoGPT understands and responds  
3. **PhoGPT response** → Text-to-Speech → User hears
4. **Pronunciation practice** → Whisper scores accuracy

This creates a complete **voice-enabled Vietnamese learning experience**! 🗣️🇻🇳