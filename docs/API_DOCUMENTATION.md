1. Tổng quan

Tất cả API của hệ thống CheckScam sử dụng chuẩn RESTful và trả về JSON.

Base URL:

http://localhost:8080/api


Auth:

Authorization: Bearer <accessToken>


Các vai trò:

USER → Người dùng thông thường

CTV → Cộng tác viên kiểm duyệt

ADMIN → Quản trị viên

2. AUTH MODULE
2.1 Register User

POST /auth/register

Request Body:

{
  "email": "user1@gmail.com",
  "name": "Nguyen Van A",
  "password": "123456"
}


Success Response:

{
  "message": "Registered successfully"
}


Error:

Lỗi	Mã	Mô tả
Email trùng	400	"Email already exists"
Password quá ngắn	400	"Invalid password"
2.2 Login

POST /auth/login

Request Body:

{
  "email": "user1@gmail.com",
  "password": "123456"
}


Success Response:

{
  "accessToken": "...",
  "refreshToken": "...",
  "role": "USER"
}


Error:

Trường hợp	Code
Sai email	404
Sai password	401
Tài khoản bị khóa	403
2.3 Refresh Token

POST /auth/refresh?token=<refreshToken>

Response:

{
  "accessToken": "newToken..."
}

3. ACCOUNT MODULE (ADMIN ONLY)
3.1 Lấy danh sách tài khoản

GET /account

Authorization: ADMIN

Response:

{
  "items": [
    {
      "id": 1,
      "email": "admin@gmail.com",
      "role": "ADMIN",
      "status": "ACTIVE"
    }
  ]
}

3.2 Khóa tài khoản

PUT /account/{id}/lock

Response:

{
  "message": "Account locked"
}

3.3 Mở khóa tài khoản

PUT /account/{id}/unlock

3.4 Gán role

PUT /account/{id}/role?role=CTV

Response:

{
  "message": "Role updated to CTV"
}

4. REPORT MODULE
4.1 Tạo Report + Upload ảnh

POST /report

Content-Type: multipart/form-data

Form-data:

Key	Value
infoValue	0912345678
type	PHONE
description	Lừa đảo chiếm đoạt
files	1–5 ảnh

Success:

{
  "id": 10,
  "status": "PENDING",
  "riskLevel": "SAFE"
}

4.2 Danh sách báo cáo

GET /report?page=0&size=10

Response:

{
  "items": [...],
  "page": 0,
  "totalItems": 30,
  "totalPages": 3
}

4.3 Chi tiết báo cáo

GET /report/{id}

4.4 Phê duyệt báo cáo

PUT /report/{id}/approve

Role: ADMIN

4.5 Từ chối báo cáo

PUT /report/{id}/reject

Role: ADMIN

4.6 Xóa báo cáo

DELETE /report/{id}

Role: ADMIN

5. LOOKUP MODULE
5.1 Lookup Phone

GET /lookup/phone?value=0912345678

Response:

{
  "type": "PHONE",
  "value": "0912345678",
  "exists": true,
  "reportCount": 3,
  "riskLevel": "MEDIUM",
  "updatedAt": "2025-12-06 09:21:00"
}

5.2 Lookup Bank

GET /lookup/bank?value=123456789012

5.3 Lookup URL

GET /lookup/url?value=https://abc.com

6. AI CHATBOT MODULE
6.1 Chat với AI

POST /ai/chat

Request Body:

{
  "message": "Số này 0912345678 có lừa đảo không?"
}


Response:

{
  "reply": "Số 0912345678 đã bị báo cáo 3 lần...",
  "hasLookup": true,
  "lookupType": "PHONE",
  "riskLevel": "MEDIUM"
}

7. NEWS MODULE
7.1 Lấy danh sách tin tức

GET /news?page=0&size=5&keyword=&categoryId=1

7.2 Chi tiết tin

GET /news/{id}

7.3 Tin mới nhất

GET /news/latest

7.4 Tạo tin mới (CTV + ADMIN)

POST /news

{
  "title": "Cảnh báo lừa đảo mới",
  "description": "Một hình thức lừa mới xuất hiện...",
  "content": "...",
  "thumbnailUrl": "/uploads/news/a.jpg",
  "categoryId": 1
}


📌 Ghi chú bổ sung (quan trọng):

Tin do CTV tạo sẽ ở trạng thái PENDING.

Chỉ ADMIN mới có quyền duyệt và công bố tin.

7.5 Duyệt tin (ADMIN)

PUT /news/{id}/approve

7.6 Từ chối tin (ADMIN)

PUT /news/{id}/reject

7.7 Xóa tin (ADMIN)

DELETE /news/{id}
7.8 Danh sách tin chờ duyệt (ADMIN)

GET /news/pending

Authorization: ADMIN

Response:
Danh sách các bài viết có trạng thái PENDING


8. DASHBOARD MODULE
8.1 Summary

GET /dashboard/summary

Response:

{
  "totalReports": 1023,
  "totalUsers": 300,
  "topToday": 25
}

8.2 Daily Statistic

GET /dashboard/daily

9. FILE UPLOAD MODULE
9.1 Upload 1 file

POST /upload/file

Response:

{
  "fileUrl": "http://localhost:8080/uploads/2025/12/08/17099999_img.png"
}

9.2 Upload multiple files

POST /upload/multiple

Response:

[
  "http://localhost:8080/uploads/.../a1.png",
  "http://localhost:8080/uploads/.../a2.png"
]

9.3 Xóa file

DELETE /upload/delete?filePath=/uploads/yyyy/MM/dd/xxx.png

📌 Việc kiểm tra quyền xóa file (ownership) được xử lý tại tầng service.

10. Trạng thái lỗi chung
Code	Ý nghĩa
400	Request không hợp lệ
401	Thiếu hoặc sai token
403	Không có quyền
404	Không tìm thấy dữ liệu
500	Lỗi server
11. Ghi chú quan trọng

Mọi API đều trả JSON

Thời gian theo format yyyy-MM-dd HH:mm:ss

Upload file ⇒ thư mục /uploads/yyyy/MM/dd/

12. ADMIN LOOKUP MODULE
12.1 Admin lookup (chi tiết – ROLE_ADMIN)

GET /api/admin/lookup

Authorization:

Bearer Token (ADMIN)

Query params:

type: PHONE | BANK | URL

value: <string>

Ví dụ:

GET http://localhost:8080/api/admin/lookup?type=PHONE&value=0886120424


Response (200 OK): (giữ nguyên như bạn đã mô tả)

Response (404):

Không tìm thấy thực thể trong lookup_cache

Response (401/403):

401: Token không hợp lệ / hết hạn

403: Không có quyền ADMIN