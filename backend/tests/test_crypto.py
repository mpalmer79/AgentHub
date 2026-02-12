"""
Tests for the encryption service.

Tests token encryption/decryption for OAuth tokens.
"""
import pytest
import os


class TestEncryptionService:
    """Tests for EncryptionService."""

    def test_encrypt_returns_string(self):
        """Encrypting a string returns a string."""
        from app.core.crypto import encryption_service

        result = encryption_service.encrypt("test_token")
        assert isinstance(result, str)
        assert result != "test_token"  # Should be encrypted

    def test_decrypt_returns_original(self):
        """Decrypting returns the original string."""
        from app.core.crypto import encryption_service

        original = "my_secret_oauth_token_12345"
        encrypted = encryption_service.encrypt(original)
        decrypted = encryption_service.decrypt(encrypted)

        assert decrypted == original

    def test_encrypt_none_returns_none(self):
        """Encrypting None returns None."""
        from app.core.crypto import encryption_service

        result = encryption_service.encrypt(None)
        assert result is None

    def test_decrypt_none_returns_none(self):
        """Decrypting None returns None."""
        from app.core.crypto import encryption_service

        result = encryption_service.decrypt(None)
        assert result is None

    def test_different_inputs_different_outputs(self):
        """Different inputs produce different encrypted outputs."""
        from app.core.crypto import encryption_service

        enc1 = encryption_service.encrypt("token_a")
        enc2 = encryption_service.encrypt("token_b")

        assert enc1 != enc2

    def test_same_input_different_outputs(self):
        """Same input produces different outputs (Fernet uses random IV)."""
        from app.core.crypto import encryption_service

        enc1 = encryption_service.encrypt("same_token")
        enc2 = encryption_service.encrypt("same_token")

        # Fernet adds random IV, so outputs should differ
        assert enc1 != enc2

        # But both should decrypt to same value
        assert encryption_service.decrypt(enc1) == encryption_service.decrypt(enc2)

    def test_handles_unicode(self):
        """Encryption handles unicode strings."""
        from app.core.crypto import encryption_service

        original = "token_with_émojis_🔐"
        encrypted = encryption_service.encrypt(original)
        decrypted = encryption_service.decrypt(encrypted)

        assert decrypted == original

    def test_handles_long_strings(self):
        """Encryption handles long strings."""
        from app.core.crypto import encryption_service

        original = "x" * 10000  # 10KB token
        encrypted = encryption_service.encrypt(original)
        decrypted = encryption_service.decrypt(encrypted)

        assert decrypted == original


class TestEncryptionServiceLazyInit:
    """Tests for lazy initialization behavior."""

    def test_service_importable_without_key(self, monkeypatch):
        """
        EncryptionService can be imported even without valid key.
        It only fails when actually used.
        """
        # This test verifies the lazy initialization works
        # The conftest.py sets a valid key, so we're testing
        # that the service doesn't crash on import
        from app.core.crypto import EncryptionService

        # Creating instance should succeed (lazy init)
        service = EncryptionService()
        assert service is not None
