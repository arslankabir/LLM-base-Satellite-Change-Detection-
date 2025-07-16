from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import os
from change_detector import detect_changes
from gpt_summary import generate_summary

app = FastAPI(
    title="SatelliteLLM API",
    description="Satellite imagery change detection and natural language summarization",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="."), name="static")
# Mount results directory for direct browser access
app.mount("/img", StaticFiles(directory="img"), name="img")

class SummaryResponse(BaseModel):
    summary: str
    confidence: float
    map_overlay_url: Optional[str] = None
    pixel_change_percentage: Optional[float] = None
    conflict_damage_detected: Optional[bool] = None

@app.get("/frontend")
async def get_frontend():
    """Serve the frontend HTML file"""
    return FileResponse("frontend.html")

from fastapi import Query

@app.post("/generate-summary", response_model=SummaryResponse)
async def generate_change_summary(
    before_image: UploadFile = File(...),
    after_image: UploadFile = File(...),
    pixel_threshold_factor: float = Query(1.0, description="Threshold factor for pixel-level change detection (default 1.0, lower is more sensitive)")
):
    """
    Generate a natural language summary of changes between two satellite images, and save a visual change map.
    """
    try:
        # Save uploaded files temporarily
        before_path = f"temp_{before_image.filename}"
        after_path = f"temp_{after_image.filename}"
        
        with open(before_path, "wb") as f:
            f.write(await before_image.read())
        with open(after_path, "wb") as f:
            f.write(await after_image.read())
        
        import time
        # Use safe file base names (remove directory and extension)
        def safe_base(filename):
            return os.path.splitext(os.path.basename(filename))[0].replace('.', '_').replace(' ', '_')
        before_base = safe_base(before_image.filename)
        after_base = safe_base(after_image.filename)
        timestamp = int(time.time())
        change_map_name = f"change_map_{before_base}_vs_{after_base}_{timestamp}.png"
        change_map_path = os.path.join("img", change_map_name)
        os.makedirs(os.path.dirname(change_map_path), exist_ok=True)
        
        # Detect changes and generate map
        change_data = detect_changes(before_path, after_path, change_map_path=change_map_path, threshold_factor=pixel_threshold_factor)
        
        # Generate summary using DeepSeek
        summary, confidence = generate_summary(change_data)
        
        # Clean up temporary files
        os.remove(before_path)
        os.remove(after_path)
        
        # Use web-accessible URL for the change map
        map_url = f"/img/{change_map_name}"
        # Flag major conflict damage if pixel change is high
        pixel_change = change_data.get('pixel_change_percentage')
        conflict_damage_detected = pixel_change is not None and pixel_change >= 10.0
        return SummaryResponse(
            summary=summary,
            confidence=confidence,
            map_overlay_url=map_url,
            pixel_change_percentage=pixel_change,
            conflict_damage_detected=conflict_damage_detected
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Welcome to SatelliteLLM API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 