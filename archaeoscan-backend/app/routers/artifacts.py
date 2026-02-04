from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Tuple
from datetime import datetime
import random

router = APIRouter()

class Artifact(BaseModel):
    id: int
    location: Tuple[float, float]  # [lat, lng]
    material: str  # ceramic, metal, stone, organic, unknown
    confidence: float
    images: List[str]
    date: str
    depth: float
    description: str
    status: str  # pending, verified, analyzed

class ArtifactsResponse(BaseModel):
    artifacts: List[Artifact]

# Mock artifacts database (in production, use real database)
artifacts_db = [
    {
        "id": 1,
        "location": (43.2345, 51.3456),
        "material": "ceramic",
        "confidence": 0.85,
        "images": ["/images/artifact1_1.jpg", "/images/artifact1_2.jpg"],
        "date": "2026-02-04",
        "depth": 12.5,
        "description": "Ancient ceramic fragment with intricate patterns",
        "status": "verified"
    },
    {
        "id": 2,
        "location": (43.2356, 51.3467),
        "material": "metal",
        "confidence": 0.92,
        "images": ["/images/artifact2_1.jpg"],
        "date": "2026-02-04",
        "depth": 8.3,
        "description": "Metal object with corrosion patterns, possibly tool",
        "status": "analyzed"
    },
    {
        "id": 3,
        "location": (43.2334, 51.3445),
        "material": "stone",
        "confidence": 0.78,
        "images": [],
        "date": "2026-02-04",
        "depth": 15.7,
        "description": "Stone tool fragment with worked edges",
        "status": "pending"
    }
]

@router.get("/", response_model=ArtifactsResponse)
async def get_artifacts():
    """Get all artifacts"""
    return {"artifacts": artifacts_db}

@router.get("/{artifact_id}", response_model=Artifact)
async def get_artifact(artifact_id: int):
    """Get specific artifact by ID"""
    artifact = next((a for a in artifacts_db if a["id"] == artifact_id), None)
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return artifact

@router.post("/", response_model=Artifact)
async def create_artifact(artifact: Artifact):
    """Create new artifact"""
    # Generate new ID
    new_id = max([a["id"] for a in artifacts_db]) + 1 if artifacts_db else 1
    artifact.id = new_id
    artifacts_db.append(artifact.dict())
    return artifact

@router.get("/export/csv")
async def export_artifacts_csv():
    """Export artifacts as CSV"""
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(["ID", "Latitude", "Longitude", "Material", "Confidence", "Date", "Depth", "Description", "Status"])
    
    # Write data
    for artifact in artifacts_db:
        writer.writerow([
            artifact["id"],
            artifact["location"][0],
            artifact["location"][1],
            artifact["material"],
            artifact["confidence"],
            artifact["date"],
            artifact["depth"],
            artifact["description"],
            artifact["status"]
        ])
    
    # Return CSV content
    from fastapi.responses import Response
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=artifacts.csv"}
    )

@router.get("/export/json")
async def export_artifacts_json():
    """Export artifacts as JSON"""
    from fastapi.responses import JSONResponse
    return JSONResponse(
        content=artifacts_db,
        headers={"Content-Disposition": "attachment; filename=artifacts.json"}
    )
