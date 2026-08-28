from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta

bp = Blueprint('permissions', __name__, url_prefix='/api/permissions')

# Reference to files_db (would be imported in production)
permissions_db = {}

@bp.route('/share', methods=['POST'])
@jwt_required()
def share_file():
    """
    Share a file with another user
    Expected JSON: {"file_id": "file_1", "username": "user2", "expiry_days": 7, "one_time": false}
    """
    current_user = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('file_id') or not data.get('username'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    file_id = data['file_id']
    username = data['username']
    expiry_days = data.get('expiry_days', 7)
    one_time = data.get('one_time', False)
    
    # In production, check if file exists and user owns it
    # For now, create permission record
    
    permission_id = f"perm_{file_id}_{username}"
    expiry_time = datetime.utcnow() + timedelta(days=expiry_days)
    
    permissions_db[permission_id] = {
        'id': permission_id,
        'file_id': file_id,
        'shared_by': current_user,
        'shared_with': username,
        'created_at': datetime.utcnow().isoformat(),
        'expiry': expiry_time.isoformat(),
        'one_time': one_time,
        'accessed': False
    }
    
    return jsonify({
        'message': 'File shared successfully',
        'permission': {
            'id': permission_id,
            'file_id': file_id,
            'shared_with': username,
            'expiry': expiry_time.isoformat(),
            'one_time': one_time
        }
    }), 201

@bp.route('/revoke/<permission_id>', methods=['DELETE'])
@jwt_required()
def revoke_access(permission_id):
    """
    Revoke access to a shared file
    """
    current_user = get_jwt_identity()
    
    if permission_id not in permissions_db:
        return jsonify({'error': 'Permission not found'}), 404
    
    permission = permissions_db[permission_id]
    
    # Check if current user is the one who shared
    if permission['shared_by'] != current_user:
        return jsonify({'error': 'Only sharer can revoke'}), 403
    
    del permissions_db[permission_id]
    
    return jsonify({
        'message': 'Access revoked successfully'
    }), 200

@bp.route('/list-shared', methods=['GET'])
@jwt_required()
def list_shared():
    """
    List all files shared by current user
    """
    current_user = get_jwt_identity()
    
    shared_files = [
        {
            'id': perm['id'],
            'file_id': perm['file_id'],
            'shared_with': perm['shared_with'],
            'expiry': perm['expiry'],
            'one_time': perm['one_time'],
            'accessed': perm['accessed']
        }
        for perm_id, perm in permissions_db.items()
        if perm['shared_by'] == current_user
    ]
    
    return jsonify({
        'shared_files': shared_files,
        'total': len(shared_files)
    }), 200

@bp.route('/received', methods=['GET'])
@jwt_required()
def list_received():
    """
    List all files shared with current user
    """
    current_user = get_jwt_identity()
    
    received_files = [
        {
            'id': perm['id'],
            'file_id': perm['file_id'],
            'shared_by': perm['shared_by'],
            'expiry': perm['expiry'],
            'one_time': perm['one_time'],
            'accessed': perm['accessed']
        }
        for perm_id, perm in permissions_db.items()
        if perm['shared_with'] == current_user
    ]
    
    return jsonify({
        'received_files': received_files,
        'total': len(received_files)
    }), 200
