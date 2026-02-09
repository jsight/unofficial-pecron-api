"""Authentication crypto functions for the Pecron/Quectel cloud API.

These implement the login flow reverse-engineered from the Pecron Android APK v1.9.0.
"""

import base64
import hashlib
import secrets
import string

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


def generate_random() -> str:
    """Generate a 16-character random string [0-9a-zA-Z].

    Matches dn0.qvVibd5qFA() in the APK.
    """
    chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(chars) for _ in range(16))


def derive_aes_key(random_str: str) -> str:
    """Derive AES key from random string: MD5(random)[8:24].upper().

    Matches u90q0bugwP.IRFb8hNXRx() in the APK.
    """
    md5_hex = hashlib.md5(random_str.encode()).hexdigest().upper()
    return md5_hex[8:24]


def encrypt_password(password: str, random_str: str) -> str:
    """AES/CBC/PKCS5 encrypt password, return base64.

    The AES key is derived from random_str. The IV is the key with its
    two halves swapped: key[8:16] + key[0:8].

    Matches HA7dSdeYya.qvVibd5qFA() and ok0.java lines 337-343 in the APK.
    """
    aes_key = derive_aes_key(random_str)
    iv = aes_key[8:16] + aes_key[0:8]
    cipher = AES.new(aes_key.encode("utf-8"), AES.MODE_CBC, iv.encode("utf-8"))
    encrypted = cipher.encrypt(pad(password.encode("utf-8"), AES.block_size))
    return base64.b64encode(encrypted).decode("utf-8")


def compute_signature(email: str, encrypted_pwd: str, random_str: str, secret: str) -> str:
    """SHA-256(email + encrypted_pwd + random + userDomainSecret).

    Matches b11.IRFb8hNXRx() and ok0.java line 354 in the APK.
    """
    data = email + encrypted_pwd + random_str + secret
    return hashlib.sha256(data.encode("utf-8")).hexdigest()
