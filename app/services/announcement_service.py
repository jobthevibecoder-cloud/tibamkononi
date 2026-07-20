"""Announcements business logic."""
from sqlalchemy.orm import Session
from app.models.announcement import Announcement
from app.models.county import County
from loguru import logger


def create_announcement(db: Session, county_code: str, data: dict) -> dict:
    """Create a county-wide announcement."""
    county = db.query(County).filter(County.code == county_code).first()
    if not county:
        raise ValueError("County not found")
    
    announcement = Announcement(
        county_id=county.id,
        type=data["type"],
        title=data["title"],
        body=data["body"],
        target_type=data.get("target_type", "ALL"),
        target_hospitals=data.get("target_hospitals"),
        is_pinned=data.get("is_pinned", False),
        published_at=data.get("published_at"),
    )
    db.add(announcement)
    db.flush()
    
    return {
        "id": announcement.id,
        "title": announcement.title,
        "type": announcement.type,
        "is_pinned": announcement.is_pinned,
        "message": "Announcement published",
    }


def get_announcements(db: Session, county_code: str = "MSA", announcement_type: str = None) -> list:
    """Get announcements for a county."""
    county = db.query(County).filter(County.code == county_code).first()
    if not county:
        return []
    
    query = db.query(Announcement).filter(Announcement.county_id == county.id)
    
    if announcement_type:
        query = query.filter(Announcement.type == announcement_type)
    
    announcements = query.order_by(
        Announcement.is_pinned.desc(),
        Announcement.created_at.desc()
    ).all()
    
    return [
        {
            "id": a.id,
            "type": a.type,
            "title": a.title,
            "body": a.body,
            "is_pinned": a.is_pinned,
            "target_type": a.target_type,
            "published_at": str(a.published_at) if a.published_at else str(a.created_at),
        }
        for a in announcements
    ]
