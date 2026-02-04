from fastapi import APIRouter, HTTPException, WebSocket
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json
import asyncio

router = APIRouter()

class ESP32SensorData(BaseModel):
    lat: float
    lng: float
    depth: float
    mag: float  # Magnetic field strength
    spectrum: List[float]  # Spectrometer data array
    timestamp: int
    device_id: Optional[str] = None

class ESP32Response(BaseModel):
    status: str
    message: str
    timestamp: int

# Store latest ESP32 data
latest_esp32_data = None
esp32_last_seen = None

@router.post("/data", response_model=ESP32Response)
async def receive_esp32_data(data: ESP32SensorData):
    """Receive sensor data from ESP32"""
    global latest_esp32_data, esp32_last_seen
    
    try:
        # Store the data
        latest_esp32_data = data.dict()
        esp32_last_seen = datetime.now()
        
        # Broadcast to WebSocket clients
        from app.websocket import manager
        await manager.broadcast(json.dumps({
            "type": "sensor_data",
            "data": data.dict()
        }))
        
        print(f"Received ESP32 data: {data.lat}, {data.lng} at depth {data.depth}m")
        
        return {
            "status": "success",
            "message": "Data received successfully",
            "timestamp": int(datetime.now().timestamp())
        }
        
    except Exception as e:
        print(f"Error processing ESP32 data: {e}")
        raise HTTPException(status_code=500, detail="Failed to process data")

@router.get("/data/latest")
async def get_latest_data():
    """Get latest ESP32 sensor data"""
    if latest_esp32_data is None:
        raise HTTPException(status_code=404, detail="No data available")
    
    return latest_esp32_data

@router.get("/status")
async def esp32_status():
    """Get ESP32 connection status"""
    if esp32_last_seen is None:
        return {
            "connected": False,
            "last_seen": None,
            "message": "No data received yet"
        }
    
    # Check if ESP32 is considered online (data received in last 30 seconds)
    time_diff = (datetime.now() - esp32_last_seen).total_seconds()
    is_online = time_diff < 30
    
    return {
        "connected": is_online,
        "last_seen": int(esp32_last_seen.timestamp()),
        "seconds_since_last": int(time_diff),
        "message": "Online" if is_online else f"Offline (last seen {int(time_diff)}s ago)"
    }

@router.websocket("/ws")
async def esp32_websocket(websocket: WebSocket):
    """WebSocket connection for real-time ESP32 data"""
    await websocket.accept()
    print("ESP32 connected via WebSocket")
    
    try:
        while True:
            # Receive data from ESP32
            data = await websocket.receive_text()
            
            try:
                # Parse JSON data
                sensor_data = ESP32SensorData(**json.loads(data))
                
                # Store and broadcast
                global latest_esp32_data, esp32_last_seen
                latest_esp32_data = sensor_data.dict()
                esp32_last_seen = datetime.now()
                
                # Broadcast to frontend clients
                from app.websocket import manager
                await manager.broadcast(json.dumps({
                    "type": "sensor_data",
                    "data": sensor_data.dict()
                }))
                
                # Send acknowledgment to ESP32
                await websocket.send_text(json.dumps({
                    "status": "received",
                    "timestamp": int(datetime.now().timestamp())
                }))
                
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "status": "error",
                    "message": "Invalid JSON format"
                }))
            except Exception as e:
                await websocket.send_text(json.dumps({
                    "status": "error", 
                    "message": str(e)
                }))
                
    except Exception as e:
        print(f"ESP32 WebSocket error: {e}")
    finally:
        print("ESP32 disconnected")
