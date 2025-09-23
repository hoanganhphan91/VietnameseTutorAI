# 🚀 Vietnamese AI Tutor - Quick Start Guide

## 📋 Cách chạy dự án (macOS/Linux)

### Bước 1: Clean project (nếu cần)
```bash
# Xóa tất cả dependencies và virtual environments cũ
./clean-project.sh
```

### Bước 2: Setup dự án lần đầu
```bash
# Cài đặt tất cả dependencies từ đầu
./setup-project.sh
```

### Bước 3: Kiểm tra hệ thống
```bash
# Test xem setup có OK không
./test-setup.sh
```

### Bước 4: Chạy dự án
```bash
# Khởi động tất cả services
./start-services.sh
```

### Bước 5: Dừng dự án
```bash
# Dừng tất cả services
./stop-services.sh
```

## 📋 Cách chạy dự án (Windows)

### Bước 1: Clean project (nếu cần)
```cmd
REM Xóa tất cả dependencies và virtual environments cũ
clean-project.bat
```

### Bước 2: Setup dự án lần đầu
```cmd
REM Cài đặt tất cả dependencies từ đầu
deploy-local.bat
```

### Bước 3: Chạy dự án
```cmd
REM Khởi động tất cả services
start-services.bat
```

### Bước 4: Dừng dự án
```cmd
REM Dừng tất cả services
stop-local.bat
```

## 🌐 URLs sau khi chạy thành công

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **AI Service**: http://localhost:5000

## ⚙️ Yêu cầu hệ thống

- **Python**: 3.11+ (tương thích với 3.13)
- **Node.js**: 18+
- **npm**: Included with Node.js
- **OS**: macOS, Linux, Windows

## 🔧 Troubleshooting

### Lỗi SQLAlchemy hoặc Dependencies
```bash
# Xóa và cài lại từ đầu
./clean-project.sh
./setup-project.sh
```

### Port 8000 đã được sử dụng
```bash
# Tìm process đang dùng port 8000
lsof -i:8000

# Kill process
sudo lsof -ti:8000 | xargs kill -9

# Hoặc dùng script stop
./stop-services.sh
```

### Dependencies lỗi
```bash
# Reset hoàn toàn và cài lại
./clean-project.sh
./setup-project.sh
```

### AI Model tải chậm
- Model PhoGPT-4B sẽ tự động tải lần đầu chạy (khoảng 4-6GB)
- Cần kết nối internet tốt
- Lần chạy tiếp theo sẽ nhanh hơn

## 📁 File structure

```
├── clean-project.sh     # Xóa tất cả và reset (Mac/Linux)
├── setup-project.sh     # Setup lần đầu (Mac/Linux)
├── start-services.sh    # Chạy dự án (Mac/Linux)
├── stop-services.sh     # Dừng dự án (Mac/Linux)
├── test-setup.sh        # Test hệ thống (Mac/Linux)
├── clean-project.bat    # Xóa tất cả và reset (Windows)
├── deploy-local.bat     # Setup lần đầu (Windows)
├── start-services.bat   # Chạy dự án (Windows)
├── stop-local.bat       # Dừng dự án (Windows)
└── README_QUICKSTART.md # File này
```

## 🎯 Tính năng

- 🤖 Chat với AI Vietnamese tutor
- 🗣️ Pronunciation feedback
- 🇻🇳 Cultural context
- 📊 Progress tracking
- 🌐 Multi-language support

## 🚨 Lưu ý quan trọng

**MỌI THAO TÁC ĐỀU PHẢI THÔNG QUA SCRIPT .SH HOẶC .BAT**

- ❌ Không chạy lệnh trực tiếp trong terminal
- ✅ Dùng script để đảm bảo tính nhất quán
- ✅ Script tự động handle dependencies và virtual environments
- ✅ Script có error checking và cleanup