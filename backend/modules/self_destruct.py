from datetime import datetime, timedelta
import uuid

class SelfDestruct:
    """
    Self-Destruct Module
    Handles time-based and one-time access expiry
    """
    
    def __init__(self):
        self.destruct_configs = {}
    
    def set_time_expiry(self, file_id: str, owner: str, expiry_hours: int = 24) -> dict:
        """
        Set file to self-destruct after specified hours
        """
        expiry = datetime.utcnow() + timedelta(hours=expiry_hours)
        
        config = {
            'id': str(uuid.uuid4()),
            'file_id': file_id,
            'owner': owner,
            'type': 'time',
            'expiry': expiry.isoformat(),
            'created_at': datetime.utcnow().isoformat(),
            'status': 'active'
        }
        
        self.destruct_configs[config['id']] = config
        return config
    
    def set_one_time_access(self, file_id: str, owner: str) -> dict:
        """
        Set file to self-destruct after first access
        """
        config = {
            'id': str(uuid.uuid4()),
            'file_id': file_id,
            'owner': owner,
            'type': 'one_time',
            'access_count': 0,
            'max_accesses': 1,
            'created_at': datetime.utcnow().isoformat(),
            'status': 'active'
        }
        
        self.destruct_configs[config['id']] = config
        return config
    
    def set_download_limit(self, file_id: str, owner: str, max_downloads: int = 1) -> dict:
        """
        Set file to self-destruct after specified number of downloads
        """
        config = {
            'id': str(uuid.uuid4()),
            'file_id': file_id,
            'owner': owner,
            'type': 'download_limit',
            'download_count': 0,
            'max_downloads': max_downloads,
            'created_at': datetime.utcnow().isoformat(),
            'status': 'active'
        }
        
        self.destruct_configs[config['id']] = config
        return config
    
    def check_should_destruct(self, file_id: str) -> tuple:
        """
        Check if file should be destructed
        Returns: (should_destruct: bool, reason: str)
        """
        configs = [
            cfg for cfg in self.destruct_configs.values()
            if cfg['file_id'] == file_id and cfg['status'] == 'active'
        ]
        
        for config in configs:
            if config['type'] == 'time':
                expiry = datetime.fromisoformat(config['expiry'])
                if datetime.utcnow() > expiry:
                    return True, f"Time-based expiry reached"
            
            elif config['type'] == 'one_time':
                if config['access_count'] >= 1:
                    return True, f"One-time access already used"
            
            elif config['type'] == 'download_limit':
                if config['download_count'] >= config['max_downloads']:
                    return True, f"Download limit reached"
        
        return False, ""
    
    def record_access(self, file_id: str) -> bool:
        """
        Record a file access/download
        Returns: True if file should be kept, False if should destruct
        """
        configs = [
            cfg for cfg in self.destruct_configs.values()
            if cfg['file_id'] == file_id and cfg['status'] == 'active'
        ]
        
        for config in configs:
            if config['type'] == 'one_time':
                config['access_count'] += 1
            elif config['type'] == 'download_limit':
                config['download_count'] += 1
        
        should_destruct, _ = self.check_should_destruct(file_id)
        return not should_destruct
    
    def cancel_destruct(self, config_id: str, owner: str) -> bool:
        """
        Cancel self-destruct configuration
        """
        if config_id not in self.destruct_configs:
            raise ValueError(f"Config {config_id} not found")
        
        config = self.destruct_configs[config_id]
        
        if config['owner'] != owner:
            raise PermissionError(f"Only owner can cancel")
        
        config['status'] = 'cancelled'
        return True
