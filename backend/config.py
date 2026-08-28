import os
from datetime import timedelta

class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///secure_file_sharing.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # File Upload
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB max file size
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'zip', 'rar'}
    
    # Security
    ENCRYPTION_ALGORITHM = os.getenv('ENCRYPTION_ALGORITHM', 'AES-256')
    HASHING_ALGORITHM = os.getenv('HASHING_ALGORITHM', 'SHA-256')
    
    # Blockchain
    BLOCKCHAIN_PROVIDER = os.getenv('BLOCKCHAIN_PROVIDER', 'http://localhost:8545')
    CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS', '')
    
    # AI/ML
    ANOMALY_DETECTION_ENABLED = os.getenv('ANOMALY_DETECTION_ENABLED', 'true').lower() == 'true'
    
    # Self-Destruct
    SELF_DESTRUCT_ENABLED = os.getenv('SELF_DESTRUCT_ENABLED', 'true').lower() == 'true'
