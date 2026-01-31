import subprocess
import sys
import os

def start_backend():
    """Start the FastAPI backend server"""
    try:
        print("Starting FastAPI backend...")
        # Change to backend directory and start the server
        os.chdir('backend')
        subprocess.run([sys.executable, 'main.py'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error starting backend: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    start_backend()
