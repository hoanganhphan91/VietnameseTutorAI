# 🇻🇳 AI Vietnamese Tutor for Foreigners

A comprehensive AI-powered Vietnamese language learning platform designed specifically for foreign learners. This application provides interactive conversation practice, pronunciation feedback, and cultural context explanations using the **PhoGPT-4B Vietnamese language model**.

## ✨ Features

- **🤖 Interactive Chat Interface**: Real-time conversation practice with AI tutor
- **🇻🇳 Vietnamese Language Model**: Powered by PhoGPT-4B-Chat for authentic Vietnamese responses  
- **📊 Progress Tracking**: Monitor learning progress and conversation history
- **🏮 Cultural Context**: Learn Vietnamese culture alongside language
- **📱 Responsive Design**: Works on desktop and mobile devices
- **⚡ Real-time Learning**: Instant feedback and corrections

## 🛠️ Tech Stack

- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS
- **Backend**: FastAPI + Python 3.11 + SQLAlchemy
- **Database**: MySQL (production) / SQLite (development)
- **AI Model**: PhoGPT-4B-Chat (Vietnamese language model)
- **Caching**: Redis
- **Deployment**: Docker Compose

## 🚀 Quick Start

### Option 1: Local Development (Recommended)

1. **Test the setup**:
   ```bash
   test-setup.bat
   ```

2. **Start all services**:
   ```bash
   start-services.bat
   ```

3. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/docs
   - AI Service: http://localhost:5000

4. **Check service status**:
   ```bash
   check-status.bat
   ```

### Option 2: Docker (Full Production)

```bash
# Start all services with Docker
docker-compose up -d

# Stop services
docker-compose down
```

## 📁 Project Structure

```
vietnamese-tutor-ai/
├── frontend/          # Next.js 14 + TypeScript
│   ├── src/app/       # App router pages
│   ├── package.json   # Frontend dependencies
│   └── tailwind.config.js
├── backend/           # FastAPI + SQLAlchemy
│   ├── main.py        # FastAPI application
│   ├── database.py    # Database models
│   ├── schemas.py     # Pydantic models
│   └── requirements.txt
├── ai/                # PhoGPT-4B service
│   ├── app.py         # Flask AI service
│   └── requirements.txt
├── database/          # Database initialization
│   └── init.sql       # MySQL schema
├── docker-compose.yml # Production deployment
├── start-services.bat # Local development
└── test-setup.bat     # Verification script
```

## 🔧 Development Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git

### Local Environment Setup

The project includes automated setup scripts for Windows:

1. **`test-setup.bat`**: Verifies all dependencies and builds
2. **`start-services.bat`**: Launches all services in separate windows
3. **`check-status.bat`**: Monitors service health

### Manual Setup (if needed)

```bash
# Backend setup
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py

# AI service setup
cd ai
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py

# Frontend setup
cd frontend
npm install
npm run dev
```

## 🎯 API Endpoints

### Backend (FastAPI) - Port 8000
- `GET /docs` - API documentation
- `POST /api/chat` - Send message to AI tutor
- `GET /api/conversations` - Get conversation history
- `POST /api/users` - Create user account
- `GET /api/progress/{user_id}` - Get learning progress

### AI Service (Flask) - Port 5000
- `POST /chat` - Process Vietnamese conversation
- `GET /health` - Service health check

## 🌐 Deployment

### Local Development
Perfect for development and testing:
```bash
start-services.bat
```

### Production (Docker)
For scalable production deployment:
```bash
docker-compose up -d
```

## 📊 Database Schema

The application uses SQLAlchemy with the following models:
- **User**: Student profiles and preferences
- **Conversation**: Chat history and context
- **Lesson**: Structured learning content
- **ProgressTracking**: Learning metrics and achievements

## 🤖 AI Model Details

**PhoGPT-4B-Chat** by VinAI Research:
- 4 billion parameters trained on Vietnamese text
- Specialized for Vietnamese conversation and cultural context
- Optimized for educational interactions
- Supports both formal and colloquial Vietnamese

## 🎨 Frontend Features

- **Modern UI**: Clean, intuitive interface with Tailwind CSS
- **Real-time Chat**: Instant messaging with AI tutor
- **Progress Dashboard**: Visual learning analytics
- **Responsive Design**: Works on all device sizes
- **Dark/Light Mode**: User preference themes

## 🛡️ Security & Performance

- **Input Validation**: Pydantic schemas for API security
- **Database ORM**: SQLAlchemy for safe database operations
- **Caching**: Redis for improved response times
- **Error Handling**: Comprehensive error management
- **Logging**: Detailed application logging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with `test-setup.bat`
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **VinAI Research** for the PhoGPT-4B-Chat model
- **FastAPI** for the excellent Python web framework
- **Next.js** for the powerful React framework
- **Tailwind CSS** for the utility-first styling

---

**Happy Vietnamese Learning! 🇻🇳**