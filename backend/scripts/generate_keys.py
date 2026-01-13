#!/usr/bin/env python3
"""
Helper script to generate cryptographic keys for development.

Usage:
    python scripts/generate_keys.py
"""
import base64
import secrets


def generate_secret_key() -> str:
    """Generate a secret key for JWT signing."""
    return secrets.token_urlsafe(32)


def generate_encryption_key() -> str:
    """Generate an AES-256 encryption key (32 bytes, base64 encoded)."""
    return base64.b64encode(secrets.token_bytes(32)).decode()


if __name__ == "__main__":
    print("=" * 60)
    print("simFocus - Cryptographic Keys Generator")
    print("=" * 60)
    print()

    print("Generate these keys and add them to your .env file:")
    print()

    secret_key = generate_secret_key()
    print(f"SECRET_KEY={secret_key}")
    print()

    encryption_key = generate_encryption_key()
    print(f"ENCRYPTION_KEY={encryption_key}")
    print()

    print("=" * 60)
    print("Copy these values to your backend/.env file")
    print("=" * 60)
