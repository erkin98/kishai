"""Encryption utilities for sensitive data"""
from cryptography.fernet import Fernet
from typing import Optional


class EncryptionService:
    """Service for encrypting and decrypting sensitive data"""
    
    def __init__(self, key: Optional[str] = None):
        """
        Initialize encryption service
        
        Args:
            key: Base64-encoded encryption key. If None, generates a new one.
        """
        if key:
            self.key = key.encode()
        else:
            self.key = Fernet.generate_key()
        
        self.fernet = Fernet(self.key)
    
    def encrypt(self, data: str) -> str:
        """
        Encrypt a string
        
        Args:
            data: String to encrypt
            
        Returns:
            Encrypted string (base64-encoded)
        """
        encrypted = self.fernet.encrypt(data.encode())
        return encrypted.decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt a string
        
        Args:
            encrypted_data: Encrypted string (base64-encoded)
            
        Returns:
            Decrypted string
        """
        decrypted = self.fernet.decrypt(encrypted_data.encode())
        return decrypted.decode()
    
    def get_key(self) -> str:
        """Get the encryption key as a string"""
        return self.key.decode()


# Global encryption service instance
_encryption_service: Optional[EncryptionService] = None


def get_encryption_service(key: Optional[str] = None) -> EncryptionService:
    """
    Get or create the global encryption service
    
    Args:
        key: Encryption key. If provided, creates a new service with this key.
        
    Returns:
        EncryptionService instance
    """
    global _encryption_service
    
    if _encryption_service is None or key is not None:
        _encryption_service = EncryptionService(key)
    
    return _encryption_service

