# Setup Instructions

## Prerequisites

- Python 3.8+
- Node.js 14+
- Docker & Docker Compose (optional)
- Git

## Phase 1: Core Web App Setup

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/smart-santhosh77/secure-file-sharing-platform.git
   cd secure-file-sharing-platform
   ```

2. **Setup Python virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp ../.env .env
   # Edit .env with your configuration
   ```

5. **Run the Flask app**
   ```bash
   python app.py
   ```
   
   Server runs on `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   REACT_APP_API_URL=http://localhost:5000
   ```

4. **Start the development server**
   ```bash
   npm start
   ```
   
   Application runs on `http://localhost:3000`

## Testing Phase 1

### Register a User
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'
```

### Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

### Get Profile
```bash
curl -X GET http://localhost:5000/api/auth/profile \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Docker Setup (Optional)

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Access services**
   - Frontend: `http://localhost:3000`
   - Backend: `http://localhost:5000`

## Phase 2: Encryption Setup (Coming Soon)

Web Crypto API integration for client-side encryption

## Phase 3: Blockchain Setup (Coming Soon)

1. **Install Ganache CLI**
   ```bash
   npm install -g ganache-cli
   ```

2. **Start local blockchain**
   ```bash
   ganache-cli
   ```

3. **Deploy contracts**
   ```bash
   cd blockchain
   npm install
   truffle migrate
   ```

## Phase 4: AI Setup (Coming Soon)

TensorFlow and Scikit-learn integration

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 5000
lsof -i :5000
# Kill process
kill -9 <PID>
```

### Database Issues
```bash
# Reset database
rm backend/secure_file_sharing.db
```

### CORS Errors
Ensure `CORS_ORIGINS` in `.env` includes your frontend URL

## Next Steps

1. Complete Phase 1 testing
2. Switch to `phase-2-encryption` branch
3. Implement Web Crypto API
4. Continue with remaining phases

## Support

For issues and questions, create a GitHub issue.
