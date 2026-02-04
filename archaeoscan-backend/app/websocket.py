import asyncio
import json
import logging
from typing import Dict, List, Set
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class SensorData(BaseModel):
    timestamp: int
    sensors: dict = {}
    spectrometer: dict = {}
    radar: dict = {}
    camera: dict = {}

class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.buffer_size = 100  # Maximum number of messages to buffer
        self.message_buffer: List[dict] = []
        self.is_broadcasting = False
        self.broadcast_task = None
        self.loop = None  # Store the event loop reference
        
        # Store the event loop when it's available
        try:
            self.loop = asyncio.get_running_loop()
        except RuntimeError:
            # If no loop is running yet, we'll set it later when possible
            pass

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        
        # Store the loop when a connection is made
        try:
            self.loop = asyncio.get_running_loop()
        except RuntimeError:
            # If no loop is running, create one or handle appropriately
            pass
            
        logger.info(f"WebSocket client connected. Active connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket client disconnected. Active connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except WebSocketDisconnect:
            self.disconnect(websocket)

    async def broadcast(self, message: str):
        """Broadcast message to all connected clients"""
        disconnected_clients = set()
        successful_sends = 0
        
        # Log connection status
        logger.info(f"Attempting broadcast to {len(self.active_connections)} clients")
        
        for connection in self.active_connections.copy():
            try:
                await connection.send_text(message)
                successful_sends += 1
            except WebSocketDisconnect:
                disconnected_clients.add(connection)
            except Exception as e:
                logger.warning(f"Failed to send message to a client: {str(e)}")
                disconnected_clients.add(connection)
        
        # Clean up disconnected clients
        for client in disconnected_clients:
            self.disconnect(client)
            
        logger.info(f"Broadcast completed: {successful_sends}/{len(self.active_connections)} clients")

    def add_to_buffer(self, data: dict):
        """Add data to buffer for potential retransmission"""
        self.message_buffer.append(data)
        if len(self.message_buffer) > self.buffer_size:
            self.message_buffer.pop(0)  # Remove oldest entry

    async def start_broadcasting(self):
        """Start the broadcasting task if not already running"""
        if not self.is_broadcasting and self.broadcast_task is None:
            self.is_broadcasting = True
            self.broadcast_task = asyncio.create_task(self._broadcast_loop())

    async def stop_broadcasting(self):
        """Stop the broadcasting task"""
        if self.is_broadcasting and self.broadcast_task:
            self.is_broadcasting = False
            self.broadcast_task.cancel()
            try:
                await self.broadcast_task
            except asyncio.CancelledError:
                pass
            self.broadcast_task = None

    async def _broadcast_loop(self):
        """Internal loop for handling broadcasts"""
        while self.is_broadcasting:
            await asyncio.sleep(0.01)  # Small delay to prevent busy waiting

    async def send_sensor_data(self, data: SensorData):
        """Send sensor data to all connected clients"""
        json_data = data.dict() if hasattr(data, 'dict') else data.model_dump()
        await self.broadcast(json.dumps(json_data))
        self.add_to_buffer(json_data)
    
    def send_sensor_data_from_thread(self, data: SensorData):
        """Send sensor data from a thread context"""
        # Ensure we have a loop reference
        if not self.loop:
            try:
                self.loop = asyncio.get_event_loop_policy().get_event_loop()
            except RuntimeError:
                logger.error("No event loop available to send sensor data from thread")
                return
        
        import json
        json_data = data.dict() if hasattr(data, 'dict') else data.model_dump()
        message = json.dumps(json_data)
        
        # Use run_coroutine_threadsafe to send from thread
        future = asyncio.run_coroutine_threadsafe(self.broadcast(message), self.loop)
        try:
            # Wait for the broadcast to complete
            result = future.result(timeout=1.0)
            logger.info(f"Successfully sent sensor data from thread")
        except Exception as e:
            logger.error(f"Failed to send sensor data from thread: {e}")

manager = ConnectionManager()

# Predefined sample data for demonstration
sample_sensor_data = {
    "timestamp": int(datetime.now().timestamp() * 1000),
    "sensors": {
        "temperature": 22.5,
        "humidity": 45.2,
        "pressure": 1013.2,
        "tds": 420,
        "turbidity": 30,
        "distance": 3.2,
        "magnetometer": [0.12, -0.45, 0.89],
        "accelerometer": [0.02, 0.01, 9.81],
        "gyroscope": [0.001, -0.002, 0.003],
        "battery": 85.5,
        "gps": {"lat": 55.7558, "lng": 37.6176, "accuracy": 2.5}
    },
    "spectrometer": {
        "wavelengths": [400, 410, 420, 430, 440, 450, 460, 470, 480, 490, 500, 510, 520, 530, 540, 550, 560, 570, 580, 590, 600, 610, 620, 630, 640, 650, 660, 670, 680, 690, 700, 710, 720, 730, 740, 750, 760, 770, 780, 790, 800, 810, 820, 830, 840, 850, 860, 870, 880, 890, 900, 910, 920, 930, 940, 950, 960, 970, 980, 990, 1000],
        "intensity": [0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95, 0.85, 0.75, 0.65, 0.55, 0.45, 0.35, 0.25, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95, 0.85, 0.75, 0.65, 0.55, 0.45, 0.35, 0.25, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95, 0.85, 0.75, 0.65, 0.55, 0.45, 0.35, 0.25, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95, 0.85, 0.75, 0.65, 0.55, 0.45, 0.35, 0.25]
    },
    "radar": {
        "depth_profile": [0.1, 0.3, 0.5, 0.7, 0.9, 1.1, 1.3, 1.5, 1.7, 1.9, 2.1, 2.3, 2.5],
        "anomalies": [{"x": 1.2, "y": 0.5, "type": "metal", "confidence": 0.85}, {"x": 2.1, "y": 1.3, "type": "stone", "confidence": 0.72}]
    },
    "camera": {
        "image_base64": "",
        "gps": {"lat": 55.7558, "lng": 37.6176}
    }
}

async def simulate_sensor_stream():
    """Simulate continuous sensor data streaming"""
    while manager.is_broadcasting:
        # Update timestamp
        sample_sensor_data["timestamp"] = int(datetime.now().timestamp() * 1000)
        
        # Slightly vary some sensor values to simulate real data
        sample_sensor_data["sensors"]["temperature"] += (0.1 - 0.2 * (datetime.now().second % 10) / 10)
        sample_sensor_data["sensors"]["humidity"] += (0.2 - 0.4 * (datetime.now().second % 10) / 10)
        sample_sensor_data["sensors"]["battery"] -= 0.001  # Simulate slight battery drain
        
        # Add subtle, varying accelerometer values within -20 to +20 range
        import random
        ax = max(-20, min(20, sample_sensor_data["sensors"]["accelerometer"][0] + random.uniform(-0.01, 0.01)))
        ay = max(-20, min(20, sample_sensor_data["sensors"]["accelerometer"][1] + random.uniform(-0.01, 0.01)))
        az = max(-20, min(20, sample_sensor_data["sensors"]["accelerometer"][2] + random.uniform(-0.01, 0.01)))
        sample_sensor_data["sensors"]["accelerometer"] = [ax, ay, az]
        
        # Add subtle, varying magnetometer values within -20 to +20 range
        mx = max(-20, min(20, sample_sensor_data["sensors"]["magnetometer"][0] + random.uniform(-0.01, 0.01)))
        my = max(-20, min(20, sample_sensor_data["sensors"]["magnetometer"][1] + random.uniform(-0.01, 0.01)))
        mz = max(-20, min(20, sample_sensor_data["sensors"]["magnetometer"][2] + random.uniform(-0.01, 0.01)))
        sample_sensor_data["sensors"]["magnetometer"] = [mx, my, mz]
        
        # Add subtle, varying spectrometer intensity values
        # Change wavelengths to be from 0 to 750 range as requested
        base_wavelengths = list(range(0, 751, 10))  # 0, 10, 20, ..., 750 (76 values)
        base_intensity = [random.uniform(0.1, 1.0) for _ in base_wavelengths]  # Random intensities between 0.1 and 1.0
        # Apply small random variations to intensity values
        varied_intensity = []
        for i, val in enumerate(base_intensity):
            variation = random.uniform(-0.01, 0.01)  # Very small variation
            new_val = max(0.0, min(1.0, val + variation))  # Clamp between 0 and 1
            varied_intensity.append(new_val)
        sample_sensor_data["spectrometer"]["wavelengths"] = base_wavelengths
        sample_sensor_data["spectrometer"]["intensity"] = varied_intensity
        
        if sample_sensor_data["sensors"]["battery"] < 20:
            sample_sensor_data["sensors"]["battery"] = 100  # Reset battery simulation
            
        await manager.send_sensor_data(SensorData(**sample_sensor_data))
        await asyncio.sleep(0.1)  # Send data at ~10Hz rate