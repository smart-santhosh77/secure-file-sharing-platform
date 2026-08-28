from datetime import datetime, timedelta
import uuid

class KeyShare:
    """
    Key Sharing & Access Control Module
    """
    
    def __init__(self):
        self.shares = {}  # Store key shares
        self.permissions = {}  # Store permissions
    
    def create_share(self, file_id: str, owner: str, recipient: str, 
                    encryption_key: bytes, expiry_days: int = 7, 
                    one_time_access: bool = False) -> dict:
        """
        Create a key share for another user
        """
        share_id = str(uuid.uuid4())
        expiry = datetime.utcnow() + timedelta(days=expiry_days)
        
        share = {
            'id': share_id,
            'file_id': file_id,
            'owner': owner,
            'recipient': recipient,
            'key': encryption_key.hex(),  # Store as hex string
            'created_at': datetime.utcnow().isoformat(),
            'expiry': expiry.isoformat(),
            'one_time': one_time_access,
            'accessed': False,
            'access_count': 0
        }
        
        self.shares[share_id] = share
        return share
    
    def get_shared_key(self, share_id: str, recipient: str) -> bytes:
        """
        Get the shared encryption key
        """
        if share_id not in self.shares:
            raise ValueError(f"Share {share_id} not found")
        
        share = self.shares[share_id]
        
        # Check recipient
        if share['recipient'] != recipient:
            raise PermissionError(f"Not authorized to access this share")
        
        # Check expiry
        expiry = datetime.fromisoformat(share['expiry'])
        if datetime.utcnow() > expiry:
            raise ValueError(f"Share has expired")
        
        # Check one-time access
        if share['one_time'] and share['accessed']:
            raise ValueError(f"One-time access already used")
        
        # Update access
        share['accessed'] = True
        share['access_count'] += 1
        
        return bytes.fromhex(share['key'])
    
    def revoke_share(self, share_id: str, owner: str) -> bool:
        """
        Revoke a key share
        """
        if share_id not in self.shares:
            raise ValueError(f"Share {share_id} not found")
        
        share = self.shares[share_id]
        
        # Check owner
        if share['owner'] != owner:
            raise PermissionError(f"Only owner can revoke")
        
        del self.shares[share_id]
        return True
    
    def list_shares(self, user: str, mode: str = 'sent') -> list:
        """
        List shares for a user
        mode: 'sent' or 'received'
        """
        if mode == 'sent':
            return [
                share for share in self.shares.values()
                if share['owner'] == user
            ]
        elif mode == 'received':
            return [
                share for share in self.shares.values()
                if share['recipient'] == user
            ]
        else:
            raise ValueError("Invalid mode")
    
    def grant_permission(self, file_id: str, owner: str, user: str, 
                        permissions: list) -> dict:
        """
        Grant permissions to a user for a file
        permissions: ['read', 'download', 'share'] etc.
        """
        perm_id = str(uuid.uuid4())
        
        permission = {
            'id': perm_id,
            'file_id': file_id,
            'owner': owner,
            'user': user,
            'permissions': permissions,
            'granted_at': datetime.utcnow().isoformat()
        }
        
        self.permissions[perm_id] = permission
        return permission
    
    def check_permission(self, file_id: str, user: str, permission: str) -> bool:
        """
        Check if user has specific permission for file
        """
        for perm in self.permissions.values():
            if perm['file_id'] == file_id and perm['user'] == user:
                return permission in perm['permissions']
        return False
