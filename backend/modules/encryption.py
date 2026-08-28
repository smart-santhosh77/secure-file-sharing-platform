from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import os

class AESEncryption:
    """
    AES-256 Encryption utility
    """
    
    @staticmethod
    def generate_key():
        """Generate a 256-bit key"""
        return os.urandom(32)
    
    @staticmethod
    def generate_iv():
        """Generate a 128-bit IV"""
        return os.urandom(16)
    
    @staticmethod
    def encrypt(plaintext: bytes, key: bytes, iv: bytes = None) -> tuple:
        """
        Encrypt data using AES-256-CBC
        Returns: (ciphertext, iv)
        """
        if iv is None:
            iv = AESEncryption.generate_iv()
        
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # Add PKCS7 padding
        padding_length = 16 - (len(plaintext) % 16)
        padded_plaintext = plaintext + bytes([padding_length] * padding_length)
        
        ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()
        return ciphertext, iv
    
    @staticmethod
    def decrypt(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
        """
        Decrypt data using AES-256-CBC
        """
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Remove PKCS7 padding
        padding_length = padded_plaintext[-1]
        plaintext = padded_plaintext[:-padding_length]
        
        return plaintext

class RSAEncryption:
    """
    RSA-2048 Encryption utility for key exchange
    """
    
    @staticmethod
    def generate_keypair(key_size=2048):
        """
        Generate RSA keypair
        Returns: (public_key, private_key)
        """
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        return public_key, private_key
    
    @staticmethod
    def encrypt(plaintext: bytes, public_key) -> bytes:
        """
        Encrypt data with public key
        """
        ciphertext = public_key.encrypt(
            plaintext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return ciphertext
    
    @staticmethod
    def decrypt(ciphertext: bytes, private_key) -> bytes:
        """
        Decrypt data with private key
        """
        plaintext = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return plaintext

class KeyDerivation:
    """
    Key derivation utility using PBKDF2
    """
    
    @staticmethod
    def derive_key(password: str, salt: bytes = None, iterations: int = 100000) -> tuple:
        """
        Derive a key from password
        Returns: (key, salt)
        """
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=iterations,
            backend=default_backend()
        )
        key = kdf.derive(password.encode())
        return key, salt
