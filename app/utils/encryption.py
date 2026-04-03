from cryptography.fernet import Fernet


def generate_key() -> str:
    return Fernet.generate_key().decode()


def encrypt_token(token: str | None, key: str) -> str:
    if not token:
        return ""
    f = Fernet(key.encode() if isinstance(key, str) else key)
    return f.encrypt(token.encode()).decode()


def decrypt_token(encrypted: str | None, key: str) -> str:
    if not encrypted:
        return ""
    f = Fernet(key.encode() if isinstance(key, str) else key)
    return f.decrypt(encrypted.encode()).decode()
