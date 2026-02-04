from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio
import aiohttp
import time

router = APIRouter()

# Global config storage (in production, use database)
config_data = {
    "esp_camera_ip": "192.168.1.45",
    "esp_data_ip": "192.168.1.46", 
    "server_ws": "wss://web-production-263d0.up.railway.app/ws",
    "esp32Ip": "192.168.1.45"
}

class ConfigModel(BaseModel):
    esp_camera_ip: str
    esp_data_ip: str
    server_ws: str
    esp32Ip: str

class StatusResponse(BaseModel):
    server: str
    esp32: Dict[str, Any]
    camera: Dict[str, Any]
    ws_clients: int

class PingResponse(BaseModel):
    status: str
    latency: Optional[int] = None

@router.get("/status", response_model=StatusResponse)
async def get_status():
    """Get system status including ESP32 connections"""
    return {
        "server": "online",
        "esp32": {
            "connected": True,  # TODO: Implement actual ESP32 connection check
            "ip": config_data["esp_data_ip"],
            "last_seen": int(time.time())
        },
        "camera": {
            "connected": True,  # TODO: Implement actual camera connection check
            "stream": "on"
        },
        "ws_clients": 0  # TODO: Get actual WebSocket client count
    }

@router.get("/config", response_model=ConfigModel)
async def get_config():
    """Get current configuration"""
    return config_data

@router.post("/config", response_model=ConfigModel)
async def update_config(config: ConfigModel):
    """Update configuration"""
    global config_data
    config_data.update(config.dict())
    return config_data

@router.get("/ping/{target}", response_model=PingResponse)
async def ping_target(target: str):
    """Ping ESP32 devices or server"""
    start_time = time.time()
    
    try:
        if target == "esp-camera":
            # Ping ESP32 camera
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://{config_data['esp_camera_ip']}/status", timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        latency = int((time.time() - start_time) * 1000)
                        return {"status": "ok", "latency": latency}
        elif target == "esp-data":
            # Ping ESP32 data module
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://{config_data['esp_data_ip']}/status", timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        latency = int((time.time() - start_time) * 1000)
                        return {"status": "ok", "latency": latency}
        elif target == "server":
            # Ping self (server)
            latency = int((time.time() - start_time) * 1000)
            return {"status": "ok", "latency": latency}
        else:
            raise HTTPException(status_code=400, detail="Invalid target. Use: esp-camera, esp-data, or server")
            
    except asyncio.TimeoutError:
        return {"status": "timeout"}
    except Exception as e:
        return {"status": "error"}
    
    return {"status": "failed"}
