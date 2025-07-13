"""
~~~~~~~~~~~~~~~~~~~
Utility functions for RSA key generation, encryption, and decryption.

Author: Ahsan Bilal, University of Oklahoma
"""

import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP


def generate_RSA_key_pairs():
    """Generate an RSA public/private key pair.

    Returns:
        tuple: (private_key, public_key), both as `Crypto.PublicKey.RSA` objects.
    """
    private_key = RSA.generate(1024)
    public_key = private_key.publickey()
    return private_key, public_key


def encrypt_text(plain_text, public_key):
    """Encrypt plaintext using the recipient's RSA public key.

    Args:
        plain_text (str): Message to be encrypted.
        public_key (Crypto.PublicKey.RSA.RsaKey): Recipient's public key.

    Returns:
        str: Base64-encoded ciphertext.
    """
    original_bytes = plain_text.encode("utf-8")
    cipher = PKCS1_OAEP.new(public_key)
    encrypted_bytes = cipher.encrypt(original_bytes)
    return base64.b64encode(encrypted_bytes).decode("utf-8")


def decrypt_text(encrypted_text, private_key):
    """Decrypt a base64-encoded RSA-encrypted ciphertext using the private key.

    Args:
        encrypted_text (str): Base64-encoded ciphertext.
        private_key (Crypto.PublicKey.RSA.RsaKey): Receiver's private RSA key.

    Returns:
        str: Decrypted original plaintext.
    """
    encrypted_bytes = base64.b64decode(encrypted_text)
    cipher = PKCS1_OAEP.new(private_key)
    decrypted_bytes = cipher.decrypt(encrypted_bytes)
    return decrypted_bytes.decode("utf-8")
