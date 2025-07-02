"""
Encryption utilities for storing sensitive data
"""
from cryptography.fernet import Fernet
import base64
import os
import tempfile
from utils.logger import get_logger

class EncryptionManager:
    def __init__(self, data_dir=None):
        if data_dir is None:
            data_dir = "data"
        
        self.key_file = os.path.join(data_dir, ".encryption_key")
        self.logger = get_logger(__name__)
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        self.key = self._get_or_create_key()
        self.cipher = Fernet(self.key)
    
    def _get_or_create_key(self) -> bytes:
        """Get existing key or create new one"""
        try:
            if os.path.exists(self.key_file):
                with open(self.key_file, 'rb') as f:
                    key = f.read()
                self.logger.info("Loaded existing encryption key")
            else:
                key = Fernet.generate_key()
                
                # Try to write to the key file
                try:
                    with open(self.key_file, 'wb') as f:
                        f.write(key)
                    
                    # Hide the key file on Windows
                    if os.name == 'nt':
                        try:
                            import ctypes
                            ctypes.windll.kernel32.SetFileAttributesW(self.key_file, 2)  # Hidden
                        except:
                            pass
                    
                    self.logger.info("Generated new encryption key")
                    
                except PermissionError:
                    # If we can't write to the intended location, use temp
                    temp_key_file = os.path.join(tempfile.gettempdir(), "wp_gen_key")
                    with open(temp_key_file, 'wb') as f:
                        f.write(key)
                    self.key_file = temp_key_file
                    self.logger.warning(f"Using temporary key file: {self.key_file}")
            
            return key
            
        except Exception as e:
            self.logger.error(f"Failed to get encryption key: {e}")
            raise
    
    # ... rest of the methods remain the same
    
    def encrypt(self, data: str) -> str:
        """Encrypt string data"""
        try:
            if not data:
                return ""
            
            encrypted_data = self.cipher.encrypt(data.encode('utf-8'))
            return base64.b64encode(encrypted_data).decode('utf-8')
            
        except Exception as e:
            self.logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt string data"""
        try:
            if not encrypted_data:
                return ""
            
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            decrypted_data = self.cipher.decrypt(encrypted_bytes)
            return decrypted_data.decode('utf-8')
            
        except Exception as e:
            self.logger.error(f"Decryption failed: {e}")
            raise