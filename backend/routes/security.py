from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from modules.anomaly_detector import AnomalyDetector
from datetime import datetime
import json

bp = Blueprint('security', __name__, url_prefix='/api/security')

# Initialize anomaly detector
detector = AnomalyDetector(contamination=0.1)
detector.train_on_default_profile()

# Store access history per user
access_history = {}
alerts = {}

@bp.route('/analyze-access', methods=['POST'])
@jwt_required()
def analyze_access():
    """
    Analyze file access for anomalies
    POST: {
        "file_id": "file_1",
        "action": "download",
        "file_size": 1024000,
        "ip_address": "192.168.1.1"
    }
    """
    current_user = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('file_id'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        # Prepare access data
        access_data = {
            'user_id': current_user,
            'file_id': data['file_id'],
            'file_size': data.get('file_size', 0),
            'action': data.get('action', 'access'),
            'ip_address': data.get('ip_address', ''),
            'timestamp': datetime.utcnow().isoformat(),
            'access_count_24h': data.get('access_count_24h', 0),
            'geo_anomaly_score': data.get('geo_anomaly_score', 0),
            'device_anomaly_score': data.get('device_anomaly_score', 0)
        }
        
        # Get user history
        if current_user not in access_history:
            access_history[current_user] = []
        
        user_history = access_history[current_user]
        
        # Perform anomaly detection
        is_anomalous, anomaly_score = detector.predict(access_data)
        
        # Detect bulk download
        bulk_download, _ = detector.detect_bulk_download(user_history, time_window_minutes=60)
        
        # Detect failed attempts
        failed_attempts, _ = detector.detect_failed_attempts(user_history, max_failed_attempts=5)
        
        # Detect unusual location
        unusual_location, location_confidence = detector.detect_unusual_location(access_data, user_history)
        
        # Detect unusual timing
        unusual_timing, timing_confidence = detector.detect_timing_anomaly(current_user)
        
        # Generate detection summary
        detections = {
            'is_anomalous': is_anomalous,
            'anomaly_score': float(anomaly_score),
            'bulk_download': bulk_download,
            'failed_attempts': failed_attempts,
            'unusual_location': unusual_location,
            'location_confidence': float(location_confidence),
            'unusual_timing': unusual_timing,
            'timing_confidence': float(timing_confidence)
        }
        
        # Generate report
        report = detector.generate_report(access_data, detections)
        
        # Store access in history
        user_history.append(access_data)
        
        # Alert if risk level is HIGH or CRITICAL
        if report['risk_level'] in ['HIGH', 'CRITICAL']:
            alert_id = f"{current_user}_{len(alerts)}"
            alerts[alert_id] = report
            report['alert_id'] = alert_id
        
        return jsonify({
            'message': 'Access analysis completed',
            'report': report
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/detect-threats', methods=['POST'])
@jwt_required()
def detect_threats():
    """
    Comprehensive threat detection
    POST: {"file_id": "file_1", "action": "download", ...}
    """
    current_user = get_jwt_identity()
    data = request.get_json()
    
    threats_detected = []
    
    try:
        if current_user in access_history:
            user_history = access_history[current_user]
            
            # Check for bulk downloads
            bulk_download, records = detector.detect_bulk_download(user_history, time_window_minutes=30)
            if bulk_download:
                threats_detected.append({
                    'type': 'BULK_DOWNLOAD',
                    'severity': 'HIGH',
                    'description': 'Multiple files downloaded in short time period',
                    'count': len(records)
                })
            
            # Check for failed attempts
            failed_attempts, records = detector.detect_failed_attempts(user_history, max_failed_attempts=3)
            if failed_attempts:
                threats_detected.append({
                    'type': 'FAILED_ATTEMPTS',
                    'severity': 'MEDIUM',
                    'description': 'Multiple failed access attempts detected',
                    'count': len(records)
                })
        
        return jsonify({
            'threats_detected': threats_detected,
            'total_threats': len(threats_detected),
            'recommended_action': 'MONITOR' if threats_detected else 'ALLOW'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/get-alerts', methods=['GET'])
@jwt_required()
def get_alerts():
    """
    Get security alerts for current user
    """
    current_user = get_jwt_identity()
    
    user_alerts = [
        alert for alert_id, alert in alerts.items()
        if alert.get('user_id') == current_user
    ]
    
    return jsonify({
        'alerts': user_alerts,
        'total_alerts': len(user_alerts)
    }), 200

@bp.route('/get-risk-score/<file_id>', methods=['GET'])
@jwt_required()
def get_risk_score(file_id):
    """
    Get risk score for a specific file
    """
    current_user = get_jwt_identity()
    
    if current_user not in access_history:
        return jsonify({
            'file_id': file_id,
            'risk_score': 0.0,
            'risk_level': 'LOW'
        }), 200
    
    user_history = access_history[current_user]
    file_accesses = [r for r in user_history if r.get('file_id') == file_id]
    
    if not file_accesses:
        return jsonify({
            'file_id': file_id,
            'risk_score': 0.0,
            'risk_level': 'LOW'
        }), 200
    
    # Calculate average risk from recent accesses
    avg_risk = sum(r.get('anomaly_score', 0) for r in file_accesses[-5:]) / len(file_accesses[-5:])
    
    if avg_risk > 0.7:
        risk_level = 'HIGH'
    elif avg_risk > 0.5:
        risk_level = 'MEDIUM'
    else:
        risk_level = 'LOW'
    
    return jsonify({
        'file_id': file_id,
        'risk_score': float(avg_risk),
        'risk_level': risk_level,
        'access_count': len(file_accesses)
    }), 200

@bp.route('/security-dashboard', methods=['GET'])
@jwt_required()
def security_dashboard():
    """
    Get security dashboard data
    """
    current_user = get_jwt_identity()
    
    user_alerts = [
        alert for alert_id, alert in alerts.items()
        if alert.get('user_id') == current_user
    ]
    
    user_history = access_history.get(current_user, [])
    
    # Calculate statistics
    total_accesses = len(user_history)
    high_risk_accesses = sum(
        1 for r in user_history
        if r.get('anomaly_score', 0) > 0.6
    )
    critical_alerts = sum(1 for a in user_alerts if a.get('risk_level') == 'CRITICAL')
    high_alerts = sum(1 for a in user_alerts if a.get('risk_level') == 'HIGH')
    
    return jsonify({
        'user_id': current_user,
        'statistics': {
            'total_accesses': total_accesses,
            'high_risk_accesses': high_risk_accesses,
            'critical_alerts': critical_alerts,
            'high_alerts': high_alerts,
            'total_alerts': len(user_alerts)
        },
        'recent_alerts': user_alerts[-5:],
        'overall_risk_level': 'CRITICAL' if critical_alerts > 0 else 'HIGH' if high_alerts > 0 else 'MEDIUM' if len(user_alerts) > 0 else 'LOW'
    }), 200
