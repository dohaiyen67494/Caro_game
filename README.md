🎮 Caro Game - AI Integration with Pygame. 
   Đồ án xây dựng ứng dụng trò chơi Caro kinh điển, kết hợp giao diện đồ họa trực quan và Trí tuệ nhân tạo (AI) thông minh. Ứng dụng được phát triển bằng ngôn ngữ Python, sử dụng thư viện Pygame.

✨ Tính năng chính:
- Chế độ Người với Người (PvP): Cho phép hai người chơi thi đấu trực tiếp, hệ thống tự động quản lý lượt đánh và kiểm tra thắng thua.
- Chế độ Người với Máy (PvAI): Thử thách với AI tích hợp thuật toán tìm kiếm thông minh, có khả năng tấn công và phòng thủ linh hoạt.
- Hệ thống Logic Hoàn thiện: Ngăn chặn ghi đè quân cờ, nhận diện các trạng thái Thắng - Thua - Hòa chính xác.
- Giao diện Thân thiện: Màn hình Menu chọn chế độ, bàn cờ chuẩn 15x15, hiệu ứng mượt mà, phản hồi tức thì.

🧠 Cấu trúc dữ liệu & Giải thuật
Đồ án tập trung vào việc tối ưu hóa hiệu suất thông qua các lựa chọn kỹ thuật sau:
1. Cấu trúc dữ liệu
   Mảng 2 chiều (2D Array): Sử dụng mảng N x N để lưu trữ trạng thái bàn cờ.
     Quy ước: 0 (ô trống), 1 (quân X), -1 (quân O).
     Ưu điểm: Truy xuất và cập nhật trạng thái tại bất kỳ ô nào với độ phức tạp O(1).
2. Giải thuật kiểm tra thắng thua
   Thay vì duyệt toàn bộ bàn cờ, thuật toán chỉ duyệt cục bộ 4 hướng (ngang, dọc, chéo chính, chéo phụ) tính từ vị trí quân cờ vừa đánh.
   Kết quả: Tối ưu hóa hiệu suất, phản hồi kết quả ngay lập tức khi đạt đủ 5 quân liên tiếp.
3. Trí tuệ nhân tạo (AI)
   AI được xây dựng dựa trên sự kết hợp của nhiều thuật toán tìm kiếm và tối ưu:
     Minimax & Cắt tỉa Alpha-Beta: Dự đoán nước đi của cả hai bên và loại bỏ các nhánh không tiềm năng để tăng độ sâu tính toán.
     Hàm lượng giá (Heuristic): Sử dụng kỹ thuật Pattern Matching để nhận diện các chuỗi cờ, chấm điểm dựa trên độ dài và trạng thái bị chặn đầu.
     Lọc nước đi (Candidate Selection): Chỉ xét các ô trống trong bán kính 2 ô quanh các quân đã đánh để thu hẹp không gian tìm kiếm, giúp AI phản ứng gần như tức thì.

🛠 Cài đặt & Sử dụng
Yêu cầu: Đã cài đặt Python.

Cài đặt thư viện:
```bash
pip install pygame
```

Chạy game:
```bash
python main.py
```

📚 Tài liệu tham khảo
Pygame Series: Lập trình Game cờ Caro (Steam for Vietnam).
Codelearn.io: Làm Game Cờ Caro qua mạng LAN bằng Python.
