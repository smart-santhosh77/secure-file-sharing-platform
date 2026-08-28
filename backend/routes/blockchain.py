from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import hashlib

bp = Blueprint('blockchain', __name__, url_prefix='/api/blockchain')

# Mock blockchain events
blockchain_logs = []

@bp.route('/log-file-upload', methods=['POST'])
@jwt_required()
def log_file_upload():
    """
    Log file upload to blockchain
    Expected JSON: {"file_id": "file_1", "file_hash": "abc123", "filename": "document.pdf"}
    """
    current_user = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('file_id') or not data.get('file_hash'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    file_id = data['file_id']
    file_hash = data['file_hash']
    filename = data.get('filename', 'unknown')
    
    # Create blockchain log entry
    log_entry = {
        'id': len(blockchain_logs) + 1,
        'type': 'FILE_UPLOAD',
        'user': current_user,
        'file_id': file_id,
        'file_hash': file_hash,
        'filename': filename,
        'timestamp': datetime.utcnow().isoformat(),
        'transaction_hash': hashlib.sha256(f"{file_id}{file_hash}{current_user}".encode()).hexdigest(),
        'block_number': len(blockchain_logs) + 1
    }
    
    blockchain_logs.append(log_entry)
    
    return jsonify({
        'message': 'File upload logged to blockchain',
        'log': log_entry
    }), 201

@bp.route('/log-file-access', methods=['POST'])
@jwt_required()
def log_file_access():
    """
    Log file access to blockchain
    Expected JSON: {"file_id": "file_1", "file_hash": "abc123", "action": "download"}
    """
    current_user = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('file_id') or not data.get('file_hash'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    file_id = data['file_id']
    file_hash = data['file_hash']
    action = data.get('action', 'access')
    
    # Create blockchain log entry
    log_entry = {
        'id': len(blockchain_logs) + 1,
        'type': 'FILE_ACCESS',
        'user': current_user,
        'file_id': file_id,
        'file_hash': file_hash,
        'action': action,
        'timestamp': datetime.utcnow().isoformat(),
        'transaction_hash': hashlib.sha256(f"{file_id}{action}{current_user}".encode()).hexdigest(),
        'block_number': len(blockchain_logs) + 1
    }
    
    blockchain_logs.append(log_entry)
    
    return jsonify({
        'message': 'File access logged to blockchain',
        'log': log_entry
    }), 201

@bp.route('/logs/<file_id>', methods=['GET'])
@jwt_required()
def get_file_logs(file_id):
    """
    Get blockchain logs for a specific file
    """
    current_user = get_jwt_identity()
    
    file_logs = [
        log for log in blockchain_logs
        if log['file_id'] == file_id and (log['user'] == current_user or True)  # Add ownership check
    ]
    
    return jsonify({
        'file_id': file_id,
        'logs': file_logs,
        'total': len(file_logs)
    }), 200

@bp.route('/all-logs', methods=['GET'])
@jwt_required()
def get_all_logs():
    """
    Get all blockchain logs for current user
    """
    current_user = get_jwt_identity()
    
    user_logs = [
        log for log in blockchain_logs
        if log['user'] == current_user
    ]
    
    return jsonify({
        'logs': user_logs,
        'total': len(user_logs)
    }), 200
