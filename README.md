# CHECKSCAM BACKEND – Anti-Fraud Platform (Spring Boot)

Backend hệ thống **Phòng Chống Lừa Đảo CheckScam**, cung cấp API cho website và mobile nhằm:

- Tra cứu thông tin lừa đảo (SĐT, STK, URL)
- Gửi báo cáo lừa đảo kèm minh chứng (ảnh)
- Quản lý báo cáo (Admin duyệt)
- Quản lý tài khoản hệ thống
- Quản lý tin tức cảnh báo (CTV tạo – Admin duyệt)
- Dashboard thống kê theo ngày/tháng
- Chatbot AI hỗ trợ cảnh báo tự động
- Upload file (hình ảnh / tài liệu)

---

## 1. Công nghệ sử dụng

| Công nghệ | Phiên bản |
|----------|-----------|
| Java | 17 |
| Spring Boot | 3.5.x |
| Spring Security | JWT |
| MySQL | 8.x |
| Lombok | ✔ |
| Maven | ✔ |
| Postman | ✔ |

---

## 2. Base URL

Tất cả API đều bắt đầu với prefix:

http://localhost:8080/api

yaml
Sao chép mã

---

## 3. Phân quyền hệ thống (RBAC)

| Chức năng | USER | CTV | ADMIN |
|-----------|------|------|--------|
| Tra cứu (Lookup) | ✔ | ✔ | ✔ |
| Gửi báo cáo | ✔ | ✔ | ✔ |
| Duyệt / từ chối báo cáo | ✖ | ✖ | ✔ |
| Xóa báo cáo | ✖ | ✖ | ✔ |
| Xem tin tức | ✔ | ✔ | ✔ |
| Tạo / sửa tin tức | ✖ | ✔ | ✔ |
| Duyệt / publish tin tức | ✖ | ✖ | ✔ |
| Xóa tin tức | ✖ | ✖ | ✔ |
| Dashboard | ✖ | ✔ | ✔ |
| Quản lý tài khoản | ✖ | ✖ | ✔ |
| Chatbot AI | ✔ | ✔ | ✔ |

---

## 4. Kiến trúc hệ thống

src/main/java/com/checkscam/backend/
│
├── controller/ # REST Controllers
├── dto/ # Data Transfer Objects
├── entity/ # JPA Entities
├── repository/ # Spring Data JPA
├── service/ # Service Interfaces
├── service/impl/ # Service Implementations
├── security/ # JWT, Authentication, Authorization
└── specification/ # Filter, search logic

yaml
Sao chép mã

---

## 5. Cài đặt & chạy dự án

### 5.1. Clone dự án
```bash
git clone https://github.com/your-repo/checkscam-backend.git
cd checkscam-backend
5.2. Tạo database MySQL
sql
Sao chép mã
CREATE DATABASE checkscam CHARACTER SET utf8mb4;
5.3. Cấu hình application.properties
properties
Sao chép mã
spring.datasource.url=jdbc:mysql://localhost:3306/checkscam
spring.datasource.username=root
spring.datasource.password=your_password

spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true
5.4. Chạy dự án
bash
Sao chép mã
mvn spring-boot:run
6. Các module chính
Dự án được chia thành các module nghiệp vụ rõ ràng:

AUTH
Register

Login

Refresh Token

Trả về accessToken & refreshToken

ACCOUNT (ADMIN)
Xem danh sách tài khoản

Khóa / mở khóa tài khoản

Gán role (theo quyền ADMIN)

REPORT
Gửi báo cáo lừa đảo + upload nhiều ảnh

Duyệt / từ chối báo cáo (ADMIN)

Xóa báo cáo

Thống kê lịch sử báo cáo

LOOKUP
Tra cứu số điện thoại

Tra cứu số tài khoản ngân hàng

Tra cứu URL

Trả về mức độ rủi ro + số lần bị báo cáo

AI CHATBOT
Phân tích nội dung người dùng gửi

Nhận dạng PHONE / BANK / URL

Tự động lookup và trả lời cảnh báo

NEWS
CRUD tin tức

Phân loại theo danh mục

Lấy danh sách tin mới nhất

CTV tạo bài → trạng thái PENDING → ADMIN duyệt

DASHBOARD
Tổng số báo cáo

Thống kê theo ngày / tháng

FILE UPLOAD
Upload 1 file

Upload nhiều file

Xóa file

Lưu theo cấu trúc thư mục: uploads/yyyy/MM/dd/

7. Postman Collection
Toàn bộ API đã được cấu hình sẵn trong Postman:

POSTMAN_COLLECTION.json

POSTMAN_ENVIRONMENT.json

Import vào Postman để test toàn bộ API theo role.

8. API Documentation
Tài liệu API chi tiết nằm trong thư mục docs/:

API_DOCUMENTATION.md

ROLE_PERMISSION_MATRIX.md

SAMPLE_RESPONSE.md

Bao gồm:

Danh sách endpoint

Method

Request / Response mẫu

Mã lỗi

Quy tắc phân quyền RBAC

📌 Ghi chú
Hệ thống sử dụng JWT Authentication

Phân quyền được kiểm soát tại tầng Security + Service

Admin Lookup là chức năng nâng cao dành riêng cho ADMIN (dấu ấn đồ án)

