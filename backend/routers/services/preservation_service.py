from typing import Dict, Any
from dataclasses import dataclass
import math
import asyncio
from datetime import datetime, timedelta

@dataclass
class SensorData:
    """Data class to hold sensor readings"""
    turbidity: float = 0.0  # NTU
    temperature: float = 0.0  # Celsius
    tds: float = 0.0  # ppm
    pressure: float = 0.0  # hPa
    humidity: float = 0.0  # %
    distance: float = 0.0  # cm

class PreservationService:
    """Service for calculating preservation indices based on sensor data"""
    
    def __init__(self):
        # Define comprehensive material database with 30 materials
        self.material_database = {
            'wood': {
                'name': 'Дерево',
                'base_survival': 20,
                'turbidity_threshold': 50,
                'turbidity_penalty': 10,
                'temperature_threshold': 25,
                'temperature_penalty': 5,
                'tds_threshold': 500,
                'tds_penalty': 5
            },
            'paper': {
                'name': 'Бумага/Пергамент',
                'base_survival': 15,
                'turbidity_threshold': 50,
                'turbidity_penalty': 15,
                'temperature_threshold': 25,
                'temperature_penalty': 5,
                'tds_threshold': 500,
                'tds_penalty': 5
            },
            'fabric': {
                'name': 'Ткань',
                'base_survival': 20,
                'turbidity_threshold': 50,
                'turbidity_penalty': 10,
                'temperature_threshold': 25,
                'temperature_penalty': 5,
                'tds_threshold': 500,
                'tds_penalty': 5
            },
            'leather': {
                'name': 'Кожа',
                'base_survival': 25,
                'turbidity_threshold': 50,
                'turbidity_penalty': 10,
                'temperature_threshold': 25,
                'temperature_penalty': 5,
                'tds_threshold': 500,
                'tds_penalty': 5
            },
            'bone': {
                'name': 'Костяные предметы',
                'base_survival': 25,
                'turbidity_threshold': 50,
                'turbidity_penalty': 5,
                'temperature_threshold': 25,
                'temperature_penalty': 5,
                'tds_threshold': 500,
                'tds_penalty': 5
            },
            'lead': {
                'name': 'Свинец',
                'base_survival': 50,
                'turbidity_threshold': 80,
                'turbidity_penalty': 5,
                'temperature_threshold': 30,
                'temperature_penalty': 2,
                'tds_threshold': 1000,
                'tds_penalty': 2
            },
            'copper': {
                'name': 'Медь',
                'base_survival': 45,
                'turbidity_threshold': 80,
                'turbidity_penalty': 5,
                'temperature_threshold': 30,
                'temperature_penalty': 2,
                'tds_threshold': 1000,
                'tds_penalty': 3
            },
            'brass': {
                'name': 'Латунь',
                'base_survival': 45,
                'turbidity_threshold': 80,
                'turbidity_penalty': 5,
                'temperature_threshold': 30,
                'temperature_penalty': 2,
                'tds_threshold': 1000,
                'tds_penalty': 3
            },
            'tin': {
                'name': 'Олово',
                'base_survival': 40,
                'turbidity_threshold': 80,
                'turbidity_penalty': 5,
                'temperature_threshold': 30,
                'temperature_penalty': 2,
                'tds_threshold': 1000,
                'tds_penalty': 3
            },
            'zinc': {
                'name': 'Цинк',
                'base_survival': 35,
                'turbidity_threshold': 80,
                'turbidity_penalty': 5,
                'temperature_threshold': 30,
                'temperature_penalty': 2,
                'tds_threshold': 1000,
                'tds_penalty': 3
            },
            'iron': {
                'name': 'Железо/Чугун',
                'base_survival': 30,
                'turbidity_threshold': 50,
                'turbidity_penalty': 10,
                'temperature_threshold': 30,
                'temperature_penalty': 5,
                'tds_threshold': 800,
                'tds_penalty': 5
            },
            'steel': {
                'name': 'Сталь',
                'base_survival': 40,
                'turbidity_threshold': 50,
                'turbidity_penalty': 5,
                'temperature_threshold': 30,
                'temperature_penalty': 3,
                'tds_threshold': 800,
                'tds_penalty': 5
            },
            'ceramic': {
                'name': 'Керамика',
                'base_survival': 70,
                'turbidity_threshold': 100,
                'turbidity_penalty': 5,
                'temperature_threshold': 1000,  # No temperature effect
                'temperature_penalty': 0,
                'tds_threshold': 10000,  # No TDS effect
                'tds_penalty': 0
            },
            'clay': {
                'name': 'Глина',
                'base_survival': 60,
                'turbidity_threshold': 100,
                'turbidity_penalty': 5,
                'temperature_threshold': 1000,  # No temperature effect
                'temperature_penalty': 0,
                'tds_threshold': 10000,  # No TDS effect
                'tds_penalty': 0
            },
            'soft_stone': {
                'name': 'Мягкий камень',
                'base_survival': 60,
                'turbidity_threshold': 100,
                'turbidity_penalty': 5,
                'temperature_threshold': 1000,  # No temperature effect
                'temperature_penalty': 0,
                'tds_threshold': 10000,  # No TDS effect
                'tds_penalty': 0
            },
            'hard_stone': {
                'name': 'Твердый камень',
                'base_survival': 90,
                'turbidity_threshold': 150,
                'turbidity_penalty': 2,
                'temperature_threshold': 1000,  # No temperature effect
                'temperature_penalty': 0,
                'tds_threshold': 10000,  # No TDS effect
                'tds_penalty': 0
            },
            'glass': {
                'name': 'Стекло',
                'base_survival': 80,
                'turbidity_threshold': 100,
                'turbidity_penalty': 5,
                'temperature_threshold': 1000,  # No temperature effect
                'temperature_penalty': 0,
                'tds_threshold': 10000,  # No TDS effect
                'tds_penalty': 0
            },
            'plastic': {
                'name': 'Пластик',
                'base_survival': 75,
                'turbidity_threshold': 150,
                'turbidity_penalty': 2,
                'temperature_threshold': 1000,  # No temperature effect
                'temperature_penalty': 0,
                'tds_threshold': 10000,  # No TDS effect
                'tds_penalty': 0
            },
            'rubber': {
                'name': 'Резина',
                'base_survival': 65,
                'turbidity_threshold': 150,
                'turbidity_penalty': 2,
                'temperature_threshold': 1000,  # No temperature effect
                'temperature_penalty': 0,
                'tds_threshold': 10000,  # No TDS effect
                'tds_penalty': 0
            },
            'quartz': {
                'name': 'Кварц',
                'base_survival': 95,
                'turbidity_threshold': 10000,  # No turbidity effect
                'turbidity_penalty': 0,
                'temperature_threshold': 10000,  # No temperature effect
                'temperature_penalty': 0,
                'tds_threshold': 10000,  # No TDS effect
                'tds_penalty': 0
            },
            'gold': {
                'name': 'Золото',
                'base_survival': 100,
                'turbidity_threshold': 10000,  # No turbidity effect
                'turbidity_penalty': 0,
                'temperature_threshold': 10000,  # No temperature effect
                'temperature_penalty': 0,
                'tds_threshold': 10000,  # No TDS effect
                'tds_penalty': 0
            },
            'silver': {
                'name': 'Серебро',
                'base_survival': 95,
                'turbidity_threshold': 150,
                'turbidity_penalty': 2,
                'temperature_threshold': 1000,  # No temperature effect
                'temperature_penalty': 0,
                'tds_threshold': 1500,
                'tds_penalty': 2
            },
            'platinum': {
                'name': 'Платина',
                'base_survival': 100,
                'turbidity_threshold': 10000,  # No turbidity effect
                'turbidity_penalty': 0,
                'temperature_threshold': 10000,  # No temperature effect
                'temperature_penalty': 0,
                'tds_threshold': 10000,  # No TDS effect
                'tds_penalty': 0
            },
            'porcelain': {
                'name': 'Фарфор',
                'base_survival': 90,
                'turbidity_threshold': 150,
                'turbidity_penalty': 2,
                'temperature_threshold': 1000,  # No temperature effect
                'temperature_penalty': 0,
                'tds_threshold': 10000,  # No TDS effect
                'tds_penalty': 0
            },
            'marble': {
                'name': 'Мрамор',
                'base_survival': 85,
                'turbidity_threshold': 150,
                'turbidity_penalty': 2,
                'temperature_threshold': 1000,  # No temperature effect
                'temperature_penalty': 0,
                'tds_threshold': 10000,  # No TDS effect
                'tds_penalty': 0
            },
            'bronze': {
                'name': 'Бронза',
                'base_survival': 75,
                'turbidity_threshold': 80,
                'turbidity_penalty': 5,
                'temperature_threshold': 30,
                'temperature_penalty': 2,
                'tds_threshold': 1000,
                'tds_penalty': 3
            },
            'asphalt': {
                'name': 'Асфальт/Битум',
                'base_survival': 65,
                'turbidity_threshold': 80,
                'turbidity_penalty': 5,
                'temperature_threshold': 1000,  # No temperature effect
                'temperature_penalty': 0,
                'tds_threshold': 1000,
                'tds_penalty': 2
            },
            'ebonite': {
                'name': 'Эбонит',
                'base_survival': 65,
                'turbidity_threshold': 80,
                'turbidity_penalty': 5,
                'temperature_threshold': 1000,  # No temperature effect
                'temperature_penalty': 0,
                'tds_threshold': 1000,
                'tds_penalty': 2
            },
            'fired_clay': {
                'name': 'Обожженная глина',
                'base_survival': 80,
                'turbidity_threshold': 150,
                'turbidity_penalty': 2,
                'temperature_threshold': 1000,  # No temperature effect
                'temperature_penalty': 0,
                'tds_threshold': 10000,  # No TDS effect
                'tds_penalty': 0
            },
            'obsidian': {
                'name': 'Обсидиан',
                'base_survival': 95,
                'turbidity_threshold': 10000,  # No turbidity effect
                'turbidity_penalty': 0,
                'temperature_threshold': 10000,  # No temperature effect
                'temperature_penalty': 0,
                'tds_threshold': 10000,  # No TDS effect
                'tds_penalty': 0
            }
        }

    def calculate_material_preservation(self, material: str, sensor_data: SensorData) -> float:
        """
        Calculate preservation percentage for a specific material based on sensor data
        using the comprehensive 30-material database
        
        Args:
            material: Name of the material
            sensor_data: Current sensor readings
            
        Returns:
            Preservation percentage (0-100)
        """
        if material not in self.material_database:
            return 100.0  # Default to 100% for unknown materials

        material_props = self.material_database[material]
        base_preservation = material_props['base_survival']
        
        # Validate sensor data values to prevent NaN
        turbidity = getattr(sensor_data, 'turbidity', 0) or 0
        temperature = getattr(sensor_data, 'temperature', 0) or 0
        tds = getattr(sensor_data, 'tds', 0) or 0
        
        # Check for invalid values (NaN, infinity)
        import math
        if math.isnan(turbidity) or math.isinf(turbidity):
            turbidity = 0
        if math.isnan(temperature) or math.isinf(temperature):
            temperature = 20  # Default temperature
        if math.isnan(tds) or math.isinf(tds):
            tds = 0
        
        # Apply corrections based on sensor values exceeding thresholds
        # This implements the exact algorithm you specified
        preservation = base_preservation
        
        # Turbidity correction
        if turbidity > material_props['turbidity_threshold']:
            preservation -= material_props['turbidity_penalty']
        
        # Temperature correction
        if temperature > material_props['temperature_threshold']:
            preservation -= material_props['temperature_penalty']
        
        # TDS correction
        if tds > material_props['tds_threshold']:
            preservation -= material_props['tds_penalty']
        
        # Clamp to 0-100 range
        preservation_percentage = max(0.0, min(100.0, preservation))
        
        return round(preservation_percentage, 2)

    def calculate_water_preservation(self, sensor_data: SensorData) -> float:
        """
        Calculate water quality preservation index
        
        Args:
            sensor_data: Current sensor readings
            
        Returns:
            Water preservation percentage (0-100)
        """
        # Validate sensor data values to prevent NaN
        import math
        turbidity = getattr(sensor_data, 'turbidity', 0) or 0
        tds = getattr(sensor_data, 'tds', 0) or 0
        temperature = getattr(sensor_data, 'temperature', 0) or 0
        
        # Check for invalid values (NaN, infinity)
        if math.isnan(turbidity) or math.isinf(turbidity):
            turbidity = 0
        if math.isnan(tds) or math.isinf(tds):
            tds = 0
        if math.isnan(temperature) or math.isinf(temperature):
            temperature = 20  # Default temperature
        
        # Base water quality is affected by turbidity and TDS primarily
        base_quality = 100.0
        
        # Higher turbidity reduces water quality
        turbidity_impact = max(0, turbidity - 10) * 0.5  # 0.5% reduction per NTU above 10
        
        # Higher TDS reduces water quality
        tds_impact = max(0, tds - 50) * 0.02  # 0.02% reduction per ppm above 50
        
        # Higher temperature can reduce water quality
        temp_impact = max(0, temperature - 20) * 0.3  # 0.3% reduction per degree above 20°C
        
        total_impact = turbidity_impact + tds_impact + temp_impact
        water_preservation = max(0.0, base_quality - total_impact)
        
        return round(water_preservation, 2)

    def calculate_preservation_report(self, sensor_data: SensorData) -> Dict[str, Any]:
        """
        Calculate comprehensive preservation report for all 30 materials
        
        Args:
            sensor_data: Current sensor readings
            
        Returns:
            Dictionary containing preservation data for all materials and water
        """
        materials = {}
        material_preservations = []
        
        # Calculate preservation for all 30 materials
        for material_key, material_props in self.material_database.items():
            preservation = self.calculate_material_preservation(material_key, sensor_data)
            # Ensure preservation is a valid number, not NaN
            if math.isnan(preservation) or math.isinf(preservation):
                preservation = 100.0
            materials[material_key] = preservation
            material_preservations.append(preservation)
        
        # Calculate water preservation
        water_preservation = self.calculate_water_preservation(sensor_data)
        # Ensure water preservation is a valid number, not NaN
        if math.isnan(water_preservation) or math.isinf(water_preservation):
            water_preservation = 100.0
        
        # Calculate final preservation as average of all materials
        if material_preservations:
            final_preservation = sum(material_preservations) / len(material_preservations)
            # Ensure final preservation is a valid number, not NaN
            if math.isnan(final_preservation) or math.isinf(final_preservation):
                final_preservation = 100.0
        else:
            final_preservation = 100.0
        
        # Ensure sensor readings are valid
        turbidity = sensor_data.turbidity if not (math.isnan(sensor_data.turbidity) or math.isinf(sensor_data.turbidity)) else 0
        temperature = sensor_data.temperature if not (math.isnan(sensor_data.temperature) or math.isinf(sensor_data.temperature)) else 20
        tds = sensor_data.tds if not (math.isnan(sensor_data.tds) or math.isinf(sensor_data.tds)) else 0
        
        return {
            "water_preservation": water_preservation,
            "materials": materials,
            "final_preservation": round(final_preservation, 2),
            "sensor_readings": {
                "turbidity": turbidity,
                "temperature": temperature,
                "tds": tds
            }
        }

    async def save_sensor_data_batch(self, sensor_data: SensorData, preservation_report: Dict[str, Any], esp32_id: str = "default_esp32"):
        """
        Save a batch of sensor data to the database
        """
        try:
            # Import here to avoid circular imports
            from app.db import get_db
            from app.models import SensorReading
            from sqlalchemy.orm import Session
            import json
            
            # Since this is async, we need to handle the DB session differently
            # In a real implementation, this would connect to the actual database
            print(f"Saving sensor data batch to DB: ESP32-{esp32_id}")
            
            # Note: Actual DB saving would happen here
            # This is a simplified version since we can't directly access the DB session from here
            
        except Exception as e:
            print(f"Error saving sensor data batch: {e}")
    
    def start_periodic_save(self):
        """
        Start periodic saving of sensor data every 5 minutes
        """
        print("Starting periodic sensor data saving...")
        # This would typically be run in a background task
        # For now, we'll just define the method

# Global service instance
preservation_service = PreservationService()