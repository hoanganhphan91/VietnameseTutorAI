from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import requests
import os
import tempfile
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from database import engine, get_db
from models import Base, User, Conversation, LearningSession, Lesson
from schemas import (
    ChatMessage, ChatResponse, UserCreate, UserResponse, 
    ConversationResponse, LessonResponse, ProgressResponse,
    MessageType
)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Vietnamese Tutor API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models (moved to schemas.py)
# AI Service URLs
AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://ai:5000")
WHISPER_SERVICE_URL = os.getenv("WHISPER_SERVICE_URL", "http://localhost:5001")

@app.get("/")
async def root():
    return {"message": "Vietnamese Tutor API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(message: ChatMessage, db: Session = Depends(get_db)):
    """
    Chat endpoint that communicates with PhoGPT AI service
    """
    try:
        # Call AI service
        response = requests.post(
            f"{AI_SERVICE_URL}/chat",
            json={"message": message.message},
            timeout=30
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="AI service error")
        
        ai_response = response.json()
        
        # Process response and add educational features
        processed_response = process_educational_response(message.message, ai_response["response"])
        
        # Save conversation to database if user_id provided
        conversation_id = None
        if hasattr(message, 'user_id') and message.user_id:
            # Save user message
            user_conv = Conversation(
                user_id=message.user_id,
                message_type=MessageType.user,
                content=message.message
            )
            db.add(user_conv)
            
            # Save AI response
            ai_conv = Conversation(
                user_id=message.user_id,
                message_type=MessageType.ai,
                content=processed_response["response"],
                corrections=processed_response.get("corrections"),
                cultural_context=processed_response.get("cultural_context")
            )
            db.add(ai_conv)
            db.commit()
            conversation_id = ai_conv.id
        
        return ChatResponse(
            response=processed_response["response"],
            corrections=processed_response.get("corrections"),
            cultural_context=processed_response.get("cultural_context"),
            conversation_id=conversation_id
        )
        
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect to AI service: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

def process_educational_response(user_message: str, ai_response: str) -> dict:
    """
    Process AI response to add educational features
    """
    corrections = []
    cultural_context = None
    
    # Simple rule-based corrections (can be enhanced with ML later)
    common_errors = {
        "tôi đi chợ": "Rất tốt! 'Tôi đi chợ' là câu hoàn chỉnh.",
        "làm sao": "Bạn có thể nói 'Làm thế nào' thay vì 'làm sao' để lịch sự hơn.",
    }
    
    # Check for common errors
    for error, correction in common_errors.items():
        if error.lower() in user_message.lower():
            corrections.append(correction)
    
    # Add cultural context for specific topics
    if any(word in user_message.lower() for word in ["chợ", "market"]):
        cultural_context = "Ở Việt Nam, việc đi chợ là hoạt động hàng ngày rất phổ biến. Người Việt thường mua thực phẩm tươi sống mỗi ngày."
    
    elif any(word in user_message.lower() for word in ["chào", "hello"]):
        cultural_context = "Người Việt có nhiều cách chào hỏi khác nhau tùy theo độ tuổi và mối quan hệ. 'Xin chào' là cách chào phổ biến nhất."
    
    return {
        "response": ai_response,
        "corrections": corrections if corrections else None,
        "cultural_context": cultural_context
    }

@app.post("/api/voice-chat")
async def voice_chat(
    audio: UploadFile = File(...),
    language: str = Form("vi"),
    detect_accent: bool = Form(False),
    db: Session = Depends(get_db)
):
    """
    Voice chat endpoint - Speech to text, then AI response
    """
    try:
        # Save uploaded audio temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            content = await audio.read()
            temp_file.write(content)
            temp_filename = temp_file.name
        
        try:
            # Call Whisper STT service
            with open(temp_filename, 'rb') as audio_file:
                files = {'audio': audio_file}
                data = {
                    'language': language,
                    'detect_accent': str(detect_accent).lower()
                }
                
                stt_response = requests.post(
                    f"{WHISPER_SERVICE_URL}/transcribe",
                    files=files,
                    data=data,
                    timeout=30
                )
            
            if stt_response.status_code != 200:
                raise HTTPException(status_code=500, detail="Speech recognition failed")
            
            transcription = stt_response.json()
            transcribed_text = transcription.get("text", "")
            
            if not transcribed_text:
                raise HTTPException(status_code=400, detail="No speech detected")
            
            # Call AI service with transcribed text
            ai_response = requests.post(
                f"{AI_SERVICE_URL}/chat",
                json={"message": transcribed_text},
                timeout=30
            )
            
            if ai_response.status_code != 200:
                raise HTTPException(status_code=500, detail="AI service error")
            
            ai_result = ai_response.json()
            
            # Process response
            processed_response = process_educational_response(transcribed_text, ai_result["response"])
            
            return {
                "transcription": transcription,
                "ai_response": processed_response["response"],
                "corrections": processed_response.get("corrections"),
                "cultural_context": processed_response.get("cultural_context"),
                "accent_info": transcription.get("accent") if detect_accent else None
            }
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
    
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Service communication error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice chat error: {str(e)}")

@app.post("/api/pronunciation")
async def check_pronunciation(
    audio: UploadFile = File(...),
    target_text: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Pronunciation checking endpoint using Whisper service
    """
    try:
        # Save uploaded audio temporarily  
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            content = await audio.read()
            temp_file.write(content)
            temp_filename = temp_file.name
        
        try:
            # Call Whisper pronunciation service
            with open(temp_filename, 'rb') as audio_file:
                files = {'audio': audio_file}
                data = {'target_text': target_text}
                
                response = requests.post(
                    f"{WHISPER_SERVICE_URL}/pronunciation",
                    files=files,
                    data=data,
                    timeout=30
                )
            
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="Pronunciation check failed")
            
            result = response.json()
            
            # Extract pronunciation assessment
            assessment = result.get("pronunciation_assessment", {})
            
            return {
                "score": assessment.get("score", 0),
                "feedback": assessment.get("feedback", "No feedback available"),
                "accuracy": assessment.get("accuracy", "N/A"),
                "transcribed": result.get("transcription", {}).get("text", ""),
                "target": target_text,
                "suggestions": assessment.get("suggestions", []),
                "error_analysis": assessment.get("error_analysis", {})
            }
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
    
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Pronunciation service error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pronunciation check error: {str(e)}")

@app.post("/api/detect-accent")
async def detect_accent(text_data: dict, db: Session = Depends(get_db)):
    """
    Detect Vietnamese regional accent from text
    """
    try:
        text = text_data.get("text", "")
        if not text:
            raise HTTPException(status_code=400, detail="No text provided")
        
        response = requests.post(
            f"{WHISPER_SERVICE_URL}/detect-accent",
            json={"text": text},
            timeout=10
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Accent detection failed")
        
        return response.json()
    
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Accent detection service error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Accent detection error: {str(e)}")

@app.post("/api/pronunciation-simple")
async def check_pronunciation_simple(audio_data: dict):
    """
    Simple pronunciation checking endpoint (legacy)
    """
    return {"score": 85, "feedback": "Phát âm tốt! Có thể cải thiện âm 'ng' cuối từ."}

@app.get("/api/lessons", response_model=List[LessonResponse])
async def get_lessons(db: Session = Depends(get_db)):
    """
    Get available lessons from database
    """
    lessons = db.query(Lesson).all()
    return lessons

@app.get("/api/progress/{user_id}", response_model=ProgressResponse)
async def get_progress(user_id: int, db: Session = Depends(get_db)):
    """
    Get user learning progress from database
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Calculate progress metrics
    total_lessons = db.query(Lesson).count()
    conversations = db.query(Conversation).filter(
        Conversation.user_id == user_id,
        Conversation.message_type == MessageType.user
    ).count()
    
    return ProgressResponse(
        user_id=user_id,
        level=user.current_level,
        lessons_completed=conversations // 10,  # Example calculation
        total_lessons=total_lessons,
        conversation_score=min(conversations * 2.5, 100),  # Example scoring
        pronunciation_score=78  # Placeholder
    )

@app.post("/api/users", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create new user
    """
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/api/users/{user_id}/conversations", response_model=List[ConversationResponse])
async def get_user_conversations(user_id: int, db: Session = Depends(get_db)):
    """
    Get user conversation history
    """
    conversations = db.query(Conversation).filter(
        Conversation.user_id == user_id
    ).order_by(Conversation.created_at.desc()).limit(50).all()
    return conversations

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)