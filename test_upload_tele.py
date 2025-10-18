#!/usr/bin/env python3
"""
Test script for upload_tele.py
Tests the basic functionality without actually uploading to Telegram
"""

import os
import sys
import tempfile
from pathlib import Path
import shutil

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required imports are available"""
    print("Testing imports...")
    try:
        import upload_tele
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
        from telegram import Bot
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_image_extensions():
    """Test that image extensions are properly defined"""
    print("\nTesting image extensions...")
    import upload_tele
    
    expected_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.ico'}
    
    if upload_tele.IMAGE_EXTENSIONS == expected_extensions:
        print(f"✅ Image extensions correct: {upload_tele.IMAGE_EXTENSIONS}")
        return True
    else:
        print(f"❌ Image extensions mismatch")
        print(f"   Expected: {expected_extensions}")
        print(f"   Got: {upload_tele.IMAGE_EXTENSIONS}")
        return False

def test_configuration_validation():
    """Test configuration validation"""
    print("\nTesting configuration validation...")
    import upload_tele
    
    # Test with missing token
    try:
        uploader = upload_tele.TelegramUploader("", "test_channel")
        print("❌ Should have raised ValueError for empty token")
        return False
    except ValueError as e:
        print(f"✅ Correctly raised ValueError for empty token: {e}")
    
    # Test with missing channel
    try:
        uploader = upload_tele.TelegramUploader("test_token", "")
        print("❌ Should have raised ValueError for empty channel")
        return False
    except ValueError as e:
        print(f"✅ Correctly raised ValueError for empty channel: {e}")
    
    return True

def test_file_detection():
    """Test file detection logic"""
    print("\nTesting file detection...")
    import upload_tele
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # Create test files
        image_files = [
            tmppath / "test1.jpg",
            tmppath / "test2.png",
            tmppath / "test3.gif",
            tmppath / "test4.JPG",  # uppercase
        ]
        
        non_image_files = [
            tmppath / "test.txt",
            tmppath / "test.pdf",
            tmppath / "test.doc",
        ]
        
        # Create the files
        for f in image_files + non_image_files:
            f.write_text("test content")
        
        # Test detection
        detected_images = []
        for ext in upload_tele.IMAGE_EXTENSIONS:
            detected_images.extend(tmppath.glob(f"*{ext}"))
            detected_images.extend(tmppath.glob(f"*{ext.upper()}"))
        
        if len(detected_images) >= len(image_files):
            print(f"✅ Detected {len(detected_images)} image files")
            return True
        else:
            print(f"❌ Only detected {len(detected_images)} of {len(image_files)} image files")
            return False

def test_script_help():
    """Test that script can show basic info"""
    print("\nTesting script execution (dry run)...")
    import upload_tele
    
    # Check that constants are defined
    assert hasattr(upload_tele, 'TELEGRAM_BOT_TOKEN')
    assert hasattr(upload_tele, 'TELEGRAM_CHANNEL_ID')
    assert hasattr(upload_tele, 'OUTPUT_FOLDER')
    assert hasattr(upload_tele, 'CHECK_INTERVAL')
    
    print("✅ All configuration constants are defined")
    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("Running tests for upload_tele.py")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_image_extensions,
        test_configuration_validation,
        test_file_detection,
        test_script_help,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed!")
        return 0
    else:
        print(f"❌ {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
