from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.services.county_service import (
    get_county_overview, get_hospital_list_atoz, 
    get_hospital_deep_dive, generate_weekly_watchlist
)
from app.services.hospital_service import approve_hospital, reject_hospital

router = APIRouter()


@router.get("/dashboard")
async def county_dashboard(county_code: str = Query("MSA"), db: Session = Depends(get_db)):
    """Get county health overview statistics."""
    try:
        overview = get_county_overview(db, county_code)
        return overview
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hospitals")
async def hospital_list(county_code: str = Query("MSA"), db: Session = Depends(get_db)):
    """Get A-Z list of hospitals with status."""
    try:
        hospitals = get_hospital_list_atoz(db, county_code)
        return {"hospitals": hospitals, "total": len(hospitals)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hospitals/{hospital_slug}")
async def hospital_deep_dive(hospital_slug: str, db: Session = Depends(get_db)):
    """Get detailed view of a specific hospital."""
    try:
        details = get_hospital_deep_dive(db, hospital_slug)
        if not details:
            raise HTTPException(status_code=404, detail="Hospital not found")
        return details
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/watchlist")
async def weekly_watchlist(county_code: str = Query("MSA"), db: Session = Depends(get_db)):
    """Get AI-generated weekly watchlist."""
    try:
        watchlist = generate_weekly_watchlist(db, county_code)
        return watchlist
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/approvals")
async def pending_approvals(db: Session = Depends(get_db)):
    """Get pending hospital registrations."""
    try:
        from app.models.hospital import Hospital
        pending = db.query(Hospital).filter(Hospital.status == "PENDING").all()
        return {
            "pending": [
                {
                    "id": h.id,
                    "name": h.name,
                    "license_number": h.license_number,
                    "type": h.type,
                    "location": h.physical_address,
                    "director": h.director_name,
                    "submitted_at": str(h.created_at),
                }
                for h in pending
            ],
            "total": len(pending)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/approvals/{hospital_id}/approve")
async def approve(hospital_id: str, db: Session = Depends(get_db)):
    """Approve a hospital registration."""
    try:
        hospital = approve_hospital(db, hospital_id, "county_director")
        if not hospital:
            raise HTTPException(status_code=404, detail="Hospital not found")
        return {"message": "Hospital approved", "status": hospital.status}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/approvals/{hospital_id}/reject")
async def reject(hospital_id: str, reason: str = Query(""), db: Session = Depends(get_db)):
    """Reject a hospital registration."""
    try:
        hospital = reject_hospital(db, hospital_id, reason)
        if not hospital:
            raise HTTPException(status_code=404, detail="Hospital not found")
        return {"message": "Hospital rejected", "status": hospital.status}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
