from django.db import models
from django.conf import settings
from cryptography.fernet import Fernet
import base64
import hashlib


class EncryptedCharField(models.CharField):
    """Custom encrypted char field using Fernet symmetric encryption."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._fernet = None

    def _get_fernet(self):
        if self._fernet is None:
            key = settings.SECRET_KEY
            # Derive a valid Fernet key from SECRET_KEY
            key_bytes = key.encode('utf-8')
            # Use SHA-256 to get a 32-byte key, then base64 encode it
            digest = hashlib.sha256(key_bytes).digest()
            fernet_key = base64.urlsafe_b64encode(digest)
            self._fernet = Fernet(fernet_key)
        return self._fernet

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        fernet = self._get_fernet()
        decrypted = fernet.decrypt(value.encode('utf-8'))
        return decrypted.decode('utf-8')

    def get_prep_value(self, value):
        if value is None:
            return value
        fernet = self._get_fernet()
        encrypted = fernet.encrypt(value.encode('utf-8'))
        return encrypted.decode('utf-8')

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        return name, path, args, kwargs
