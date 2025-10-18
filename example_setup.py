#!/usr/bin/env python3
"""
Example usage of upload_tele.py
This script demonstrates how to set up and use the Telegram uploader
"""

import os
import time
from pathlib import Path

def setup_example():
    """Set up example environment"""
    print("=" * 60)
    print("Telegram Upload Service - Example Setup")
    print("=" * 60)
    
    # Create output folder
    output_folder = Path("output")
    if not output_folder.exists():
        output_folder.mkdir(parents=True)
        print(f"✅ Created output folder: {output_folder.absolute()}")
    else:
        print(f"✅ Output folder exists: {output_folder.absolute()}")
    
    # Check for .env file
    env_file = Path(".env")
    if not env_file.exists():
        print("\n⚠️  .env file not found!")
        print("📝 Steps to set up:")
        print("   1. Copy .env.example to .env")
        print("      cp .env.example .env")
        print("   2. Edit .env and add your credentials:")
        print("      - TELEGRAM_BOT_TOKEN (from @BotFather)")
        print("      - TELEGRAM_CHANNEL_ID (your channel ID or @username)")
        print("\n   OR set environment variables directly:")
        print('      export TELEGRAM_BOT_TOKEN="your_token"')
        print('      export TELEGRAM_CHANNEL_ID="@yourchannel"')
    else:
        print(f"✅ .env file exists: {env_file.absolute()}")
        print("   Make sure to configure your bot token and channel ID")
    
    # Show example images that could be created
    print("\n📸 To test the uploader:")
    print("   1. Make sure you've configured your Telegram bot")
    print("   2. Run: python upload_tele.py")
    print("   3. Create/copy image files to the 'output' folder")
    print("   4. Watch the console for upload notifications")
    
    print("\n💡 Example: Create a test image")
    print("   # Using PIL (if installed)")
    print("   python -c \"from PIL import Image; img=Image.new('RGB', (400,300), 'blue'); img.save('output/test.png')\"")
    print("\n   # Or simply copy an image:")
    print("   cp /path/to/your/image.jpg output/")
    
    print("\n🔍 Supported formats:")
    print("   JPG, JPEG, PNG, GIF, BMP, WEBP, TIFF, ICO")
    
    print("\n" + "=" * 60)
    print("Ready to start!")
    print("=" * 60)

if __name__ == "__main__":
    setup_example()
