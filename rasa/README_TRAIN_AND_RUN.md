# Hướng dẫn train và chạy Rasa cho VietnameseTutorAI

## 1. Cài đặt môi trường
- Đảm bảo đã cài Python 3.8+ và pip.
- Cài đặt các thư viện cần thiết:
  ```bash
  cd rasa
  pip install -r requirements.txt
  ```

## 2. Train mô hình Rasa
- Di chuyển vào thư mục `rasa`:
  ```bash
  cd rasa
  ```
- Train mô hình:
  ```bash
  rasa train
  ```
- Sau khi train thành công, file model sẽ được tạo trong thư mục `models/`.

## 3. Chạy Rasa server
- Khởi động server:
  ```bash
  rasa run --enable-api --cors "*" --debug
  ```
- Mặc định server sẽ chạy ở cổng 5005.
- Có thể kiểm tra bằng cách gửi request tới endpoint `/webhooks/rest/webhook`.

## 4. Chạy toàn bộ dịch vụ (backend, ai, frontend, database)
- Quay lại thư mục gốc dự án:
  ```bash
  cd ..
  ```
- Chạy script khởi động tất cả dịch vụ:
  ```bash
  ./start-services.sh
  ```
- Script này sẽ khởi động các container Docker cho backend, ai, frontend, database, và Rasa.

## 5. Lưu ý
- Nếu muốn dừng toàn bộ dịch vụ, dùng:
  ```bash
  ./stop-local.bat
  ```
- Đảm bảo các file cấu hình (nlu.yml, domain.yml, rules.yml, config.yml) đã được cập nhật trước khi train.
- Nếu gặp lỗi, kiểm tra log của từng service hoặc container.

---

**Tóm tắt quy trình:**
1. Cài Python và các thư viện.
2. Train Rasa bằng `rasa train`.
3. Chạy Rasa server hoặc toàn bộ hệ thống bằng `./start-services.sh`.
