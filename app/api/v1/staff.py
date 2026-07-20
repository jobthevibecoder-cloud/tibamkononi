from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.services.staff_service import clock_in, clock_out, get_staff_attendance

router = APIRouter()


@router.post("/{hospital_slug}/staff/{staff_id}/clock-in")
async def staff_clock_in(hospital_slug: str, staff_id: str, db: Session = Depends(get_db)):
    """Clock in a staff member."""
    try:
        result = clock_in(db, hospital_slug, staff_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{hospital_slug}/staff/{staff_id}/clock-out")
async def staff_clock_out(hospital_slug: str, staff_id: str, db: Session = Depends(get_db)):
    """Clock out a staff member."""
    try:
        result = clock_out(db, staff_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{hospital_slug}/attendance")
async def view_attendance(hospital_slug: str, days: int = Query(30), db: Session = Depends(get_db)):
    """View staff attendance records."""
    try:
        records = get_staff_attendance(db, hospital_slug, days)
        return {"staff": records, "total": len(records)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
