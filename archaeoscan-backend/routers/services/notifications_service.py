from typing import List, Dict, Any
from datetime import datetime, timedelta
from models.database_models import SensorData, Settings
from fastapi import WebSocket
import asyncio
import json

class NotificationType:
    BATTERY_LOW = "battery_low"
    SIGNAL_WEAK = "signal_weak"
    TURBIDITY_HIGH = "turbidity_high"
    TEMPERATURE_EXTREME = "temperature_extreme"
    TDS_HIGH = "tds_high"
    NEW_ARTIFACT = "new_artifact"
    PRESERVATION_CRITICAL = "preservation_critical"

class NotificationsService:
    """
    Service for handling notifications and alerts
    """
    
    def __init__(self):
        self.active_websockets: List[WebSocket] = []
        self.settings = None
        self.last_notifications = {}
    
    async def broadcast_notification(self, notification: Dict[str, Any]):
        """
        Broadcast notification to all connected websockets
        """
        notification['timestamp'] = datetime.utcnow().isoformat()
        self.last_notifications[notification['type']] = notification
        
        disconnected = []
        for websocket in self.active_websockets:
            try:
                await websocket.send_text(json.dumps(notification))
            except:
                disconnected.append(websocket)
        
        # Remove disconnected websockets
        for websocket in disconnected:
            if websocket in self.active_websockets:
                self.active_websockets.remove(websocket)
    
    def add_websocket(self, websocket: WebSocket):
        """
        Add a websocket to the list of active connections
        """
        if websocket not in self.active_websockets:
            self.active_websockets.append(websocket)
    
    def remove_websocket(self, websocket: WebSocket):
        """
        Remove a websocket from the list of active connections
        """
        if websocket in self.active_websockets:
            self.active_websockets.remove(websocket)
    
    def check_for_alerts(self, sensor_data: SensorData, settings: Settings = None):
        """
        Check if any sensor readings trigger alerts based on settings
        """
        if not settings:
            # Default settings if none provided
            settings = {
                "battery_threshold": 20,
                "signal_threshold": "Weak",
                "temperature_range": [-10, 40],
                "turbidity_threshold": 50,
                "tds_threshold": 500
            }
        else:
            settings = settings.alerts if hasattr(settings, 'alerts') else {}
        
        alerts = []
        
        # Check battery level
        if sensor_data.battery is not None and sensor_data.battery < settings.get("battery_threshold", 20):
            alerts.append({
                "type": NotificationType.BATTERY_LOW,
                "severity": "high",
                "message": f"Battery level critical: {sensor_data.battery:.1f}%",
                "value": sensor_data.battery,
                "threshold": settings.get("battery_threshold", 20)
            })
        
        # Check signal strength
        if sensor_data.signal_strength and sensor_data.signal_strength == settings.get("signal_threshold", "Weak"):
            alerts.append({
                "type": NotificationType.SIGNAL_WEAK,
                "severity": "medium",
                "message": f"Weak signal detected: {sensor_data.signal_strength}",
                "value": sensor_data.signal_strength,
                "threshold": settings.get("signal_threshold", "Weak")
            })
        
        # Check turbidity
        if sensor_data.turbidity is not None and sensor_data.turbidity > settings.get("turbidity_threshold", 50):
            alerts.append({
                "type": NotificationType.TURBIDITY_HIGH,
                "severity": "medium",
                "message": f"High water turbidity: {sensor_data.turbidity:.2f} NTU",
                "value": sensor_data.turbidity,
                "threshold": settings.get("turbidity_threshold", 50)
            })
        
        # Check temperature
        if sensor_data.temperature is not None:
            temp_range = settings.get("temperature_range", [-10, 40])
            if sensor_data.temperature < temp_range[0] or sensor_data.temperature > temp_range[1]:
                severity = "high" if (sensor_data.temperature < temp_range[0] - 5 or sensor_data.temperature > temp_range[1] + 5) else "medium"
                alerts.append({
                    "type": NotificationType.TEMPERATURE_EXTREME,
                    "severity": severity,
                    "message": f"Extreme temperature: {sensor_data.temperature:.2f}°C",
                    "value": sensor_data.temperature,
                    "threshold": temp_range
                })
        
        # Check TDS
        if sensor_data.tds is not None and sensor_data.tds > settings.get("tds_threshold", 500):
            alerts.append({
                "type": NotificationType.TDS_HIGH,
                "severity": "medium",
                "message": f"High TDS level: {sensor_data.tds:.2f} ppm",
                "value": sensor_data.tds,
                "threshold": settings.get("tds_threshold", 500)
            })
        
        # Check preservation level
        if sensor_data.final_preservation is not None and sensor_data.final_preservation < 30:
            alerts.append({
                "type": NotificationType.PRESERVATION_CRITICAL,
                "severity": "high",
                "message": f"Critical preservation level: {sensor_data.final_preservation:.2f}%",
                "value": sensor_data.final_preservation,
                "threshold": 30
            })
        
        return alerts
    
    def create_new_artifact_notification(self, artifact_data: Dict[str, Any]):
        """
        Create a notification for a newly discovered artifact
        """
        return {
            "type": NotificationType.NEW_ARTIFACT,
            "severity": "info",
            "message": f"New artifact discovered: {artifact_data.get('name', 'Unknown')}",
            "artifact_id": artifact_data.get('id'),
            "material": artifact_data.get('material'),
            "location": {
                "latitude": artifact_data.get('latitude'),
                "longitude": artifact_data.get('longitude')
            },
            "preservation": artifact_data.get('preservation')
        }

# Global service instance
notifications_service = NotificationsService()