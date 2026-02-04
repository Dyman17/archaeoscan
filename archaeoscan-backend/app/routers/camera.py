from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Response
from fastapi.responses import StreamingResponse
import os
from pathlib import Path
import requests
from datetime import datetime
import subprocess
import threading
import cv2
import numpy as np
from sqlalchemy.orm import Session
from typing import List, Optional
import base64
import binascii
from datetime import datetime
import httpx
import asyncio

from app import models, db
from app.schemas import (
    CameraReadingRequest, CameraReadingResponse
)

router = APIRouter()

@router.post("/camera")
def upload_camera_image(camera_data: CameraReadingRequest, db: Session = Depends(db.get_db)):
    """
    Receive images/video streams from ESP32-CAM.
    """
    # Validate base64 image data
    try:
        # Attempt to decode the base64 string to validate it
        base64_bytes = camera_data.image_base64.encode('utf-8')
        decoded_bytes = base64.b64decode(base64_bytes)
        # Re-encode to ensure it's valid
        reencoded = base64.b64encode(decoded_bytes).decode('utf-8')
    except (binascii.Error, ValueError):
        raise HTTPException(status_code=400, detail="Invalid base64 image data")
    
    # Create camera reading record
    db_camera_reading = models.CameraReading(
        timestamp=datetime.fromtimestamp(camera_data.timestamp / 1000) if camera_data.timestamp else datetime.utcnow(),
        image_base64=camera_data.image_base64,
        location_lat=camera_data.location_lat,
        location_lng=camera_data.location_lng,
        accuracy=camera_data.accuracy,
        battery_level=camera_data.battery_level,
        device_id=camera_data.device_id
    )
    
    db.add(db_camera_reading)
    db.commit()
    db.refresh(db_camera_reading)
    
    return {
        "message": "Camera image received successfully",
        "id": db_camera_reading.id,
        "timestamp": db_camera_reading.timestamp
    }

@router.get("/camera/images", response_model=List[CameraReadingResponse])
def get_camera_images(
    device_id: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(db.get_db)
):
    """
    Get stored camera images with optional filtering.
    """
    query = db.query(models.CameraReading)
    
    if device_id:
        query = query.filter(models.CameraReading.device_id == device_id)
    if start_time:
        query = query.filter(models.CameraReading.timestamp >= start_time)
    if end_time:
        query = query.filter(models.CameraReading.timestamp <= end_time)
    
    query = query.order_by(models.CameraReading.timestamp.desc())
    query = query.offset(skip).limit(limit)
    
    camera_readings = query.all()
    
    response_images = []
    for reading in camera_readings:
        response_images.append(CameraReadingResponse(
            id=reading.id,
            timestamp=reading.timestamp,
            image_base64=reading.image_base64,
            location_lat=reading.location_lat,
            location_lng=reading.location_lng,
            accuracy=reading.accuracy,
            battery_level=reading.battery_level,
            device_id=reading.device_id
        ))
    
    return response_images

@router.get("/camera/latest")
def get_latest_camera_image(
    device_id: Optional[str] = "default_camera",
    db: Session = Depends(db.get_db)
):
    """
    Get the most recent camera image from a specific device.
    """
    camera_reading = db.query(models.CameraReading)\
        .filter(models.CameraReading.device_id == device_id)\
        .order_by(models.CameraReading.timestamp.desc())\
        .first()
    
    if not camera_reading:
        raise HTTPException(status_code=404, detail="No camera images found for the device")
    
    return CameraReadingResponse(
        id=camera_reading.id,
        timestamp=camera_reading.timestamp,
        image_base64=camera_reading.image_base64,
        location_lat=camera_reading.location_lat,
        location_lng=camera_reading.location_lng,
        accuracy=camera_reading.accuracy,
        battery_level=camera_reading.battery_level,
        device_id=camera_reading.device_id
    )

@router.get("/camera/stream")
async def stream_camera_video():
    """
    Proxy MJPEG stream from ESP32-CAM through backend to avoid mixed content issues.
    This allows HTTPS websites to display HTTP camera streams.
    """
    # Get ESP32-CAM IP from settings
    from .settings import _settings_storage
    esp32_ip = _settings_storage.get("esp32Ip", "172.20.10.9")
    stream_url = f"http://{esp32_ip}:81/stream"
    
    try:
        # Use httpx to stream the response
        async with httpx.AsyncClient() as client:
            async with client.stream("GET", stream_url) as response:
                # Set appropriate headers for MJPEG stream
                headers = {
                    "Content-Type": "multipart/x-mixed-replace; boundary=frame",
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Access-Control-Allow-Origin": "*",
                }
                
                async def stream_generator():
                    async for chunk in response.aiter_bytes():
                        yield chunk
                
                return StreamingResponse(
                    stream_generator(),
                    media_type="multipart/x-mixed-replace; boundary=frame",
                    headers=headers
                )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect to ESP32-CAM: {str(e)}")


@router.get("/snapshot")
async def capture_snapshot():
    """
    Capture a snapshot from ESP32-CAM and save to media folder.
    """
    # Get ESP32-CAM IP from settings
    from .settings import _settings_storage
    esp32_ip = _settings_storage.get("esp32Ip", "172.20.10.9")
    snapshot_url = f"http://{esp32_ip}/capture"
    
    try:
        # Create media directories if they don't exist
        media_path = Path("media")
        snapshots_path = media_path / "snapshots"
        snapshots_path.mkdir(parents=True, exist_ok=True)
        
        # Capture the snapshot from ESP32
        response = requests.get(snapshot_url, timeout=10)
        if response.status_code == 200:
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
            filename = f"snapshot_{timestamp}.jpg"
            filepath = snapshots_path / filename
            
            # Save the image to the snapshots folder
            with open(filepath, "wb") as f:
                f.write(response.content)
            
            return {
                "message": "Snapshot captured successfully",
                "filename": filename,
                "path": str(filepath)
            }
        else:
            raise HTTPException(status_code=response.status_code, detail="Failed to capture snapshot from ESP32-CAM")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to capture snapshot: {str(e)}")


# Global variable to track recording process
recording_process = None
recording_filename = None

capturing_frames = False  # Flag to control frame capture

@router.post("/record/start")
async def start_recording():
    """
    Start recording video from ESP32-CAM.
    """
    global recording_process, recording_filename
    
    if recording_process is not None and recording_process.poll() is None:
        raise HTTPException(status_code=400, detail="Recording is already in progress")
    
    try:
        # Get ESP32-CAM IP from settings
        from .settings import _settings_storage
        esp32_ip = _settings_storage.get("esp32Ip", "172.20.10.9")
        stream_url = f"http://{esp32_ip}:81/stream"
        
        # Create media directories if they don't exist
        media_path = Path("media")
        recordings_path = media_path / "recordings"
        recordings_path.mkdir(parents=True, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
        recording_filename = f"recording_{timestamp}.mp4"
        filepath = recordings_path / recording_filename
        
        # Try to use FFmpeg first, fallback to OpenCV if not available
        try:
            # Use FFmpeg to capture the MJPEG stream and convert to MP4
            cmd = [
                "ffmpeg",
                "-i", stream_url,
                "-t", "300",  # Maximum recording time: 5 minutes
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-pix_fmt", "yuv420p",
                "-movflags", "faststart",
                str(filepath),
                "-y"  # Overwrite output files without asking
            ]
            
            # Start FFmpeg process in a separate thread
            recording_process = subprocess.Popen(cmd)
        except FileNotFoundError:
            # FFmpeg not found, use OpenCV as fallback
            print("FFmpeg not found, using OpenCV fallback for recording")
            # Start recording thread with OpenCV
            recording_thread = threading.Thread(target=record_with_opencv, args=(stream_url, str(filepath)))
            recording_thread.daemon = True
            recording_thread.start()
            recording_process = recording_thread  # Store thread reference instead of process
        
        return {
            "message": "Recording started successfully",
            "filename": recording_filename,
            "path": str(filepath)
        }
        
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="FFmpeg is not installed or not found in PATH")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start recording: {str(e)}")


@router.post("/record/stop")
async def stop_recording():
    """
    Stop recording video from ESP32-CAM.
    """
    global recording_process, recording_filename
    
    if recording_process is None:
        raise HTTPException(status_code=400, detail="No recording is in progress")
    
    try:
        # Check if recording_process is a subprocess (FFmpeg) or thread (OpenCV)
        if hasattr(recording_process, 'terminate'):  # FFmpeg process
            recording_process.terminate()
            recording_process.wait(timeout=5)  # Wait up to 5 seconds for graceful shutdown
        else:  # OpenCV thread
            stop_opencv_recording()
            # Wait a moment for the thread to finish
            import time
            time.sleep(1)
        
        recording_process = None
        
        return {
            "message": "Recording stopped successfully",
            "filename": recording_filename
        }
        
    except subprocess.TimeoutExpired:
        # Force kill if it doesn't terminate gracefully
        recording_process.kill()
        recording_process = None
        
        return {
            "message": "Recording stopped (forced termination)",
            "filename": recording_filename
        }
    except Exception as e:
        recording_process = None
        raise HTTPException(status_code=500, detail=f"Failed to stop recording: {str(e)}")


def record_with_opencv(stream_url: str, output_path: str):
    """
    Record video using OpenCV as fallback when FFmpeg is not available.
    """
    global capturing_frames
    capturing_frames = True
    
    # Open the video stream
    cap = cv2.VideoCapture(stream_url)
    
    # Get the frames per second and frame dimensions
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    if fps <= 0:  # Sometimes FPS is not available from MJPEG stream
        fps = 15  # Default to 15 FPS
    
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    start_time = time.time()
    max_duration = 300  # Maximum recording time: 5 minutes
    
    while capturing_frames and (time.time() - start_time) < max_duration:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame from stream")
            break
        
        # Write the frame
        out.write(frame)
    
    # Release everything
    cap.release()
    out.release()
    capturing_frames = False
    print(f"Recording finished: {output_path}")


def stop_opencv_recording():
    """
    Stop recording that was started with OpenCV.
    """
    global capturing_frames
    capturing_frames = False