# Microservice Demo - Phase 2: DB Riêng + Service Communication + Nginx Advanced

## 🎯 Kiến trúc Phase 2

```
Client
   |
   | HTTP :8080
   v
Nginx (API Gateway)
   |  [Rate Limit: 10 req/s]
   |  [Load Balancing]
   |
   |--> User Service Instance 1 (port 8001) --> user_db
   |
   |--> User Service Instance 2 (port 8003) --> user_db
   |
   |--> Order Service (port 8002) --> order_db
              |
              | HTTP Call
              v
         User Service (qua Nginx hoặc trực tiếp)
```

## 📋 Khác biệt Phase 2 vs Phase 1

| Tính năng | Phase 1 | Phase 2 |
|-----------|---------|---------|
| Database | Shared (`microservice_demo`) | Riêng biệt (`user_db`, `order_db`) |
| Service Communication | Không | Order Service gọi User Service qua HTTP |
| Load Balancing | Không | Nginx load balance User Service |
| Rate Limiting | Không | 10 requests/second |
| Database Access | Order Service query trực tiếp `users` table | Order Service gọi User Service API |

## 🗄️ Database Schema Phase 2

### Database: `user_db` (User Service)
```sql
CREATE DATABASE user_db;
CREATE TABLE users (id, name, email);
```

### Database: `order_db` (Order Service)
```sql
CREATE DATABASE order_db;
CREATE TABLE orders (id, user_id, product, amount);
-- Note: NO foreign key constraint
```

## 🚀 Hướng dẫn thiết lập Phase 2

### 1. Tạo Databases

Chạy script:
```bash
mysql -u root -p < database_schema_phase2.sql
```

Hoặc thủ công:
```sql
-- Tạo user_db
CREATE DATABASE IF NOT EXISTS user_db;
USE user_db;
CREATE TABLE users (id INT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(255), email VARCHAR(255));

-- Tạo order_db
CREATE DATABASE IF NOT EXISTS order_db;
USE order_db;
CREATE TABLE orders (id INT PRIMARY KEY AUTO_INCREMENT, user_id INT, product VARCHAR(255), amount INT);
```

### 2. Cập nhật Database Configuration

**user-service/database.py** - Đã được cập nhật để dùng `user_db`:
```python
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:12345@localhost:3306/user_db"
```

**order-service/database.py** - Đã được cập nhật để dùng `order_db`:
```python
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:12345@localhost:3306/order_db"
```

### 3. Cài đặt Dependencies

**Order Service cần thêm httpx:**
```bash
cd order-service
pip install -r requirements.txt  # httpx đã được thêm vào
```

### 4. Chạy Services

#### Terminal 1: User Service Instance 1
```bash
cd user-service
uvicorn main:app --port 8001 --reload
```

#### Terminal 2: User Service Instance 2 (Cho Load Balancing)
```bash
cd user-service
uvicorn main:app --port 8003 --reload
```

#### Terminal 3: Order Service
```bash
cd order-service
uvicorn main:app --port 8002 --reload
```

**Lưu ý:** Order Service sẽ gọi User Service tại `http://localhost:8001` (mặc định). Có thể thay đổi qua environment variable:
```bash
set USER_SERVICE_URL=http://localhost:8080/api/users
```

### 5. Cấu hình Nginx Phase 2

File `nginx/nginx.conf` đã được cập nhật với:

#### Load Balancing
```nginx
upstream user_service {
    least_conn;  # Phân tải theo số kết nối ít nhất
    server localhost:8001;
    server localhost:8003;  # Instance thứ 2
}
```

#### Rate Limiting
```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
limit_req zone=api_limit burst=20 nodelay;
```

Khởi động Nginx:
```bash
nginx -c path/to/nginx/nginx.conf
```

## 🧪 Testing Phase 2

### 1. Test Database Separation

**Tạo user qua API:**
```bash
POST http://localhost:8080/api/users
{
  "name": "John Doe",
  "email": "john@example.com"
}
```

**Kiểm tra user trong user_db:**
```sql
USE user_db;
SELECT * FROM users;
```

**Kiểm tra order_db (KHÔNG có bảng users):**
```sql
USE order_db;
SHOW TABLES;  -- Chỉ có bảng orders
```

### 2. Test Service Communication

**Tạo order (Order Service sẽ gọi User Service để verify):**
```bash
POST http://localhost:8080/api/orders
{
  "user_id": 1,
  "product": "Laptop",
  "amount": 1000
}
```

**Kết quả mong đợi:**
- ✅ Nếu user_id=1 tồn tại → Order được tạo
- ❌ Nếu user_id=999 không tồn tại → 404 "User not found"
- ❌ Nếu User Service down → 503 "User service unavailable"

### 3. Test Load Balancing

**Chạy nhiều requests liên tiếp:**
```bash
# Chạy 10 requests
for i in {1..10}; do curl http://localhost:8080/api/users; done
```

**Kiểm tra logs của cả 2 User Service instances:**
- Requests sẽ được phân tải giữa port 8001 và 8003
- Dùng `least_conn` nên instance có ít kết nối hơn sẽ nhận request

### 4. Test Rate Limiting

**Gửi nhiều requests nhanh (PowerShell):**
```powershell
1..30 | ForEach-Object { Invoke-WebRequest -Uri "http://localhost:8080/api/users" -UseBasicParsing }
```

**Kết quả:**
- 10 requests đầu: ✅ 200 OK
- Requests tiếp theo (burst=20): ✅ Có thể xử lý
- Vượt quá limit: ❌ 503 Too Many Requests

### 5. Test Order Service → User Service Call

**Kiểm tra logs Order Service:**
- Khi tạo order, Order Service sẽ gọi User Service API
- Xem network requests hoặc logs để verify

## ✅ Acceptance Criteria Phase 2

- [x] User DB & Order DB tách biệt
- [x] Order Service KHÔNG truy cập User DB
- [x] Order Service gọi User Service qua HTTP
- [x] User Service chạy nhiều instance (8001, 8003)
- [x] Nginx phân tải request
- [x] Rate limit hoạt động (10 req/s)
- [x] Client chỉ gọi qua :8080

## 🔍 Monitoring & Debugging

### Kiểm tra Load Balancing
```bash
# Xem logs của từng User Service instance
# Requests sẽ phân bổ giữa 8001 và 8003
```

### Kiểm tra Service Communication
```bash
# Order Service logs sẽ show HTTP calls đến User Service
# Hoặc dùng network monitoring tools
```

### Kiểm tra Rate Limit
```bash
# Xem Nginx error logs: logs/error.log
# Rate limited requests sẽ được log
```

## 📝 Configuration

### Environment Variables

**Order Service:**
- `USER_SERVICE_URL`: URL của User Service (default: `http://localhost:8001`)
  - Direct: `http://localhost:8001`
  - Via Nginx: `http://localhost:8080/api/users`

### Nginx Configuration

**Rate Limit Settings:**
- `rate=10r/s`: 10 requests per second
- `burst=20`: Cho phép burst 20 requests
- `nodelay`: Không delay requests trong burst

**Load Balancing Method:**
- `least_conn`: Phân tải theo số kết nối ít nhất

## 🐛 Troubleshooting

### Order Service không gọi được User Service

**Kiểm tra:**
1. User Service có đang chạy không?
2. `USER_SERVICE_URL` có đúng không?
3. Firewall có block connection không?

**Test trực tiếp:**
```bash
curl http://localhost:8001/users
```

### Load Balancing không hoạt động

**Kiểm tra:**
1. Cả 2 User Service instances đã start?
2. Nginx config có đúng upstream?
3. Test: gửi nhiều requests và xem logs

### Rate Limit quá strict

**Điều chỉnh trong nginx.conf:**
```nginx
rate=10r/s    # Giảm hoặc tăng
burst=20      # Tăng burst limit
```

## 🔄 Migration từ Phase 1

Nếu bạn đã có data ở Phase 1:

1. Export data từ `microservice_demo.users`:
```sql
mysqldump -u root -p microservice_demo users > users_backup.sql
```

2. Import vào `user_db`:
```sql
mysql -u root -p user_db < users_backup.sql
```

3. Export orders:
```sql
mysqldump -u root -p microservice_demo orders > orders_backup.sql
mysql -u root -p order_db < orders_backup.sql
```

---

**Phase 2 hoàn thành!** 🎉

Hệ thống hiện có:
- Database tách biệt theo service
- Service-to-service communication
- Load balancing
- Rate limiting

