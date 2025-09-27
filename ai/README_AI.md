# Hướng dẫn sử dụng Vietnamese Teacher AI

## Cấu trúc dự án

- `trainer.py` - Script để train model AI Vietnamese Teacher
- `app.py` - API service chạy trên cổng 5003 
- `run_training.py` - Script chạy training riêng biệt
- `test_api.py` - Script test API
- `premium_teacher_data.txt` - Dữ liệu training chất lượng cao

## Cách sử dụng

### 1. Training model (tùy chọn)

```bash
cd /Users/Shared/PearBit/VietnameseTutorAI/ai
venv/bin/python run_training.py
```

### 2. Chạy AI Service

```bash
cd /Users/Shared/PearBit/VietnameseTutorAI/ai
venv/bin/python app.py
```

Service sẽ chạy tại: `http://localhost:5003`

### 3. Test API

Mở terminal khác và chạy:

```bash
cd /Users/Shared/PearBit/VietnameseTutorAI/ai
venv/bin/python test_api.py
```

## API Endpoints

- `GET /health` - Kiểm tra trạng thái service
- `GET /model-info` - Thông tin về model  
- `POST /chat` - Chat với AI teacher

### Ví dụ sử dụng /chat endpoint:

```bash
curl -X POST http://localhost:5003/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Xin chào cô!"}'
```

## Trạng thái hiện tại

✅ **THÀNH CÔNG**: AI service đang chạy ở cổng 5003 với trained model!

Model đã được train thành công với dữ liệu Vietnamese teacher conversations và sẵn sàng trả lời câu hỏi như một giáo viên tiếng Việt chuyên nghiệp.

## Kiểm tra nhanh

Để test nhanh, bạn có thể dùng curl:

```bash
# Kiểm tra health
curl http://localhost:5003/health

# Chat với AI
curl -X POST http://localhost:5003/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "6 thanh điệu là những thanh nào ạ?"}'
```