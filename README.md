# Microservice Demo với FastAPI + MySQL + Nginx API Gateway

## Kiến trúc

```
Client
   |
   | HTTP :8080
   v
Nginx (API Gateway)
   |
   |--> User Service  (FastAPI, :8001)
   |
   |--> Order Service (FastAPI, :8002)
             |
             v
         MySQL Database (shared)
```

## Yêu cầu

- Python 3.8+
- MySQL Server
- Nginx

## Cấu trúc thư mục

```
backend_demo/
├── database_schema.sql      # SQL script tạo database
├── user-service/            # User Service (port 8001)
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   └── requirements.txt
├── order-service/           # Order Service (port 8002)
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   └── requirements.txt
└── nginx/
    └── nginx.conf           # Nginx API Gateway config
```

## Hướng dẫn thiết lập

### 1. Tạo Database

Đăng nhập MySQL và chạy script:

```bash
mysql -u root -p < database_schema.sql
```

Hoặc chạy từng lệnh trong MySQL console:

```sql
CREATE DATABASE IF NOT EXISTS microservice_demo;
USE microservice_demo;
-- ... (xem database_schema.sql)
```

### 2. Cấu hình Database Connection

Cập nhật connection string trong các file:

- `user-service/database.py`
- `order-service/database.py`

Mặc định: `mysql+pymysql://root:password@localhost:3306/microservice_demo`

Thay đổi `root` và `password` theo MySQL của bạn.

### 3. Cài đặt Dependencies

#### User Service

```bash
cd user-service
pip install -r requirements.txt
```

#### Order Service

```bash
cd order-service
pip install -r requirements.txt
```

### 4. Chạy Services

#### Terminal 1: User Service

```bash
cd user-service
uvicorn main:app --port 8001 --reload
```

Swagger UI: http://localhost:8001/docs

#### Terminal 2: Order Service

```bash
cd order-service
uvicorn main:app --port 8002 --reload
```

Swagger UI: http://localhost:8002/docs

### 5. Cấu hình và Chạy Nginx

#### Cách 1: Dùng Nginx đã cài trên Windows

1. Tìm thư mục cài đặt Nginx (thường là `C:\nginx` hoặc `C:\Program Files\nginx`)

2. Copy file `nginx/nginx.conf` và thay thế file config mặc định, hoặc:

   - Tạo thư mục `logs` trong thư mục nginx
   - Chỉnh sửa `nginx.conf` để sử dụng đường dẫn tuyệt đối nếu cần

3. Test cấu hình:
   ```bash
   nginx -t -c path/to/nginx.conf
   ```

4. Chạy Nginx:
   ```bash
   nginx -c path/to/nginx.conf
   ```

#### Cách 2: Dùng Nginx từ nginx.org

1. Download Nginx for Windows: http://nginx.org/en/download.html

2. Extract và chạy `nginx.exe`

3. Copy `nginx.conf` của bạn vào thư mục `conf` của Nginx

## API Endpoints

Tất cả requests đều gửi qua Nginx (port 8080):

### User Service

- `GET http://localhost:8080/api/users` - Lấy danh sách users
- `POST http://localhost:8080/api/users` - Tạo user mới

**Body cho POST /api/users:**
```json
{
  "name": "John Doe",
  "email": "john@example.com"
}
```

### Order Service

- `GET http://localhost:8080/api/orders` - Lấy danh sách orders
- `POST http://localhost:8080/api/orders` - Tạo order mới

**Body cho POST /api/orders:**
```json
{
  "user_id": 1,
  "product": "Laptop",
  "amount": 1000
}
```

## Testing với Postman/Browser

### 1. Tạo User

```bash
POST http://localhost:8080/api/users
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com"
}
```

### 2. Lấy danh sách Users

```bash
GET http://localhost:8080/api/users
```

### 3. Tạo Order

```bash
POST http://localhost:8080/api/orders
Content-Type: application/json

{
  "user_id": 1,
  "product": "Laptop",
  "amount": 1000
}
```

### 4. Lấy danh sách Orders

```bash
GET http://localhost:8080/api/orders
```

## Kiểm tra trạng thái Services

- User Service: http://localhost:8001/
- Order Service: http://localhost:8002/
- Nginx: http://localhost:8080/

## Lưu ý

- Client **chỉ giao tiếp qua Nginx** (port 8080), không cần biết port 8001/8002
- Mỗi service có Swagger UI riêng tại `/docs` khi truy cập trực tiếp
- Database được dùng chung cho demo (không phải best practice cho production)

## Troubleshooting

### Lỗi kết nối MySQL

- Kiểm tra MySQL đang chạy
- Kiểm tra username/password trong `database.py`
- Kiểm tra database `microservice_demo` đã được tạo

### Lỗi Nginx

- Kiểm tra port 8080 không bị chiếm
- Kiểm tra file config: `nginx -t`
- Kiểm tra logs trong thư mục `logs/`

### Lỗi import Python

- Đảm bảo đã cài đủ dependencies: `pip install -r requirements.txt`
- Chạy từ đúng thư mục service (user-service hoặc order-service)

---

## 🚀 Phase 2: Nâng cấp với DB Riêng + Service Communication + Load Balancing

Đây là **Phase 1** với shared database. Để nâng cấp lên **Phase 2** với:

- ✅ Database riêng biệt cho mỗi service (`user_db`, `order_db`)
- ✅ Service-to-service communication (Order Service gọi User Service qua HTTP)
- ✅ Nginx Load Balancing (nhiều instances của User Service)
- ✅ Rate Limiting (10 requests/second)

Xem hướng dẫn chi tiết tại: **[README_PHASE2.md](README_PHASE2.md)**

### Quick Start Phase 2

1. Tạo databases: `mysql -u root -p < database_schema_phase2.sql`
2. Cập nhật database configs (đã được update sẵn)
3. Cài dependencies: `pip install -r requirements.txt` (order-service)
4. Chạy 2 instances User Service (port 8001, 8003)
5. Chạy Order Service (port 8002)
6. Cấu hình Nginx với load balancing (đã update trong `nginx/nginx.conf`)

Chi tiết đầy đủ xem [README_PHASE2.md](README_PHASE2.md)

