# Docker Deployment Guide

## Using Docker

### Build the Docker Image
```bash
docker build -t telegram-uploader .
```

### Run with Docker
```bash
docker run -d \
  --name telegram-uploader \
  -e TELEGRAM_BOT_TOKEN="your_token" \
  -e TELEGRAM_CHANNEL_ID="@yourchannel" \
  -v $(pwd)/output:/app/output \
  telegram-uploader
```

### Run with Docker Compose

1. Create a `.env` file:
```bash
cp .env.example .env
# Edit .env with your credentials
```

2. Start the service:
```bash
docker-compose up -d
```

3. Check logs:
```bash
docker-compose logs -f
```

4. Stop the service:
```bash
docker-compose down
```

### Docker Commands

#### View logs
```bash
docker logs -f telegram-uploader
```

#### Stop container
```bash
docker stop telegram-uploader
```

#### Start container
```bash
docker start telegram-uploader
```

#### Restart container
```bash
docker restart telegram-uploader
```

#### Remove container
```bash
docker rm -f telegram-uploader
```

### Volume Mounting

The output folder is mounted as a volume, so you can:

1. **Add images from host:**
```bash
cp /path/to/image.jpg output/
```

2. **Generate images from another container:**
```bash
# Mount the same volume in your image generation container
docker run -v $(pwd)/output:/output your-image-gen-container
```

### Environment Variables

All environment variables can be passed via `-e` flag:

```bash
docker run -d \
  --name telegram-uploader \
  -e TELEGRAM_BOT_TOKEN="123456:ABC..." \
  -e TELEGRAM_CHANNEL_ID="@channel" \
  -e OUTPUT_FOLDER="/app/output" \
  -e CHECK_INTERVAL="10" \
  -v $(pwd)/output:/app/output \
  telegram-uploader
```

## Using with RunPod and Docker

On RunPod, you can use Docker to run this service:

```bash
# Build the image
docker build -t telegram-uploader .

# Run on RunPod
docker run -d \
  --name telegram-uploader \
  -e TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN" \
  -e TELEGRAM_CHANNEL_ID="$TELEGRAM_CHANNEL_ID" \
  -v /workspace/output:/app/output \
  telegram-uploader
```

## Multi-Container Setup

If you're running multiple services (e.g., Stable Diffusion + Uploader):

```yaml
version: '3.8'

services:
  stable-diffusion:
    image: your-sd-image
    volumes:
      - shared-output:/output

  telegram-uploader:
    build: .
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - TELEGRAM_CHANNEL_ID=${TELEGRAM_CHANNEL_ID}
    volumes:
      - shared-output:/app/output

volumes:
  shared-output:
```

Run with:
```bash
docker-compose up -d
```
