"""Distress signal business logic."""
from typing import Optional
from sqlalchemy.orm import Session
from app.models.distress_signal import DistressSignal
from app.models.hospital import Hospital
from app.models.inventory import Medicine
from app.ai.services import recommend_redistribution
from app.utils.geo import haversine_distance
from loguru import logger


def create_distress_signal(db: Session, from_hospital_slug: str, data: dict) -> dict:
    """Create a distress signal and get AI redistribution recommendation."""
    hospital = db.query(Hospital).filter(Hospital.slug == from_hospital_slug).first()
    if not hospital:
        raise ValueError("Hospital not found")
    
    # Find nearby hospitals with this medicine
    medicine_name = data.get("medicine_name", "")
    nearby_hospitals = []
    
    other_hospitals = db.query(Hospital).filter(
        Hospital.id != hospital.id,
        Hospital.status == "APPROVED"
    ).all()
    
    for h in other_hospitals:
        if h.latitude and h.longitude and hospital.latitude and hospital.longitude:
            dist = haversine_distance(hospital.latitude, hospital.longitude, h.latitude, h.longitude)
            nearby_hospitals.append({"id": h.id, "name": h.name, "slug": h.slug, "distance_km": round(dist, 1)})
    
    nearby_hospitals.sort(key=lambda x: x["distance_km"])
    
    # Get AI recommendation
    ai_result = recommend_redistribution(
        hospital_name=hospital.name,
        resource=medicine_name,
        current=data.get("current_stock", 0),
        daily_rate=data.get("daily_usage", 0),
        hours=data.get("hours_until_stockout", 24),
        nearby_json=str(nearby_hospitals[:5]),
    )
    
    signal = DistressSignal(
        from_hospital_id=hospital.id,
        resource_type=data.get("resource_type", "MEDICINE"),
        urgency=data.get("urgency", "CRITICAL"),
        medicine_name=medicine_name,
        quantity_needed=data.get("quantity_needed"),
        current_stock=data.get("current_stock"),
        hours_until_stockout=data.get("hours_until_stockout"),
        reason=data.get("reason"),
        ai_message=ai_result.get("ai_message"),
        ai_suggested_source=ai_result.get("suggested_source"),
        sent_to_county=True,
        status="OPEN",
    )
    db.add(signal)
    db.flush()
    
    logger.info(f"Distress signal created: {hospital.name} needs {medicine_name}")
    
    return {
        "signal_id": signal.id,
        "hospital": hospital.name,
        "medicine": medicine_name,
        "urgency": signal.urgency,
        "ai_recommendation": ai_result.get("ai_message"),
        "suggested_source": ai_result.get("suggested_source"),
        "nearby_hospitals": nearby_hospitals[:5],
        "status": "OPEN",
    }


def get_hospital_distress_signals(db: Session, hospital_slug: str) -> list:
    """Get all distress signals for a hospital."""
    hospital = db.query(Hospital).filter(Hospital.slug == hospital_slug).first()
    if not hospital:
        return []
    
    signals = db.query(DistressSignal).filter(
        DistressSignal.from_hospital_id == hospital.id
    ).order_by(DistressSignal.created_at.desc()).all()
    
    return [
        {
            "id": s.id,
            "resource_type": s.resource_type,
            "urgency": s.urgency,
            "medicine_name": s.medicine_name,
            "quantity_needed": s.quantity_needed,
            "ai_message": s.ai_message,
            "status": s.status,
            "created_at": str(s.created_at),
        }
        for s in signals
    ]
