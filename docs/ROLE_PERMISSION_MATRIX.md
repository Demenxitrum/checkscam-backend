1. Giới thiệu

Hệ thống CheckScam sử dụng RBAC – Role-Based Access Control để phân quyền theo 3 vai trò chính:
        USER – Người dùng thông thường
        CTV – Cộng tác viên kiểm duyệt báo cáo
        ADMIN – Quản trị viên hệ thống

Tài liệu này mô tả chi tiết quyền truy cập của từng role đối với từng API endpoint và từng module nghiệp vụ.

2. Bảng tổng hợp quyền hệ thống
Module	                                USER	            CTV	            ADMIN
Auth	                                ✔	                ✔	            ✔
Lookup	                                ✔	                ✔	            ✔
Report – Gửi báo cáo	                ✔	                ✔	            ✔
Report – Xem tất cả	                    ✖	                ✔	            ✔
Report – Duyệt (approve/reject)	        ✖	                ✔	            ✔
Report – Chỉnh sửa báo cáo	            ✖	                ✔	            ✔
Report – Xóa báo cáo	                ✖	                ✖	            ✔
News – Xem bài viết	                    ✔	                ✔	            ✔
News – Tạo/Sửa bài viết	                ✖	                ✔	            ✔
News – Xóa bài viết	                    ✖	                ✖	            ✔
Dashboard	                            ✖	                ✔	            ✔
Account Management	                    ✖	                ✖	            ✔
AI Chatbot	                            ✔	                ✔	            ✔
Upload File	                            ✔	                ✔	            ✔
3. Phân quyền theo từng module
3.1 AUTH MODULE
API	                                    USER	            CTV	            ADMIN
POST /auth/register	                    ✔	                ✔	            ✔
POST /auth/login	                    ✔	                ✔	            ✔
POST /auth/refresh	                    ✔	                ✔	            ✔

Auth luôn mở công khai.

3.2 ACCOUNT MODULE (ADMIN ONLY)
API	                                    USER	            CTV	            ADMIN
GET /account	                        ✖	                ✖	            ✔
PUT /account/{id}/lock	                ✖	                ✖	            ✔
PUT /account/{id}/unlock	            ✖	                ✖	            ✔
PUT /account/{id}/role?role=CTV	        ✖	                ✖	            ✔

CTV và USER không bao giờ được quản lý tài khoản.

3.3 REPORT MODULE
Chức năng	                            USER	            CTV	            ADMIN
Gửi report (POST /report)	            ✔	                ✔	            ✔
Xem tất cả report	                    ✖	                ✔	            ✔
Xem chi tiết report	                    ✖	                ✔	            ✔
Approve / Reject report	                ✖	                ✔	            ✔
Cập nhật report	                        ✖	                ✔	            ✔
Xóa report	                            ✖	                ✖	            ✔

CTV có toàn quyền trên report ngoại trừ xoá.

3.4 NEWS MODULE
API	                                    USER	            CTV	            ADMIN
GET /news/**	                        ✔	                ✔	            ✔
POST /news	                            ✖	                ✔	            ✔
PUT /news/{id}	                        ✖	                ✔	            ✔
DELETE /news/{id}	                    ✖	                ✖	            ✔

CTV có thể tạo bài viết và chỉnh sửa – nhưng không được xóa.

3.5 DASHBOARD MODULE
API	                                    USER	              CTV	        ADMIN
GET /dashboard/summary	                ✖	                  ✔	            ✔
GET /dashboard/daily	                ✖	                  ✔	            ✔
GET /dashboard/top-values	            ✖	                  ✔	            ✔

Dashboard là module phân tích nâng cao — chỉ CTV & Admin.

3.6 LOOKUP MODULE
API	                                    USER	              CTV	        ADMIN
GET /lookup/phone	                     ✔	                  ✔	            ✔
GET /lookup/bank	                     ✔	                  ✔	            ✔
GET /lookup/url	                         ✔	                  ✔	            ✔

Ai cũng tra cứu được — không yêu cầu đăng nhập.

3.7 AI MODULE
API	                                    USER	              CTV	        ADMIN
POST /ai/chat	                         ✔	                  ✔	            ✔

Chatbot phục vụ cho tất cả người dùng.

3.8 FILE UPLOAD MODULE
API	                                    USER	                        CTV	            ADMIN
POST /upload/file	                    ✔	                            ✔	            ✔
POST /upload/multiple	                ✔	                            ✔	            ✔
DELETE /upload/delete	                ✔ (chỉ xóa file user upload)	✔	            ✔

📌 Phân quyền thực tế phụ thuộc FE: người nào upload file nào thì được xoá file đó.

🔐 4. Ma trận vai trò – API chi tiết
API Endpoint	                        USER	               CTV	        ADMIN
/auth/**	                            ✔	                    ✔	        ✔
GET /lookup/**	                        ✔	                    ✔	        ✔
POST /report	                        ✔	                    ✔	        ✔
GET /report/**	                        ✖	                    ✔	        ✔
PUT /report/**	                        ✖	                    ✔	        ✔
DELETE /report/**	                    ✖	                    ✖	        ✔
GET /news/**	                        ✔	                    ✔	        ✔
POST /news	                            ✖	                    ✔	        ✔
PUT /news/**	                        ✖	                    ✔	        ✔
DELETE /news/**	                        ✖	                    ✖	        ✔
/dashboard/**	                        ✖	                    ✔	        ✔
/account/**	                            ✖	                    ✖	        ✔
/ai/chat	                            ✔	                    ✔	        ✔
/upload/**	                            ✔	                    ✔	         ✔