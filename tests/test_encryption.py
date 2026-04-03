from app.utils.encryption import encrypt_token, decrypt_token, generate_key


def test_encrypt_decrypt_roundtrip():
    key = generate_key()
    original = "sk-test-token-12345"
    encrypted = encrypt_token(original, key)
    assert encrypted != original
    decrypted = decrypt_token(encrypted, key)
    assert decrypted == original


def test_encrypt_returns_different_each_time():
    key = generate_key()
    e1 = encrypt_token("sk-test", key)
    e2 = encrypt_token("sk-test", key)
    assert e1 != e2


def test_encrypt_empty_returns_empty():
    key = generate_key()
    assert encrypt_token("", key) == ""
    assert decrypt_token("", key) == ""


def test_encrypt_none_returns_empty():
    key = generate_key()
    assert encrypt_token(None, key) == ""
    assert decrypt_token(None, key) == ""
