"""County Director dashboard business logic."""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.hospital import Hospital
from app.models.county import County
from app.models.inventory import Medicine
from app.models.staff import Staff, Attendance
from app.models.patient import Patient
from app.ai.services import generate_daily_summary
from loguru import logger


def get_county_overview(db: Session, county_code: str = "MSA") -> dict:
    """Get county-wide health statistics."""
    county = db.query(County).filter(County.code == county_code).first()
    if not county:
        return {}
    
    hospitals = db.query(Hospital).filter(
        Hospital.county_id == county.id,
        Hospital.status == "APPROVED"
    ).all()
    
    total_beds = 0
    occupied_beds = 0
    critical_alerts = 0
    stock_warnings = 0
    
    for h in hospitals:
        # Count beds
        from app.models.hospital import HospitalWard
        wards = db.query(HospitalWard).filter(HospitalWard.hospital_id == h.id).all()
        for w in wards:
            total_beds += w.total_beds
            occupied_beds += w.occupied_beds
        
        # Count stock alerts
        medicines = db.query(Medicine).filter(Medicine.hospital_id == h.id).all()
        for m in medicines:
            if m.current_stock <= (m.critical_threshold or 0):
                critical_alerts += 1
            elif m.current_stock <= (m.minimum_threshold or 0):
                stock_warnings += 1
    
    return {
        "county_name": county.name,
        "total_hospitals": len(hospitals),
        "total_beds": total_beds,
        "beds_available": total_beds - occupied_beds,
        "occupancy_rate": round((occupied_beds / total_beds * 100), 1) if total_beds > 0 else 0,
        "critical_alerts": critical_alerts,
        "stock_warnings": stock_warnings,
    }


def get_hospital_list_atoz(db: Session, county_code: str = "MSA") -> List[dict]:
    """Get A-Z list of hospitals with status indicators."""
    county = db.query(County).filter(County.code == county_code).first()
    if not county:
        return []
    
    hospitals = db.query(Hospital).filter(
        Hospital.county_id == county.id,
        Hospital.status == "APPROVED"
    ).order_by(Hospital.name).all()
    
    results = []
    for h in hospitals:
        # Determine status color
        alerts = db.query(Medicine).filter(
            Medicine.hospital_id == h.id,
            Medicine.current_stock <= Medicine.critical_threshold
        ).count()
        
        warnings = db.query(Medicine).filter(
            Medicine.hospital_id == h.id,
            Medicine.current_stock <= Medicine.minimum_threshold,
            Medicine.current_stock > Medicine.critical_threshold
        ).count()
        
        if alerts > 0:
            status_color = "red"
            status_text = f"{alerts} critical"
        elif warnings > 2:
            status_color = "yellow"
            status_text = f"{warnings} warnings"
        else:
            status_color = "green"
            status_text = "Normal"
        
        results.append({
            "id": h.id,
            "name": h.name,
            "slug": h.slug,
            "type": h.type,
            "location": h.physical_address or "N/A",
            "status_color": status_color,
            "status_text": status_text,
            "performance_score": h.performance_score,
            "alerts": alerts,
            "warnings": warnings,
        })
    
    return results


def get_hospital_deep_dive(db: Session, hospital_slug: str) -> dict:
    """Get detailed hospital information for county director."""
    hospital = db.query(Hospital).filter(Hospital.slug == hospital_slug).first()
    if not hospital:
        return {}
    
    # Medicines grouped by category
    medicines = db.query(Medicine).filter(Medicine.hospital_id == hospital.id).all()
    medicine_list = []
    for m in medicines:
        if m.current_stock <= (m.critical_threshold or 0):
            stock_status = "critical"
        elif m.current_stock <= (m.minimum_threshold or 0):
            stock_status = "warning"
        else:
            stock_status = "ok"
        
        days_left = int(m.current_stock / m.daily_usage_rate) if m.daily_usage_rate > 0 else 999
        
        medicine_list.append({
            "id": m.id,
            "name": m.name,
            "current_stock": m.current_stock,
            "unit": m.unit,
            "minimum_threshold": m.minimum_threshold,
            "daily_usage_rate": m.daily_usage_rate,
            "days_left": days_left,
            "status": stock_status,
            "last_restock": m.last_restock_date,
        })
    
    # Staff overview
    staff = db.query(Staff).filter(Staff.hospital_id == hospital.id, Staff.is_active == True).all()
    staff_list = []
    for s in staff:
        # Get recent attendance
        from datetime import date, timedelta
        today = date.today().isoformat()
        recent_attendance = db.query(Attendance).filter(
            Attendance.staff_id == s.id,
            Attendance.date >= (date.today() - timedelta(days=7)).isoformat()
        ).all()
        
        present_days = sum(1 for a in recent_attendance if a.status == "PRESENT")
        total_days = len(recent_attendance) or 1
        
        staff_list.append({
            "id": s.id,
            "name": s.full_name,
            "role": s.role,
            "specialization": s.specialization,
            "attendance_rate": round(present_days / total_days * 100),
            "recent_attendance": [{"date": a.date, "status": a.status} for a in recent_attendance],
        })
    
    # Generate AI summary
    total_patients = db.query(Patient).filter(Patient.hospital_id == hospital.id).count()
    
    ai_summary = generate_daily_summary(
        hospital_name=hospital.name,
        date=date.today().isoformat(),
        total_patients=total_patients,
        admissions=0,
        discharges=0,
        alerts=str(len([m for m in medicine_list if m["status"] == "critical"])),
        bed_percent=50.0,
        staff_count=len([s for s in staff_list if s["attendance_rate"] > 80]),
        total_staff=len(staff_list),
        language="en",
    )
    
    return {
        "hospital": {
            "id": hospital.id,
            "name": hospital.name,
            "slug": hospital.slug,
            "type": hospital.type,
            "location": hospital.physical_address,
            "phone": hospital.phone,
            "director": hospital.director_name,
            "performance_score": hospital.performance_score,
        },
        "medicines": medicine_list,
        "staff": staff_list,
        "ai_summary": ai_summary.get("summary", "No summary available"),
        "ai_recommendations": ai_summary.get("recommendations", []),
    }


def generate_weekly_watchlist(db: Session, county_code: str = "MSA") -> dict:
    """Generate AI-powered weekly watchlist of hospitals needing attention."""
    county = db.query(County).filter(County.code == county_code).first()
    if not county:
        return {}
    
    hospitals = db.query(Hospital).filter(
        Hospital.county_id == county.id,
        Hospital.status == "APPROVED"
    ).all()
    
    watchlist = []
    for h in hospitals:
        # Calculate scores
        medicines = db.query(Medicine).filter(Medicine.hospital_id == h.id).all()
        critical_count = sum(1 for m in medicines if m.current_stock <= (m.critical_threshold or 0))
        warning_count = sum(1 for m in medicines if m.current_stock <= (m.minimum_threshold or 0) and m.current_stock > (m.critical_threshold or 0))
        
        staff = db.query(Staff).filter(Staff.hospital_id == h.id, Staff.is_active == True).all()
        
        # Simple scoring
        score = 100
        score -= critical_count * 15
        score -= warning_count * 5
        if len(staff) < 5:
            score -= 10
        
        severity = "critical" if score < 30 else ("warning" if score < 60 else "normal")
        
        watchlist.append({
            "hospital_name": h.name,
            "slug": h.slug,
            "score": max(0, score),
            "severity": severity,
            "critical_alerts": critical_count,
            "warnings": warning_count,
            "staff_count": len(staff),
        })
    
    watchlist.sort(key=lambda x: x["score"])
    
    return {
        "county": county.name,
        "generated_date": "2026-07-31",
        "hospitals": watchlist,
        "requires_attention": [w for w in watchlist if w["severity"] in ["critical", "warning"]],
    }
