# Rasa Chatbot for Vietnamese Tutor

Thư mục này chứa cấu hình và dữ liệu để train chatbot Rasa thay thế cho AI cũ.

## Cấu trúc thư mục
- `config.yml`: Pipeline và policies cho Rasa.
- `domain.yml`: Định nghĩa intent, response.
- `data/nlu.yml`: Dữ liệu hội thoại (sẽ sinh tự động từ premium_teacher_data.txt).
- `data/rules.yml`: Rule cho bot trả lời.

## Hướng dẫn train
1. Cài đặt Rasa:
   ```sh
   pip install rasa
   ```
2. Chạy train:
   ```sh
   rasa train
   ```
3. Chạy bot:
   ```sh
   rasa shell
   ```

## Ghi chú
- Dữ liệu nlu sẽ được sinh tự động từ file `ai/premium_teacher_data.txt`.
- Mỗi câu hỏi sẽ là intent, câu trả lời là response.
