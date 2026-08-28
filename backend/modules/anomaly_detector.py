import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import json

class AnomalyDetector:
    """
    AI-based Anomaly Detection using Isolation Forest
    Detects unusual file access patterns
    """
    
    def __init__(self, contamination: float = 0.1):
        """
        Initialize detector
        contamination: expected proportion of anomalies (0.0-1.0)
        """
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.access_history = {}
    
    def extract_features(self, access_data: Dict) -> np.ndarray:
        """
        Extract features from access data
        Features: [time_diff, download_size, access_count, time_of_day, day_of_week]
        """
        features = []
        
        # Time difference from last access (hours)
        if 'last_access_time' in access_data:
            time_diff = (datetime.utcnow() - 
                        datetime.fromisoformat(access_data['last_access_time'])).total_seconds() / 3600
            features.append(time_diff)
        else:
            features.append(24)  # Default to 24 hours
        
        # File size (MB)
        file_size_mb = access_data.get('file_size', 0) / (1024 * 1024)
        features.append(file_size_mb)
        
        # Access count in last 24 hours
        access_count = access_data.get('access_count_24h', 0)
        features.append(access_count)
        
        # Time of day (0-23)
        time_of_day = datetime.utcnow().hour
        features.append(time_of_day)
        
        # Day of week (0-6)
        day_of_week = datetime.utcnow().weekday()
        features.append(day_of_week)
        
        # Geographic anomaly score (0-1)
        geo_anomaly = access_data.get('geo_anomaly_score', 0)
        features.append(geo_anomaly)
        
        # Device deviation score (0-1)
        device_anomaly = access_data.get('device_anomaly_score', 0)
        features.append(device_anomaly)
        
        return np.array(features).reshape(1, -1)
    
    def train(self, training_data: List[Dict]) -> bool:
        """
        Train the anomaly detector
        training_data: List of access records with features
        """
        if len(training_data) < 10:
            print("Warning: Need at least 10 samples for training")
            return False
        
        try:
            # Extract features from all training data
            features_list = []
            for data in training_data:
                features = self.extract_features(data)
                features_list.append(features[0])
            
            X_train = np.array(features_list)
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            
            # Train model
            self.model.fit(X_train_scaled)
            self.is_trained = True
            
            print(f"Model trained on {len(training_data)} samples")
            return True
        except Exception as e:
            print(f"Error training model: {e}")
            return False
    
    def predict(self, access_data: Dict) -> Tuple[bool, float]:
        """
        Predict if access is anomalous
        Returns: (is_anomalous, anomaly_score)
        """
        if not self.is_trained:
            print("Warning: Model not trained. Training on default data...")
            self.train_on_default_profile()
        
        try:
            features = self.extract_features(access_data)
            X_scaled = self.scaler.transform(features)
            
            # Predict (-1 for anomalies, 1 for normal)
            prediction = self.model.predict(X_scaled)[0]
            
            # Get anomaly score (negative values closer to 0 are more anomalous)
            anomaly_score = -self.model.score_samples(X_scaled)[0]
            
            is_anomalous = prediction == -1
            
            return is_anomalous, anomaly_score
        except Exception as e:
            print(f"Error predicting: {e}")
            return False, 0.0
    
    def train_on_default_profile(self):
        """
        Train on default normal behavior profile
        """
        default_data = [
            # Normal business hours access
            {'time_diff': 8, 'file_size': 1024000, 'access_count_24h': 1, 'geo_anomaly_score': 0, 'device_anomaly_score': 0},
            {'time_diff': 12, 'file_size': 2048000, 'access_count_24h': 1, 'geo_anomaly_score': 0, 'device_anomaly_score': 0},
            {'time_diff': 6, 'file_size': 512000, 'access_count_24h': 2, 'geo_anomaly_score': 0, 'device_anomaly_score': 0},
            {'time_diff': 4, 'file_size': 1024000, 'access_count_24h': 1, 'geo_anomaly_score': 0, 'device_anomaly_score': 0},
            {'time_diff': 24, 'file_size': 5120000, 'access_count_24h': 0, 'geo_anomaly_score': 0, 'device_anomaly_score': 0},
            # Repeat for model stability
            {'time_diff': 8, 'file_size': 1024000, 'access_count_24h': 1, 'geo_anomaly_score': 0, 'device_anomaly_score': 0},
            {'time_diff': 12, 'file_size': 2048000, 'access_count_24h': 1, 'geo_anomaly_score': 0, 'device_anomaly_score': 0},
            {'time_diff': 6, 'file_size': 512000, 'access_count_24h': 2, 'geo_anomaly_score': 0, 'device_anomaly_score': 0},
            {'time_diff': 4, 'file_size': 1024000, 'access_count_24h': 1, 'geo_anomaly_score': 0, 'device_anomaly_score': 0},
            {'time_diff': 24, 'file_size': 5120000, 'access_count_24h': 0, 'geo_anomaly_score': 0, 'device_anomaly_score': 0},
        ]
        
        self.train(default_data)
    
    def detect_bulk_download(self, access_records: List[Dict], time_window_minutes: int = 60) -> Tuple[bool, List[Dict]]:
        """
        Detect bulk download pattern
        Returns: (is_suspicious, anomalous_records)
        """
        anomalous_records = []
        
        # Group accesses by time window
        current_time = datetime.utcnow()
        window_start = current_time - timedelta(minutes=time_window_minutes)
        
        recent_accesses = [
            record for record in access_records
            if datetime.fromisoformat(record.get('timestamp', '')) > window_start
        ]
        
        # If more than 5 downloads in time window, it's suspicious
        if len(recent_accesses) > 5:
            anomalous_records = recent_accesses
            return True, anomalous_records
        
        return False, anomalous_records
    
    def detect_failed_attempts(self, access_records: List[Dict], max_failed_attempts: int = 5) -> Tuple[bool, List[Dict]]:
        """
        Detect multiple failed access attempts
        Returns: (is_suspicious, anomalous_records)
        """
        anomalous_records = []
        failed_attempts = [r for r in access_records if not r.get('success', True)]
        
        if len(failed_attempts) >= max_failed_attempts:
            anomalous_records = failed_attempts
            return True, anomalous_records
        
        return False, anomalous_records
    
    def detect_unusual_location(self, access_data: Dict, user_history: List[Dict]) -> Tuple[bool, float]:
        """
        Detect access from unusual geographic location
        Returns: (is_unusual, confidence_score)
        """
        if 'ip_address' not in access_data:
            return False, 0.0
        
        current_ip = access_data['ip_address']
        
        # Check if this IP appears in user's history
        ip_count = sum(1 for record in user_history if record.get('ip_address') == current_ip)
        
        # If IP is new (count == 0), it's potentially unusual
        if ip_count == 0:
            total_accesses = len(user_history)
            confidence = 0.8 if total_accesses > 10 else 0.5
            return True, confidence
        
        return False, 0.0
    
    def detect_timing_anomaly(self, user_id: str, current_time: datetime = None) -> Tuple[bool, float]:
        """
        Detect access at unusual times (outside normal hours)
        Returns: (is_anomalous, confidence_score)
        """
        if current_time is None:
            current_time = datetime.utcnow()
        
        hour = current_time.hour
        day = current_time.weekday()
        
        # Assume normal business hours are 9-17 on weekdays
        is_business_hours = 9 <= hour < 17 and day < 5
        
        if not is_business_hours:
            # High confidence if access outside business hours
            return True, 0.7
        
        return False, 0.0
    
    def generate_report(self, access_data: Dict, detections: Dict) -> Dict:
        """
        Generate anomaly detection report
        """
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': access_data.get('user_id'),
            'file_id': access_data.get('file_id'),
            'access_type': access_data.get('action'),
            'detections': detections,
            'risk_level': self._calculate_risk_level(detections),
            'recommendations': self._generate_recommendations(detections)
        }
        
        return report
    
    def _calculate_risk_level(self, detections: Dict) -> str:
        """
        Calculate overall risk level based on detections
        """
        anomaly_score = detections.get('anomaly_score', 0)
        
        if anomaly_score > 0.8:
            return 'CRITICAL'
        elif anomaly_score > 0.6:
            return 'HIGH'
        elif anomaly_score > 0.4:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _generate_recommendations(self, detections: Dict) -> List[str]:
        """
        Generate security recommendations based on detections
        """
        recommendations = []
        
        if detections.get('is_anomalous'):
            recommendations.append('Review this access pattern for potential security threat')
        
        if detections.get('bulk_download'):
            recommendations.append('Large number of downloads detected - verify if intentional')
        
        if detections.get('failed_attempts'):
            recommendations.append('Multiple failed access attempts - monitor for brute force attack')
        
        if detections.get('unusual_location'):
            recommendations.append('Access from new location - enable additional verification')
        
        if detections.get('unusual_timing'):
            recommendations.append('Access outside normal business hours - manual review recommended')
        
        return recommendations if recommendations else ['No security concerns detected']
