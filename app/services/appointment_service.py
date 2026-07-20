"""Appointment booking business logic."""
import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.appointment import Appointment
from app.models.hospital import Hospital
from app.models.staff import Staff
from loguru import logger


def generate_booking_reference() -> str:
    """Generate a unique booking reference."""
    return f"TMA-{uuid.uuid4().hex[:8].upper()}"


def get_available_slots(db: Session, hospital_slug: str, appointment_date: str, 
                        department: str) -> List[dict]:
    """Get available appointment slots for a hospital."""
    hospital = db.query(Hospital).filter(Hospital.slug == hospital_slug).first()
    if not hospital:
        return []
    
    # Get doctors in that department
    doctors = db.query(Staff).filter(
        Staff.hospital_id == hospital.id,
        Staff.role == "DOCTOR",
        Staff.is_active == True
    ).all()
    
    # Get existing bookings for that date
    existing = db.query(Appointment).filter(
        Appointment.hospital_id == hospital.id,
        Appointment.appointment_date == appointment_date,
        Appointment.status != "CANCELLED"
    ).all()
    
    booked_slots = [(a.doctor_id, a.appointment_time) for a in existing]
    
    # Generate time slots (8 AM to 4 PM, 30 min intervals)
    slots = []
    for doctor in doctors:
        for hour in range(8, 16):
            for minute in ["00", "30"]:
                time_str = f"{hour:02d}:{minute}"
                is_booked = (doctor.id, time_str) in booked_slots
                slots.append({
                    "time": time_str,
                    "doctor_id": doctor.id,
                    "doctor_name": doctor.full_name,
                    "available": not is_booked,
                    "specialization": doctor.specialization or "General Practitioner",
                })
    
    return slots


def book_appointment(db: Session, data: dict) -> dict:
    """Book an appointment."""
    hospital = db.query(Hospital).filter(Hospital.slug == data["hospital_slug"]).first()
    if not hospital:
        raise ValueError("Hospital not found")
    
    doctor = db.query(Staff).filter(Staff.id == data["doctor_id"]).first()
    if not doctor:
        raise ValueError("Doctor not found")
    
    # Check if slot is already booked
    existing = db.query(Appointment).filter(
        Appointment.hospital_id == hospital.id,
        Appointment.doctor_id == data["doctor_id"],
        Appointment.appointment_date == data["appointment_date"],
        Appointment.appointment_time == data["appointment_time"],
        Appointment.status != "CANCELLED"
    ).first()
    
    if existing:
        raise ValueError("This slot is already booked")
    
    booking_ref = generate_booking_reference()
    
    appointment = Appointment(
        hospital_id=hospital.id,
        doctor_id=data["doctor_id"],
        patient_name=data["patient_name"],
        patient_phone=data["patient_phone"],
        patient_nhif=data.get("patient_nhif"),
        department=data["department"],
        appointment_date=data["appointment_date"],
        appointment_time=data["appointment_time"],
        reason=data.get("reason"),
        pre_filled_from_triage=data.get("pre_filled_from_triage", False),
        status="CONFIRMED",
        reminder_sent=False,
    )
    db.add(appointment)
    db.flush()
    
    logger.info(f"Appointment booked: {booking_ref} - {data['patient_name']} with {doctor.full_name}")
    
    return {
        "id": appointment.id,
        "hospital_name": hospital.name,
        "department": data["department"],
        "doctor_name": doctor.full_name,
        "appointment_date": data["appointment_date"],
        "appointment_time": data["appointment_time"],
        "patient_name": data["patient_name"],
        "status": "CONFIRMED",
        "booking_reference": booking_ref,
    }


def get_hospital_appointments(db: Session, hospital_slug: str, appointment_date: Optional[str] = None) -> List[dict]:
    """Get all appointments for a hospital."""
    hospital = db.query(Hospital).filter(Hospital.slug == hospital_slug).first()
    if not hospital:
        return []
    
    query = db.query(Appointment).filter(Appointment.hospital_id == hospital.id)
    
    if appointment_date:
        query = query.filter(Appointment.appointment_date == appointment_date)
    
    appointments = query.order_by(Appointment.appointment_time).all()
    
    results = []
    for a in appointments:
        doctor = db.query(Staff).filter(Staff.id == a.doctor_id).first()
        results.append({
            "id": a.id,
            "patient_name": a.patient_name,
            "patient_phone": a.patient_phone,
            "department": a.department,
            "doctor_name": doctor.full_name if doctor else "Unknown",
            "appointment_date": a.appointment_date,
            "appointment_time": a.appointment_time,
            "status": a.status,
            "reason": a.reason,
        })
    
    return results


def cancel_appointment(db: Session, appointment_id: str) -> dict:
    """Cancel an appointment."""
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise ValueError("Appointment not found")
    
    appointment.status = "CANCELLED"
    db.flush()
    
    return {"message": "Appointment cancelled", "id": appointment_id, "status": "CANCELLED"}
