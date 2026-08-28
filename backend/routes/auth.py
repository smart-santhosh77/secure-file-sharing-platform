from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Mock database - replace with actual DB
users_db = {}

@bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    Expected JSON: {"username": "user", "email": "user@example.com", "password": "password"}
    """
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    username = data['username']
    email = data['email']
    password = data['password']
    
    # Check if user already exists
    if username in users_db:
        return jsonify({'error': 'User already exists'}), 409
    
    # Hash password
    hashed_password = generate_password_hash(password)
    
    # Store user
    users_db[username] = {
        'username': username,
        'email': email,
        'password': hashed_password,
        'created_at': datetime.utcnow().isoformat(),
        'files': [],
        'shared_with': []
    }
    
    return jsonify({
        'message': 'User registered successfully',
        'user': {
            'username': username,
            'email': email
        }
    }), 201

@bp.route('/login', methods=['POST'])
def login():
    """
    Login user and return JWT tokens
    Expected JSON: {"username": "user", "password": "password"}
    """
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Missing username or password'}), 400
    
    username = data['username']
    password = data['password']
    
    # Check if user exists
    if username not in users_db:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    user = users_db[username]
    
    # Check password
    if not check_password_hash(user['password'], password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Create tokens
    access_token = create_access_token(identity=username)
    refresh_token = create_refresh_token(identity=username)
    
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': {
            'username': username,
            'email': user['email']
        }
    }), 200

@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh access token using refresh token
    """
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    return jsonify({'access_token': access_token}), 200

@bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    """
    Get current user profile
    """
    current_user = get_jwt_identity()
    
    if current_user not in users_db:
        return jsonify({'error': 'User not found'}), 404
    
    user = users_db[current_user]
    return jsonify({
        'username': user['username'],
        'email': user['email'],
        'created_at': user['created_at'],
        'file_count': len(user['files'])
    }), 200

@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Logout user (token invalidation handled by client)
    """
    return jsonify({'message': 'Logout successful'}), 200
