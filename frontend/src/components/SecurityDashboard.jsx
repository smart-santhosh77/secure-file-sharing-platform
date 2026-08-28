import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './SecurityDashboard.css';

const SecurityDashboard = () => {
  const [dashboard, setDashboard] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchSecurityData();
    // Refresh every 30 seconds
    const interval = setInterval(fetchSecurityData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchSecurityData = async () => {
    try {
      const token = localStorage.getItem('access_token');
      
      const [dashboardRes, alertsRes] = await Promise.all([
        axios.get(
          `${process.env.REACT_APP_API_URL}/api/security/security-dashboard`,
          { headers: { Authorization: `Bearer ${token}` } }
        ),
        axios.get(
          `${process.env.REACT_APP_API_URL}/api/security/get-alerts`,
          { headers: { Authorization: `Bearer ${token}` } }
        )
      ]);

      setDashboard(dashboardRes.data);
      setAlerts(alertsRes.data.alerts);
      setError('');
    } catch (err) {
      setError('Failed to fetch security data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading security data...</div>;
  }

  if (!dashboard) {
    return <div className="error">{error}</div>;
  }

  const getRiskLevelColor = (level) => {
    switch (level) {
      case 'CRITICAL':
        return '#e53935';
      case 'HIGH':
        return '#fb8c00';
      case 'MEDIUM':
        return '#fdd835';
      case 'LOW':
        return '#43a047';
      default:
        return '#666';
    }
  };

  return (
    <div className="security-dashboard">
      <h2>🛡️ Security Dashboard</h2>

      {/* Risk Level Card */}
      <div className="risk-card" style={{ borderLeft: `5px solid ${getRiskLevelColor(dashboard.overall_risk_level)}` }}>
        <div className="risk-info">
          <h3>Overall Risk Level</h3>
          <p className="risk-level" style={{ color: getRiskLevelColor(dashboard.overall_risk_level) }}>
            {dashboard.overall_risk_level}
          </p>
        </div>
      </div>

      {/* Statistics Grid */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{dashboard.statistics.total_accesses}</div>
          <div className="stat-label">Total Accesses</div>
        </div>
        <div className="stat-card warning">
          <div className="stat-value">{dashboard.statistics.high_risk_accesses}</div>
          <div className="stat-label">High Risk Accesses</div>
        </div>
        <div className="stat-card danger">
          <div className="stat-value">{dashboard.statistics.critical_alerts}</div>
          <div className="stat-label">Critical Alerts</div>
        </div>
        <div className="stat-card warning">
          <div className="stat-value">{dashboard.statistics.high_alerts}</div>
          <div className="stat-label">High Alerts</div>
        </div>
      </div>

      {/* Recent Alerts */}
      <div className="alerts-section">
        <h3>Recent Security Alerts</h3>
        {alerts.length === 0 ? (
          <p className="no-alerts">✓ No security alerts detected</p>
        ) : (
          <div className="alerts-list">
            {alerts.map((alert, index) => (
              <div key={index} className={`alert-item alert-${alert.risk_level.toLowerCase()}`}>
                <div className="alert-header">
                  <span className="alert-title">{alert.file_id}</span>
                  <span className="alert-risk" style={{ color: getRiskLevelColor(alert.risk_level) }}>
                    {alert.risk_level}
                  </span>
                </div>
                <div className="alert-body">
                  <p><strong>Access Type:</strong> {alert.access_type}</p>
                  <p><strong>Timestamp:</strong> {new Date(alert.timestamp).toLocaleString()}</p>
                  <div className="alert-recommendations">
                    <strong>Recommendations:</strong>
                    <ul>
                      {alert.recommendations.map((rec, i) => (
                        <li key={i}>{rec}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default SecurityDashboard;
