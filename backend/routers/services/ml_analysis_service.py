from typing import Dict, List, Tuple, Any
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd
import pickle
import json
from datetime import datetime, timedelta
from models.database_models import SensorData, Artifacts
from .preservation_service import preservation_service

class MLAnalysisService:
    """
    Machine Learning Analysis Service for preservation prediction and material comparison
    """
    
    def __init__(self):
        self.model = LinearRegression()
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_columns = ['temperature', 'turbidity', 'tds', 'pressure', 'humidity', 'distance']
        
    def prepare_training_data(self, sensor_data_records: List[SensorData]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare training data from sensor records and calculated preservation values
        """
        features = []
        targets = []
        
        for record in sensor_data_records:
            # Use sensor readings as features
            feature_row = [
                record.temperature or 0,
                record.turbidity or 0,
                record.tds or 0,
                record.pressure or 0,
                record.humidity or 0,
                record.distance or 0
            ]
            
            # Use calculated final preservation as target
            if record.final_preservation is not None:
                features.append(feature_row)
                targets.append(record.final_preservation)
        
        return np.array(features), np.array(targets)
    
    def train_model(self, sensor_data_records: List[SensorData]):
        """
        Train the ML model on historical sensor data
        """
        X, y = self.prepare_training_data(sensor_data_records)
        
        if len(X) == 0:
            print("No training data available")
            return
            
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train the model
        self.model.fit(X_scaled, y)
        self.is_trained = True
        print(f"Model trained with {len(X)} samples")
    
    def predict_preservation(self, sensor_reading: Dict[str, float]) -> Dict[str, float]:
        """
        Predict preservation values based on current sensor readings
        """
        if not self.is_trained:
            # If model is not trained, use the preservation service calculation
            from .preservation_service import SensorData as SensorDataClass
            sensor_data = SensorDataClass(
                turbidity=sensor_reading.get('turbidity', 0),
                temperature=sensor_reading.get('temperature', 0),
                tds=sensor_reading.get('tds', 0),
                pressure=sensor_reading.get('pressure', 0),
                humidity=sensor_reading.get('humidity', 0),
                distance=sensor_reading.get('distance', 0)
            )
            return preservation_service.calculate_preservation_report(sensor_data)
        
        # Prepare features
        features = np.array([[
            sensor_reading.get('temperature', 0),
            sensor_reading.get('turbidity', 0),
            sensor_reading.get('tds', 0),
            sensor_reading.get('pressure', 0),
            sensor_reading.get('humidity', 0),
            sensor_reading.get('distance', 0)
        ]])
        
        # Scale features
        features_scaled = self.scaler.transform(features)
        
        # Predict
        predicted_preservation = self.model.predict(features_scaled)[0]
        
        # Calculate detailed preservation report using the existing service
        from .preservation_service import SensorData as SensorDataClass
        sensor_data = SensorDataClass(
            turbidity=sensor_reading.get('turbidity', 0),
            temperature=sensor_reading.get('temperature', 0),
            tds=sensor_reading.get('tds', 0),
            pressure=sensor_reading.get('pressure', 0),
            humidity=sensor_reading.get('humidity', 0),
            distance=sensor_reading.get('distance', 0)
        )
        
        report = preservation_service.calculate_preservation_report(sensor_data)
        # Override final preservation with ML prediction
        report['final_preservation'] = predicted_preservation
        
        return report
    
    def compare_materials(self, sensor_reading: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Compare preservation across different materials based on current conditions
        """
        report = self.predict_preservation(sensor_reading)
        materials = report['materials']
        
        # Sort materials by preservation (ascending - most vulnerable first)
        sorted_materials = sorted(
            [(mat, pres) for mat, pres in materials.items()],
            key=lambda x: x[1]
        )
        
        return [
            {
                'material': mat,
                'preservation': pres,
                'rank': idx + 1,
                'risk_level': self._get_risk_level(pres)
            }
            for idx, (mat, pres) in enumerate(sorted_materials)
        ]
    
    def _get_risk_level(self, preservation: float) -> str:
        """Determine risk level based on preservation percentage"""
        if preservation >= 80:
            return "low"
        elif preservation >= 50:
            return "medium"
        else:
            return "high"
    
    def generate_trend_analysis(self, sensor_data_records: List[SensorData]) -> Dict[str, Any]:
        """
        Generate trend analysis for historical data
        """
        if not sensor_data_records:
            return {}
        
        # Extract time series data
        timestamps = []
        temperatures = []
        turbidities = []
        tds_levels = []
        preservation_scores = []
        
        for record in sensor_data_records:
            timestamps.append(record.timestamp)
            temperatures.append(record.temperature or 0)
            turbidities.append(record.turbidity or 0)
            tds_levels.append(record.tds or 0)
            preservation_scores.append(record.final_preservation or 0)
        
        # Calculate trends
        temp_trend = self._calculate_trend(temperatures)
        turbidity_trend = self._calculate_trend(turbidities)
        tds_trend = self._calculate_trend(tds_levels)
        preservation_trend = self._calculate_trend(preservation_scores)
        
        return {
            "time_series": {
                "timestamps": [ts.isoformat() for ts in timestamps],
                "temperatures": temperatures,
                "turbidities": turbidities,
                "tds_levels": tds_levels,
                "preservation_scores": preservation_scores
            },
            "trends": {
                "temperature": temp_trend,
                "turbidity": turbidity_trend,
                "tds": tds_trend,
                "preservation": preservation_trend
            },
            "statistics": {
                "avg_temperature": np.mean(temperatures),
                "avg_turbidity": np.mean(turbidities),
                "avg_tds": np.mean(tds_levels),
                "avg_preservation": np.mean(preservation_scores),
                "min_preservation": min(preservation_scores),
                "max_preservation": max(preservation_scores)
            }
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction based on last few values"""
        if len(values) < 3:
            return "stable"
        
        recent_avg = np.mean(values[-3:])
        older_avg = np.mean(values[:-3][-3:]) if len(values) > 5 else np.mean(values[:3])
        
        if recent_avg > older_avg * 1.1:
            return "increasing"
        elif recent_avg < older_avg * 0.9:
            return "decreasing"
        else:
            return "stable"

# Global service instance
ml_analysis_service = MLAnalysisService()