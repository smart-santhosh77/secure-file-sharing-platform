from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import hashlib
from web3 import Web3
from datetime import datetime

bp = Blueprint('blockchain_integration', __name__, url_prefix='/api/blockchain/integration')

# Initialize Web3 (configure with your provider)
w3 = Web3(Web3.HTTPProvider('http://localhost:8545'))
CONTRACT_ADDRESS = None  # Set after deployment
CONTRACT_ABI = None  # Set with contract ABI

class BlockchainLogger:
    def __init__(self):
        self.w3 = w3
        self.contract = None
        self.is_connected = False
    
    def initialize(self, contract_address, contract_abi):
        """Initialize blockchain connection"""
        try:
            self.contract = self.w3.eth.contract(address=contract_address, abi=contract_abi)
            self.is_connected = self.w3.is_connected()
            return self.is_connected
        except Exception as e:
            print(f"Error initializing blockchain: {e}")
            return False
    
    def log_file_upload(self, file_hash, file_name, file_size, encryption_algo, from_address, private_key):
        """Log file upload to blockchain"""
        try:
            if not self.contract:
                return None
            
            # Build transaction
            tx = self.contract.functions.logFileUpload(
                bytes.fromhex(file_hash[2:]) if file_hash.startswith('0x') else bytes.fromhex(file_hash),
                file_name,
                file_size,
                encryption_algo,
                True
            ).build_transaction({
                'from': from_address,
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(from_address),
            })
            
            # Sign and send
            signed_tx = self.w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            return {
                'tx_hash': self.w3.to_hex(tx_hash),
                'status': 'pending'
            }
        except Exception as e:
            print(f"Error logging file upload: {e}")
            return None
    
    def log_file_access(self, file_hash, action, from_address, private_key):
        """Log file access to blockchain"""
        try:
            if not self.contract:
                return None
            
            # Build transaction
            tx = self.contract.functions.logAccess(
                bytes.fromhex(file_hash[2:]) if file_hash.startswith('0x') else bytes.fromhex(file_hash),
                action,
                True
            ).build_transaction({
                'from': from_address,
                'gas': 150000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(from_address),
            })
            
            # Sign and send
            signed_tx = self.w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            return {
                'tx_hash': self.w3.to_hex(tx_hash),
                'status': 'pending'
            }
        except Exception as e:
            print(f"Error logging file access: {e}")
            return None

blockchain_logger = BlockchainLogger()

@bp.route('/connect', methods=['POST'])
@jwt_required()
def connect_blockchain():
    """
    Connect to blockchain and initialize contract
    POST: {"contract_address": "0x...", "contract_abi": [...]}
    """
    current_user = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('contract_address'):
        return jsonify({'error': 'Missing contract address'}), 400
    
    contract_address = data['contract_address']
    contract_abi = data.get('contract_abi', [])
    
    try:
        connected = blockchain_logger.initialize(contract_address, contract_abi)
        
        if connected:
            return jsonify({
                'message': 'Connected to blockchain',
                'network_id': blockchain_logger.w3.net.version,
                'latest_block': blockchain_logger.w3.eth.block_number
            }), 200
        else:
            return jsonify({'error': 'Failed to connect to blockchain'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/log-upload', methods=['POST'])
@jwt_required()
def log_upload():
    """
    Log file upload to blockchain
    POST: {"file_hash": "...", "file_name": "...", "file_size": 1024, ...}
    """
    current_user = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('file_hash'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        file_hash = data['file_hash']
        file_name = data['file_name']
        file_size = data['file_size']
        encryption_algo = data.get('encryption_algorithm', 'AES-256-GCM')
        
        # Log to blockchain (requires user's wallet setup)
        result = blockchain_logger.log_file_upload(
            file_hash,
            file_name,
            file_size,
            encryption_algo,
            data.get('from_address'),
            data.get('private_key')  # Should be handled securely
        )
        
        if result:
            return jsonify({
                'message': 'File upload logged to blockchain',
                'transaction': result
            }), 201
        else:
            return jsonify({'error': 'Failed to log to blockchain'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/log-access', methods=['POST'])
@jwt_required()
def log_access():
    """
    Log file access to blockchain
    POST: {"file_hash": "...", "action": "download", ...}
    """
    current_user = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('file_hash'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        result = blockchain_logger.log_file_access(
            data['file_hash'],
            data.get('action', 'access'),
            data.get('from_address'),
            data.get('private_key')
        )
        
        if result:
            return jsonify({
                'message': 'File access logged to blockchain',
                'transaction': result
            }), 201
        else:
            return jsonify({'error': 'Failed to log to blockchain'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/status', methods=['GET'])
@jwt_required()
def blockchain_status():
    """
    Get blockchain connection status
    """
    try:
        return jsonify({
            'connected': blockchain_logger.is_connected,
            'network_id': blockchain_logger.w3.net.version if blockchain_logger.is_connected else None,
            'latest_block': blockchain_logger.w3.eth.block_number if blockchain_logger.is_connected else None
        }), 200
    except Exception as e:
        return jsonify({
            'connected': False,
            'error': str(e)
        }), 400
