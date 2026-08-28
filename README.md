# Secure File Sharing Platform

A comprehensive cybersecurity project featuring end-to-end encryption, zero-knowledge storage, AI threat detection, self-destruct files, and blockchain logging.

## Features

✅ **End-to-End Encryption** - AES-256 encryption on client-side  
✅ **Zero-Knowledge Storage** - Server never sees plaintext  
✅ **AI Threat Detection** - Detect anomalous access patterns  
✅ **Self-Destruct Files** - Time-based, one-time, or download-limit expiry  
✅ **Blockchain Logs** - Immutable audit trail on distributed ledger  
✅ **Key Sharing** - Secure key distribution with expiry  
✅ **Access Control** - Fine-grained permission management  

## Project Structure

```
secure-file-sharing-platform/
├── backend/              # Flask API & Core Logic
├── frontend/             # React Web Application
├── blockchain/           # Smart Contracts (Solidity)
├── docker-compose.yml    # Docker Orchestration
├── .env                  # Environment Variables
└── README.md            # Documentation
```

## Phase 1: Core Web App

### Backend (Flask)
- User registration and authentication (JWT)
- File upload/download endpoints
- Permission management
- Blockchain event logging

### Frontend (React)
- User dashboard
- File upload interface
- Access control UI
- File download interface

### Getting Started

#### Backend Setup
```bash
cd backend
pip install -r requirements.txt
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

The API will be available at `http://localhost:5000`

#### API Endpoints

**Authentication**
- `POST /api/auth/register` - Register user
- `POST /api/auth/login` - Login user
- `POST /api/auth/refresh` - Refresh token
- `GET /api/auth/profile` - Get user profile
- `POST /api/auth/logout` - Logout

**Files**
- `POST /api/files/upload` - Upload file
- `GET /api/files/list` - List user files
- `GET /api/files/download/<file_id>` - Download file
- `DELETE /api/files/delete/<file_id>` - Delete file
- `GET /api/files/info/<file_id>` - Get file info

**Permissions**
- `POST /api/permissions/share` - Share file
- `DELETE /api/permissions/revoke/<permission_id>` - Revoke access
- `GET /api/permissions/list-shared` - List shared files
- `GET /api/permissions/received` - List received files

**Blockchain**
- `POST /api/blockchain/log-file-upload` - Log upload
- `POST /api/blockchain/log-file-access` - Log access
- `GET /api/blockchain/logs/<file_id>` - Get file logs
- `GET /api/blockchain/all-logs` - Get all logs

## Phase 2: Zero-Knowledge & Encryption

Implement Web Crypto API for client-side encryption:
- File encryption before upload
- Key generation and management
- Secure key exchange

## Phase 3: Blockchain Integration

Deploy Solidity smart contracts:
- File sharing contract
- Access control contract
- Event logging

## Phase 4: Advanced Security

Add AI and advanced features:
- Anomaly detection
- Unusual access patterns
- Intelligent threat detection

## Technologies

- **Backend**: Flask, Python, SQLAlchemy
- **Frontend**: React, Web Crypto API
- **Blockchain**: Solidity, Web3.js, Truffle
- **Security**: AES-256, RSA-2048, SHA-256
- **AI/ML**: TensorFlow, Scikit-learn
- **Deployment**: Docker, Docker Compose

## Contributing

Fork the repository and create a feature branch for your work.

## License

MIT License - See LICENSE file for details
