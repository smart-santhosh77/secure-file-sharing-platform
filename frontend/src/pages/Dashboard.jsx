import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import FileUpload from '../components/FileUpload';
import FileList from '../components/FileList';
import './Dashboard.css';

const Dashboard = () => {
  const [user, setUser] = useState(null);
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (!storedUser) {
      navigate('/login');
      return;
    }
    setUser(JSON.parse(storedUser));
    fetchFiles();
  }, [navigate]);

  const fetchFiles = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(
        `${process.env.REACT_APP_API_URL}/api/files/list`,
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );
      setFiles(response.data.files);
    } catch (err) {
      setError('Failed to fetch files');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  const handleFileUpload = async (newFile) => {
    setFiles(prev => [newFile, ...prev]);
  };

  const handleFileDelete = async (fileId) => {
    try {
      const token = localStorage.getItem('access_token');
      await axios.delete(
        `${process.env.REACT_APP_API_URL}/api/files/delete/${fileId}`,
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );
      setFiles(prev => prev.filter(f => f.id !== fileId));
    } catch (err) {
      setError('Failed to delete file');
    }
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="dashboard-container">
      <nav className="navbar">
        <div className="navbar-brand">
          <h2>🔒 Secure File Sharing</h2>
        </div>
        <div className="navbar-user">
          <span>Welcome, {user?.username}!</span>
          <button onClick={handleLogout} className="logout-btn">Logout</button>
        </div>
      </nav>

      <div className="dashboard-content">
        {error && <div className="alert error">{error}</div>}

        <div className="dashboard-section">
          <h3>Upload New File</h3>
          <FileUpload onUploadSuccess={handleFileUpload} />
        </div>

        <div className="dashboard-section">
          <h3>Your Files ({files.length})</h3>
          {files.length === 0 ? (
            <p className="empty-state">No files uploaded yet. Upload your first file to get started!</p>
          ) : (
            <FileList files={files} onDelete={handleFileDelete} />
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
