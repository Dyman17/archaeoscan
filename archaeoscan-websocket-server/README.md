---
title: Archaeoscan WebSocket Server
emoji: 🌖
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: "4.44.0"
app_file: app.py
python_version: 3.11
pinned: false
---

# 🏺 ArchaeoScan WebSocket Server

Real-time archaeological monitoring WebSocket server for underwater sensors.

## 🚀 Features

- 🌊 **Real-time WebSocket streaming** - Live sensor data every second
- 📡 **CORS enabled** - Ready for frontend connections
- 🏥 **Health monitoring** - Track active connections
- 📊 **Rich sensor data** - Multiple sensor types supported
- 🔧 **FastAPI powered** - Modern async Python server

## 📡 API Endpoints

### WebSocket
- **URL**: `wss://dyman17-archaeoscan-ws.hf.space/ws`
- **Protocol**: WebSocket
- **Data**: JSON sensor data every 1 second

### HTTP Endpoints
- **Root**: `https://dyman17-archaeoscan-ws.hf.space/`
- **Health**: `https://dyman17-archaeoscan-ws.hf.space/health`
- **API Docs**: `https://dyman17-archaeoscan-ws.hf.space/docs`

## 📊 Sensor Data Format

```json
{
  "timestamp": "2026-01-31T18:00:00.000Z",
  "device_id": "archaeoscan_001",
  "sensors": {
    "battery": 85.2,
    "temperature": 22.5,
    "pressure": 1005.3,
    "humidity": 65.8,
    "magnetometer": { "x": 12.3, "y": -5.7, "z": 8.1 },
    "accelerometer": { "x": 0.1, "y": -0.2, "z": 9.8 },
    "gyroscope": { "x": 15.2, "y": -8.7, "z": 2.1 },
    "turbidity": 45.6,
    "tds": 450,
    "depth": 15.2,
    "ph": 7.2
  },
  "status": "active",
  "location": {
    "lat": 40.7128,
    "lng": -74.0060,
    "depth": 15.2
  }
}
```

## 🔧 Frontend Integration

### WebSocket Connection (JavaScript)
```javascript
const ws = new WebSocket('wss://dyman17-archaeoscan-ws.hf.space/ws');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Sensor data:', data);
    // Update your UI with sensor data
};
```

### React Hook Example
```javascript
import { useEffect, useState } from 'react';

function useArchaeoScanWebSocket() {
    const [data, setData] = useState(null);
    
    useEffect(() => {
        const ws = new WebSocket('wss://dyman17-archaeoscan-ws.hf.space/ws');
        
        ws.onmessage = (event) => {
            setData(JSON.parse(event.data));
        };
        
        return () => ws.close();
    }, []);
    
    return data;
}
```

## 🏗️ Architecture

```
Frontend (React/Vue/JS) ←→ WebSocket Server ←→ ESP32 Sensors
```

## 📱 Supported Sensors

- **TLV493D** - Magnetometer (3-axis magnetic field)
- **MPU-9250** - Accelerometer + Gyroscope (9-axis IMU)
- **AS7343** - Spectrometer (light spectrum analysis)
- **TS-300b** - Turbidity sensor (water clarity)
- **DS18B20** - Water temperature sensor
- **TDS Meter** - Total dissolved solids
- **HC-SR04T** - Ultrasonic distance sensor
- **pH Sensor** - Water acidity/alkalinity

## 🚀 Deployment

This server is deployed on HuggingFace Spaces and automatically:
- ✅ Handles WebSocket connections
- ✅ Manages connection lifecycle
- ✅ Simulates real sensor data
- ✅ Provides CORS for frontend access
- ✅ Monitors active connections

## 📈 Real-time Data

The server generates realistic sensor data every second:
- Battery levels fluctuate between 75-95%
- Temperature varies 18-25°C
- Pressure ranges 990-1020 hPa
- Location coordinates (NYC area)
- All sensor values with realistic noise

**Perfect for testing and development!** 🎯
