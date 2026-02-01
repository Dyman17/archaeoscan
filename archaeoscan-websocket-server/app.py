from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import json
import asyncio
import random
from datetime import datetime

app = FastAPI(title="ArchaeoScan WebSocket Server")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                self.disconnect(connection)

manager = ConnectionManager()

@app.get("/")
async def root():
    return {
        "message": "ArchaeoScan WebSocket Server",
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "websocket": "/ws",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "connections": len(manager.active_connections)}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Simulate real sensor data
            sensor_data = {
                "timestamp": datetime.now().isoformat(),
                "device_id": "archaeoscan_001",
                "sensors": {
                    "battery": round(random.uniform(75, 95), 1),
                    "temperature": round(random.uniform(18, 25), 1),
                    "pressure": round(random.uniform(990, 1020), 1),
                    "humidity": round(random.uniform(55, 75), 1),
                    "magnetometer": {
                        "x": round(random.uniform(-50, 50), 2),
                        "y": round(random.uniform(-50, 50), 2),
                        "z": round(random.uniform(-50, 50), 2)
                    },
                    "accelerometer": {
                        "x": round(random.uniform(-2, 2), 2),
                        "y": round(random.uniform(-2, 2), 2),
                        "z": round(random.uniform(-2, 2), 2)
                    },
                    "gyroscope": {
                        "x": round(random.uniform(-180, 180), 1),
                        "y": round(random.uniform(-180, 180), 1),
                        "z": round(random.uniform(-180, 180), 1)
                    },
                    "turbidity": round(random.uniform(0, 100), 1),
                    "tds": round(random.uniform(200, 800), 0),
                    "depth": round(random.uniform(0, 50), 1),
                    "ph": round(random.uniform(6.5, 8.5), 1)
                },
                "status": "active",
                "location": {
                    "lat": 40.7128,
                    "lng": -74.0060,
                    "depth": 15.2
                }
            }
            
            await manager.send_personal_message(json.dumps(sensor_data), websocket)
            await asyncio.sleep(1)  # Send data every second
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
