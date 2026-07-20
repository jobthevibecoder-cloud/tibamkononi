from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.ai.services import analyze_symptoms, rank_hospitals

router = APIRouter()


class TriageRequest(BaseModel):
    symptoms_text: str
    language: str = "sw"
    age: int = 30
    gender: str = "Female"
    latitude: Optional[float] = None
    longitude: Optional[float] = None


@router.post("/analyze")
async def analyze_symptoms_endpoint(request: TriageRequest, db: Session = Depends(get_db)):
    """Analyze symptoms and recommend hospitals."""
    try:
        # Get AI diagnosis
        ai_result = analyze_symptoms(
            symptoms_text=request.symptoms_text,
            language=request.language,
            age=request.age,
            gender=request.gender,
        )
        
        # Get hospital recommendations if location provided
        hospitals = []
        if request.latitude and request.longitude:
            hospitals_result = rank_hospitals(
                patient_lat=request.latitude,
                patient_lng=request.longitude,
                required_tests=ai_result.get("tests", []),
                required_medicines=[t.get("medicine") for t in ai_result.get("treatment", [])],
                hospitals_json="[]",  # Would be populated from DB
                language=request.language,
            )
            hospitals = hospitals_result.get("ranked_hospitals", [])
        
        return {
            "diagnosis": ai_result.get("diagnosis", []),
            "triage_level": ai_result.get("triage_level", "ROUTINE"),
            "recommended_tests": ai_result.get("tests", []),
            "recommended_treatment": ai_result.get("treatment", []),
            "self_care_advice": ai_result.get("self_care_advice", []),
            "nearby_hospitals": hospitals,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
