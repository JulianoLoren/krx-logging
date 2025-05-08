# Dịch vụ Logging KRX

Dịch vụ này giám sát và ghi log dữ liệu KRX (Sở Giao dịch Hàn Quốc) sử dụng giao thức MQTT.

## Yêu cầu

- Docker và Docker Compose
- Python 3.x

## Cài đặt

1. Sao chép file `.env.example` để tạo file `.env`:
   ```bash
   cp .env.example .env
   ```

2. Chỉnh sửa file `.env` và thay thế các giá trị placeholder bằng thông tin thực tế của bạn:
   - `KRX_USERNAME`: Tên đăng nhập KRX của bạn
   - `KRX_PASSWORD`: Mật khẩu KRX của bạn
   - `KRX_TOPICS`: Danh sách các topic cần theo dõi, được phân cách bằng dấu chấm phẩy (;)
     - `plaintext/quotes/krx/mdds/tick/v1/roundlot/symbol/+`: All ticks
     - `plaintext/quotes/krx/mdds/v2/ohlc/stock/1/+`: Stock OHLC 1min
     - `plaintext/quotes/krx/mdds/v2/ohlc/stock/1D/+`: Stock OHLC 1D
     - `plaintext/quotes/krx/mdds/v2/ohlc/derivative/1/+`: Derivative OHLC 1min
     - `plaintext/quotes/krx/mdds/v2/ohlc/derivative/1D/+`: Derivative OHLC 1D
     - `plaintext/quotes/krx/mdds/v2/ohlc/index/1/+`: Index OHLC 1min
     - `plaintext/quotes/krx/mdds/v2/ohlc/index/1D/+`: Index OHLC 1D
     - `plaintext/quotes/krx/mdds/index/+`: Index

## Chạy Dịch vụ

1. Xây dựng và khởi động dịch vụ:
   ```bash
   docker-compose down && docker-compose up --build -d
   ```

2. Dịch vụ sẽ:
   - Kết nối với KRX sử dụng thông tin đăng nhập đã cung cấp
   - Giám sát và ghi log dữ liệu
   - Lưu logs trong thư mục `logs`

## Hệ thống Log

- Logs được lưu trữ trong thư mục `logs`
- Log của container Docker được cấu hình với driver json-file
- Kích thước tối đa file log là 10MB với 3 file luân phiên

## Cấu trúc Dự án

- `check_socket_krx.py`: File dịch vụ chính
- `logs/`: Thư mục lưu trữ logs ứng dụng
- `.env`: Cấu hình biến môi trường
- `.env.example`: Mẫu cho biến môi trường
- `docker-compose.yml`: Cấu hình dịch vụ Docker

## Bảo mật

- Không bao giờ commit file `.env` vào version control
- Bảo mật thông tin đăng nhập của bạn
- Kiểm tra và cập nhật thông tin định kỳ

## Quản lý Topic

Để thêm hoặc bớt topic, bạn chỉ cần chỉnh sửa biến `KRX_TOPICS` trong file `.env`:

```bash
KRX_TOPICS=topic1;topic2;topic3
```

Mỗi topic được phân cách bằng dấu chấm phẩy (;). Bạn có thể thêm hoặc bớt topic tùy theo nhu cầu của mình.
