from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
import os
import json
import base64
from typing import Tuple, Dict

class WebCryptoAPI:
    """
    Implements Web Crypto API-compatible encryption/decryption
    for client-server communication
    """
    
    @staticmethod
    def generate_rsa_keypair(key_size: int = 2048) -> Dict:
        """
        Generate RSA keypair compatible with Web Crypto API
        Returns dict with public and private keys in JWK format
        """
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        
        # Export as PEM
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode()
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()
        
        return {
            'private_key': private_pem,
            'public_key': public_pem,
            'key_size': key_size,
            'algorithm': 'RSA-OAEP'
        }
    
    @staticmethod
    def generate_aes_key(key_length: int = 256) -> bytes:
        """
        Generate AES key (128, 192, or 256 bits)
        """
        key_bytes = key_length // 8
        return os.urandom(key_bytes)
    
    @staticmethod
    def aes_encrypt(plaintext: bytes, key: bytes, iv: bytes = None) -> Tuple[bytes, bytes]:
        """
        Encrypt using AES-GCM (more secure than CBC)
        Returns (ciphertext, iv)
        """
        if iv is None:
            iv = os.urandom(12)  # 96-bit IV for GCM
        
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        
        return ciphertext + encryptor.tag, iv
    
    @staticmethod
    def aes_decrypt(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
        """
        Decrypt using AES-GCM
        """
        # Extract tag from ciphertext (last 16 bytes)
        actual_ciphertext = ciphertext[:-16]
        tag = ciphertext[-16:]
        
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv, tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(actual_ciphertext) + decryptor.finalize()
        
        return plaintext
    
    @staticmethod
    def rsa_encrypt_aes_key(aes_key: bytes, public_key_pem: str) -> bytes:
        """
        Encrypt AES key with RSA public key
        """
        public_key = serialization.load_pem_public_key(
            public_key_pem.encode(),
            backend=default_backend()
        )
        
        encrypted_key = public_key.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return encrypted_key
    
    @staticmethod
    def rsa_decrypt_aes_key(encrypted_key: bytes, private_key_pem: str) -> bytes:
        """
        Decrypt AES key with RSA private key
        """
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode(),
            password=None,
            backend=default_backend()
        )
        
        aes_key = private_key.decrypt(
            encrypted_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return aes_key
    
    @staticmethod
    def derive_key_from_password(password: str, salt: bytes = None) -> Tuple[bytes, bytes]:
        """
        Derive encryption key from password using PBKDF2
        Returns (key, salt)
        """
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = kdf.derive(password.encode())
        
        return key, salt
    
    @staticmethod
    def encrypt_file_payload(file_data: bytes, password: str) -> Dict:
        """
        Encrypt file with password-derived key
        Returns dict with encrypted data and metadata
        """
        key, salt = WebCryptoAPI.derive_key_from_password(password)
        ciphertext, iv = WebCryptoAPI.aes_encrypt(file_data, key)
        
        return {
            'ciphertext': base64.b64encode(ciphertext).decode(),
            'iv': base64.b64encode(iv).decode(),
            'salt': base64.b64encode(salt).decode(),
            'algorithm': 'AES-256-GCM',
            'kdf': 'PBKDF2-SHA256'
        }
    
    @staticmethod
    def decrypt_file_payload(payload: Dict, password: str) -> bytes:
        """
        Decrypt file from payload
        """
        ciphertext = base64.b64decode(payload['ciphertext'])
        iv = base64.b64decode(payload['iv'])
        salt = base64.b64decode(payload['salt'])
        
        key, _ = WebCryptoAPI.derive_key_from_password(password, salt)
        plaintext = WebCryptoAPI.aes_decrypt(ciphertext, key, iv)
        
        return plaintext
