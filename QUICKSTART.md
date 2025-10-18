# Quick Start Guide

⚡ Get started in 3 minutes!

## Prerequisites
- Python 3.8+ installed
- A Telegram bot token (get from [@BotFather](https://t.me/BotFather))
- A Telegram channel where the bot is an admin

## Installation

### Step 1: Get the code
```bash
git clone https://github.com/lkanghee366/hii.git
cd hii
```

### Step 2: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure
```bash
# Set your credentials (replace with actual values)
export TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
export TELEGRAM_CHANNEL_ID="@yourchannel"
```

### Step 4: Run
```bash
python upload_tele.py
```

That's it! 🎉

## First Test

In another terminal, create a test image:

```bash
# Create output folder if not exists
mkdir -p output

# Copy or download an image
wget -O output/test.jpg https://picsum.photos/400/300

# Or if you have an image:
cp /path/to/your/image.jpg output/
```

Check your Telegram channel - the image should appear! 📸

## What Happens?

1. The script monitors the `output` folder
2. When you add an image file, it's automatically detected
3. The image is uploaded to your Telegram channel
4. Logs appear in console and `upload_tele.log`

## Common Issues

### "TELEGRAM_BOT_TOKEN is not set"
```bash
export TELEGRAM_BOT_TOKEN="your_actual_token"
```

### "Telegram error: Forbidden"
- Make sure the bot is added to your channel
- Make sure the bot has admin rights to post messages

### "Channel ID format"
- Username format: `@yourchannel`
- Numeric ID format: `-100123456789`

## Next Steps

- Read [README.md](README.md) for detailed Vietnamese documentation
- See [RUNPOD_GUIDE.md](RUNPOD_GUIDE.md) for RunPod deployment
- See [DOCKER_GUIDE.md](DOCKER_GUIDE.md) for Docker deployment

## Need Help?

Check the logs:
```bash
tail -f upload_tele.log
```

## Supported Image Formats

✅ JPG/JPEG
✅ PNG
✅ GIF
✅ BMP
✅ WEBP
✅ TIFF
✅ ICO

Happy uploading! 🚀
