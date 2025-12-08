# CHECKSCAM BACKEND – Anti-Fraud Platform (Spring Boot)

Backend hệ thống **Phòng Chống Lừa Đảo CheckScam**, cung cấp API cho website và mobile nhằm:

- Tra cứu thông tin lừa đảo (SĐT, STK, URL)
- Gửi báo cáo lừa đảo kèm minh chứng (ảnh)
- Quản lý báo cáo (CTV + Admin)
- Quản lý tài khoản hệ thống
- Quản lý tin tức cảnh báo
- Dashboard thống kê theo ngày/tháng
- Chatbot AI hỗ trợ cảnh báo tự động
- Upload file (hình ảnh / tài liệu)

# 1. Công nghệ sử dụng

| Công nghệ | Phiên bản |
|----------|-----------|
| Java | 17 |
| Spring Boot | 3.5.x |
| Spring Security | + JWT |
| MySQL | 8.x |
| Lombok | ✔ |
| Maven | ✔ |
| Postman | ✔ |


# 2. Base URL

Tất cả API đều bắt đầu với prefix: http://localhost:8080/api

# 3. Phân quyền hệ thống

| Chức năng | USER | CTV | ADMIN |
|-----------|------|------|--------|
| Tra cứu (Lookup) | ✔ | ✔ | ✔ |
| Gửi báo cáo | ✔ | ✔ | ✔ |
| Duyệt báo cáo | ✖ | ✔ | ✔ |
| Xóa báo cáo | ✖ | ✖ | ✔ |
| Xem tin tức | ✔ | ✔ | ✔ |
| Tạo/Sửa tin tức | ✖ | ✔ | ✔ |
| Xóa tin tức | ✖ | ✖ | ✔ |
| Dashboard | ✖ | ✔ | ✔ |
| Quản lý tài khoản | ✖ | ✖ | ✔ |
| Chatbot AI | ✔ | ✔ | ✔ |


# 4. Kiến trúc hệ thống
src/main/java/com/checkscam/backend/
│
├── controller/ # REST Controllers
├── dto/ # Data Transfer Objects
├── entity/ # JPA Entities
├── repository/ # Spring Data JPA
├── service/ # Interfaces
├── service/impl/ # Implementations
├── security/ # JWT + Authentication
└── specification/ # Filter, search logic

# 5. Cài đặt & chạy dự án

## 5.1. Clone dự án

git clone https://github.com/your-repo/checkscam-backend.git

## 5.2. Tạo database MySQL
CREATE DATABASE checkscam CHARACTER SET utf8mb4;

## 5.3. Cập nhật `application.properties`
spring.datasource.url=jdbc:mysql://localhost:3306/checkscam
spring.datasource.username=root
spring.datasource.password=your_password
spring.jpa.hibernate.ddl-auto=update

## 5.4. Chạy dự án
mvn spring-boot:run

# 6. Các Module chính

Dự án gồm 8 module trách nhiệm rõ ràng:

## **AUTH**  
- Login  
- Register  
- Refresh Token  
- Trả về accessToken & refreshToken  

## **ACCOUNT (ADMIN)**  
- Xem danh sách tài khoản  
- Khóa / Mở khóa  
- Gán role (USER → CTV → ADMIN)  

## **REPORT**  
- Gửi báo cáo + upload nhiều ảnh  
- Review (approve/reject)  
- Xóa report  
- Lịch sử báo cáo  

## **LOOKUP**  
- Tra cứu số điện thoại  
- Tra cứu số tài khoản ngân hàng  
- Tra cứu URL  
- Trả về mức độ nguy hiểm + số lần báo cáo  

## **AI CHATBOT**  
- Tự động phân tích tin nhắn  
- Nhận dạng số điện thoại / STK / URL  
- Lookup và trả lời cảnh báo  

## **NEWS**  
- CRUD tin tức  
- Lọc theo danh mục  
- Lấy top 5 tin mới nhất  

## **DASHBOARD**  
- Tổng số report  
- Báo cáo theo ngày/tháng  
- Top PHONE/STK/URL bị lừa nhiều nhất  

## **FILE UPLOAD**  
- Upload 1 file  
- Upload multiple files  
- Delete file  
- Lưu theo thư mục ngày (`uploads/yyyy/MM/dd/`)  

---

# 7. Postman Collection

Toàn bộ API đã được cấu hình trong collection: CheckScam_API_Collection.json

Import vào Postman → chạy test ngay.


# 📄 8. API Documentation

File tài liệu API đầy đủ: API_DOCUMENTATION.md

Bao gồm:

- Endpoint  
- Method  
- Request body  
- Response mẫu  
- Lỗi trả về  
- Quy tắc phân quyền  








