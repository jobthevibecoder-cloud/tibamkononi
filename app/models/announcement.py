import uuid
from sqlalchemy import String, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel

class Announcement(BaseModel):
    __tablename__ = "announcements"

    county_id: Mapped[str] = mapped_column(String(36), ForeignKey("counties.id"), nullable=False)
    posted_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    type: Mapped[str] = mapped_column(String(30), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    attachment_url: Mapped[str] = mapped_column(Text, nullable=True)
    target_type: Mapped[str] = mapped_column(String(20), default="ALL")
    target_hospitals: Mapped[dict] = mapped_column(JSON, nullable=True)
    target_sub_counties: Mapped[dict] = mapped_column(JSON, nullable=True)
    target_hospital_types: Mapped[dict] = mapped_column(JSON, nullable=True)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    scheduled_for: Mapped[str] = mapped_column(String(30), nullable=True)
    published_at: Mapped[str] = mapped_column(String(30), nullable=True)
    expires_at: Mapped[str] = mapped_column(String(30), nullable=True)
