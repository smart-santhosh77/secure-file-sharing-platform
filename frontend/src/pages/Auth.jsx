import React, { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Auth.css';

const Auth = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isLogin) {
        // Login
        const response = await axios.post(
          `${process.env.REACT_APP_API_URL}/api/auth/login`,
          {
            username: formData.username,
            password: formData.password
          }
        );
        
        // Store tokens
        localStorage.setItem('access_token', response.data.access_token);
        localStorage.setItem('refresh_token', response.data.refresh_token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
        
        navigate('/dashboard');
      } else {
        // Register
        if (formData.password !== formData.confirmPassword) {
          setError('Passwords do not match');
          setLoading(false);
          return;
        }

        const response = await axios.post(
          `${process.env.REACT_APP_API_URL}/api/auth/register`,
          {
            username: formData.username,
            email: formData.email,
            password: formData.password
          }
        );
        
        setFormData({
          username: '',
          email: '',
          password: '',
          confirmPassword: ''
        });
        setIsLogin(true);
        setError('Registration successful! Please login.');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1>{isLogin ? 'Login' : 'Register'}</h1>
        
        {error && <div className={`alert ${isLogin && error.includes('successful') ? 'success' : 'error'}`}>{error}</div>}
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Username</label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              required
            />
          </div>

          {!isLogin && (
            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
              />
            </div>
          )}

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
            />
          </div>

          {!isLogin && (
            <div className="form-group">
              <label>Confirm Password</label>
              <input
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                required
              />
            </div>
          )}

          <button type="submit" disabled={loading}>
            {loading ? 'Processing...' : isLogin ? 'Login' : 'Register'}
          </button>
        </form>

        <p className="toggle-auth">
          {isLogin ? "Don't have an account?" : 'Already have an account?'}
          <button type="button" onClick={() => setIsLogin(!isLogin)}>
            {isLogin ? 'Register here' : 'Login here'}
          </button>
        </p>
      </div>
    </div>
  );
};

export default Auth;
