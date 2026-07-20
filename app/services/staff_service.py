"""Staff attendance business logic."""
from sqlalchemy.orm import Session
from app.models.staff import Staff, Attendance
from app.models.hospital import Hospital
from app.ai.services import detect_attendance_anomaly
from datetime import date, timedelta
from loguru import logger


def clock_in(db: Session, hospital_slug: str, staff_id: str) -> dict:
    """Clock in a staff member."""
    today = date.today().isoformat()
    
    existing = db.query(Attendance).filter(
        Attendance.staff_id == staff_id,
        Attendance.date == today
    ).first()
    
    if existing:
        return {"message": "Already clocked in today", "time": existing.clock_in}
    
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    
    attendance = Attendance(
        staff_id=staff_id,
        hospital_id=staff.hospital_id,
        date=today,
        clock_in=date.today().strftime("%H:%M"),
        status="PRESENT",
    )
    db.add(attendance)
    db.flush()
    
    return {"message": f"Clocked in: {staff.full_name}", "date": today, "time": attendance.clock_in}


def clock_out(db: Session, staff_id: str) -> dict:
    """Clock out a staff member."""
    today = date.today().isoformat()
    
    attendance = db.query(Attendance).filter(
        Attendance.staff_id == staff_id,
        Attendance.date == today
    ).first()
    
    if not attendance:
        return {"message": "Not clocked in today"}
    
    attendance.clock_out = date.today().strftime("%H:%M")
    db.flush()
    
    return {"message": "Clocked out successfully", "time": attendance.clock_out}


def get_staff_attendance(db: Session, hospital_slug: str, days: int = 30) -> list:
    """Get attendance records for all staff."""
    hospital = db.query(Hospital).filter(Hospital.slug == hospital_slug).first()
    if not hospital:
        return []
    
    staff_members = db.query(Staff).filter(
        Staff.hospital_id == hospital.id,
        Staff.is_active == True
    ).all()
    
    results = []
    for s in staff_members:
        records = db.query(Attendance).filter(
            Attendance.staff_id == s.id,
            Attendance.date >= (date.today() - timedelta(days=days)).isoformat()
        ).order_by(Attendance.date.desc()).all()
        
        present = sum(1 for r in records if r.status == "PRESENT")
        absent = sum(1 for r in records if r.status == "ABSENT")
        
        # Detect anomalies
        anomaly_result = None
        if absent > len(records) * 0.3:  # More than 30% absence
            anomaly_result = detect_attendance_anomaly(
                staff_name=s.full_name,
                role=s.role,
                attendance_data=str([{"date": r.date, "status": r.status} for r in records]),
            )
        
        results.append({
            "staff_id": s.id,
            "name": s.full_name,
            "role": s.role,
            "specialization": s.specialization,
            "total_days": len(records),
            "present": present,
            "absent": absent,
            "attendance_rate": round(present / len(records) * 100) if records else 0,
            "anomaly": anomaly_result.get("pattern_description") if anomaly_result else None,
            "recent": [{"date": r.date, "clock_in": r.clock_in, "clock_out": r.clock_out, "status": r.status} for r in records[:7]],
        })
    
    return results
