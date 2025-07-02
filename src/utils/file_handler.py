"""
File handling utilities with permission handling
"""
import os
import stat
import platform
from utils.logger import get_logger

def ensure_directories():
    """Ensure all required directories exist with proper permissions"""
    directories = [
        "data",
        "data/logs", 
        "data/temp"
    ]
    
    logger = get_logger(__name__)
    
    for directory in directories:
        try:
            # Create directory if it doesn't exist
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                logger.info(f"Created directory: {directory}")
            
            # Set proper permissions
            set_directory_permissions(directory)
            logger.debug(f"Set permissions for directory: {directory}")
            
        except Exception as e:
            logger.error(f"Failed to create/set permissions for directory {directory}: {e}")
            # Try alternative location
            try_alternative_location(directory, logger)

def set_directory_permissions(directory):
    """Set appropriate permissions for directory"""
    try:
        if platform.system() == "Windows":
            # On Windows, try to ensure write access
            os.chmod(directory, stat.S_IWRITE | stat.S_IREAD | stat.S_IEXEC)
        else:
            # On Unix-like systems
            os.chmod(directory, 0o755)
            
    except Exception as e:
        print(f"Warning: Could not set permissions for {directory}: {e}")

def try_alternative_location(original_dir, logger):
    """Try alternative location if original fails"""
    import tempfile
    import sys
    
    try:
        # Use temp directory as fallback
        temp_base = tempfile.gettempdir()
        alt_dir = os.path.join(temp_base, "wordpress_content_generator", original_dir)
        
        os.makedirs(alt_dir, exist_ok=True)
        
        # Update global data directory
        if hasattr(sys.modules[__name__], 'DATA_DIR'):
            sys.modules[__name__].DATA_DIR = alt_dir
        
        logger.warning(f"Using alternative location: {alt_dir}")
        return alt_dir
        
    except Exception as e:
        logger.error(f"Failed to create alternative location: {e}")
        raise

def get_data_dir() -> str:
    """Get data directory path"""
    # Check if alternative location is being used
    import tempfile
    alt_location = os.path.join(tempfile.gettempdir(), "wordpress_content_generator", "data")
    
    if os.path.exists(alt_location) and os.access(alt_location, os.W_OK):
        return alt_location
    
    return "data"

def test_write_permission(directory: str) -> bool:
    """Test if we can write to directory"""
    try:
        test_file = os.path.join(directory, "test_write.tmp")
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        return True
    except:
        return False