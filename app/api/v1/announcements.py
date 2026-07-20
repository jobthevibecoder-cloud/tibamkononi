from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.services.announcement_service import create_announcement, get_announcements

router = APIRouter()


class AnnouncementRequest(BaseModel):
    type: str  # MEDICINE_DELIVERY, FUNDING, INSPECTION, HEALTH_ALERT, TRAINING, GENERAL
    title: str
    body: str
    target_type: str = "ALL"
    target_hospitals: Optional[list] = None
    is_pinned: bool = False
    published_at: Optional[str] = None


@router.get("/")
async def view_announcements(
    county_code: str = Query("MSA"),
    type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """View public announcements."""
    try:
        announcements = get_announcements(db, county_code, type)
        return {"announcements": announcements, "total": len(announcements)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create")
async def post_announcement(
    request: AnnouncementRequest,
    county_code: str = Query("MSA"),
    db: Session = Depends(get_db)
):
    """Create a new announcement (county director only)."""
    try:
        result = create_announcement(db, county_code, request.model_dump())
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
