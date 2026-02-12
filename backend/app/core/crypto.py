from cryptography.fernet import Fernet
from typing import Optional
from app.core.config import settings


class EncryptionService:
    """
    Handles encryption/decryption of sensitive data like OAuth tokens.
    Uses Fernet symmetric encryption (AES-128-CBC with HMAC).
    """
    
    _instance: Optional["EncryptionService"] = None
    _fernet: Optional[Fernet] = None
    
    def __init__(self):
        # Lazy initialization - don't create Fernet until actually needed
        pass
    
    def _get_fernet(self) -> Fernet:
        """Lazy initialization of Fernet cipher."""
        if self._fernet is None:
            key = settings.INTEGRATION_ENCRYPTION_KEY
            if not key:
                raise RuntimeError(
                    "INTEGRATION_ENCRYPTION_KEY not configured. "
                    "Generate one with: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
                )
            try:
                self._fernet = Fernet(key.encode())
            except Exception as e:
                raise RuntimeError(
                    f"Invalid INTEGRATION_ENCRYPTION_KEY: {e}. "
                    "Key must be 32 url-safe base64-encoded bytes. "
                    "Generate one with: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
                )
        return self._fernet

    def encrypt(self, value: str | None) -> str | None:
        """Encrypt a string value. Returns None if input is None."""
        if value is None:
            return None
        return self._get_fernet().encrypt(value.encode()).decode()

    def decrypt(self, value: str | None) -> str | None:
        """Decrypt a string value. Returns None if input is None."""
        if value is None:
            return None
        return self._get_fernet().decrypt(value.encode()).decode()


# Singleton instance - safe to import, won't crash until actually used
encryption_service = EncryptionService()
