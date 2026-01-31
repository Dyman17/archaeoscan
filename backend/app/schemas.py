from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class SensorType(str, Enum):
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    PRESSURE = "pressure"
    TDS = "tds"
    TURBIDITY = "turbidity"
    DISTANCE = "distance"
    MAGNETOMETER = "magnetometer"
    ACCELEROMETER = "accelerometer"
    GYROSCOPE = "gyroscope"
    BATTERY = "battery"
    GPS = "gps"

class MaterialType(str, Enum):
    METAL = "metal"
    CERAMIC = "ceramic"
    ORGANIC = "organic"
    STONE = "stone"
    UNKNOWN = "unknown"

class ConnectionStatus(str, Enum):
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    OFFLINE = "offline"

# Request/Response schemas
class SensorReadingRequest(BaseModel):
    timestamp: int
    sensor_type: SensorType
    value: Optional[float] = None
    values_json: Optional[List[float]] = None
    unit: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    accuracy: Optional[float] = None
    battery_level: Optional[float] = None
    device_id: str

class SensorReadingResponse(BaseModel):
    id: int
    timestamp: datetime
    sensor_type: SensorType
    value: Optional[float] = None
    values_json: Optional[List[float]] = None
    unit: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    accuracy: Optional[float] = None
    battery_level: Optional[float] = None
    device_id: str

class SpectrometerReadingRequest(BaseModel):
    timestamp: int
    wavelengths: List[float]
    intensity: List[float]
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    accuracy: Optional[float] = None
    battery_level: Optional[float] = None
    device_id: str

class SpectrometerReadingResponse(BaseModel):
    id: int
    timestamp: datetime
    wavelengths: List[float]
    intensity: List[float]
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    accuracy: Optional[float] = None
    battery_level: Optional[float] = None
    device_id: str

class RadarReadingRequest(BaseModel):
    timestamp: int
    depth_profile: List[float]
    anomalies: List[Dict[str, Any]]
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    accuracy: Optional[float] = None
    battery_level: Optional[float] = None
    device_id: str

class RadarReadingResponse(BaseModel):
    id: int
    timestamp: datetime
    depth_profile: List[float]
    anomalies: List[Dict[str, Any]]
    processed_anomalies: Optional[List[Dict[str, Any]]] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    accuracy: Optional[float] = None
    battery_level: Optional[float] = None
    device_id: str

class CameraReadingRequest(BaseModel):
    timestamp: int
    image_base64: str
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    accuracy: Optional[float] = None
    battery_level: Optional[float] = None
    device_id: str

class CameraReadingResponse(BaseModel):
    id: int
    timestamp: datetime
    image_base64: str
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    accuracy: Optional[float] = None
    battery_level: Optional[float] = None
    device_id: str

class MaterialClassificationRequest(BaseModel):
    spectrometer_reading_id: int
    material_type: MaterialType
    confidence: float
    spectral_signature: Dict[str, Any]
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    device_id: str

class MaterialClassificationResponse(BaseModel):
    id: int
    timestamp: datetime
    spectrometer_reading_id: int
    material_type: MaterialType
    confidence: float
    spectral_signature: Dict[str, Any]
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    device_id: str

class PreservationIndexRequest(BaseModel):
    location_lat: float
    location_lng: float
    preservation_percentage: float
    environmental_factors: Dict[str, Any]
    calculated_from_readings: List[int]
    device_id: str

class PreservationIndexResponse(BaseModel):
    id: int
    timestamp: datetime
    location_lat: float
    location_lng: float
    preservation_percentage: float
    environmental_factors: Dict[str, Any]
    calculated_from_readings: List[int]
    device_id: str

class SystemStatusRequest(BaseModel):
    device_id: str
    battery_level: Optional[float] = None
    connection_status: ConnectionStatus
    sensor_statuses: Optional[Dict[str, str]] = None
    active_alerts: Optional[List[Dict[str, Any]]] = None
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    disk_usage: Optional[float] = None

class SystemStatusResponse(BaseModel):
    id: int
    timestamp: datetime
    device_id: str
    battery_level: Optional[float] = None
    connection_status: ConnectionStatus
    sensor_statuses: Optional[Dict[str, str]] = None
    active_alerts: Optional[List[Dict[str, Any]]] = None
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    disk_usage: Optional[float] = None

class CalibrationRequest(BaseModel):
    sensor_type: str
    device_id: str
    calibration_parameters: Dict[str, Any]

class CalibrationResponse(BaseModel):
    id: int
    timestamp: datetime
    sensor_type: str
    device_id: str
    calibration_parameters: Dict[str, Any]
    is_active: bool

class ReportRequest(BaseModel):
    report_type: str
    content: Dict[str, Any]
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    device_id: str
    generated_by_ai: Optional[bool] = False

class ReportResponse(BaseModel):
    id: int
    timestamp: datetime
    report_type: str
    content: Dict[str, Any]
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    device_id: str
    generated_by_ai: bool

# Additional schemas for API endpoints
class CalibrationCommand(BaseModel):
    sensor_type: str
    command: str  # e.g., "start_calibration", "reset", "set_offset"
    parameters: Optional[Dict[str, Any]] = None

class ControlCommand(BaseModel):
    command: str  # e.g., "start_scan", "stop_scan", "reset_sensors"
    parameters: Optional[Dict[str, Any]] = None

class TimeRangeFilter(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    sensor_types: Optional[List[SensorType]] = None

class SensorHistoricalData(BaseModel):
    sensor_readings: List[SensorReadingResponse]
    total_count: int

class AnalysisResult(BaseModel):
    preservation_index: Optional[PreservationIndexResponse] = None
    material_analysis: Optional[MaterialClassificationResponse] = None
    anomaly_detection: Optional[RadarReadingResponse] = None
    summary: str