import axios from 'axios';
import Web3 from 'web3';
import contract from '@truffle/contract';

/**
 * BlockchainIntegration
 * Manages interaction with Ethereum blockchain for file logging
 */
class BlockchainIntegration {
  constructor(web3Provider = null, contractAddress = null, contractABI = null) {
    this.web3 = web3Provider ? new Web3(web3Provider) : null;
    this.contractAddress = contractAddress;
    this.contractABI = contractABI;
    this.contract = null;
    this.initialized = false;
  }

  /**
   * Initialize blockchain connection
   */
  async initialize() {
    if (!this.web3) {
      this.web3 = new Web3(window.ethereum || 'http://localhost:8545');
    }

    if (this.contractAddress && this.contractABI) {
      this.contract = new this.web3.eth.Contract(this.contractABI, this.contractAddress);
      this.initialized = true;
      console.log('Blockchain integration initialized');
      return true;
    }
    return false;
  }

  /**
   * Get user's connected wallet address
   */
  async getConnectedAddress() {
    if (window.ethereum) {
      const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
      return accounts[0];
    }
    return null;
  }

  /**
   * Log file upload to blockchain
   */
  async logFileUpload(fileHash, fileName, fileSize, encryptionAlgorithm = 'AES-256-GCM') {
    if (!this.initialized) {
      console.error('Blockchain not initialized');
      return null;
    }

    try {
      const userAddress = await this.getConnectedAddress();
      
      const txHash = await this.contract.methods
        .logFileUpload(
          fileHash,
          fileName,
          fileSize,
          encryptionAlgorithm,
          true // isEncrypted
        )
        .send({ from: userAddress });

      console.log('File upload logged:', txHash);
      return {
        success: true,
        transactionHash: txHash.transactionHash,
        blockNumber: txHash.blockNumber,
      };
    } catch (error) {
      console.error('Error logging file upload:', error);
      return {
        success: false,
        error: error.message,
      };
    }
  }

  /**
   * Log file access to blockchain
   */
  async logFileAccess(fileHash, action = 'download') {
    if (!this.initialized) {
      console.error('Blockchain not initialized');
      return null;
    }

    try {
      const userAddress = await this.getConnectedAddress();
      
      const txHash = await this.contract.methods
        .logAccess(fileHash, action, true)
        .send({ from: userAddress });

      console.log('File access logged:', txHash);
      return {
        success: true,
        transactionHash: txHash.transactionHash,
        blockNumber: txHash.blockNumber,
      };
    } catch (error) {
      console.error('Error logging file access:', error);
      return {
        success: false,
        error: error.message,
      };
    }
  }

  /**
   * Share file with another user
   */
  async shareFile(fileHash, recipientAddress, expiresAt = 0, oneTimeAccess = false) {
    if (!this.initialized) {
      console.error('Blockchain not initialized');
      return null;
    }

    try {
      const userAddress = await this.getConnectedAddress();
      
      const txHash = await this.contract.methods
        .shareFile(fileHash, recipientAddress, expiresAt, oneTimeAccess)
        .send({ from: userAddress });

      console.log('File shared:', txHash);
      return {
        success: true,
        transactionHash: txHash.transactionHash,
        blockNumber: txHash.blockNumber,
      };
    } catch (error) {
      console.error('Error sharing file:', error);
      return {
        success: false,
        error: error.message,
      };
    }
  }

  /**
   * Get file details from blockchain
   */
  async getFileDetails(fileHash) {
    if (!this.initialized) {
      console.error('Blockchain not initialized');
      return null;
    }

    try {
      const fileDetails = await this.contract.methods.getFileDetails(fileHash).call();
      return {
        owner: fileDetails.owner,
        fileName: fileDetails.fileName,
        fileSize: fileDetails.fileSize,
        uploadTime: fileDetails.uploadTime,
        encryptionAlgorithm: fileDetails.encryptionAlgorithm,
        isEncrypted: fileDetails.isEncrypted,
        accessCount: fileDetails.accessCount,
      };
    } catch (error) {
      console.error('Error getting file details:', error);
      return null;
    }
  }

  /**
   * Get access logs for a file
   */
  async getAccessLogs(fileHash) {
    if (!this.initialized) {
      console.error('Blockchain not initialized');
      return null;
    }

    try {
      const logs = await this.contract.methods.getAccessLogs(fileHash).call();
      return logs.map(log => ({
        accessor: log.accessor,
        action: log.action,
        timestamp: log.timestamp,
        success: log.success,
      }));
    } catch (error) {
      console.error('Error getting access logs:', error);
      return null;
    }
  }

  /**
   * Revoke file access
   */
  async revokeAccess(fileHash, recipientAddress) {
    if (!this.initialized) {
      console.error('Blockchain not initialized');
      return null;
    }

    try {
      const userAddress = await this.getConnectedAddress();
      
      const txHash = await this.contract.methods
        .revokeAccess(fileHash, recipientAddress)
        .send({ from: userAddress });

      console.log('Access revoked:', txHash);
      return {
        success: true,
        transactionHash: txHash.transactionHash,
        blockNumber: txHash.blockNumber,
      };
    } catch (error) {
      console.error('Error revoking access:', error);
      return {
        success: false,
        error: error.message,
      };
    }
  }

  /**
   * Get contract statistics
   */
  async getStats() {
    if (!this.initialized) {
      console.error('Blockchain not initialized');
      return null;
    }

    try {
      const stats = await this.contract.methods.getStats().call();
      return {
        totalFiles: stats[0],
        totalAccesses: stats[1],
      };
    } catch (error) {
      console.error('Error getting stats:', error);
      return null;
    }
  }
}

export default BlockchainIntegration;
