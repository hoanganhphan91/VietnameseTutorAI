"""SQLAlchemy models for Vietnamese Tutor"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum
from datetime import datetime

class UserLevel(enum.Enum):
    """User proficiency levels"""
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"

class NativeLanguage(enum.Enum):
    """Supported native languages"""
    english = "english"
    japanese = "japanese"
    korean = "korean"
    chinese = "chinese"
    french = "french"
    spanish = "spanish"

class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    native_language = Column(Enum(NativeLanguage), nullable=False)
    current_level = Column(Enum(UserLevel), default=UserLevel.beginner)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    progress = relationship("UserProgress", back_populates="user")
    conversations = relationship("Conversation", back_populates="user")

class Lesson(Base):
    """Lesson model"""
    __tablename__ = "lessons"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    level = Column(Enum(UserLevel), nullable=False)
    category = Column(String(50), nullable=False)
    content = Column(JSON, nullable=False)  # Store lesson content as JSON
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    progress = relationship("UserProgress", back_populates="lesson")

class UserProgress(Base):
    """User progress tracking"""
    __tablename__ = "user_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    completed_at = Column(DateTime(timezone=True), server_default=func.now())
    score = Column(Integer, default=0)  # 0-100
    notes = Column(Text)
    
    # Relationships
    user = relationship("User", back_populates="progress")
    lesson = relationship("Lesson", back_populates="progress")

class Conversation(Base):
    """AI conversation history"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String(100), nullable=False)  # To group related messages
    message_type = Column(String(20), nullable=False)  # 'user' or 'ai'
    content = Column(Text, nullable=False)
    context = Column(JSON)  # Additional context like lesson reference, corrections
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="conversations")

class Vocabulary(Base):
    """Vocabulary words and phrases"""
    __tablename__ = "vocabulary"
    
    id = Column(Integer, primary_key=True, index=True)
    vietnamese_word = Column(String(100), nullable=False)
    pronunciation = Column(String(200))  # Phonetic pronunciation
    meaning = Column(JSON, nullable=False)  # Meanings in different languages
    level = Column(Enum(UserLevel), nullable=False)
    category = Column(String(50))  # Topic category
    example_sentence = Column(Text)
    audio_url = Column(String(500))  # URL to audio pronunciation
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class LearningSession(Base):
    """Learning session tracking"""
    __tablename__ = "learning_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_type = Column(String(50), nullable=False)  # 'conversation', 'lesson', 'practice'
    duration_minutes = Column(Integer)
    score = Column(Integer)  # 0-100
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="sessions")

# Update User model to include sessions relationship
User.sessions = relationship("LearningSession", back_populates="user")