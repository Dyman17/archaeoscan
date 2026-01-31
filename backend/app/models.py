from sqlalchemy import Column, Integer, String, Float, DateTime, LargeBinary, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class SensorReading(Base):
    __tablename__ = "sensor_readings"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    sensor_type = Column(String, index=True)  # e.g., "temperature", "humidity", "magnetometer"
    value = Column(Float)  # For single-value sensors
    values_json = Column(JSON)  # For multi-value sensors like accelerometer [x,y,z]
    unit = Column(String)  # Unit of measurement
    location_lat = Column(Float)  # GPS coordinates
    location_lng = Column(Float)
    accuracy = Column(Float)  # GPS accuracy
    battery_level = Column(Float)  # Battery percentage
    device_id = Column(String, index=True)  # Device identifier
    
class SpectrometerReading(Base):
    __tablename__ = "spectrometer_readings"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    wavelengths = Column(JSON)  # Array of wavelength values
    intensity = Column(JSON)  # Array of intensity values
    location_lat = Column(Float)
    location_lng = Column(Float)
    accuracy = Column(Float)
    battery_level = Column(Float)
    device_id = Column(String, index=True)
    
class RadarReading(Base):
    __tablename__ = "radar_readings"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    depth_profile = Column(JSON)  # Array of depth readings
    anomalies = Column(JSON)  # Array of anomaly objects
    processed_anomalies = Column(JSON)  # AI-processed anomalies with classifications
    location_lat = Column(Float)
    location_lng = Column(Float)
    accuracy = Column(Float)
    battery_level = Column(Float)
    device_id = Column(String, index=True)
    
class CameraReading(Base):
    __tablename__ = "camera_readings"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    image_data = Column(LargeBinary)  # Binary image data
    image_base64 = Column(String)  # Base64 encoded image
    location_lat = Column(Float)
    location_lng = Column(Float)
    accuracy = Column(Float)
    battery_level = Column(Float)
    device_id = Column(String, index=True)
    
class MaterialClassification(Base):
    __tablename__ = "material_classifications"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    spectrometer_reading_id = Column(Integer)  # Foreign key reference
    material_type = Column(String)  # metal, ceramic, organic, stone, unknown
    confidence = Column(Float)  # Confidence percentage
    spectral_signature = Column(JSON)  # Original spectral data used for classification
    location_lat = Column(Float)
    location_lng = Column(Float)
    device_id = Column(String, index=True)
    
class PreservationIndex(Base):
    __tablename__ = "preservation_indices"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    location_lat = Column(Float)
    location_lng = Column(Float)
    preservation_percentage = Column(Float)  # 0-100%
    environmental_factors = Column(JSON)  # Factors used in calculation
    calculated_from_readings = Column(JSON)  # IDs of sensor readings used for calculation
    device_id = Column(String, index=True)
    
class SystemStatus(Base):
    __tablename__ = "system_status"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    device_id = Column(String, index=True)
    battery_level = Column(Float)
    connection_status = Column(String)  # connected, reconnecting, offline
    sensor_statuses = Column(JSON)  # Status of each sensor
    active_alerts = Column(JSON)  # Current system alerts
    cpu_usage = Column(Float)
    memory_usage = Column(Float)
    disk_usage = Column(Float)
    
class CalibrationData(Base):
    __tablename__ = "calibration_data"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    sensor_type = Column(String, index=True)  # Type of sensor being calibrated
    device_id = Column(String, index=True)
    calibration_parameters = Column(JSON)  # Calibration coefficients and settings
    is_active = Column(Boolean, default=True)  # Whether this calibration is currently active
    
class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    report_type = Column(String, index=True)  # analysis, summary, anomaly_detection
    content = Column(JSON)  # Report content in structured format
    location_lat = Column(Float)
    location_lng = Column(Float)
    device_id = Column(String, index=True)
    generated_by_ai = Column(Boolean, default=False)