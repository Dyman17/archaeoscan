from fastapi import APIRouter, HTTPException, Response
from typing import Dict, Any, Optional
import json
import csv
from datetime import datetime
import io

router = APIRouter()

# Mock settings storage (in real app, this would be in database)
_settings_storage = {
    "websocketUrl": "ws://localhost:8000/ws",
    "esp32Ip": "172.20.10.9",
    "units": "metric"
}

# Mock data for export (in real app, this would come from database)
_mock_data = [
    {
        "timestamp": "2024-01-15T10:30:00Z",
        "sensor_type": "temperature",
        "value": 22.5,
        "location_lat": 40.7128,
        "location_lng": -74.0060,
        "accuracy": 2.5
    },
    {
        "timestamp": "2024-01-15T10:31:00Z",
        "sensor_type": "humidity",
        "value": 65.2,
        "location_lat": 40.7128,
        "location_lng": -74.0060,
        "accuracy": 2.5
    },
    {
        "timestamp": "2024-01-15T10:32:00Z",
        "sensor_type": "pressure",
        "value": 1013.25,
        "location_lat": 40.7128,
        "location_lng": -74.0060,
        "accuracy": 2.5
    }
]

@router.get("/settings/config")
def get_settings():
    """Get current application settings"""
    return _settings_storage

@router.post("/settings/config")
def update_settings(settings: Dict[str, Any]):
    """Update application settings"""
    global _settings_storage
    
    # Validate settings
    allowed_keys = {"websocketUrl", "esp32Ip", "units"}
    for key in settings:
        if key not in allowed_keys:
            raise HTTPException(status_code=400, detail=f"Invalid setting key: {key}")
    
    # Update settings
    _settings_storage.update(settings)
    
    return {
        "message": "Settings updated successfully",
        "settings": _settings_storage
    }

@router.post("/settings/export/csv")
def export_data_csv():
    """Export collected data as CSV file"""
    # Create CSV content
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    if _mock_data:
        writer.writerow(_mock_data[0].keys())
        
        # Write data rows
        for row in _mock_data:
            writer.writerow(row.values())
    
    # Create response with CSV content
    csv_content = output.getvalue()
    output.close()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"archaeoscan_data_{timestamp}.csv"
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

@router.post("/settings/export/pdf")
def export_data_pdf():
    """Export collected data as PDF file (simplified version)"""
    # In a real implementation, you would use a PDF library like reportlab
    # This is a simplified text-based PDF representation
    
    pdf_content = f"""ArchaeoScan Data Export
======================

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total Records: {len(_mock_data)}

Data Summary:
-------------
"""
    
    # Add data summary
    for record in _mock_data:
        pdf_content += f"""
Timestamp: {record['timestamp']}
Sensor: {record['sensor_type']}
Value: {record['value']}
Location: {record['location_lat']}, {record['location_lng']}
Accuracy: ±{record['accuracy']}m
"""
    
    # Convert to bytes for PDF response
    pdf_bytes = pdf_content.encode('utf-8')
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"archaeoscan_data_{timestamp}.pdf"
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

@router.post("/settings/reset")
def reset_settings():
    """Reset settings to default values"""
    global _settings_storage
    _settings_storage = {
        "websocketUrl": "ws://localhost:8000/ws",
        "esp32Ip": "172.20.10.9",
        "units": "metric"
    }
    
    return {
        "message": "Settings reset to defaults",
        "settings": _settings_storage
    }