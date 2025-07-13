import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import DES, AES
from Crypto.Util.Padding import pad, unpad

# This code taken from answer https://stackoverflow.com/a/21928790/4791963

class CipherClass(object):
    """
    A unified cipher wrapper supporting AES-128 and DES-56 in CBC mode with PKCS#7 padding.

    This class derives a fixed-size key from an arbitrary-length passphrase using SHA-256,
    then provides methods to encrypt and decrypt text via symmetric block ciphers.

    Args:
        key (str): Passphrase used to derive the AES or DES key.
        algo (str, optional): Cipher algorithm to use. "AES" selects AES-128 (16-byte key).
                              "DES" selects DES-56 (8-byte key + parity). Defaults to "DES".

    Raises:
        ValueError: If `algo` is not "AES" or "DES".
    """
    def __init__(self, key: str, algo: str = "DES"):
        algo = algo.upper()
        if algo == "AES":
            # AES block size is 16 bytes
            self.bs = AES.block_size
            # Derive a 16-byte key from the passphrase
            self.key = hashlib.sha256(key.encode('utf-8')).digest()[:16]
            self.cipher_mod = AES
        elif algo == "DES":
            # DES block size is 8 bytes
            self.bs = DES.block_size
            # Derive an 8-byte key (56 bits used + parity) from the passphrase
            self.key = hashlib.sha256(key.encode('utf-8')).digest()[:8]
            self.cipher_mod = DES
        else:
            raise ValueError("Unsupported algorithm: choose 'AES' or 'DES'")

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a UTF-8 string and return a base64-encoded ciphertext.

        The plaintext is padded to a multiple of the block size using PKCS#7 padding,
        then encrypted in CBC mode with a random IV prepended.

        Args:
            plaintext (str): Text to encrypt.

        Returns:
            str: Base64-encoded string containing IV + ciphertext.
        """
        data = plaintext.encode('utf-8')
        data = self._pad(data)
        iv = Random.new().read(self.bs)
        cipher = self.cipher_mod.new(self.key, self.cipher_mod.MODE_CBC, iv)
        ct = cipher.encrypt(data)
        return base64.b64encode(iv + ct).decode('utf-8')

    def decrypt(self, b64cipher: str) -> str:
        """
        Decrypt a base64-encoded ciphertext (IV + data) and return the plaintext string.

        The input is decoded from base64, split into IV and ciphertext,
        then decrypted in CBC mode and unpadded using PKCS#7.

        Args:
            b64cipher (str): Base64-encoded IV + ciphertext.

        Returns:
            str: Decrypted UTF-8 plaintext.

        Raises:
            ValueError: If padding is invalid.
        """
        raw = base64.b64decode(b64cipher)
        iv, ct = raw[:self.bs], raw[self.bs:]
        cipher = self.cipher_mod.new(self.key, self.cipher_mod.MODE_CBC, iv)
        data = cipher.decrypt(ct)
        return self._unpad(data).decode('utf-8')

    def _pad(self, data: bytes) -> bytes:
        """
        Apply PKCS#7 padding to the data to align to the block size.

        Args:
            data (bytes): Data to pad.

        Returns:
            bytes: Padded data.
        """
        pad_len = self.bs - (len(data) % self.bs)
        return data + bytes([pad_len]) * pad_len

    def _unpad(self, data: bytes) -> bytes:
        """
        Remove PKCS#7 padding from decrypted data.

        Args:
            data (bytes): Padded decrypted data.

        Returns:
            bytes: Original unpadded data.

        Raises:
            ValueError: If padding is invalid or corrupted.
        """
        pad_len = data[-1]
        if pad_len < 1 or pad_len > self.bs:
            raise ValueError("Invalid padding length")
        return data[:-pad_len]
