import json
from typing import Dict, List
from datetime import datetime, timedelta
import hashlib

class ClientEncryptionManager:
    """
    Manages client-side encryption state and keys
    Tracks which files are encrypted and their key metadata
    """
    
    def __init__(self):
        self.encrypted_files = {}
        self.key_registry = {}  # Store encrypted keys
    
    def register_encrypted_file(self, file_id: str, user: str, 
                               file_hash: str, encryption_metadata: Dict) -> Dict:
        """
        Register a file as encrypted in the system
        """
        file_record = {
            'id': file_id,
            'owner': user,
            'file_hash': file_hash,
            'encryption_metadata': encryption_metadata,
            'encrypted_at': datetime.utcnow().isoformat(),
            'encryption_algorithm': encryption_metadata.get('algorithm'),
            'key_encryption_algorithm': 'RSA-OAEP',
            'access_log': []
        }
        
        self.encrypted_files[file_id] = file_record
        return file_record
    
    def store_encrypted_key(self, file_id: str, recipient_user: str, 
                           encrypted_key: str, key_metadata: Dict) -> Dict:
        """
        Store encrypted AES key for key sharing
        """
        key_id = f"{file_id}_{recipient_user}"
        
        key_record = {
            'id': key_id,
            'file_id': file_id,
            'recipient': recipient_user,
            'encrypted_key': encrypted_key,
            'key_metadata': key_metadata,
            'created_at': datetime.utcnow().isoformat(),
            'accessed': False,
            'access_count': 0
        }
        
        self.key_registry[key_id] = key_record
        return key_record
    
    def get_encrypted_key(self, key_id: str, user: str) -> str:
        """
        Retrieve encrypted key for decryption
        """
        if key_id not in self.key_registry:
            raise ValueError(f"Key {key_id} not found")
        
        key_record = self.key_registry[key_id]
        
        # Verify user is recipient
        if key_record['recipient'] != user:
            raise PermissionError(f"User not authorized for this key")
        
        # Update access log
        key_record['accessed'] = True
        key_record['access_count'] += 1
        
        return key_record['encrypted_key']
    
    def get_file_encryption_info(self, file_id: str, user: str) -> Dict:
        """
        Get encryption metadata for a file
        """
        if file_id not in self.encrypted_files:
            raise ValueError(f"File {file_id} not found")
        
        file_record = self.encrypted_files[file_id]
        
        # Check access (owner or granted access)
        if file_record['owner'] != user:
            raise PermissionError(f"No access to file encryption info")
        
        return {
            'file_id': file_record['id'],
            'encryption_algorithm': file_record['encryption_algorithm'],
            'key_encryption_algorithm': file_record['key_encryption_algorithm'],
            'encryption_metadata': file_record['encryption_metadata'],
            'encrypted_at': file_record['encrypted_at']
        }
    
    def list_encrypted_files(self, user: str) -> List[Dict]:
        """
        List all encrypted files for a user
        """
        return [
            {
                'id': record['id'],
                'file_hash': record['file_hash'],
                'encryption_algorithm': record['encryption_algorithm'],
                'encrypted_at': record['encrypted_at'],
                'access_count': len(record['access_log'])
            }
            for record in self.encrypted_files.values()
            if record['owner'] == user
        ]
