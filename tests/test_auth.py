"""Tests for auth crypto functions."""

from unofficial_pecron_api.auth import (
    compute_signature,
    derive_aes_key,
    encrypt_password,
    generate_random,
)


def test_generate_random_length():
    result = generate_random()
    assert len(result) == 16


def test_generate_random_charset():
    result = generate_random()
    assert result.isalnum()


def test_generate_random_not_constant():
    # Two calls should produce different values (extremely unlikely to collide)
    a = generate_random()
    b = generate_random()
    assert a != b


def test_derive_aes_key_length():
    key = derive_aes_key("abcdefghijklmnop")
    assert len(key) == 16


def test_derive_aes_key_uppercase():
    key = derive_aes_key("abcdefghijklmnop")
    assert key == key.upper()


def test_derive_aes_key_deterministic():
    a = derive_aes_key("testinput1234567")
    b = derive_aes_key("testinput1234567")
    assert a == b


def test_encrypt_password_roundtrip():
    """Verify encrypt_password produces consistent output for the same inputs."""
    random_str = "AAAAAAAAAAAAAAAA"
    enc1 = encrypt_password("mypassword", random_str)
    enc2 = encrypt_password("mypassword", random_str)
    assert enc1 == enc2
    assert len(enc1) > 0


def test_encrypt_password_different_random():
    """Different random strings should produce different ciphertext."""
    enc1 = encrypt_password("mypassword", "AAAAAAAAAAAAAAAA")
    enc2 = encrypt_password("mypassword", "BBBBBBBBBBBBBBBB")
    assert enc1 != enc2


def test_compute_signature_deterministic():
    sig1 = compute_signature("a@b.com", "encpwd", "rand1234567890AB", "secret")
    sig2 = compute_signature("a@b.com", "encpwd", "rand1234567890AB", "secret")
    assert sig1 == sig2


def test_compute_signature_is_hex_sha256():
    sig = compute_signature("a@b.com", "encpwd", "rand1234567890AB", "secret")
    assert len(sig) == 64  # SHA-256 hex digest
    assert all(c in "0123456789abcdef" for c in sig)


def test_encrypt_decrypt_known_vector():
    """Verify encryption with a known random string produces expected base64 output."""
    import base64

    from Crypto.Cipher import AES
    from Crypto.Util.Padding import unpad

    password = "TestPassword123"
    random_str = "Xt9kMpQr2sWvYzAb"

    # Encrypt
    encrypted_b64 = encrypt_password(password, random_str)

    # Manually decrypt to verify
    aes_key = derive_aes_key(random_str)
    iv = aes_key[8:16] + aes_key[0:8]
    cipher = AES.new(aes_key.encode(), AES.MODE_CBC, iv.encode())
    decrypted = unpad(cipher.decrypt(base64.b64decode(encrypted_b64)), AES.block_size)
    assert decrypted.decode("utf-8") == password
