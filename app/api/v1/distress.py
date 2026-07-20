from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.services.distress_service import create_distress_signal, get_hospital_distress_signals

router = APIRouter()

class DistressRequest(BaseModel):
    resource_type: str = "MEDICINE"
    urgency: str = "CRITICAL"
    medicine_name: Optional[str] = None
    quantity_needed: Optional[float] = None
    current_stock: Optional[float] = None
    daily_usage: Optional[float] = None
    hours_until_stockout: Optional[float] = None
    reason: Optional[str] = None

@router.post("/{hospital_slug}/distress")
async def send_distress(hospital_slug: str, request: DistressRequest, db: Session = Depends(get_db)):
    try:
        result = create_distress_signal(db, hospital_slug, request.model_dump())
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{hospital_slug}/distress")
async def view_distress(hospital_slug: str, db: Session = Depends(get_db)):
    try:
        signals = get_hospital_distress_signals(db, hospital_slug)
        return {"signals": signals, "total": len(signals)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
