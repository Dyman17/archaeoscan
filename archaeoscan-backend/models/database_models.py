from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from models import Base
from enum import Enum

class MaterialType(Enum):
    WOOD = "wood"
    PAPER = "paper"
    COPPER = "copper"
    IRON = "iron"
    BRONZE = "bronze"
    STONE = "stone"
    GLASS = "glass"
    GOLD = "gold"
    CERAMIC = "ceramic"

class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True)
    artifact_id = Column(Integer, ForeignKey("artifacts.id"))  # Link to specific artifact
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    esp32_id = Column(String(50), nullable=False)  # ID of the ESP32 device
    
    # Environmental sensor data
    turbidity = Column(Float)    # from TS-300B
    temperature = Column(Float)  # from DS18B20
    tds = Column(Float)          # from TDS Meter
    
    # GPS and location data
    latitude = Column(Float)
    longitude = Column(Float)
    accuracy = Column(Float)     # GPS accuracy in meters
    signal_strength = Column(String(20))  # Signal strength (Strong/Medium/Weak)
    battery = Column(Float)      # Battery level percentage
    
    # Additional sensor data
    pressure = Column(Float)
    humidity = Column(Float)
    distance = Column(Float)     # From ultrasonic sensor
    
    # Calculated preservation data
    water_preservation = Column(Float)  # Calculated water preservation index
    material_preservation = Column(JSON)  # JSON with material preservation percentages
    final_preservation = Column(Float)    # Final calculated preservation index
    


class Artifacts(Base):
    __tablename__ = "artifacts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200))  # Name of the artifact if known
    material = Column(String(50))  # Material type (wood, iron, etc.)
    
    # Location data
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    depth = Column(Float)  # Depth underwater in meters
    
    # Discovery and preservation data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    preservation = Column(Float)  # Final preservation percentage
    
    # Foreign keys
    sensor_data_id = Column(Integer, ForeignKey("sensor_data.id"))  # Link to sensor data at discovery
    
    # Media references
    images = Column(JSON)  # JSON array of image URLs/paths
    radar_image = Column(String(500))  # Path to radar image
    video_url = Column(String(500))  # URL/path to related video
    


class RadarImages(Base):
    __tablename__ = "radar_images"

    id = Column(Integer, primary_key=True, index=True)
    artifact_id = Column(Integer, ForeignKey("artifacts.id"), nullable=True)  # Optional link to artifact
    image_url = Column(String(500), nullable=False)  # Path to image file
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    


class MapSnapshots(Base):
    __tablename__ = "map_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    artifact_id = Column(Integer, ForeignKey("artifacts.id"), nullable=True)  # Optional link to artifact
    image_url = Column(String(500), nullable=False)  # Path to image file
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    


class VideoStreams(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    artifact_id = Column(Integer, ForeignKey("artifacts.id"))  # Link to artifact (not optional)
    file_path = Column(String(500), nullable=False)  # Path to video file
    timestamp = Column(DateTime(timezone=True), server_default=func.now())  # Time of recording
    duration = Column(Float)  # Duration in seconds
    


class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    esp32_ip = Column(String(50), default="172.20.10.9")  # ESP32 IP address
    
    # Camera settings
    camera_settings = Column(JSON, default=lambda: {
        "fps": 15,
        "quality": 75,
        "resolution": "640x480"
    })
    
    # Map settings
    map_zoom = Column(Integer, default=15)
    map_center = Column(JSON, default=lambda: {"lat": 51.5074, "lng": -0.1278})
    
    # Alert settings
    alerts = Column(JSON, default=lambda: {
        "battery_threshold": 20,
        "signal_threshold": "Weak",
        "temperature_range": [-10, 40],
        "turbidity_threshold": 50
    })
    
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

