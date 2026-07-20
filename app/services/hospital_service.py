"""Hospital business logic."""
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.hospital import Hospital, Building, HospitalWard, Bed, Amenity
from app.models.county import County, SubCounty
from loguru import logger


def register_hospital(db: Session, data: dict) -> Hospital:
    """Register a new hospital."""
    slug = data["name"].lower().replace(" ", "-").replace("'", "")
    
    hospital = Hospital(
        slug=slug,
        name=data["name"],
        license_number=data["license_number"],
        type=data["type"],
        county_id=data.get("county_id"),
        sub_county_id=data.get("sub_county_id"),
        physical_address=data.get("physical_address"),
        latitude=data.get("latitude"),
        longitude=data.get("longitude"),
        phone=data.get("phone"),
        email=data.get("email"),
        director_name=data.get("director_name"),
        director_email=data.get("director_email"),
        director_phone=data.get("director_phone"),
        status="PENDING",
    )
    db.add(hospital)
    db.flush()
    
    for b_data in data.get("buildings", []):
        building = Building(
            hospital_id=hospital.id,
            name=b_data["name"],
            floors=b_data.get("floors", 1),
        )
        db.add(building)
        db.flush()
        
        for w_data in b_data.get("wards", []):
            ward = HospitalWard(
                building_id=building.id,
                hospital_id=hospital.id,
                name=w_data["name"],
                type=w_data["type"],
                total_beds=w_data.get("total_beds", 0),
            )
            db.add(ward)
    
    for a_name in data.get("amenities", []):
        amenity = Amenity(hospital_id=hospital.id, name=a_name)
        db.add(amenity)
    
    logger.info(f"Hospital registered: {hospital.name} (pending approval)")
    return hospital


def approve_hospital(db: Session, hospital_id: str, approved_by: str) -> Hospital:
    """Approve a hospital registration."""
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if hospital:
        hospital.status = "APPROVED"
        hospital.approved_by = approved_by
    return hospital


def reject_hospital(db: Session, hospital_id: str, reason: str) -> Hospital:
    """Reject a hospital registration."""
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if hospital:
        hospital.status = "REJECTED"
        hospital.rejection_reason = reason
    return hospital


def get_hospitals_by_county(db: Session, county_id: str) -> List[Hospital]:
    """Get all hospitals in a county."""
    return db.query(Hospital).filter(
        Hospital.county_id == county_id,
        Hospital.status == "APPROVED"
    ).all()


def get_hospital_by_slug(db: Session, slug: str) -> Optional[Hospital]:
    """Get hospital by slug."""
    return db.query(Hospital).filter(Hospital.slug == slug).first()
