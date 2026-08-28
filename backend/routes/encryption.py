from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import json
from modules.webcrypto import WebCryptoAPI
from modules.client_encryption import ClientEncryptionManager

bp = Blueprint('encryption', __name__, url_prefix='/api/encryption')
encryption_manager = ClientEncryptionManager()

@bp.route('/generate-keypair', methods=['POST'])
@jwt_required()
def generate_keypair():
    """
    Generate RSA keypair for user
    POST: {}
    """
    current_user = get_jwt_identity()
    
    keypair = WebCryptoAPI.generate_rsa_keypair()
    
    return jsonify({
        'message': 'Keypair generated successfully',
        'keypair': {
            'public_key': keypair['public_key'],
            'algorithm': keypair['algorithm'],
            'key_size': keypair['key_size']
        }
    }), 200

@bp.route('/generate-aes-key', methods=['POST'])
@jwt_required()
def generate_aes_key():
    """
    Generate AES key for file encryption
    POST: {"key_length": 256}
    """
    current_user = get_jwt_identity()
    data = request.get_json() or {}
    key_length = data.get('key_length', 256)
    
    if key_length not in [128, 192, 256]:
        return jsonify({'error': 'Invalid key length. Use 128, 192, or 256'}), 400
    
    aes_key = WebCryptoAPI.generate_aes_key(key_length)
    
    return jsonify({
        'message': 'AES key generated successfully',
        'key': aes_key.hex(),
        'key_length': key_length,
        'algorithm': 'AES-GCM'
    }), 200

@bp.route('/register-encrypted-file', methods=['POST'])
@jwt_required()
def register_encrypted_file():
    """
    Register an encrypted file in the system
    POST: {
        "file_id": "file_1",
        "file_hash": "abc123...",
        "encryption_metadata": {
            "algorithm": "AES-256-GCM",
            "iv": "...",
            "salt": "..."
        }
    }
    """
    current_user = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('file_id') or not data.get('file_hash'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    file_id = data['file_id']
    file_hash = data['file_hash']
    encryption_metadata = data.get('encryption_metadata', {})
    
    try:
        file_record = encryption_manager.register_encrypted_file(
            file_id, current_user, file_hash, encryption_metadata
        )
        
        return jsonify({
            'message': 'Encrypted file registered successfully',
            'file_record': file_record
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/store-encrypted-key', methods=['POST'])
@jwt_required()
def store_encrypted_key():
    """
    Store encrypted AES key for sharing
    POST: {
        "file_id": "file_1",
        "recipient_user": "user2",
        "encrypted_key": "...",
        "key_metadata": {...}
    }
    """
    current_user = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('file_id') or not data.get('recipient_user'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        key_record = encryption_manager.store_encrypted_key(
            data['file_id'],
            data['recipient_user'],
            data['encrypted_key'],
            data.get('key_metadata', {})
        )
        
        return jsonify({
            'message': 'Encrypted key stored successfully',
            'key_record': key_record
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/get-encrypted-key/<key_id>', methods=['GET'])
@jwt_required()
def get_encrypted_key(key_id):
    """
    Retrieve encrypted key for decryption
    """
    current_user = get_jwt_identity()
    
    try:
        encrypted_key = encryption_manager.get_encrypted_key(key_id, current_user)
        
        return jsonify({
            'encrypted_key': encrypted_key,
            'key_id': key_id
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except PermissionError as e:
        return jsonify({'error': str(e)}), 403

@bp.route('/file-encryption-info/<file_id>', methods=['GET'])
@jwt_required()
def get_file_encryption_info(file_id):
    """
    Get encryption metadata for a file
    """
    current_user = get_jwt_identity()
    
    try:
        info = encryption_manager.get_file_encryption_info(file_id, current_user)
        return jsonify(info), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except PermissionError as e:
        return jsonify({'error': str(e)}), 403

@bp.route('/list-encrypted-files', methods=['GET'])
@jwt_required()
def list_encrypted_files():
    """
    List all encrypted files for current user
    """
    current_user = get_jwt_identity()
    
    files = encryption_manager.list_encrypted_files(current_user)
    
    return jsonify({
        'files': files,
        'total': len(files)
    }), 200
