"""
Test script to verify the ArchaeoScan backend functionality
"""
import asyncio
import json
from datetime import datetime
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.websocket import manager, simulate_sensor_stream
from app.services.material_classification import classify_material
from app.services.radar_processing import process_radar_data
from app.services.preservation_index import calculate_preservation_index


def test_material_classification():
    """Test the material classification service"""
    print("Testing material classification...")
    
    # Sample spectrometer data (simulated)
    wavelengths = list(range(400, 1001, 10))  # From 400nm to 1000nm in 10nm increments
    # Simulate a metallic signature (peaks at certain wavelengths)
    intensities = []
    for wl in wavelengths:
        intensity = 0.1  # Base noise
        if 650 <= wl <= 670:  # Simulate copper peak
            intensity += 0.8
        elif 290 <= wl <= 310:  # Simulate iron peak
            intensity += 0.6
        else:
            # Add some random variation
            import random
            intensity += random.uniform(0, 0.1)
        intensities.append(min(1.0, intensity))  # Cap at 1.0
    
    result = classify_material(wavelengths, intensities, {'temperature': 22.5, 'humidity': 45})
    print(f"  Result: {result}")
    print(f"  Material: {result['material_type']}, Confidence: {result['confidence']:.2f}")
    print("Material classification test completed.\n")


def test_radar_processing():
    """Test the radar processing service"""
    print("Testing radar processing...")
    
    # Simulate depth profile data (simple pattern)
    depth_profile = [0.1, 0.2, 0.15, 0.3, 0.8, 0.9, 0.85, 0.3, 0.2, 0.15, 0.1]
    
    result = process_radar_data(depth_profile, coordinates=(55.7558, 37.6176))
    print(f"  Result: {result}")
    print(f"  Anomalies detected: {result['total_detected']}")
    print("Radar processing test completed.\n")


def test_preservation_index():
    """Test the preservation index calculation"""
    print("Testing preservation index calculation...")
    
    # Test with reasonable environmental values
    preservation_pct, factors = calculate_preservation_index(
        temperature=15.0,  # Celsius
        tds=400.0,         # ppm
        turbidity=20.0,    # NTU
        depth=2.0,         # meters
        ph=7.2
    )
    
    print(f"  Preservation Index: {preservation_pct:.2f}%")
    print(f"  Factors: {factors}")
    print("Preservation index test completed.\n")


async def test_websocket_simulation():
    """Test the WebSocket simulation"""
    print("Testing WebSocket simulation...")
    
    # Start the simulation
    manager.is_broadcasting = True
    simulation_task = asyncio.create_task(simulate_sensor_stream())
    
    # Let it run for a few seconds
    await asyncio.sleep(2)
    
    # Stop the simulation
    manager.is_broadcasting = False
    if simulation_task:
        simulation_task.cancel()
        try:
            await simulation_task
        except asyncio.CancelledError:
            pass
    
    print("WebSocket simulation test completed.\n")


async def main():
    """Run all tests"""
    print("Starting ArchaeoScan Backend Tests...\n")
    
    test_material_classification()
    test_radar_processing()
    test_preservation_index()
    await test_websocket_simulation()
    
    print("All tests completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())