from cryptography.fernet import Fernet
from app.core.config import settings


class EncryptionService:
    def __init__(self):
        if not settings.INTEGRATION_ENCRYPTION_KEY:
            raise RuntimeError("INTEGRATION_ENCRYPTION_KEY not configured")
        self._fernet = Fernet(settings.INTEGRATION_ENCRYPTION_KEY.encode())

    def encrypt(self, value: str | None) -> str | None:
        if value is None:
            return None
        return self._fernet.encrypt(value.encode()).decode()

    def decrypt(self, value: str | None) -> str | None:
        if value is None:
            return None
        return self._fernet.decrypt(value.encode()).decode()


encryption_service = EncryptionService()
