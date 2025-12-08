1. AUTH MODULE
1.1 Login — Success
    {
        "accessToken": "eyJhbGciOiJIUzI1NiIsInR...",
        "refreshToken": "eyJhbGciOiJIUzI1NiIsInR...",
        "role": "USER"
    }

1.2 Login — Wrong password
    {
        "error": "Invalid credentials"
    }

1.3 Register — Success
    {
        "message": "Registered successfully"
    }

1.4 Refresh Token — Success
    {
        "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI..."
    }

2. ACCOUNT MODULE (ADMIN ONLY)
2.1 Get all accounts
    {
    "items": [
        {
            "id": 1,
            "email": "admin@gmail.com",
            "name": "Admin",
            "role": "ADMIN",
            "status": "ACTIVE"
        },
        {
            "id": 2,
             "email": "ctv@gmail.com",
            "name": "CTV A",
            "role": "CTV",
            "status": "LOCKED"
        }
    ],
    "page": 0,
    "totalItems": 2
    }

2.2 Lock account
    {
        "message": "Account locked"
    }

2.3 Unlock account
    {
        "message": "Account unlocked"
    }

2.4 Update role
    {
        "message": "Role updated to CTV"
    }

3. REPORT MODULE
3.1 Create Report — Success
    {
        "id": 18,
        "type": "PHONE",
        "value": "0912345678",
        "description": "Lừa đảo mạo danh ngân hàng",
        "status": "PENDING",
        "riskLevel": "SAFE",
        "createdAt": "2025-12-08 10:15:22",
        "files": [
            "/uploads/2025/12/08/170999_image1.png",
            "/uploads/2025/12/08/170999_image2.jpg"
        ]
    }

3.2 Report List
    {
        "items": [
        {
            "id": 18,
            "type": "PHONE",
            "value": "0912345678",
            "reportCount": 3,
            "riskLevel": "MEDIUM",
            "status": "APPROVED",
            "createdAt": "2025-12-08 10:15:22"
        },
        {
            "id": 19,
            "type": "BANK",
            "value": "123456789012",
            "reportCount": 1,
            "riskLevel": "HIGH",
            "status": "PENDING",
            "createdAt": "2025-12-08 10:30:02"
        }
        ],
        "totalItems": 20,
        "page": 0
    }

3.3 Report Detail
    {
        "id": 18,
        "type": "PHONE",
        "value": "0912345678",
        "description": "Lừa đảo mạo danh ngân hàng",
        "status": "APPROVED",
        "riskLevel": "MEDIUM",
        "reportCount": 3,
        "files": [
            "/uploads/2025/12/08/170999_image1.png",
            "/uploads/2025/12/08/170999_image2.jpg"
        ],
        "createdAt": "2025-12-08 10:15:22"
    }

3.4 Approve report
    {
        "message": "Report approved"
    }

3.5 Reject report
    {
        "message": "Report rejected"
    }

3.6 Delete report
    {
        "message": "Report deleted"
    }

🧩 4. LOOKUP MODULE
4.1 Lookup Phone — Found
    {
        "typeId": 1,
        "typeName": "PHONE",
        "value": "0912345678",
        "reportCount": 3,
        "riskLevelId": 2,
        "riskLevelName": "MEDIUM",
        "exists": true,
        "updatedAt": "2025-12-08 09:12:55"
    }

4.2 Lookup Phone — Not found
    {
        "exists": false,
        "value": "0912345678",
        "reportCount": 0,
        "riskLevelName": "SAFE"
    }

5. AI CHATBOT MODULE
5.1 AI chat — With lookup detection
    {
        "reply": "Theo dữ liệu mới nhất, số 0912345678 đã bị báo cáo 3 lần và được đánh giá RỦI RO TRUNG BÌNH. Bạn cần cảnh giác.",
        "hasLookup": true,
        "lookupType": "PHONE",
        "lookupValue": "0912345678",
        "reportCount": 3,
        "riskLevel": "MEDIUM"
    }

5.2 AI chat — No lookup
    {
        "reply": "Dưới đây là hướng dẫn chung để phòng tránh lừa đảo...",
        "hasLookup": false
    }

6. NEWS MODULE
6.1 News list
    {
        "items": [
            {
            "id": 10,
            "title": "Cảnh báo thủ đoạn mạo danh ngân hàng",
            "thumbnailUrl": "/uploads/2025/12/08/news1.jpg",
            "categoryName": "Cảnh báo lừa đảo",
            "createdAt": "2025-12-08 08:30:21"
            }
        ],
        "page": 0,
        "totalItems": 12
    }

6.2 News detail
    {
        "id": 10,
        "title": "Cảnh báo thủ đoạn mạo danh ngân hàng",
        "description": "Nội dung mô tả...",
        "content": "<p>Nội dung chi tiết...</p>",
        "thumbnailUrl": "/uploads/2025/12/08/news1.jpg",
        "categoryId": 1,
        "categoryName": "Cảnh báo lừa đảo",
        "createdAt": "2025-12-08 08:30:21"
    }

6.3 Create news
    {
        "id": 11,
        "title": "Hướng dẫn tránh lừa đảo trên mạng",
        "description": "Các bước nhận diện dấu hiệu lừa đảo...",
        "content": "...",
        "thumbnailUrl": "/uploads/2025/12/08/news2.jpg",
        "categoryId": 1,
        "createdAt": "2025-12-08 11:20:12"
    }

7. DASHBOARD MODULE
7.1 Summary
    {
        "totalUsers": 300,
        "totalReports": 1023,
        "pendingReports": 50,
        "approvedReports": 850,
        "todayReports": 12
    }

7.2 Daily Report
    {
        "labels": ["2025-12-01", "2025-12-02", "2025-12-03"],
        "values": [10, 18, 25]
    }

7.3 Top Values
    {
        "topPhone": [
            { "value": "0912345678", "count": 12 },
            { "value": "0987654321", "count": 9 }
        ],
        "topBank": [
            { "value": "123456789012", "count": 6 }
        ],
        "topUrl": [
        { "value": "https://abc.com", "count": 5 }
        ]
    }

8. FILE UPLOAD MODULE
8.1 Upload 1 file
    {
        "fileUrl": "http://localhost:8080/uploads/2025/12/08/170999_avatar.png"
    }

8.2 Upload multiple files
    [
        "http://localhost:8080/uploads/2025/12/08/170999_img1.jpg",
        "http://localhost:8080/uploads/2025/12/08/170999_img2.png"
    ]

8.3 Delete file
    {
        "message": "File deleted"
    }
