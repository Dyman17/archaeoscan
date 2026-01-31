# ArchaeoScan Backend

This is the backend for the ArchaeoScan web application - a professional platform for archaeological surveying, particularly focused on underwater sensors and ocean floor studies. The backend is built with FastAPI and provides real-time data streaming, data processing, and AI-powered analysis.

## Features Implemented

### 1. WebSocket Streaming
- Endpoint: `ws://<server>:<port>/ws`
- Real-time sensor readings, radar, GPS, and camera data streaming
- 1–10Hz frequency depending on sensor type
- Automatic reconnection and buffering for temporary disconnects
- Data structure includes timestamp, sensors, spectrometer, radar, and camera data

### 2. REST API Endpoints

#### `/api/sensors`
- GET historical sensor data with filtering by time range and sensor type
- POST new sensor readings
- Supports 8 main sensors: TLV493D (magnetometer), MPU-9250 (accelerometer/gyro), piezo, AS7343 (spectrometer), TS-300b (turbidity), DS18B20 (water temp), TDS meter, HC-SR04T (ultrasonic)

#### `/api/calibrate`
- POST calibration commands per sensor type
- Supports all sensor types mentioned above

#### `/api/system/status`
- GET current system health status
- Connection status, battery level, sensor statuses, active alerts

#### `/api/control`
- POST device commands (start scan, stop scan, reset sensor, etc.)

#### `/api/reports`
- GET pre-calculated analysis and summaries
- POST to generate analysis reports

#### `/api/camera`
- POST images/video from ESP32-CAM with GPS

#### `/api/materials/analyze`
- POST spectrometer + sensor data, return material classification

### 3. Data Processing & AI Services

#### Material Classification
- Input: spectrometer readings, environmental context
- Output: material type (metal, ceramic, organic, stone, unknown) + confidence
- Uses Random Forest classifier with spectral feature extraction

#### Environmental Preservation Index
- Calculates preservation likelihood based on temperature, TDS, turbidity, depth, and pH
- Weighted combination formula for 0-100% preservation percentage
- Recommendations based on preservation index

#### Radar Processing
- Filters and processes GPR (Ground Penetrating Radar) signals
- Detects anomalies and classifies them (metal, stone, void, organic)
- Analyzes depth profiles and identifies geological layers

### 4. Data Storage
- SQL database (SQLite/PostgreSQL) with tables for:
  - Raw sensor readings
  - Spectrometer data
  - Radar results
  - Camera images + GPS
  - Calculated preservation indices
  - Material classification results
  - System status logs
  - Calibration data
  - Reports

### 5. Performance & Scalability
- Async FastAPI + WebSockets for real-time updates
- Support for up to 10Hz updates per sensor
- Efficient database queries and indexing
- Minimal CPU/memory footprint

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │◄──►│   FastAPI        │◄──►│  ESP32 Sensors  │
│ (React +       │   │   Backend        │   │                 │
│  Tailwind CSS)  │   │                  │   │                 │
└─────────────────┘   └──────────────────┘   └─────────────────┘
                          │    │    │
                          ▼    ▼    ▼
                    ┌──────────────────┐
                    │  Data Processing │
                    │  & AI Services   │
                    └──────────────────┘
                          │
                          ▼
                    ┌──────────────────┐
                    │   Database       │
                    │  (SQL/NoSQL)     │
                    └──────────────────┘
```

## Setup Instructions

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python main.py
```

3. The application will be available at `http://localhost:8000`

## API Documentation

Full API documentation is available at `http://localhost:8000/docs` when the application is running.

## Security & Reliability

- Input validation for all endpoints
- Proper error handling with clear JSON error messages
- Data integrity validation for JSON and base64 image data
- Automatic reconnection for WebSocket clients
- Logging for debugging and audit purposes