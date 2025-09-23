from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserLevel(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"

class NativeLanguage(str, Enum):
    english = "english"
    korean = "korean"
    japanese = "japanese"
    chinese = "chinese"
    other = "other"

class MessageType(str, Enum):
    user = "user"
    ai = "ai"

# Request schemas
class UserCreate(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    native_language: NativeLanguage
    current_level: UserLevel = UserLevel.beginner

class ChatMessage(BaseModel):
    message: str
    user_id: Optional[int] = None

class ConversationCreate(BaseModel):
    user_id: int
    message_type: MessageType
    content: str
    audio_url: Optional[str] = None
    corrections: Optional[List[str]] = None
    cultural_context: Optional[str] = None

# Response schemas
class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    native_language: NativeLanguage
    current_level: UserLevel
    created_at: datetime
    
    class Config:
        from_attributes = True

class ChatResponse(BaseModel):
    response: str
    corrections: Optional[List[str]] = None
    cultural_context: Optional[str] = None
    conversation_id: Optional[int] = None

class ConversationResponse(BaseModel):
    id: int
    message_type: MessageType
    content: str
    corrections: Optional[List[str]]
    cultural_context: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class LessonResponse(BaseModel):
    id: int
    title: str
    level: UserLevel
    category: str
    
    class Config:
        from_attributes = True

class ProgressResponse(BaseModel):
    user_id: int
    level: UserLevel
    lessons_completed: int
    total_lessons: int
    conversation_score: float
    pronunciation_score: float
    
    class Config:
        from_attributes = True