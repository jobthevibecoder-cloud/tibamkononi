from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.models.patient import Patient

router = APIRouter()


@router.get("/{hospital_slug}/patients")
async def list_patients(
    hospital_slug: str,
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List patients for a hospital."""
    from app.models.hospital import Hospital
    hospital = db.query(Hospital).filter(Hospital.slug == hospital_slug).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    
    query = db.query(Patient).filter(Patient.hospital_id == hospital.id)
    if status:
        query = query.filter(Patient.status == status)
    
    patients = query.order_by(Patient.created_at.desc()).all()
    
    return {
        "patients": [
            {
                "id": p.id,
                "full_name": p.full_name,
                "age": p.age,
                "gender": p.gender,
                "phone": p.phone,
                "nhif_number": p.nhif_number,
                "address": p.address,
                "visit_type": p.visit_type,
                "status": p.status,
                "blood_pressure": p.blood_pressure,
                "pulse": p.pulse,
                "temperature": p.temperature,
                "spo2": p.spo2,
                "created_at": str(p.created_at),
            }
            for p in patients
        ],
        "total": len(patients)
    }
