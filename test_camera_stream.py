#!/usr/bin/env python3
"""
Test script to verify camera stream connectivity
"""

import requests
import time

def test_direct_connection():
    """Test direct connection to ESP32-CAM"""
    esp32_ip = "172.20.10.9"
    url = f"http://{esp32_ip}:81/stream"
    
    print(f"Testing direct connection to {url}")
    
    try:
        response = requests.get(url, timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {response.headers}")
        print("Direct connection successful!")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Direct connection failed: {e}")
        return False

def test_backend_proxy():
    """Test backend proxy connection"""
    backend_url = "http://localhost:8000"
    proxy_url = f"{backend_url}/api/camera/stream"
    
    print(f"Testing backend proxy connection to {proxy_url}")
    
    try:
        response = requests.get(proxy_url, timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {response.headers}")
        print("Backend proxy connection successful!")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Backend proxy connection failed: {e}")
        return False

def test_frontend_accessibility():
    """Test if frontend can access backend"""
    frontend_port = 5173  # Default Vite port
    backend_port = 8000
    
    print("Testing frontend-backend communication...")
    
    try:
        # Test if backend is running
        backend_response = requests.get(f"http://localhost:{backend_port}/", timeout=2)
        print(f"Backend status: {backend_response.status_code}")
        
        # Test CORS if frontend tries to access backend
        frontend_response = requests.options(
            f"http://localhost:{backend_port}/api/camera/stream",
            headers={"Origin": f"http://localhost:{frontend_port}"}
        )
        print(f"CORS test status: {frontend_response.status_code}")
        
        return True
    except requests.exceptions.RequestException as e:
        print(f"Frontend-backend communication test failed: {e}")
        return False

if __name__ == "__main__":
    print("=== Camera Stream Connectivity Test ===\n")
    
    results = {
        "direct_connection": test_direct_connection(),
        "backend_proxy": test_backend_proxy(),
        "frontend_accessibility": test_frontend_accessibility()
    }
    
    print("\n=== Test Results ===")
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name}: {status}")
    
    if all(results.values()):
        print("\n🎉 All tests passed! Camera stream should work correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the specific issues above.")