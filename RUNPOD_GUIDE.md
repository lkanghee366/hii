# RunPod Deployment Guide

## Quick Setup on RunPod

### 1. Clone Repository
```bash
# Clone the repository (replace with your actual repo URL)
git clone https://github.com/lkanghee366/hii.git
cd hii
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
# Set your Telegram credentials
export TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
export TELEGRAM_CHANNEL_ID="@yourchannel"  # or -100123456789

# Optional: customize output folder and check interval
export OUTPUT_FOLDER="output"
export CHECK_INTERVAL="5"
```

### 4. Run the Service

#### Option A: Foreground (for testing)
```bash
python upload_tele.py
```

#### Option B: Background with nohup
```bash
nohup python upload_tele.py > upload.log 2>&1 &
echo $! > upload_tele.pid
```

#### Option C: With screen/tmux (recommended)
```bash
# Using screen
screen -S telegram_upload
python upload_tele.py
# Press Ctrl+A, D to detach

# To reattach later
screen -r telegram_upload

# Using tmux
tmux new -s telegram_upload
python upload_tele.py
# Press Ctrl+B, D to detach

# To reattach later
tmux attach -t telegram_upload
```

### 5. Test the Service
```bash
# In another terminal, create a test image
mkdir -p output
echo "Test" > output/test.txt  # Will be ignored
touch output/test.jpg  # Will be uploaded

# Or download a real image
wget -O output/sample.jpg https://picsum.photos/400/300
```

### 6. Check Logs
```bash
# Real-time log monitoring
tail -f upload_tele.log

# Or if using nohup
tail -f upload.log
```

### 7. Stop the Service
```bash
# If using nohup
kill $(cat upload_tele.pid)
rm upload_tele.pid

# If using screen
screen -S telegram_upload -X quit

# If using tmux
tmux kill-session -t telegram_upload
```

## RunPod-Specific Tips

### Persistent Storage
Make sure your output folder is on persistent storage (e.g., `/workspace/output`) to survive pod restarts:

```bash
export OUTPUT_FOLDER="/workspace/output"
python upload_tele.py
```

### Auto-start on Pod Launch
Add to your RunPod startup script:

```bash
#!/bin/bash
# Navigate to your cloned repository directory
cd /workspace/hii  # Adjust path to match your setup
export TELEGRAM_BOT_TOKEN="your_token"
export TELEGRAM_CHANNEL_ID="@yourchannel"
nohup python upload_tele.py > /workspace/upload.log 2>&1 &
```

### Environment Variables in RunPod
Set environment variables in RunPod's pod configuration:
- `TELEGRAM_BOT_TOKEN=123456789:ABC...`
- `TELEGRAM_CHANNEL_ID=@yourchannel`
- `OUTPUT_FOLDER=/workspace/output`

### Monitor GPU Workloads
If you're generating images with AI models, you can monitor both:

```bash
# Terminal 1: Run your image generation
python your_stable_diffusion_script.py

# Terminal 2: Run the uploader
python upload_tele.py
```

The uploader will automatically detect and upload new images as they're generated!

## Troubleshooting

### Port/Network Issues
RunPod should have outbound internet access by default. If you have issues:
- Check firewall settings
- Verify internet connectivity: `ping telegram.org`

### Dependencies Issues
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Permission Issues
```bash
chmod +x upload_tele.py
chmod 755 output/
```
