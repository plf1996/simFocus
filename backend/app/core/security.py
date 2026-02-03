from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64
import os
from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password

    Note: bcrypt has a maximum password length of 72 bytes.
    Passwords longer than this will be truncated.
    """
    # Truncate password to 72 bytes (bcrypt limit)
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        # Truncate to 72 bytes
        password = password_bytes[:72].decode('utf-8', errors='ignore')
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode a JWT access token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


class APIKeyEncryption:
    """API Key encryption using AES-256-GCM"""

    def __init__(self, key: bytes = None):
        """
        Initialize encryption with 32-byte key
        If no key provided, use from settings
        """
        if key is None:
            raw_key = settings.ENCRYPTION_KEY.encode('utf-8')
            # Ensure exactly 32 bytes (take first 32 or pad if needed)
            if len(raw_key) >= 32:
                key = raw_key[:32]
            else:
                # Pad with zeros if needed (should not happen with proper config)
                key = raw_key.ljust(32, b'0')
        else:
            if len(key) != 32:
                raise ValueError("Encryption key must be exactly 32 bytes")
        
        self.cipher = AESGCM(key)

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt API key, return base64-encoded result
        Format: base64(nonce + ciphertext)
        """
        nonce = os.urandom(12)  # 96-bit nonce for GCM
        ciphertext = self.cipher.encrypt(nonce, plaintext.encode('utf-8'), None)
        encrypted_data = nonce + ciphertext
        return base64.b64encode(encrypted_data).decode('utf-8')

    def decrypt(self, encrypted: str) -> str:
        """
        Decrypt encrypted API key
        Input: base64-encoded data (nonce + ciphertext)
        """
        try:
            encrypted_data = base64.b64decode(encrypted)
            nonce = encrypted_data[:12]
            ciphertext = encrypted_data[12:]
            plaintext = self.cipher.decrypt(nonce, ciphertext, None)
            return plaintext.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Failed to decrypt API key: {str(e)}")


def encrypt_api_key(api_key: str) -> str:
    """Encrypt an API key for storage"""
    return api_key_encryption.encrypt(api_key)


def decrypt_api_key(encrypted_key: str) -> str:
    """Decrypt an encrypted API key"""
    return api_key_encryption.decrypt(encrypted_key)


# Global instance
api_key_encryption = APIKeyEncryption()
