-- Initialize Vietnamese Tutor Database
CREATE DATABASE IF NOT EXISTS vietnamese_tutor;
USE vietnamese_tutor;

-- Users table
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    full_name VARCHAR(255),
    native_language ENUM('english', 'korean', 'japanese', 'chinese', 'other') NOT NULL,
    current_level ENUM('beginner', 'intermediate', 'advanced') DEFAULT 'beginner',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_level (current_level)
);

-- Learning sessions
CREATE TABLE learning_sessions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    session_type ENUM('conversation', 'pronunciation', 'grammar', 'culture') NOT NULL,
    content TEXT,
    ai_response TEXT,
    corrections JSON,
    cultural_context TEXT,
    score DECIMAL(5,2),
    duration_seconds INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_sessions (user_id, created_at),
    INDEX idx_session_type (session_type)
);

-- Conversation history
CREATE TABLE conversations (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    session_id BIGINT,
    message_type ENUM('user', 'ai') NOT NULL,
    content TEXT NOT NULL,
    audio_url VARCHAR(500),
    corrections JSON,
    pronunciation_score DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES learning_sessions(id) ON DELETE SET NULL,
    INDEX idx_user_conversations (user_id, created_at),
    INDEX idx_session_conversations (session_id)
);

-- Lessons content
CREATE TABLE lessons (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    level ENUM('beginner', 'intermediate', 'advanced') NOT NULL,
    category ENUM('greeting', 'shopping', 'work', 'culture', 'grammar', 'pronunciation') NOT NULL,
    content JSON,
    objectives JSON,
    vocabulary JSON,
    example_conversations JSON,
    cultural_notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_level_category (level, category),
    INDEX idx_active (is_active)
);

-- User progress tracking
CREATE TABLE user_progress (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    lesson_id BIGINT NOT NULL,
    status ENUM('not_started', 'in_progress', 'completed') DEFAULT 'not_started',
    completion_percentage DECIMAL(5,2) DEFAULT 0.00,
    best_score DECIMAL(5,2),
    time_spent_seconds INT DEFAULT 0,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_lesson (user_id, lesson_id),
    INDEX idx_user_progress (user_id, status)
);

-- Common errors tracking
CREATE TABLE error_patterns (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_native_language VARCHAR(50) NOT NULL,
    error_type ENUM('pronunciation', 'grammar', 'vocabulary', 'tone') NOT NULL,
    incorrect_text VARCHAR(500),
    correct_text VARCHAR(500),
    explanation TEXT,
    frequency_count INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_language_error (user_native_language, error_type),
    INDEX idx_frequency (frequency_count DESC)
);

-- Cultural context database
CREATE TABLE cultural_contexts (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    keyword VARCHAR(255) NOT NULL,
    context_type ENUM('social', 'business', 'daily_life', 'tradition', 'food') NOT NULL,
    explanation TEXT NOT NULL,
    examples JSON,
    do_and_donts JSON,
    language_notes TEXT,
    region_specific ENUM('north', 'central', 'south', 'general') DEFAULT 'general',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_keyword (keyword),
    INDEX idx_context_type (context_type),
    INDEX idx_region (region_specific)
);

-- Pronunciation feedback
CREATE TABLE pronunciation_feedback (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    text_content VARCHAR(1000) NOT NULL,
    audio_url VARCHAR(500),
    phonetic_transcription TEXT,
    score DECIMAL(5,2),
    detailed_feedback JSON,
    problem_sounds JSON,
    improvement_tips TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_pronunciation (user_id, created_at),
    INDEX idx_score_range (score)
);

-- Insert sample data
INSERT INTO lessons (title, description, level, category, content, objectives, vocabulary, cultural_notes) VALUES 
('Chào hỏi cơ bản', 'Học cách chào hỏi trong các tình huống khác nhau', 'beginner', 'greeting', 
 '{"phrases": ["Xin chào", "Chào bạn", "Hẹn gặp lại"], "formal": ["Kính chào"], "informal": ["Chào"]}',
 '["Biết cách chào hỏi phù hợp", "Phân biệt formal/informal", "Hiểu văn hóa chào hỏi"]',
 '{"greetings": {"xin_chao": {"meaning": "Hello", "usage": "formal and informal"}}}',
 'Người Việt Nam rất coi trọng việc chào hỏi. Người trẻ tuổi thường chào người lớn tuổi trước.'),

('Đi chợ mua sắm', 'Học từ vựng và cách giao tiếp khi mua sắm', 'beginner', 'shopping',
 '{"phrases": ["Cái này bao nhiêu tiền?", "Cho tôi xem", "Tôi muốn mua"], "numbers": ["một", "hai", "ba"]}',
 '["Biết hỏi giá", "Mặc cả cơ bản", "Từ vựng thực phẩm"]',
 '{"shopping": {"gia_ca": {"meaning": "price", "phrase": "bao nhiêu tiền"}}}',
 'Ở Việt Nam, việc mặc cả là điều bình thường ở chợ truyền thống nhưng không nên mặc cả ở siêu thị.'),

('Giới thiệu bản thân', 'Học cách tự giới thiệu một cách tự nhiên', 'intermediate', 'work',
 '{"phrases": ["Tôi tên là...", "Tôi đến từ...", "Tôi làm việc tại..."]}',
 '["Giới thiệu tên tuổi", "Nói về quê quán", "Nói về công việc"]',
 '{"introduction": {"ten": {"meaning": "name"}, "que_quan": {"meaning": "hometown"}}}',
 'Khi giới thiệu, người Việt thường khiêm tốn và không quá nhấn mạnh thành tích cá nhân.');

INSERT INTO cultural_contexts (keyword, context_type, explanation, examples, do_and_donts, region_specific) VALUES
('chào hỏi', 'social', 'Văn hóa chào hỏi của người Việt rất đa dạng tùy theo độ tuổi và mối quan hệ',
 '["Chào anh/chị", "Chào bác", "Chào em"]',
 '{"do": ["Chào người lớn tuổi trước", "Dùng xưng hô phù hợp"], "dont": ["Không chào bằng tên với người lớn tuổi"]}',
 'general'),

('ăn cơm', 'daily_life', 'Bữa cơm là trung tâm của văn hóa gia đình Việt',
 '["Mời bác dùng cơm", "Cơm nước đầy đủ"]',
 '{"do": ["Chờ người lớn ăn trước", "Không để đũa thẳng đứng trong bát"], "dont": ["Không rời bàn khi chưa xin phép"]}',
 'general');

INSERT INTO error_patterns (user_native_language, error_type, incorrect_text, correct_text, explanation, frequency_count) VALUES
('english', 'pronunciation', 'tôi đi chợ', 'tôi đi chợ (with proper tone)', 'English speakers often miss Vietnamese tones', 15),
('english', 'grammar', 'tôi có hai con mèo', 'tôi có hai con mèo', 'Classifier usage is correct here', 8),
('korean', 'pronunciation', 'xin chào', 'xin chào (proper x sound)', 'Korean speakers may pronounce x as s', 12),
('japanese', 'tone', 'cơm', 'cơm (mid-level tone)', 'Japanese speakers may add pitch accent', 10);

-- Create admin user (password should be hashed in real application)
INSERT INTO users (email, password_hash, full_name, native_language, current_level) VALUES
('admin@vietnamesetutor.com', 'hashed_password_here', 'Admin User', 'english', 'advanced'),
('demo@vietnamesetutor.com', 'demo_password_hash', 'Demo User', 'english', 'beginner');