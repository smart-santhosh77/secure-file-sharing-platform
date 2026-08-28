# Phase 3: Blockchain Integration

## Overview

Phase 3 implements Ethereum smart contracts to log all file operations (upload, access, sharing) on an immutable blockchain for audit trail and accountability.

## Features Implemented

✅ **Smart Contracts** - Solidity contracts for file logging  
✅ **Access Control** - Fine-grained permission management on-chain  
✅ **File Audit Trail** - Immutable log of all file operations  
✅ **Web3.js Integration** - Connect frontend to Ethereum  
✅ **Local Blockchain** - Ganache for local development  
✅ **Event Logging** - Blockchain events for real-time updates  

## Smart Contracts

### SecureFileSharing.sol

Main contract for file operation logging:

**Data Structures:**
- `FileRecord` - File metadata (hash, owner, upload time, encryption info)
- `AccessLog` - Access history (who accessed, when, action)
- `ShareRecord` - File sharing records (owner, recipient, expiry)

**Functions:**

```solidity
// Upload file
logFileUpload(
  bytes32 fileHash,
  string memory fileName,
  uint256 fileSize,
  string memory encryptionAlgorithm,
  bool isEncrypted
)

// Log access
logAccess(
  bytes32 fileHash,
  string memory action,
  bool success
)

// Share file
shareFile(
  bytes32 fileHash,
  address recipient,
  uint256 expiresAt,
  bool oneTimeAccess
)

// Revoke access
revokeAccess(bytes32 fileHash, address recipient)

// Query functions
getFileDetails(bytes32 fileHash)
getAccessLogs(bytes32 fileHash)
getShareRecords(bytes32 fileHash)
getUserFiles(address owner)
getStats()
```

### AccessControl.sol

Fine-grained access control contract:

**Functions:**

```solidity
// Grant permissions
grantPermission(
  bytes32 fileHash,
  address user,
  string[] memory permissions,
  uint256 expiresAt
)

// Revoke permissions
revokePermission(bytes32 fileHash, address user)

// Check permissions
hasUserPermission(
  bytes32 fileHash,
  address user,
  string memory permission
)
```

## Setup Instructions

### Prerequisites

```bash
# Install Node.js and npm
node --version
npm --version

# Install Truffle
npm install -g truffle

# Install Ganache CLI
npm install -g ganache-cli
```

### Deploy Locally

```bash
cd blockchain

# Install dependencies
npm install

# Start Ganache
ganache-cli --host 0.0.0.0 --port 8545

# In another terminal, compile contracts
truffle compile

# Deploy to local blockchain
truffle migrate

# Run interaction script
truffle exec scripts/interact.js --network development
```

### Output

```
Compiling your contracts...
==========================
✔ Compilation successful

Deploying contracts...
======================
✔ SecureFileSharing deployed at: 0x...
✔ AccessControl deployed at: 0x...

Network: development
Contract Address: 0x...
```

## Backend Integration

### Routes

```bash
# Connect to blockchain
POST /api/blockchain/integration/connect
{
  "contract_address": "0x...",
  "contract_abi": [...]
}

# Log file upload
POST /api/blockchain/integration/log-upload
{
  "file_hash": "0x...",
  "file_name": "document.pdf",
  "file_size": 1024000,
  "encryption_algorithm": "AES-256-GCM",
  "from_address": "0x...",
  "private_key": "0x..."
}

# Log file access
POST /api/blockchain/integration/log-access
{
  "file_hash": "0x...",
  "action": "download",
  "from_address": "0x...",
  "private_key": "0x..."
}

# Get blockchain status
GET /api/blockchain/integration/status
```

## Frontend Integration

### BlockchainIntegration.js

Browser-based Web3 integration:

```javascript
import BlockchainIntegration from './utils/BlockchainIntegration';

// Initialize
const blockchain = new BlockchainIntegration(
  window.ethereum,
  contractAddress,
  contractABI
);
await blockchain.initialize();

// Log file upload
await blockchain.logFileUpload(
  fileHash,
  'document.pdf',
  1024000,
  'AES-256-GCM'
);

// Log file access
await blockchain.logFileAccess(fileHash, 'download');

// Get file details
const details = await blockchain.getFileDetails(fileHash);

// Get access logs
const logs = await blockchain.getAccessLogs(fileHash);

// Share file
await blockchain.shareFile(
  fileHash,
  recipientAddress,
  expiresAt,
  oneTimeAccess
);
```

## Configuration

### .env

```env
# Blockchain
BLOCKCHAIN_PROVIDER=http://localhost:8545
CONTRACT_ADDRESS=0x...
CONTRACT_ABI=[...]

# For production
INFURA_API_KEY=...
ETHERSCAN_API_KEY=...
PRIVATE_KEY=...
```

## Security Considerations

⚠️ **Private Keys** - Never hardcode private keys. Use environment variables or secure vaults.  
⚠️ **Gas Costs** - Each operation incurs gas fees. Plan accordingly.  
⚠️ **Network** - Use testnet (Goerli, Sepolia) before mainnet.  
⚠️ **Contract Audit** - Have contracts audited before mainnet deployment.  

## Deployment to Mainnet

### Testnet (Goerli)

```bash
# Update truffle-config.js
goerli: {
  provider: () => new HDWalletProvider(PRIVATE_KEY, INFURA_URL),
  network_id: 5,
  gas: 4000000,
  gasPrice: 20000000000
}

# Deploy
truffle migrate --network goerli
```

## Events

Monitor smart contract events for real-time updates:

```javascript
// Watch FileUploaded events
contract.events.FileUploaded()
  .on('data', (event) => {
    console.log('File uploaded:', event.returnValues);
  })
  .on('error', (error) => {
    console.error('Error:', error);
  });
```

## Testing

```bash
# Run contract tests
truffle test

# Test coverage
npm install --save-dev solidity-coverage
truffle run coverage
```

## Next Steps

1. Deploy contracts to testnet
2. Connect frontend to deployed contracts
3. Test file logging workflows
4. Implement event listeners
5. Deploy to mainnet

## Resources

- [Truffle Documentation](https://trufflesuite.com/docs/)
- [Solidity Docs](https://docs.soliditylang.org/)
- [Web3.js Documentation](https://web3js.readthedocs.io/)
- [Ganache](https://trufflesuite.com/ganache/)
- [Ethereum Development](https://ethereum.org/developers)
