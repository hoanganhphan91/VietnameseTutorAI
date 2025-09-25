# AI Vietnamese Tutor

Ứng dụng AI Gia sư Tiếng Việt cho người nước ngoài sử dụng PhoGPT-4B-Chat.

## Tech Stack
- **Frontend**: NextJS 14 + TypeScript + ANTD
- **Backend**: FastAPI + Python 3.11
- **Database**: MySQL 8.0
- **Cache**: Redis
- **AI Model**: PhoGPT-4B-Chat (VinAI)
- **Deployment**: Docker Compose

## Quick Start

### Docker (Recommended)
```bash
# Clone và khởi chạy
git clone <repo-url>
cd ai-vietnamese-tutor
chmod +x deploy.sh
./deploy.sh
```

### Local Development (Windows)
```bash
# One-command local setup
deploy-local.bat

# Stop services
stop-local.bat
```

## Services
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **AI Service**: http://localhost:5000

## Features
- 🤖 Conversation practice với AI
- 🗣️ Pronunciation feedback
- 🇻🇳 Cultural context explanations
- 📊 Progress tracking
- 🌐 Multi-language support

## Development

```bash
# Start development
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   NextJS    │───▶│   FastAPI   │───▶│    MySQL    │
│  Frontend   │    │   Backend   │    │  Database   │
└─────────────┘    └─────────────┘    └─────────────┘
                           │
                   ┌───────┴───────┐
                   │               │
            ┌─────────────┐ ┌─────────────┐
            │    Redis    │ │  PhoGPT-4B  │
            │    Cache    │ │ AI Service  │
            └─────────────┘ └─────────────┘
```
