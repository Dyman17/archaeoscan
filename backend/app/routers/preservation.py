from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from models.database_models import SensorData
from routers.services.database_service import get_db_service, DatabaseService
from routers.services.preservation_service import preservation_service, SensorData as SensorDataClass
from models import get_db
from pydantic import BaseModel

router = APIRouter(prefix="/preservation", tags=["preservation"])

class SensorReading(BaseModel):
    """Request model for sensor data"""
    esp32_id: str
    temperature: float = 0.0
    turbidity: float = 0.0
    tds: float = 0.0
    pressure: float = 0.0
    humidity: float = 0.0
    distance: float = 0.0
    latitude: float = 0.0
    longitude: float = 0.0
    accuracy: float = 0.0
    signal_strength: str = "Strong"
    battery: float = 100.0

class PreservationReport(BaseModel):
    """Response model for preservation data"""
    water_preservation: float
    materials: dict
    final_preservation: float
    sensor_readings: dict

@router.post("/calculate")
async def calculate_preservation(data: SensorReading, db: Session = Depends(get_db)):
    """
    Calculate preservation indices based on sensor readings
    """
    # Convert incoming data to SensorData class
    sensor_data = SensorDataClass(
        turbidity=data.turbidity,
        temperature=data.temperature,
        tds=data.tds,
        pressure=data.pressure,
        humidity=data.humidity,
        distance=data.distance
    )
    
    # Calculate preservation report
    report = preservation_service.calculate_preservation_report(sensor_data)
    
    # Also save the sensor data to the database
    db_service = get_db_service(db)
    sensor_record = db_service.create_sensor_data(
        artifact_id=None,  # No specific artifact yet
        esp32_id=data.esp32_id,
        temperature=data.temperature,
        turbidity=data.turbidity,
        tds=data.tds,
        latitude=data.latitude,
        longitude=data.longitude,
        accuracy=data.accuracy,
        signal_strength=data.signal_strength,
        battery=data.battery,
        pressure=data.pressure,
        humidity=data.humidity,
        distance=data.distance
    )
    
    # Return the full response as specified in the requirements
    return {
        "artifact_id": None,  # No artifact yet
        "material": "unknown",  # Would be determined when artifact is identified
        "preservation": report["final_preservation"],
        "sensor_data": {
            "turbidity": data.turbidity,
            "temperature": data.temperature,
            "TDS": data.tds
        },
        "images": [],
        "radar_image": None,
        "gps": {
            "lat": data.latitude,
            "lng": data.longitude
        },
        "video": None
    }

@router.get("/history/{limit}", response_model=List[dict])
async def get_preservation_history(limit: int = 100, db: Session = Depends(get_db)):
    """
    Get historical preservation data
    """
    db_service = get_db_service(db)
    sensor_data_list = db_service.get_recent_sensor_data(limit)
    
    history = []
    for record in sensor_data_list:
        history.append({
            "id": record.id,
            "timestamp": record.timestamp,
            "water_preservation": record.water_preservation,
            "material_preservation": record.material_preservation,
            "final_preservation": record.final_preservation,
            "sensor_readings": {
                "temperature": record.temperature,
                "turbidity": record.turbidity,
                "tds": record.tds,
                "pressure": record.pressure,
                "humidity": record.humidity,
                "distance": record.distance
            }
        })
    
    return history

@router.get("/material-sensitivity")
async def get_material_sensitivity():
    """
    Get information about material sensitivities to different sensors
    """
    return {
        "materials": list(preservation_service.material_database.keys()),
        "material_details": preservation_service.material_database,
        "total_materials": len(preservation_service.material_database)
    }