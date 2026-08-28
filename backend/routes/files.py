from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
from datetime import datetime
import hashlib

bp = Blueprint('files', __name__, url_prefix='/api/files')

# Mock database
files_db = {}
file_counter = 0

@bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    """
    Upload a file
    """
    current_user = get_jwt_identity()
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Read file content
    file_content = file.read()
    file_hash = hashlib.sha256(file_content).hexdigest()
    
    # Generate file ID
    global file_counter
    file_counter += 1
    file_id = f"file_{file_counter}"
    
    # Store file metadata
    files_db[file_id] = {
        'id': file_id,
        'filename': file.filename,
        'owner': current_user,
        'size': len(file_content),
        'hash': file_hash,
        'uploaded_at': datetime.utcnow().isoformat(),
        'content': file_content,
        'encrypted': False,
        'access_list': [current_user],
        'download_count': 0,
        'self_destruct': None
    }
    
    return jsonify({
        'message': 'File uploaded successfully',
        'file': {
            'id': file_id,
            'filename': file.filename,
            'size': len(file_content),
            'hash': file_hash,
            'uploaded_at': files_db[file_id]['uploaded_at']
        }
    }), 201

@bp.route('/list', methods=['GET'])
@jwt_required()
def list_files():
    """
    List all files for current user
    """
    current_user = get_jwt_identity()
    
    user_files = [
        {
            'id': file_id,
            'filename': file_data['filename'],
            'size': file_data['size'],
            'hash': file_data['hash'],
            'uploaded_at': file_data['uploaded_at'],
            'encrypted': file_data['encrypted'],
            'download_count': file_data['download_count']
        }
        for file_id, file_data in files_db.items()
        if current_user in file_data['access_list']
    ]
    
    return jsonify({
        'files': user_files,
        'total': len(user_files)
    }), 200

@bp.route('/download/<file_id>', methods=['GET'])
@jwt_required()
def download_file(file_id):
    """
    Download a file
    """
    current_user = get_jwt_identity()
    
    if file_id not in files_db:
        return jsonify({'error': 'File not found'}), 404
    
    file_data = files_db[file_id]
    
    # Check access
    if current_user not in file_data['access_list']:
        return jsonify({'error': 'Access denied'}), 403
    
    # Update download count
    file_data['download_count'] += 1
    
    return jsonify({
        'message': 'File download initiated',
        'file': {
            'id': file_id,
            'filename': file_data['filename'],
            'size': file_data['size'],
            'hash': file_data['hash']
        }
    }), 200

@bp.route('/delete/<file_id>', methods=['DELETE'])
@jwt_required()
def delete_file(file_id):
    """
    Delete a file (only owner can delete)
    """
    current_user = get_jwt_identity()
    
    if file_id not in files_db:
        return jsonify({'error': 'File not found'}), 404
    
    file_data = files_db[file_id]
    
    # Check ownership
    if current_user != file_data['owner']:
        return jsonify({'error': 'Only owner can delete'}), 403
    
    filename = file_data['filename']
    del files_db[file_id]
    
    return jsonify({
        'message': f'File {filename} deleted successfully'
    }), 200

@bp.route('/info/<file_id>', methods=['GET'])
@jwt_required()
def file_info(file_id):
    """
    Get file information
    """
    current_user = get_jwt_identity()
    
    if file_id not in files_db:
        return jsonify({'error': 'File not found'}), 404
    
    file_data = files_db[file_id]
    
    # Check access
    if current_user not in file_data['access_list']:
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify({
        'id': file_data['id'],
        'filename': file_data['filename'],
        'owner': file_data['owner'],
        'size': file_data['size'],
        'hash': file_data['hash'],
        'uploaded_at': file_data['uploaded_at'],
        'encrypted': file_data['encrypted'],
        'download_count': file_data['download_count'],
        'access_list': file_data['access_list'],
        'self_destruct': file_data['self_destruct']
    }), 200
