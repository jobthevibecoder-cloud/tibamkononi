from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.schemas.appointment import AppointmentBookRequest
from app.services.appointment_service import (
    get_available_slots, book_appointment, get_hospital_appointments, cancel_appointment
)

router = APIRouter()


@router.get("/available")
async def available_slots(
    hospital_slug: str = Query("mama-ngina-hospital"),
    date: str = Query("2026-08-01"),
    department: str = Query("GENERAL_OPD"),
    db: Session = Depends(get_db)
):
    """Get available appointment slots for a hospital."""
    try:
        slots = get_available_slots(db, hospital_slug, date, department)
        hospital_name = hospital_slug.replace("-", " ").title()
        available_count = sum(1 for s in slots if s.get("available", False))
        return {
            "hospital_name": hospital_name,
            "date": date,
            "department": department,
            "slots": slots,
            "total_slots": len(slots),
            "total_available": available_count,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/book")
async def book(request: AppointmentBookRequest, db: Session = Depends(get_db)):
    """Book an appointment. If no doctor_id provided, assigns first available."""
    try:
        data = request.model_dump()
        
        # If no doctor specified, find first available
        if not data.get("doctor_id"):
            slots = get_available_slots(db, data["hospital_slug"], data["appointment_date"], data["department"])
            available = [s for s in slots if s.get("available") and s["time"] == data["appointment_time"]]
            if not available:
                raise HTTPException(status_code=400, detail="No available doctors at this time")
            data["doctor_id"] = available[0]["doctor_id"]
        
        result = book_appointment(db, data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hospital/{hospital_slug}")
async def hospital_appointments(
    hospital_slug: str,
    date: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all appointments for a hospital."""
    try:
        appointments = get_hospital_appointments(db, hospital_slug, date)
        return {"appointments": appointments, "total": len(appointments)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{appointment_id}/cancel")
async def cancel(appointment_id: str, db: Session = Depends(get_db)):
    """Cancel an appointment."""
    try:
        result = cancel_appointment(db, appointment_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
