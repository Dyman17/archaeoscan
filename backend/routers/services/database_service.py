from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from datetime import datetime
from models.database_models import (
    SensorData, Artifacts, RadarImages, MapSnapshots, 
    VideoStreams, Settings, MaterialType
)
from .preservation_service import preservation_service, SensorData as SensorDataClass
from .notifications_service import notifications_service

class DatabaseService:
    """Service for database operations"""
    
    def __init__(self, db: Session):
        self.db = db

    def create_sensor_data(self, 
                          artifact_id: Optional[int],
                          esp32_id: str,
                          temperature: Optional[float] = None,
                          turbidity: Optional[float] = None,
                          tds: Optional[float] = None,
                          latitude: Optional[float] = None,
                          longitude: Optional[float] = None,
                          accuracy: Optional[float] = None,
                          signal_strength: Optional[str] = None,
                          battery: Optional[float] = None,
                          pressure: Optional[float] = None,
                          humidity: Optional[float] = None,
                          distance: Optional[float] = None) -> SensorData:
        """
        Create a new sensor data record and calculate preservation indices
        """
        # Create sensor data object
        sensor_data = SensorData(
            artifact_id=artifact_id,
            esp32_id=esp32_id,
            temperature=temperature,
            turbidity=turbidity,
            tds=tds,
            latitude=latitude,
            longitude=longitude,
            accuracy=accuracy,
            signal_strength=signal_strength,
            battery=battery,
            pressure=pressure,
            humidity=humidity,
            distance=distance
        )
        
        # Calculate preservation indices using the preservation service
        sensor_obj = SensorDataClass(
            turbidity=turbidity or 0,
            temperature=temperature or 0,
            tds=tds or 0,
            pressure=pressure or 0,
            humidity=humidity or 0,
            distance=distance or 0
        )
        
        preservation_report = preservation_service.calculate_preservation_report(sensor_obj)
        
        # Add preservation data to the sensor record
        sensor_data.water_preservation = preservation_report["water_preservation"]
        sensor_data.material_preservation = preservation_report["materials"]
        sensor_data.final_preservation = preservation_report["final_preservation"]
        
        try:
            self.db.add(sensor_data)
            self.db.commit()
            self.db.refresh(sensor_data)
            
            # Check for alerts based on sensor data
            settings = self.db.query(Settings).first()
            alerts = notifications_service.check_for_alerts(sensor_data, settings)
            
            # Send notifications for any alerts
            for alert in alerts:
                import asyncio
                # Schedule notification in a separate task to avoid blocking
                asyncio.create_task(notifications_service.broadcast_notification(alert))
            
            return sensor_data
        except IntegrityError:
            self.db.rollback()
            raise

    def get_sensor_data(self, sensor_id: int) -> Optional[SensorData]:
        """Get a specific sensor data record"""
        return self.db.query(SensorData).filter(SensorData.id == sensor_id).first()

    def get_recent_sensor_data(self, limit: int = 100) -> List[SensorData]:
        """Get recent sensor data records"""
        return self.db.query(SensorData).order_by(SensorData.timestamp.desc()).limit(limit).all()

    def create_artifact(self,
                       name: Optional[str],
                       material: str,
                       latitude: float,
                       longitude: float,
                       depth: Optional[float] = None,
                       preservation: Optional[float] = None,
                       sensor_data_id: Optional[int] = None,
                       images: Optional[List[str]] = None,
                       video_url: Optional[str] = None,
                       radar_image: Optional[str] = None) -> Artifacts:
        """
        Create a new artifact record
        """
        artifact = Artifacts(
            name=name,
            material=material,
            latitude=latitude,
            longitude=longitude,
            depth=depth,
            preservation=preservation,
            sensor_data_id=sensor_data_id,
            images=images,
            video_url=video_url,
            radar_image=radar_image
        )
        
        try:
            self.db.add(artifact)
            self.db.commit()
            self.db.refresh(artifact)
            
            # Send notification for new artifact
            import asyncio
            artifact_notification = notifications_service.create_new_artifact_notification({
                "id": artifact.id,
                "name": artifact.name,
                "material": artifact.material,
                "latitude": artifact.latitude,
                "longitude": artifact.longitude,
                "preservation": artifact.preservation
            })
            asyncio.create_task(notifications_service.broadcast_notification(artifact_notification))
            
            return artifact
        except IntegrityError:
            self.db.rollback()
            raise

    def get_artifact(self, artifact_id: int) -> Optional[Artifacts]:
        """Get a specific artifact"""
        return self.db.query(Artifacts).filter(Artifacts.id == artifact_id).first()

    def get_artifacts_by_location(self, latitude: float, longitude: float, radius_km: float = 1.0) -> List[Artifacts]:
        """Get artifacts near a specific location"""
        # Simple distance calculation (not accurate for large distances)
        # For production, use proper geospatial queries
        return self.db.query(Artifacts).all()  # Simplified for now

    def create_radar_image(self, artifact_id: Optional[int], image_url: str) -> RadarImages:
        """Create a new radar image record"""
        radar_image = RadarImages(
            artifact_id=artifact_id,
            image_url=image_url
        )
        
        try:
            self.db.add(radar_image)
            self.db.commit()
            self.db.refresh(radar_image)
            return radar_image
        except IntegrityError:
            self.db.rollback()
            raise

    def create_map_snapshot(self, artifact_id: Optional[int], image_url: str) -> MapSnapshots:
        """Create a new map snapshot record"""
        map_snapshot = MapSnapshots(
            artifact_id=artifact_id,
            image_url=image_url
        )
        
        try:
            self.db.add(map_snapshot)
            self.db.commit()
            self.db.refresh(map_snapshot)
            return map_snapshot
        except IntegrityError:
            self.db.rollback()
            raise

    def create_video_stream(self, artifact_id: Optional[int], file_path: str, duration: Optional[float] = None) -> VideoStreams:
        """Create a new video stream record"""
        video_stream = VideoStreams(
            artifact_id=artifact_id,
            file_path=file_path,
            duration=duration
        )
        
        try:
            self.db.add(video_stream)
            self.db.commit()
            self.db.refresh(video_stream)
            return video_stream
        except IntegrityError:
            self.db.rollback()
            raise

    def get_or_create_settings(self) -> Settings:
        """Get existing settings or create default settings"""
        settings = self.db.query(Settings).first()
        if not settings:
            settings = Settings()
            self.db.add(settings)
            self.db.commit()
            self.db.refresh(settings)
        return settings

    def update_settings(self, 
                       esp32_ip: Optional[str] = None,
                       camera_settings: Optional[dict] = None,
                       map_zoom: Optional[int] = None,
                       map_center: Optional[dict] = None,
                       alerts: Optional[dict] = None) -> Settings:
        """Update settings"""
        settings = self.get_or_create_settings()
        
        if esp32_ip is not None:
            settings.esp32_ip = esp32_ip
        if camera_settings is not None:
            settings.camera_settings = camera_settings
        if map_zoom is not None:
            settings.map_zoom = map_zoom
        if map_center is not None:
            settings.map_center = map_center
        if alerts is not None:
            settings.alerts = alerts
            
        settings.last_updated = datetime.utcnow()
        
        try:
            self.db.commit()
            self.db.refresh(settings)
            return settings
        except IntegrityError:
            self.db.rollback()
            raise

# Global service instance
db_service = None

def get_db_service(db: Session) -> DatabaseService:
    """Get database service instance"""
    global db_service
    if db_service is None:
        db_service = DatabaseService(db)
    return db_service