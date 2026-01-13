"""
Security utilities for authentication and encryption

Provides:
- JWT token creation and verification
- Password hashing and verification
- AES-256 encryption for sensitive data
"""
import base64
import secrets
from datetime import datetime, timedelta
from typing import Any, Optional

import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from passlib.context import CryptContext

from app.config import get_settings
from app.core.exceptions import UnauthorizedException


settings = get_settings()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password for storage.

    Args:
        password: Plain text password to hash

    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def create_access_token(
    data: dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a JWT access token.

    Args:
        data: Data to encode in the token (e.g., {"sub": user_id})
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token

    Example:
        >>> token = create_access_token(
        ...     data={"sub": "user-123"},
        ...     expires_delta=timedelta(hours=1)
        ... )
    """
    to_encode = data.copy()

    # Set expiration
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })

    # Encode token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


def create_refresh_token(
    data: dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a JWT refresh token.

    Args:
        data: Data to encode in the token
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT refresh token
    """
    to_encode = data.copy()

    # Set expiration
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        )

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })

    # Encode token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


def decode_token(token: str) -> dict[str, Any]:
    """
    Decode and verify a JWT token.

    Args:
        token: JWT token to decode

    Returns:
        Decoded token payload

    Raises:
        UnauthorizedException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY.get_secret_value(),
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise UnauthorizedException("Token has expired")
    except jwt.InvalidTokenError as e:
        raise UnauthorizedException(f"Invalid token: {str(e)}")


def verify_token(token: str, token_type: str = "access") -> dict[str, Any]:
    """
    Verify a JWT token and check its type.

    Args:
        token: JWT token to verify
        token_type: Expected token type ("access" or "refresh")

    Returns:
        Decoded token payload

    Raises:
        UnauthorizedException: If token is invalid, expired, or wrong type
    """
    payload = decode_token(token)

    # Check token type
    if payload.get("type") != token_type:
        raise UnauthorizedException(
            f"Invalid token type. Expected '{token_type}', "
            f"got '{payload.get('type')}'"
        )

    return payload


class AESEncryption:
    """
    AES-256 encryption for sensitive data (e.g., API keys).

    Uses PBKDF2 for key derivation and GCM mode for authenticated encryption.
    """

    def __init__(self, password: Optional[str] = None):
        """
        Initialize encryption with password or settings key.

        Args:
            password: Optional password for key derivation.
                     If not provided, uses ENCRYPTION_KEY from settings.
        """
        if password:
            self.password = password.encode()
        elif settings.ENCRYPTION_KEY:
            self.password = settings.ENCRYPTION_KEY.get_secret_value().encode()
        else:
            raise ValueError(
                "Encryption key not configured. Set ENCRYPTION_KEY in settings."
            )

        self.backend = default_backend()

    def _derive_key(self, salt: bytes) -> bytes:
        """
        Derive encryption key from password using PBKDF2.

        Args:
            salt: Salt for key derivation

        Returns:
            Derived key (32 bytes for AES-256)
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=self.backend
        )
        return kdf.derive(self.password)

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext string.

        Args:
            plaintext: String to encrypt

        Returns:
            Base64 encoded encrypted data (salt + nonce + ciphertext + tag)

        Example:
            >>> cipher = AESEncryption()
            >>> encrypted = cipher.encrypt("my-secret-api-key")
        """
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM

        # Generate random salt and nonce
        salt = secrets.token_bytes(16)
        nonce = secrets.token_bytes(12)

        # Derive key
        key = self._derive_key(salt)

        # Encrypt
        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)

        # Combine: salt (16) + nonce (12) + ciphertext (with tag)
        combined = salt + nonce + ciphertext

        # Return base64 encoded
        return base64.b64encode(combined).decode("utf-8")

    def decrypt(self, encrypted: str) -> str:
        """
        Decrypt encrypted string.

        Args:
            encrypted: Base64 encoded encrypted data

        Returns:
            Decrypted plaintext

        Raises:
            ValueError: If decryption fails

        Example:
            >>> cipher = AESEncryption()
            >>> decrypted = cipher.decrypt(encrypted)
        """
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM

        try:
            # Decode base64
            combined = base64.b64decode(encrypted.encode("utf-8"))

            # Extract components
            salt = combined[:16]
            nonce = combined[16:28]
            ciphertext = combined[28:]

            # Derive key
            key = self._derive_key(salt)

            # Decrypt
            aesgcm = AESGCM(key)
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)

            return plaintext.decode("utf-8")

        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")


def generate_secure_token(length: int = 32) -> str:
    """
    Generate a cryptographically secure random token.

    Args:
        length: Length of token in bytes (default: 32)

    Returns:
        Hex-encoded secure token

    Example:
        >>> token = generate_secure_token()
        >>> print(token)
        'a1b2c3d4e5f6...'
    """
    return secrets.token_hex(length)


def generate_api_key() -> str:
    """
    Generate a secure API key.

    Returns:
        API key in format: sk_live_xxx (for production) or sk_test_xxx (for dev)
    """
    prefix = "sk_live" if settings.is_production else "sk_test"
    random_part = secrets.token_urlsafe(32)
    return f"{prefix}_{random_part}"
