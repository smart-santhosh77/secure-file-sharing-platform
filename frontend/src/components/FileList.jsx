import React from 'react';
import axios from 'axios';
import './FileList.css';

const FileList = ({ files, onDelete }) => {
  const handleDownload = async (fileId, filename) => {
    try {
      const token = localStorage.getItem('access_token');
      await axios.get(
        `${process.env.REACT_APP_API_URL}/api/files/download/${fileId}`,
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );
      // In a real app, this would trigger a file download
      alert(`Download initiated for ${filename}`);
    } catch (err) {
      alert('Download failed');
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div className="file-list">
      <table>
        <thead>
          <tr>
            <th>Filename</th>
            <th>Size</th>
            <th>Uploaded</th>
            <th>Downloads</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {files.map(file => (
            <tr key={file.id}>
              <td className="filename">
                <span className="file-icon">📄</span>
                {file.filename}
              </td>
              <td>{formatFileSize(file.size)}</td>
              <td>{formatDate(file.uploaded_at)}</td>
              <td>{file.download_count}</td>
              <td className="actions">
                <button
                  onClick={() => handleDownload(file.id, file.filename)}
                  className="btn-download"
                >
                  Download
                </button>
                <button
                  onClick={() => onDelete(file.id)}
                  className="btn-delete"
                >
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default FileList;
