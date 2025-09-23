# 🚀 Local Development Setup

## Quick Start (Windows)

### Requirements
- Python 3.11+
- Node.js 18+
- Git

### One-Command Deploy
```bash
# Deploy all services locally
deploy-local.bat

# Stop all services  
stop-local.bat
```

### Manual Setup

1. **Backend (FastAPI)**
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python create_sample_data.py
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

2. **AI Service (PhoGPT)**
```bash
cd ai
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

3. **Frontend (NextJS)**
```bash
cd frontend
npm install
npm run dev
```

### Services URLs
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **AI Service**: http://localhost:5000
- **API Docs**: http://localhost:8000/docs

### Database
- Local development uses **SQLite** (`vietnamese_tutor.db`)
- Docker deployment uses **MySQL**
- Database auto-migrates on startup

### Environment Files
- `backend/.env` - Backend configuration
- `frontend/.env.local` - Frontend configuration

### Troubleshooting
- If ports are busy, change ports in deploy script
- If dependencies fail, try `pip install --upgrade pip`
- If Node modules fail, delete `node_modules` and run `npm install` again