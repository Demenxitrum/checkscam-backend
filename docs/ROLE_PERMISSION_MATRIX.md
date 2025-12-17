# ROLE PERMISSION MATRIX — CheckScam (RBAC)

## 1. Giới thiệu

Hệ thống CheckScam sử dụng RBAC – Role-Based Access Control để phân quyền theo 3 vai trò chính:

- **USER** – Người dùng thông thường
- **CTV** – Cộng tác viên (tạo tin, xem dashboard, xử lý nghiệp vụ được phân quyền)
- **ADMIN** – Quản trị viên hệ thống (quản trị tài khoản, duyệt tin tức, duyệt báo cáo, admin-lookup)

Tài liệu này mô tả quyền truy cập của từng role đối với từng API endpoint và từng module nghiệp vụ.

---

## 2. Bảng tổng hợp quyền hệ thống

| Module | USER | CTV | ADMIN |
|---|---:|---:|---:|
| Auth | ✔ | ✔ | ✔ |
| Lookup (public) | ✔ | ✔ | ✔ |
| Report – Gửi báo cáo | ✔ | ✔ | ✔ |
| Report – Xem tất cả | ✖ | ✔ | ✔ |
| Report – Duyệt (approve/reject) | ✖ | ✖ | ✔ |
| Report – Xóa báo cáo | ✖ | ✖ | ✔ |
| News – Xem bài viết (public) | ✔ | ✔ | ✔ |
| News – Tạo/Sửa bài viết | ✖ | ✔ | ✔ |
| News – Duyệt / Publish bài viết | ✖ | ✖ | ✔ |
| News – Xóa bài viết | ✖ | ✖ | ✔ |
| Dashboard | ✖ | ✔ | ✔ |
| Account Management | ✖ | ✖ | ✔ |
| AI Chatbot | ✔ | ✔ | ✔ |
| Upload File | ✔ | ✔ | ✔ |
| Admin Lookup (chi tiết) | ✖ | ✖ | ✔ |

> Ghi chú: “Report – Duyệt” được thực hiện **chỉ bởi ADMIN** theo Postman collection hiện tại.

---

## 3. Phân quyền theo từng module

### 3.1 AUTH MODULE (Public)
| API | USER | CTV | ADMIN |
|---|---:|---:|---:|
| POST /auth/register | ✔ | ✔ | ✔ |
| POST /auth/login | ✔ | ✔ | ✔ |
| POST /auth/refresh | ✔ | ✔ | ✔ |

Auth luôn mở công khai.

---

### 3.2 ACCOUNT MODULE (ADMIN ONLY)
| API | USER | CTV | ADMIN |
|---|---:|---:|---:|
| GET /account | ✖ | ✖ | ✔ |
| PUT /account/{id}/lock | ✖ | ✖ | ✔ |
| PUT /account/{id}/unlock | ✖ | ✖ | ✔ |
| PUT /account/{id}/role?role=CTV | ✖ | ✖ | ✔ |

CTV và USER không được quản lý tài khoản.

---

### 3.3 REPORT MODULE
| Chức năng | USER | CTV | ADMIN |
|---|---:|---:|---:|
| Gửi report (POST /report) | ✔ | ✔ | ✔ |
| Xem danh sách report (GET /report) | ✖ | ✔ | ✔ |
| Xem chi tiết report (GET /report/{id}) | ✖ | ✔ | ✔ |
| Approve report (PUT /report/{id}/approve) | ✖ | ✖ | ✔ |
| Reject report (PUT /report/{id}/reject) | ✖ | ✖ | ✔ |
| Xóa report (DELETE /report/{id}) | ✖ | ✖ | ✔ |

> Ghi chú: CTV có quyền **xem danh sách / chi tiết report** theo Postman collection, nhưng **không có quyền duyệt hoặc xóa report**.

---

### 3.4 NEWS MODULE
| API | USER | CTV | ADMIN |
|---|---:|---:|---:|
| GET /news/** | ✔ | ✔ | ✔ |
| GET /news/pending | ✖ | ✖ | ✔ |
| POST /news | ✖ | ✔ | ✔ |
| PUT /news/{id} | ✖ | ✔ | ✔ |
| PUT /news/{id}/approve | ✖ | ✖ | ✔ |
| PUT /news/{id}/reject | ✖ | ✖ | ✔ |
| DELETE /news/{id} | ✖ | ✖ | ✔ |

Ghi chú:
- Bài viết do **CTV** tạo sẽ ở trạng thái **PENDING** và cần **ADMIN** duyệt trước khi hiển thị công khai.
- **CTV chỉ được chỉnh sửa bài viết PENDING do chính mình tạo** (backend đã chặn trong service).

---

### 3.5 DASHBOARD MODULE
| API | USER | CTV | ADMIN |
|---|---:|---:|---:|
| GET /dashboard/summary | ✖ | ✔ | ✔ |
| GET /dashboard/daily | ✖ | ✔ | ✔ |

Dashboard là module phân tích — chỉ CTV & Admin.

---

### 3.6 LOOKUP MODULE (Public)
| API | USER | CTV | ADMIN |
|---|---:|---:|---:|
| GET /lookup/phone | ✔ | ✔ | ✔ |
| GET /lookup/bank | ✔ | ✔ | ✔ |
| GET /lookup/url | ✔ | ✔ | ✔ |

Ai cũng tra cứu được — không yêu cầu đăng nhập.

---

### 3.7 AI MODULE
| API | USER | CTV | ADMIN |
|---|---:|---:|---:|
| POST /ai/chat | ✔ | ✔ | ✔ |

Chatbot phục vụ cho tất cả người dùng.

---

### 3.8 FILE UPLOAD MODULE
| API | USER | CTV | ADMIN |
|---|---:|---:|---:|
| POST /upload/file | ✔ | ✔ | ✔ |
| POST /upload/multiple | ✔ | ✔ | ✔ |
| DELETE /upload/delete | ✔ | ✔ | ✔ |

Ghi chú: việc kiểm tra quyền xoá file (ownership) được xử lý tại tầng service.

---

## 4. Ma trận vai trò – API chi tiết (Route-level)

| API Endpoint Pattern | USER | CTV | ADMIN |
|---|---:|---:|---:|
| /auth/** | ✔ | ✔ | ✔ |
| GET /lookup/** | ✔ | ✔ | ✔ |
| POST /report | ✔ | ✔ | ✔ |
| GET /report/** | ✖ | ✔ | ✔ |
| PUT /report/** | ✖ | ✖ | ✔ |
| DELETE /report/** | ✖ | ✖ | ✔ |
| GET /news/** | ✔ | ✔ | ✔ |
| POST /news | ✖ | ✔ | ✔ |
| PUT /news/** | ✖ | ✔ | ✔ |
| PUT /news/*/approve | ✖ | ✖ | ✔ |
| PUT /news/*/reject | ✖ | ✖ | ✔ |
| DELETE /news/** | ✖ | ✖ | ✔ |
| /dashboard/** | ✖ | ✔ | ✔ |
| /account/** | ✖ | ✖ | ✔ |
| /ai/chat | ✔ | ✔ | ✔ |
| /upload/** | ✔ | ✔ | ✔ |
| /api/admin/lookup | ✖ | ✖ | ✔ |

---

## 5. ADMIN LOOKUP MODULE
| API | USER | CTV | ADMIN |
|---|---:|---:|---:|
| GET /api/admin/lookup | ✖ | ✖ | ✔ |

Chỉ ADMIN được phép tra cứu chi tiết (risk score, signals, sources).
USER và CTV không được truy cập API này.
