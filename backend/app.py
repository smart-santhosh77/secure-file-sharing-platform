from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os
from config import Config
from routes import auth, files, permissions, blockchain

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
CORS(app)
jwt = JWTManager(app)

# Register blueprints
app.register_blueprint(auth.bp)
app.register_blueprint(files.bp)
app.register_blueprint(permissions.bp)
app.register_blueprint(blockchain.bp)

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'message': 'Secure File Sharing Platform is running'}), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not Found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal Server Error'}), 500

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_ENV') == 'development', host='0.0.0.0', port=5000)
