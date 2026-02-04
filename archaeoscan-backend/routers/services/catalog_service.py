from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from models.database_models import Artifacts, SensorData
from .database_service import DatabaseService

class CatalogService:
    """
    Service for managing and filtering artifacts
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.db_service = DatabaseService(db)
    
    def get_artifacts_filtered(
        self,
        material: Optional[str] = None,
        preservation_min: Optional[float] = None,
        preservation_max: Optional[float] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        radius_km: Optional[float] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get artifacts with various filters
        """
        query = self.db.query(Artifacts)
        
        # Apply filters
        if material:
            query = query.filter(Artifacts.material.ilike(f"%{material}%"))
        
        if preservation_min is not None:
            query = query.filter(Artifacts.preservation >= preservation_min)
        
        if preservation_max is not None:
            query = query.filter(Artifacts.preservation <= preservation_max)
        
        if date_from:
            query = query.filter(Artifacts.discovered_at >= date_from)
        
        if date_to:
            query = query.filter(Artifacts.discovered_at <= date_to)
        
        # Apply location filter if provided
        if latitude is not None and longitude is not None and radius_km is not None:
            # Simple location filtering (in production, use proper geospatial queries)
            # For now, we'll just filter by a simple proximity check
            all_artifacts = query.all()
            filtered_artifacts = []
            
            for artifact in all_artifacts:
                if artifact.latitude and artifact.longitude:
                    # Simple distance approximation (not accurate for large distances)
                    lat_diff = abs(artifact.latitude - latitude)
                    lon_diff = abs(artifact.longitude - longitude)
                    
                    # Approximate km per degree: 111km per degree of latitude
                    approx_distance = ((lat_diff * 111) ** 2 + (lon_diff * 111) ** 2) ** 0.5
                    
                    if approx_distance <= radius_km:
                        filtered_artifacts.append(artifact)
            
            # Apply limit and offset manually since we're filtering in memory
            start_idx = offset
            end_idx = start_idx + limit
            filtered_results = filtered_artifacts[start_idx:end_idx]
            
            return self._format_artifacts(filtered_results)
        else:
            # Apply limit and offset to database query
            artifacts = query.offset(offset).limit(limit).all()
            return self._format_artifacts(artifacts)
    
    def _format_artifacts(self, artifacts: List[Artifacts]) -> List[Dict[str, Any]]:
        """
        Format artifacts for API response
        """
        result = []
        for artifact in artifacts:
            artifact_dict = {
                "id": artifact.id,
                "name": artifact.name,
                "material": artifact.material,
                "location": {
                    "latitude": artifact.latitude,
                    "longitude": artifact.longitude,
                    "depth": artifact.depth
                },
                "discovered_at": artifact.discovered_at.isoformat() if artifact.discovered_at else None,
                "preservation": artifact.preservation,
                "sensor_data_id": artifact.sensor_data_id,
                "images": artifact.images or [],
                "video_url": artifact.video_url
            }
            
            # Add sensor data if available
            if artifact.sensor_data_record:
                # Handle case where sensor_data might be a list
                sensor_data_item = artifact.sensor_data_record[0] if isinstance(artifact.sensor_data_record, list) else artifact.sensor_data_record
                artifact_dict["sensor_data"] = {
                    "temperature": sensor_data_item.temperature,
                    "turbidity": sensor_data_item.turbidity,
                    "tds": sensor_data_item.tds,
                    "water_preservation": sensor_data_item.water_preservation,
                    "final_preservation": sensor_data_item.final_preservation
                }
            elif artifact.sensor_data_id:
                # If we have sensor_data_id but no joined data, fetch it separately
                sensor_record = self.db.query(SensorData).filter(SensorData.id == artifact.sensor_data_id).first()
                if sensor_record:
                    artifact_dict["sensor_data"] = {
                        "temperature": sensor_record.temperature,
                        "turbidity": sensor_record.turbidity,
                        "tds": sensor_record.tds,
                        "water_preservation": sensor_record.water_preservation,
                        "final_preservation": sensor_record.final_preservation
                    }
            
            result.append(artifact_dict)
        
        return result
    
    def get_material_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about different materials
        """
        artifacts = self.db.query(Artifacts).all()
        
        material_counts = {}
        preservation_by_material = {}
        total_artifacts = len(artifacts)
        
        for artifact in artifacts:
            material = artifact.material or "unknown"
            preservation = artifact.preservation or 0
            
            # Count materials
            if material in material_counts:
                material_counts[material] += 1
            else:
                material_counts[material] = 1
            
            # Track preservation by material
            if material in preservation_by_material:
                preservation_by_material[material].append(preservation)
            else:
                preservation_by_material[material] = [preservation]
        
        # Calculate average preservation by material
        avg_preservation_by_material = {}
        for material, pres_list in preservation_by_material.items():
            avg_preservation_by_material[material] = sum(pres_list) / len(pres_list) if pres_list else 0
        
        return {
            "total_artifacts": total_artifacts,
            "material_distribution": material_counts,
            "average_preservation_by_material": avg_preservation_by_material,
            "top_materials": sorted(
                material_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]  # Top 5 materials
        }
    
    def get_preservation_trends(self) -> Dict[str, Any]:
        """
        Get trends in preservation over time
        """
        # Get recent sensor data
        recent_data = self.db_service.get_recent_sensor_data(limit=100)
        
        if not recent_data:
            return {}
        
        # Group by date and calculate averages
        daily_stats = {}
        for record in recent_data:
            if not record.timestamp:
                continue
                
            date_key = record.timestamp.date().isoformat()
            if date_key not in daily_stats:
                daily_stats[date_key] = {
                    "water_preservation": [],
                    "final_preservation": [],
                    "count": 0
                }
            
            if record.water_preservation is not None:
                daily_stats[date_key]["water_preservation"].append(record.water_preservation)
            
            if record.final_preservation is not None:
                daily_stats[date_key]["final_preservation"].append(record.final_preservation)
                
            daily_stats[date_key]["count"] += 1
        
        # Calculate daily averages
        result = []
        for date_key, stats in daily_stats.items():
            result.append({
                "date": date_key,
                "avg_water_preservation": sum(stats["water_preservation"]) / len(stats["water_preservation"]) if stats["water_preservation"] else 0,
                "avg_final_preservation": sum(stats["final_preservation"]) / len(stats["final_preservation"]) if stats["final_preservation"] else 0,
                "sample_count": stats["count"]
            })
        
        # Sort by date
        result.sort(key=lambda x: x["date"], reverse=True)
        
        return {
            "daily_trends": result,
            "overall_average": sum([r["avg_final_preservation"] for r in result]) / len(result) if result else 0
        }

# Global service instance placeholder (will be instantiated per request)
catalog_service = None

def get_catalog_service(db: Session) -> CatalogService:
    """Get catalog service instance"""
    return CatalogService(db)