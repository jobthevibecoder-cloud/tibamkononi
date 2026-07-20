from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from app.core.database import get_db
from app.services.hospital_service import (
    register_hospital, get_hospitals_by_county, get_hospital_by_slug,
    approve_hospital, reject_hospital
)

router = APIRouter()


class HospitalRegisterRequest(BaseModel):
    name: str
    license_number: str
    type: str
    county_id: Optional[str] = None
    sub_county_id: Optional[str] = None
    physical_address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    director_name: Optional[str] = None
    director_email: Optional[str] = None
    director_phone: Optional[str] = None
    buildings: list = []
    amenities: list = []


@router.get("/")
async def list_hospitals(
    county_id: Optional[str] = Query(None),
    status: Optional[str] = Query("APPROVED"),
    db: Session = Depends(get_db)
):
    """List hospitals with optional filters."""
    return {"hospitals": [], "total": 0, "message": "Connect database for real data"}


@router.post("/register")
async def register_new_hospital(request: HospitalRegisterRequest, db: Session = Depends(get_db)):
    """Register a new hospital."""
    try:
        hospital = register_hospital(db, request.model_dump())
        return {
            "message": "Hospital registered successfully. Pending approval.",
            "hospital_id": hospital.id,
            "slug": hospital.slug,
            "status": hospital.status,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{slug}")
async def get_hospital(slug: str, db: Session = Depends(get_db)):
    """Get hospital by slug."""
    hospital = get_hospital_by_slug(db, slug)
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return {"hospital": {"id": hospital.id, "name": hospital.name, "slug": hospital.slug}}


@router.post("/{hospital_id}/approve")
async def approve(hospital_id: str, approved_by: str = "admin", db: Session = Depends(get_db)):
    """Approve a hospital."""
    hospital = approve_hospital(db, hospital_id, approved_by)
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return {"message": "Hospital approved", "status": hospital.status}


@router.post("/{hospital_id}/reject")
async def reject(hospital_id: str, reason: str = "", db: Session = Depends(get_db)):
    """Reject a hospital."""
    hospital = reject_hospital(db, hospital_id, reason)
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return {"message": "Hospital rejected", "status": hospital.status}
