"""Fernet AES-256 encryption for tenant credentials.

Adapted from Domus SaaS (031) TenantCredential model.
Framework-agnostic: no Django dependency, just encryption/decryption.
"""


from cryptography.fernet import Fernet


class CredentialEncryptor:
    """
    AES-256 encryption using Fernet for sensitive credential storage.

    Usage:
        encryptor = CredentialEncryptor(key=FERNET_KEY)
        encrypted = encryptor.encrypt("my-api-key")
        decrypted = encryptor.decrypt(encrypted)
    """

    def __init__(self, key: str):
        """
        Args:
            key: Fernet key (base64-encoded 32-byte key).
                 Generate with CredentialEncryptor.generate_key()
        """
        self._fernet = Fernet(key.encode() if isinstance(key, str) else key)

    @staticmethod
    def generate_key() -> str:
        """Generate a new Fernet key."""
        return Fernet.generate_key().decode()

    def encrypt(self, value: str) -> str:
        """Encrypt a string value. Returns base64-encoded ciphertext."""
        return self._fernet.encrypt(value.encode()).decode()

    def decrypt(self, encrypted_value: str) -> str:
        """
        Decrypt a previously encrypted value.

        Raises:
            InvalidToken: If the token is invalid or corrupted
        """
        return self._fernet.decrypt(encrypted_value.encode()).decode()

    def rotate_key(self, encrypted_value: str, new_key: str) -> str:
        """
        Re-encrypt a value with a new key.

        Args:
            encrypted_value: Value encrypted with current key
            new_key: New Fernet key to encrypt with

        Returns:
            Value encrypted with the new key
        """
        decrypted = self.decrypt(encrypted_value)
        new_encryptor = CredentialEncryptor(key=new_key)
        return new_encryptor.encrypt(decrypted)


# Common service types for reference (from 031 Domus)
SERVICE_TYPES = [
    "whatsapp",
    "deepseek",
    "openai",
    "claude",
    "telegram",
    "facebook",
    "smtp",
    "stripe",
    "custom",
]
