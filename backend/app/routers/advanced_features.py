from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel
import json
from models import get_db
from models.database_models import Settings
from routers.services.ml_analysis_service import ml_analysis_service
from routers.services.notifications_service import notifications_service
from routers.services.catalog_service import get_catalog_service
from routers.services.database_service import get_db_service
from routers.services.preservation_service import SensorData as SensorDataClass

router = APIRouter(prefix="/advanced", tags=["advanced"])

# Request/Response models
class SensorReadingForAnalysis(BaseModel):
    temperature: float = 0.0
    turbidity: float = 0.0
    tds: float = 0.0
    pressure: float = 0.0
    humidity: float = 0.0
    distance: float = 0.0

class MaterialComparisonResponse(BaseModel):
    material: str
    preservation: float
    rank: int
    risk_level: str

class TrendAnalysisResponse(BaseModel):
    time_series: Dict[str, Any]
    trends: Dict[str, str]
    statistics: Dict[str, float]

@router.post("/analyze-preservation", response_model=Dict[str, Any])
async def analyze_preservation(data: SensorReadingForAnalysis, db: Session = Depends(get_db)):
    """
    Advanced AI/ML analysis of preservation based on sensor data
    """
    # Train the model with historical data if not already trained
    db_service = get_db_service(db)
    historical_data = db_service.get_recent_sensor_data(limit=50)
    
    if historical_data and not ml_analysis_service.is_trained:
        ml_analysis_service.train_model(historical_data)
    
    # Perform prediction
    sensor_dict = data.dict()
    prediction = ml_analysis_service.predict_preservation(sensor_dict)
    
    return {
        "prediction": prediction,
        "analysis": {
            "is_ml_prediction": ml_analysis_service.is_trained,
            "training_samples_used": len(historical_data) if historical_data else 0
        }
    }

@router.post("/compare-materials", response_model=List[MaterialComparisonResponse])
async def compare_materials(data: SensorReadingForAnalysis, db: Session = Depends(get_db)):
    """
    Compare preservation across different materials based on current conditions
    """
    sensor_dict = data.dict()
    comparison = ml_analysis_service.compare_materials(sensor_dict)
    
    return comparison

@router.get("/trend-analysis", response_model=TrendAnalysisResponse)
async def trend_analysis(db: Session = Depends(get_db)):
    """
    Analyze historical trends in sensor data
    """
    db_service = get_db_service(db)
    historical_data = db_service.get_recent_sensor_data(limit=100)
    
    analysis = ml_analysis_service.generate_trend_analysis(historical_data)
    
    return analysis

@router.websocket("/notifications")
async def websocket_notifications(websocket: WebSocket):
    """
    WebSocket endpoint for real-time notifications
    """
    await websocket.accept()
    notifications_service.add_websocket(websocket)
    
    try:
        while True:
            # Keep the connection alive
            data = await websocket.receive_text()
            # Process any commands if needed
            await notifications_service.broadcast_notification({
                "type": "echo",
                "message": f"Server received: {data}",
                "timestamp": "now"
            })
    except WebSocketDisconnect:
        notifications_service.remove_websocket(websocket)

@router.get("/catalog/filter")
async def filter_artifacts(
    material: str = None,
    preservation_min: float = None,
    preservation_max: float = None,
    date_from: str = None,
    date_to: str = None,
    latitude: float = None,
    longitude: float = None,
    radius_km: float = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Filter artifacts based on various criteria
    """
    from datetime import datetime
    
    # Parse date strings if provided
    from datetime import datetime as dt
    parsed_date_from = dt.fromisoformat(date_from) if date_from else None
    parsed_date_to = dt.fromisoformat(date_to) if date_to else None
    
    catalog_service = get_catalog_service(db)
    artifacts = catalog_service.get_artifacts_filtered(
        material=material,
        preservation_min=preservation_min,
        preservation_max=preservation_max,
        date_from=parsed_date_from,
        date_to=parsed_date_to,
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        limit=limit,
        offset=offset
    )
    
    return {
        "artifacts": artifacts,
        "total_count": len(artifacts)
    }

@router.get("/catalog/statistics")
async def get_catalog_statistics(db: Session = Depends(get_db)):
    """
    Get statistics about artifacts and materials
    """
    catalog_service = get_catalog_service(db)
    stats = catalog_service.get_material_statistics()
    
    return stats

@router.get("/catalog/trends")
async def get_preservation_trends(db: Session = Depends(get_db)):
    """
    Get trends in preservation over time
    """
    catalog_service = get_catalog_service(db)
    trends = catalog_service.get_preservation_trends()
    
    return trends

@router.post("/train-model")
async def train_ml_model(db: Session = Depends(get_db)):
    """
    Manually trigger training of the ML model with historical data
    """
    db_service = get_db_service(db)
    historical_data = db_service.get_recent_sensor_data(limit=100)
    
    if not historical_data:
        return {"message": "No historical data available for training"}
    
    ml_analysis_service.train_model(historical_data)
    
    return {
        "message": f"Model trained successfully with {len(historical_data)} samples",
        "is_trained": ml_analysis_service.is_trained
    }