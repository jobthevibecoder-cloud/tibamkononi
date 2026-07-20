from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.services.emergency_service import process_emergency

router = APIRouter()


class EmergencyRequest(BaseModel):
    input_type: str  # "text", "voice", "photo"
    latitude: float
    longitude: float
    text: Optional[str] = None
    photo_description: Optional[str] = None
    language: str = "sw"


class EmergencyDispatchRequest(BaseModel):
    emergency_id: str
    hospital_id: str


@router.post("/analyze")
async def analyze_emergency(request: EmergencyRequest, db: Session = Depends(get_db)):
    """Analyze emergency and return nearest hospitals."""
    try:
        emergency, data = process_emergency(
            db=db,
            input_type=request.input_type,
            lat=request.latitude,
            lng=request.longitude,
            text=request.text,
            photo_description=request.photo_description,
            language=request.language,
        )
        return {
            "emergency": data,
            "message": "Emergency analyzed. Select hospital to dispatch."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dispatch")
async def dispatch_emergency(request: EmergencyDispatchRequest, db: Session = Depends(get_db)):
    """Dispatch emergency to a specific hospital."""
    return {
        "message": "Emergency dispatched",
        "emergency_id": request.emergency_id,
        "hospital_id": request.hospital_id,
        "status": "DISPATCHED"
    }
