import gradio as gr
import subprocess
import sys
import os
import requests
import json

def start_backend():
    """Start the FastAPI backend server"""
    try:
        print("Starting FastAPI backend...")
        os.chdir('backend')
        process = subprocess.Popen([sys.executable, 'main.py'])
        return process
    except Exception as e:
        return f"Error starting backend: {e}"

def get_backend_status():
    """Check if backend is running"""
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        return "✅ Backend is running" if response.status_code == 200 else "❌ Backend not responding"
    except:
        return "❌ Backend not running"

def create_interface():
    """Create Gradio interface for ArchaeoScan"""
    
    with gr.Blocks(title="ArchaeoScan - Archaeological Monitoring") as demo:
        gr.Markdown("# 🏺 ArchaeoScan")
        gr.Markdown("Real-time archaeological monitoring platform for underwater sensors")
        
        with gr.Tabs():
            with gr.TabItem("🎛️ Control Panel"):
                with gr.Row():
                    start_btn = gr.Button("🚀 Start Backend", variant="primary")
                    status_btn = gr.Button("📊 Check Status")
                
                with gr.Row():
                    status_output = gr.Textbox(label="Backend Status", interactive=False)
                
                with gr.Row():
                    gr.Markdown("### 📡 API Endpoints")
                    gr.Markdown("- **WebSocket**: `ws://localhost:8000/ws`")
                    gr.Markdown("- **API Docs**: `http://localhost:8000/docs`")
                    gr.Markdown("- **Health**: `http://localhost:8000/`")
            
            with gr.TabItem("📊 Live Dashboard"):
                gr.HTML("""
                <iframe src="http://localhost:5173" width="100%" height="800px" frameborder="0">
                    <p>Your browser does not support iframes.</p>
                </iframe>
                """)
            
            with gr.TabItem("📖 Documentation"):
                gr.Markdown("""
                ## 🏗️ Architecture
                
                ```
                Frontend (React) ←→ Backend (FastAPI) ←→ ESP32 Sensors
                ```
                
                ## 📡 Supported Sensors
                - TLV493D (magnetometer)
                - MPU-9250 (accelerometer/gyro)
                - AS7343 (spectrometer)
                - TS-300b (turbidity)
                - DS18B20 (water temperature)
                - TDS meter
                - HC-SR04T (ultrasonic)
                - ESP32-CAM
                
                ## 🚀 Local Development
                - **Frontend**: Run `npm run dev` in frontend directory
                - **Backend**: Run `python main.py` in backend directory
                - **Sensors**: ESP32 with custom firmware
                """)
        
        # Event handlers
        start_btn.click(
            fn=start_backend,
            outputs=status_output
        )
        
        status_btn.click(
            fn=get_backend_status,
            outputs=status_output
        )
    
    return demo

if __name__ == "__main__":
    demo = create_interface()
    demo.launch(server_name="0.0.0.0", server_port=7860)
