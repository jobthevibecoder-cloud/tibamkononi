"""Emergency handling business logic."""
from typing import Optional
from sqlalchemy.orm import Session
from app.models.emergency import Emergency
from app.models.hospital import Hospital
from app.ai.services import analyze_emergency_text, analyze_emergency_photo
from app.utils.geo import haversine_distance, estimate_travel_time
from loguru import logger


def process_emergency(db: Session, input_type: str, lat: float, lng: float,
                      text: Optional[str] = None, photo_description: Optional[str] = None,
                      language: str = "sw") -> Emergency:
    """Process an emergency report."""
    
    # Get AI analysis
    if input_type == "photo" and photo_description:
        ai_result = analyze_emergency_photo(photo_description, language, lat, lng)
    else:
        ai_result = analyze_emergency_text(text or "", language, lat, lng)
    
    # Find nearest hospitals
    hospitals = db.query(Hospital).filter(
        Hospital.status == "APPROVED",
        Hospital.latitude.isnot(None)
    ).all()
    
    nearest_hospitals = []
    for h in hospitals:
        if h.latitude and h.longitude:
            dist = haversine_distance(lat, lng, h.latitude, h.longitude)
            nearest_hospitals.append({
                "id": h.id,
                "name": h.name,
                "slug": h.slug,
                "distance_km": round(dist, 1),
                "eta_minutes": estimate_travel_time(dist, "ambulance"),
                "phone": h.phone,
            })
    
    nearest_hospitals.sort(key=lambda x: x["distance_km"])
    
    # Create emergency record
    emergency = Emergency(
        input_type=input_type,
        text_description=text,
        photo_url=None,
        voice_transcript=text if input_type == "voice" else None,
        input_language=language,
        emergency_type=ai_result.get("emergency_type"),
        severity=ai_result.get("severity"),
        casualties_estimated=ai_result.get("casualties_estimated"),
        hazards_detected=ai_result.get("hazards_detected"),
        latitude=lat,
        longitude=lng,
        auto_message=ai_result.get("auto_message"),
        status="ANALYZED",
    )
    db.add(emergency)
    db.flush()
    
    # Attach nearest hospitals info
    emergency_data = {
        "id": emergency.id,
        "type": emergency.emergency_type,
        "severity": emergency.severity,
        "message": emergency.auto_message,
        "nearest_hospitals": nearest_hospitals[:5],
    }
    
    logger.info(f"Emergency processed: {emergency.emergency_type} at ({lat}, {lng})")
    return emergency, emergency_data
