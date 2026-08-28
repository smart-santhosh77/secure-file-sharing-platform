import React, { useState, useRef } from 'react';
import axios from 'axios';
import WebCryptoManager from '../utils/WebCryptoManager';
import './EncryptedFileUpload.css';

const EncryptedFileUpload = ({ onUploadSuccess }) => {
  const fileInputRef = useRef(null);
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [progress, setProgress] = useState(0);
  const [encryptionProgress, setEncryptionProgress] = useState('');

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      if (selectedFile.size > 500 * 1024 * 1024) {
        setError('File size exceeds 500MB limit');
        return;
      }
      setFile(selectedFile);
      setError('');
    }
  };

  const handleEncryptAndUpload = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Step 1: Generate AES key
      setEncryptionProgress('Generating encryption key...');
      const { derivedKey, salt } = await WebCryptoManager.deriveKeyFromPassword(
        'secure-password-change-this'
      );

      // Step 2: Generate IV
      const iv = window.crypto.getRandomValues(new Uint8Array(12));

      // Step 3: Encrypt file
      setEncryptionProgress('Encrypting file...');
      const fileBuffer = await file.arrayBuffer();
      const encryptedData = await window.crypto.subtle.encrypt(
        {
          name: 'AES-GCM',
          iv: iv,
        },
        derivedKey,
        fileBuffer
      );

      // Step 4: Hash original file
      setEncryptionProgress('Generating file hash...');
      const fileHash = await WebCryptoManager.hashFile(file);

      // Step 5: Upload encrypted file
      setEncryptionProgress('Uploading encrypted file...');
      const formData = new FormData();
      formData.append('file', file);
      formData.append('encrypted', 'true');
      formData.append('encryption_metadata', JSON.stringify({
        algorithm: 'AES-256-GCM',
        iv: WebCryptoManager.arrayBufferToBase64(iv),
        salt: WebCryptoManager.arrayBufferToBase64(salt),
      }));
      formData.append('file_hash', fileHash);

      const token = localStorage.getItem('access_token');
      const response = await axios.post(
        `${process.env.REACT_APP_API_URL}/api/files/upload`,
        formData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'multipart/form-data',
          },
          onUploadProgress: (progressEvent) => {
            const percentCompleted = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
            setProgress(percentCompleted);
          },
        }
      );

      // Step 6: Register encrypted file
      setEncryptionProgress('Registering encrypted file...');
      await axios.post(
        `${process.env.REACT_APP_API_URL}/api/encryption/register-encrypted-file`,
        {
          file_id: response.data.file.id,
          file_hash: fileHash,
          encryption_metadata: {
            algorithm: 'AES-256-GCM',
            iv: WebCryptoManager.arrayBufferToBase64(iv),
            salt: WebCryptoManager.arrayBufferToBase64(salt),
          },
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      onUploadSuccess(response.data.file);
      setFile(null);
      setProgress(0);
      setEncryptionProgress('');
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Encryption/Upload failed');
    } finally {
      setLoading(false);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      setFile(droppedFile);
      setError('');
    }
  };

  return (
    <div className="encrypted-file-upload">
      {error && <div className="alert error">{error}</div>}

      <div className="encryption-badge">🔐 End-to-End Encrypted</div>

      <div
        className="upload-area"
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      >
        <input
          ref={fileInputRef}
          type="file"
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />
        <div onClick={() => fileInputRef.current?.click()}>
          <p className="upload-icon">🔒</p>
          <p className="upload-text">
            {file ? file.name : 'Drag file here or click to select (Encrypted)'}
          </p>
          <p className="upload-subtext">Maximum file size: 500MB</p>
        </div>
      </div>

      {encryptionProgress && (
        <div className="encryption-status">
          <p>{encryptionProgress}</p>
        </div>
      )}

      {progress > 0 && progress < 100 && (
        <div className="progress-bar">
          <div className="progress" style={{ width: `${progress}%` }}>
            {progress}%
          </div>
        </div>
      )}

      <button
        onClick={handleEncryptAndUpload}
        disabled={!file || loading}
        className="upload-btn encrypted"
      >
        {loading
          ? `Encrypting & Uploading... ${progress}%`
          : 'Encrypt & Upload File'}
      </button>
    </div>
  );
};

export default EncryptedFileUpload;
