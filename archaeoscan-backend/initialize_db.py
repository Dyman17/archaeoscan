#!/usr/bin/env python3
"""
Script to initialize the database with sample data and test the preservation calculations
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.db import SessionLocal, engine
from models.database_models import Settings
from services.preservation_service import preservation_service, SensorData as SensorDataClass
from services.database_service import DatabaseService

def init_sample_data():
    """Initialize database with sample data"""
    db: Session = SessionLocal()
    
    try:
        # Create or get settings
        settings = db.query(Settings).first()
        if not settings:
            settings = Settings(esp32_ip="192.168.1.100")
            db.add(settings)
            db.commit()
            print("Created default settings")
        else:
            print("Found existing settings")
        
        # Test preservation calculation with sample sensor data
        sample_sensor_data = SensorDataClass(
            turbidity=45.0,
            temperature=22.5,
            tds=350.0,
            pressure=1013.25,
            humidity=45.0,
            distance=15.0
        )
        
        preservation_report = preservation_service.calculate_preservation_report(sample_sensor_data)
        
        print("\nSample Preservation Calculation:")
        print(f"Water Preservation: {preservation_report['water_preservation']}%")
        print(f"Final Preservation: {preservation_report['final_preservation']}%")
        print("Material Preservations:")
        for material, preservation in preservation_report['materials'].items():
            print(f"  {material.capitalize()}: {preservation}%")
        
        # Create database service and save sample sensor data
        db_service = DatabaseService(db)
        sensor_record = db_service.create_sensor_data(
            artifact_id=None,  # No artifact yet
            esp32_id="ESP32_SAMPLE_001",
            temperature=22.5,
            turbidity=45.0,
            tds=350.0,
            latitude=51.5074,
            longitude=-0.1278,
            accuracy=2.5,
            signal_strength="Strong",
            battery=85.0,
            pressure=1013.25,
            humidity=45.0,
            distance=15.0
        )
        
        print(f"\nSaved sensor data with ID: {sensor_record.id}")
        print(f"Calculated water preservation: {sensor_record.water_preservation}%")
        print(f"Calculated final preservation: {sensor_record.final_preservation}%")
        
        # Create a sample artifact
        artifact = db_service.create_artifact(
            name="Ancient Pottery Fragment",
            material="ceramic",
            latitude=51.5074,
            longitude=-0.1278,
            depth=0.5,
            preservation=sensor_record.final_preservation,
            sensor_data_id=sensor_record.id,
            images=["/images/pottery_1.jpg", "/images/pottery_2.jpg"],
            video_url="/videos/pottery_discovery.mp4",
            radar_image="/images/radar_artifact_1.png"
        )
        
        print(f"Created artifact: {artifact.name} with ID: {artifact.id}")
        
        # Create sample video
        video = db_service.create_video_stream(
            artifact_id=artifact.id,
            file_path="/videos/pottery_discovery.mp4"
        )
        
        print(f"Created video with ID: {video.id}")
        
        # Create sample radar image
        radar_img = db_service.create_radar_image(
            artifact_id=artifact.id,
            image_url="/images/radar_artifact_1.png"
        )
        
        print(f"Created radar image with ID: {radar_img.id}")
        
        # Create sample map snapshot
        map_snapshot = db_service.create_map_snapshot(
            artifact_id=artifact.id,
            image_url="/images/map_artifact_1.png"
        )
        
        print(f"Created map snapshot with ID: {map_snapshot.id}")
        
        print("\nDatabase initialization completed successfully!")
        
    except Exception as e:
        print(f"Error during database initialization: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_sample_data()