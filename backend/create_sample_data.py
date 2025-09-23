"""Create sample data for Vietnamese Tutor"""
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, User, Lesson, NativeLanguage, UserLevel

def create_sample_data():
    """Create sample lessons and users"""
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Create sample lessons
        lessons_data = [
            {
                "title": "Chào hỏi cơ bản",
                "level": UserLevel.beginner,
                "category": "greeting",
                "content": {
                    "phrases": ["Xin chào", "Chào bạn", "Hẹn gặp lại"],
                    "grammar": "Vietnamese greetings vary by relationship and time",
                    "cultural_notes": "Always greet older people first"
                }
            },
            {
                "title": "Đi chợ mua sắm", 
                "level": UserLevel.beginner,
                "category": "shopping",
                "content": {
                    "phrases": ["Bao nhiêu tiền?", "Đắt quá", "Giảm giá được không?"],
                    "grammar": "Question formation with 'bao nhiêu'",
                    "cultural_notes": "Bargaining is common in Vietnamese markets"
                }
            },
            {
                "title": "Giới thiệu bản thân",
                "level": UserLevel.intermediate, 
                "category": "introduction",
                "content": {
                    "phrases": ["Tôi tên là...", "Tôi đến từ...", "Tôi làm nghề..."],
                    "grammar": "Using 'tôi' and basic sentence structure",
                    "cultural_notes": "Include family information in introductions"
                }
            },
            {
                "title": "Văn hóa Việt Nam",
                "level": UserLevel.advanced,
                "category": "culture", 
                "content": {
                    "phrases": ["Tết Nguyên Đán", "Phong tục tập quán", "Lịch sử"],
                    "grammar": "Advanced vocabulary and expressions",
                    "cultural_notes": "Understanding Vietnamese festivals and traditions"
                }
            }
        ]
        
        # Check if lessons already exist
        existing_lessons = db.query(Lesson).count()
        if existing_lessons == 0:
            for lesson_data in lessons_data:
                lesson = Lesson(**lesson_data)
                db.add(lesson)
            
            db.commit()
            print(f"Created {len(lessons_data)} sample lessons")
        else:
            print(f"Found {existing_lessons} existing lessons, skipping creation")
            
    except Exception as e:
        print(f"Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()