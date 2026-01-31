from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app import models, db
from app.schemas import (
    SystemStatusResponse, SystemStatusRequest, ConnectionStatus
)

router = APIRouter()

@router.get("/system/status", response_model=SystemStatusResponse)
def get_system_status(
    device_id: Optional[str] = "default_device",
    db: Session = Depends(db.get_db)
):
    """
    Get current system health status.
    """
    # Get the most recent status for the device
    system_status = db.query(models.SystemStatus)\
        .filter(models.SystemStatus.device_id == device_id)\
        .order_by(models.SystemStatus.timestamp.desc())\
        .first()
    
    if not system_status:
        # Return a default status if none exists
        return SystemStatusResponse(
            id=0,
            timestamp=datetime.utcnow(),
            device_id=device_id,
            battery_level=85.0,
            connection_status=ConnectionStatus.CONNECTED,
            sensor_statuses={
                "temperature": "ok",
                "humidity": "ok", 
                "pressure": "ok",
                "tds": "ok",
                "turbidity": "ok",
                "distance": "ok",
                "magnetometer": "ok",
                "accelerometer": "ok",
                "gyroscope": "ok"
            },
            active_alerts=[],
            cpu_usage=25.0,
            memory_usage=45.0,
            disk_usage=60.0
        )
    
    return SystemStatusResponse(
        id=system_status.id,
        timestamp=system_status.timestamp,
        device_id=system_status.device_id,
        battery_level=system_status.battery_level,
        connection_status=system_status.connection_status,
        sensor_statuses=system_status.sensor_statuses,
        active_alerts=system_status.active_alerts,
        cpu_usage=system_status.cpu_usage,
        memory_usage=system_status.memory_usage,
        disk_usage=system_status.disk_usage
    )

@router.post("/system/status")
def update_system_status(
    system_status: SystemStatusRequest,
    db: Session = Depends(db.get_db)
):
    """
    Update system status.
    """
    db_system_status = models.SystemStatus(
        device_id=system_status.device_id,
        battery_level=system_status.battery_level,
        connection_status=system_status.connection_status,
        sensor_statuses=system_status.sensor_statuses,
        active_alerts=system_status.active_alerts,
        cpu_usage=system_status.cpu_usage,
        memory_usage=system_status.memory_usage,
        disk_usage=system_status.disk_usage
    )
    
    db.add(db_system_status)
    db.commit()
    db.refresh(db_system_status)
    
    return {
        "message": "System status updated successfully",
        "id": db_system_status.id
    }

@router.get("/system/logs")
def get_system_logs(
    device_id: Optional[str] = None,
    log_level: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(db.get_db)
):
    """
    Get system logs with optional filtering.
    """
    # This would typically connect to a logging system
    # For now, we'll return a mock response
    return {
        "logs": [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "level": "INFO",
                "message": "System operational",
                "device_id": device_id or "default_device"
            }
        ],
        "total_count": 1,
        "skip": skip,
        "limit": limit
    }

@router.get("/system/config")
def get_system_config(device_id: Optional[str] = "default_device"):
    """
    Get system configuration.
    """
    return {
        "device_id": device_id,
        "config": {
            "sensor_update_frequency": 10,  # Hz
            "radar_pulse_frequency": 1000,  # Hz
            "camera_resolution": "640x480",
            "data_retention_days": 30,
            "calibration_intervals": {
                "temperature": 86400,  # seconds (24 hours)
                "spectrometer": 3600,  # seconds (1 hour)
                "radar": 7200  # seconds (2 hours)
            }
        }
    }

@router.post("/system/config")
def update_system_config(config_data: dict, device_id: Optional[str] = "default_device"):
    """
    Update system configuration.
    """
    # In a real implementation, this would update the device configuration
    # For now, we'll just return the configuration
    return {
        "message": "Configuration updated successfully",
        "device_id": device_id,
        "updated_config": config_data
    }