#!/usr/bin/env python3
"""
Telegram Image Upload Script for RunPod
Monitors the output folder and automatically uploads new images to a Telegram channel.
"""

import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Set
import asyncio

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileCreatedEvent
    from telegram import Bot
    from telegram.error import TelegramError
except ImportError:
    print("Error: Required packages not installed.")
    print("Please run: pip install python-telegram-bot watchdog")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('upload_tele.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Supported image formats
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.ico'}

# Configuration from environment variables
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')
OUTPUT_FOLDER = os.getenv('OUTPUT_FOLDER', 'output')
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '5'))  # seconds


class TelegramUploader:
    """Handles uploading images to Telegram channel"""
    
    def __init__(self, bot_token: str, channel_id: str):
        """
        Initialize Telegram uploader
        
        Args:
            bot_token: Telegram bot token
            channel_id: Telegram channel ID (e.g., @channelname or -100123456789)
        """
        if not bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN is not set")
        if not channel_id:
            raise ValueError("TELEGRAM_CHANNEL_ID is not set")
            
        self.bot = Bot(token=bot_token)
        self.channel_id = channel_id
        self.uploaded_files: Set[str] = set()
        
    async def upload_image(self, file_path: Path) -> bool:
        """
        Upload an image to Telegram channel
        
        Args:
            file_path: Path to the image file
            
        Returns:
            True if upload successful, False otherwise
        """
        file_path_str = str(file_path.absolute())
        
        # Skip if already uploaded
        if file_path_str in self.uploaded_files:
            logger.debug(f"File already uploaded: {file_path.name}")
            return False
            
        try:
            # Check if file exists and is readable
            if not file_path.exists():
                logger.warning(f"File not found: {file_path}")
                return False
                
            # Wait a bit to ensure file is fully written
            await asyncio.sleep(0.5)
            
            # Open and send the image
            with open(file_path, 'rb') as photo:
                caption = f"📸 {file_path.name}\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                await self.bot.send_photo(
                    chat_id=self.channel_id,
                    photo=photo,
                    caption=caption
                )
            
            self.uploaded_files.add(file_path_str)
            logger.info(f"✅ Successfully uploaded: {file_path.name}")
            return True
            
        except TelegramError as e:
            logger.error(f"❌ Telegram error uploading {file_path.name}: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error uploading {file_path.name}: {e}")
            return False


class ImageFileHandler(FileSystemEventHandler):
    """Handles file system events for new images"""
    
    def __init__(self, uploader: TelegramUploader):
        """
        Initialize file handler
        
        Args:
            uploader: TelegramUploader instance
        """
        super().__init__()
        self.uploader = uploader
        
    def on_created(self, event):
        """Handle file creation event"""
        if event.is_directory:
            return
            
        file_path = Path(event.src_path)
        
        # Check if it's an image file
        if file_path.suffix.lower() in IMAGE_EXTENSIONS:
            logger.info(f"🔍 New image detected: {file_path.name}")
            # Run upload in async context
            asyncio.run(self.uploader.upload_image(file_path))


async def scan_existing_files(output_folder: Path, uploader: TelegramUploader):
    """
    Scan and upload existing images in the output folder
    
    Args:
        output_folder: Path to output folder
        uploader: TelegramUploader instance
    """
    logger.info(f"📂 Scanning existing files in {output_folder}")
    
    if not output_folder.exists():
        logger.warning(f"Output folder does not exist: {output_folder}")
        return
        
    image_files = []
    for ext in IMAGE_EXTENSIONS:
        image_files.extend(output_folder.glob(f"*{ext}"))
        image_files.extend(output_folder.glob(f"*{ext.upper()}"))
    
    # Sort by modification time
    image_files.sort(key=lambda x: x.stat().st_mtime)
    
    logger.info(f"Found {len(image_files)} existing image(s)")
    
    for file_path in image_files:
        await uploader.upload_image(file_path)
        # Small delay between uploads to avoid rate limiting
        await asyncio.sleep(1)


def main():
    """Main function to start the monitoring service"""
    logger.info("=" * 60)
    logger.info("🚀 Telegram Image Upload Service Starting...")
    logger.info("=" * 60)
    
    # Validate configuration
    if not TELEGRAM_BOT_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN environment variable is not set")
        logger.error("Please set it with: export TELEGRAM_BOT_TOKEN='your_bot_token'")
        sys.exit(1)
        
    if not TELEGRAM_CHANNEL_ID:
        logger.error("❌ TELEGRAM_CHANNEL_ID environment variable is not set")
        logger.error("Please set it with: export TELEGRAM_CHANNEL_ID='@yourchannel' or '-100123456789'")
        sys.exit(1)
    
    # Create output folder if it doesn't exist
    output_folder = Path(OUTPUT_FOLDER)
    if not output_folder.exists():
        logger.info(f"📁 Creating output folder: {output_folder}")
        output_folder.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"📁 Monitoring folder: {output_folder.absolute()}")
    logger.info(f"🤖 Bot token: {TELEGRAM_BOT_TOKEN[:10]}...{TELEGRAM_BOT_TOKEN[-4:]}")
    logger.info(f"📢 Channel ID: {TELEGRAM_CHANNEL_ID}")
    logger.info(f"⏱️  Check interval: {CHECK_INTERVAL}s")
    
    try:
        # Initialize uploader
        uploader = TelegramUploader(TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID)
        
        # Test bot connection
        logger.info("🔌 Testing Telegram bot connection...")
        try:
            bot_info = asyncio.run(uploader.bot.get_me())
            logger.info(f"✅ Connected as: @{bot_info.username}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Telegram: {e}")
            sys.exit(1)
        
        # Upload existing files first
        asyncio.run(scan_existing_files(output_folder, uploader))
        
        # Set up file system monitoring
        event_handler = ImageFileHandler(uploader)
        observer = Observer()
        observer.schedule(event_handler, str(output_folder.absolute()), recursive=False)
        observer.start()
        
        logger.info("👀 Watching for new images...")
        logger.info("Press Ctrl+C to stop")
        
        try:
            while True:
                time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            logger.info("\n🛑 Stopping monitoring service...")
            observer.stop()
            
        observer.join()
        logger.info("👋 Service stopped")
        
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
