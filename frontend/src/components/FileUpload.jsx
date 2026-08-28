import React, { useRef, useState } from 'react';
import axios from 'axios';
import './FileUpload.css';

const FileUpload = ({ onUploadSuccess }) => {
  const fileInputRef = useRef(null);
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [progress, setProgress] = useState(0);

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

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('file', file);

      const token = localStorage.getItem('access_token');
      const response = await axios.post(
        `${process.env.REACT_APP_API_URL}/api/files/upload`,
        formData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          },
          onUploadProgress: (progressEvent) => {
            const percentCompleted = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
            setProgress(percentCompleted);
          }
        }
      );

      onUploadSuccess(response.data.file);
      setFile(null);
      setProgress(0);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Upload failed');
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
    <div className="file-upload">
      {error && <div className="alert error">{error}</div>}

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
          <p className="upload-icon">📁</p>
          <p className="upload-text">
            {file ? file.name : 'Drag file here or click to select'}
          </p>
          <p className="upload-subtext">
            Maximum file size: 500MB
          </p>
        </div>
      </div>

      {progress > 0 && progress < 100 && (
        <div className="progress-bar">
          <div className="progress" style={{ width: `${progress}%` }}>
            {progress}%
          </div>
        </div>
      )}

      <button
        onClick={handleUpload}
        disabled={!file || loading}
        className="upload-btn"
      >
        {loading ? `Uploading... ${progress}%` : 'Upload File'}
      </button>
    </div>
  );
};

export default FileUpload;
