import gradio as gr
import uvicorn
from fastapi import FastAPI
from main import app

# Create Gradio interface
def create_gradio_interface():
    with gr.Blocks(title="ArchaeoScan Backend API") as demo:
        gr.Markdown("# 🏺 ArchaeoScan Backend API")
        
        with gr.Tab("📊 API Status"):
            gr.Markdown("### Backend API Status")
            status_btn = gr.Button("Check Status")
            status_output = gr.JSON(label="Status Response")
            
            def check_status():
                import requests
                try:
                    response = requests.get("http://localhost:7860/api/status", timeout=5)
                    return response.json()
                except:
                    return {"error": "Backend not ready"}
            
            status_btn.click(check_status, outputs=status_output)
        
        with gr.Tab("🤖 AI Analysis"):
            gr.Markdown("### AI Water & Material Analysis")
            analyze_btn = gr.Button("Run AI Analysis")
            analyze_output = gr.JSON(label="Analysis Results")
            
            def run_analysis():
                import requests
                try:
                    response = requests.get("http://localhost:7860/api/ai/analyze", timeout=5)
                    return response.json()
                except:
                    return {"error": "Analysis not ready"}
            
            analyze_btn.click(run_analysis, outputs=analyze_output)
        
        with gr.Tab("🗄️ Artifacts"):
            gr.Markdown("### Artifacts Database")
            artifacts_btn = gr.Button("Get Artifacts")
            artifacts_output = gr.JSON(label="Artifacts Data")
            
            def get_artifacts():
                import requests
                try:
                    response = requests.get("http://localhost:7860/api/artifacts", timeout=5)
                    return response.json()
                except:
                    return {"error": "Artifacts not ready"}
            
            artifacts_btn.click(get_artifacts, outputs=artifacts_output)
    
    return demo

# Mount FastAPI app
app = FastAPI()

# Include all routers from main.py
from main import app as main_app
app.mount("/api", main_app)

# Create Gradio demo
demo = create_gradio_interface()

# Mount Gradio app
app = gr.mount_gradio_app(app, demo, path="/")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
