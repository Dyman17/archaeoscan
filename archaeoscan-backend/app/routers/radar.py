from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from datetime import datetime

from app import models, db
from app.schemas import (
    RadarReadingRequest, RadarReadingResponse
)
from app.services.radar_processing import process_radar_data, analyze_depth_layers

router = APIRouter()

@router.post("/radar/process")
def process_radar_reading(
    radar_data: RadarReadingRequest,
    db: Session = Depends(db.get_db)
):
    """
    Process radar data and detect anomalies.
    """
    # Process the radar data to detect anomalies
    processed_result = process_radar_data(
        depth_profile=radar_data.depth_profile,
        coordinates=(radar_data.location_lat or 0.0, radar_data.location_lng or 0.0) if radar_data.location_lat and radar_data.location_lng else None
    )
    
    # Create radar reading record
    db_radar_reading = models.RadarReading(
        timestamp=datetime.fromtimestamp(radar_data.timestamp / 1000) if radar_data.timestamp else datetime.utcnow(),
        depth_profile=radar_data.depth_profile,
        anomalies=radar_data.anomalies,
        processed_anomalies=processed_result['anomalies'],
        location_lat=radar_data.location_lat,
        location_lng=radar_data.location_lng,
        accuracy=radar_data.accuracy,
        battery_level=radar_data.battery_level,
        device_id=radar_data.device_id
    )
    
    db.add(db_radar_reading)
    db.commit()
    db.refresh(db_radar_reading)
    
    return {
        "id": db_radar_reading.id,
        "timestamp": db_radar_reading.timestamp,
        "original_anomalies": radar_data.anomalies,
        "processed_anomalies": processed_result['anomalies'],
        "total_detected": processed_result['total_detected'],
        "message": "Radar data processed successfully"
    }

@router.get("/radar/anomalies", response_model=List[dict])
def get_radar_anomalies(
    device_id: Optional[str] = None,
    anomaly_type: Optional[str] = None,
    min_confidence: Optional[float] = 0.0,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(db.get_db)
):
    """
    Get detected radar anomalies with optional filtering.
    """
    query = db.query(models.RadarReading)
    
    if device_id:
        query = query.filter(models.RadarReading.device_id == device_id)
    
    query = query.order_by(models.RadarReading.timestamp.desc())
    query = query.offset(skip).limit(limit)
    
    radar_readings = query.all()
    
    all_anomalies = []
    for reading in radar_readings:
        if reading.processed_anomalies:
            for anomaly in reading.processed_anomalies:
                if anomaly_type and anomaly.get('type') != anomaly_type:
                    continue
                if anomaly.get('confidence', 0) < min_confidence:
                    continue
                anomaly['reading_id'] = reading.id
                anomaly['timestamp'] = reading.timestamp
                anomaly['location'] = {
                    'lat': reading.location_lat,
                    'lng': reading.location_lng
                }
                all_anomalies.append(anomaly)
    
    return all_anomalies

@router.post("/radar/analyze-layers")
def analyze_radar_layers(radar_data: RadarReadingRequest):
    """
    Analyze radar depth profile to identify geological layers.
    """
    layer_analysis = analyze_depth_layers(radar_data.depth_profile)
    return layer_analysis