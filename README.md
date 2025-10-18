# Telegram Image Upload Service

Tự động upload ảnh từ folder `output` lên Telegram channel. Script này được thiết kế để chạy trên RunPod và tự động phát hiện file mới được tạo.

## Tính năng

- ✅ Tự động giám sát folder `output` để phát hiện ảnh mới
- ✅ Upload ảnh lên Telegram channel thông qua Bot API
- ✅ Hỗ trợ nhiều định dạng ảnh: JPG, PNG, GIF, BMP, WEBP, TIFF, ICO
- ✅ Tự động upload các ảnh có sẵn khi khởi động
- ✅ Logging chi tiết để debug
- ✅ Xử lý lỗi và retry tự động
- ✅ Không upload trùng file

## Cài đặt

### 1. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 2. Tạo Telegram Bot

1. Mở Telegram và tìm [@BotFather](https://t.me/BotFather)
2. Gửi lệnh `/newbot` và làm theo hướng dẫn
3. Lưu lại **bot token** (format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
4. Thêm bot vào channel của bạn với quyền post messages

### 3. Lấy Channel ID

**Cách 1: Sử dụng username**
- Nếu channel có username public: `@yourchannel`

**Cách 2: Lấy ID số**
1. Thêm bot [@userinfobot](https://t.me/userinfobot) vào channel
2. Forward một message từ channel đến @userinfobot
3. Lưu ID (format: `-100123456789`)

### 4. Cấu hình

Tạo file `.env` từ template:

```bash
cp .env.example .env
```

Sửa file `.env` với thông tin của bạn:

```env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHANNEL_ID=@yourchannel
OUTPUT_FOLDER=output
CHECK_INTERVAL=5
```

**Hoặc** export trực tiếp environment variables:

```bash
export TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
export TELEGRAM_CHANNEL_ID="@yourchannel"
export OUTPUT_FOLDER="output"
export CHECK_INTERVAL="5"
```

## Sử dụng

### Chạy script

```bash
python upload_tele.py
```

### Chạy trên RunPod

**1. Tạo container với script này:**

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export TELEGRAM_BOT_TOKEN="your_token"
export TELEGRAM_CHANNEL_ID="@yourchannel"

# Run the service
python upload_tele.py
```

**2. Chạy trong background (nohup):**

```bash
nohup python upload_tele.py > upload.log 2>&1 &
```

**3. Chạy với screen/tmux:**

```bash
screen -S telegram_upload
python upload_tele.py
# Press Ctrl+A, D to detach
```

**4. Kiểm tra log:**

```bash
tail -f upload_tele.log
```

## Cách hoạt động

1. **Khởi động**: Script sẽ scan tất cả ảnh có sẵn trong folder `output` và upload lên channel
2. **Giám sát**: Sử dụng `watchdog` để theo dõi file system events
3. **Upload tự động**: Khi có file ảnh mới được tạo, script sẽ tự động upload
4. **Không trùng lặp**: Script lưu danh sách file đã upload để tránh upload trùng

## Định dạng ảnh được hỗ trợ

- `.jpg`, `.jpeg`
- `.png`
- `.gif`
- `.bmp`
- `.webp`
- `.tiff`
- `.ico`

## Logs

Script tạo 2 loại logs:
- **Console output**: Hiển thị trên terminal
- **File log**: Lưu vào `upload_tele.log`

Format log:
```
2025-10-18 01:27:34 - __main__ - INFO - 🚀 Telegram Image Upload Service Starting...
2025-10-18 01:27:35 - __main__ - INFO - ✅ Connected as: @your_bot_name
2025-10-18 01:27:36 - __main__ - INFO - 🔍 New image detected: image.png
2025-10-18 01:27:37 - __main__ - INFO - ✅ Successfully uploaded: image.png
```

## Troubleshooting

### Bot không upload được

1. Kiểm tra bot đã được thêm vào channel chưa
2. Kiểm tra bot có quyền post messages
3. Kiểm tra channel ID có đúng format không

### File không được detect

1. Kiểm tra `OUTPUT_FOLDER` path có đúng không
2. Kiểm tra file extension có trong danh sách hỗ trợ không
3. Kiểm tra permissions của folder

### Rate limit errors

- Telegram giới hạn số lượng messages/giây
- Script có delay 1s giữa các uploads
- Nếu cần upload nhiều ảnh, hãy tăng delay

## Environment Variables

| Variable | Mô tả | Default | Bắt buộc |
|----------|-------|---------|----------|
| `TELEGRAM_BOT_TOKEN` | Token từ @BotFather | - | ✅ |
| `TELEGRAM_CHANNEL_ID` | ID hoặc @username của channel | - | ✅ |
| `OUTPUT_FOLDER` | Folder chứa ảnh cần upload | `output` | ❌ |
| `CHECK_INTERVAL` | Interval kiểm tra (seconds) | `5` | ❌ |

## Ví dụ

### Upload ảnh từ folder khác

```bash
export OUTPUT_FOLDER="/path/to/images"
python upload_tele.py
```

### Chạy với custom check interval

```bash
export CHECK_INTERVAL="10"
python upload_tele.py
```

## License

MIT License
