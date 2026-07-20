import uuid
from sqlalchemy import String, Integer, Boolean, Text, Float, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel

class Emergency(BaseModel):
    __tablename__ = "emergencies"

    sender_name: Mapped[str] = mapped_column(String(200), nullable=True)
    sender_phone: Mapped[str] = mapped_column(String(20), nullable=True)
    input_type: Mapped[str] = mapped_column(String(10), nullable=False)
    photo_url: Mapped[str] = mapped_column(Text, nullable=True)
    voice_transcript: Mapped[str] = mapped_column(Text, nullable=True)
    text_description: Mapped[str] = mapped_column(Text, nullable=True)
    input_language: Mapped[str] = mapped_column(String(10), default="sw")
    emergency_type: Mapped[str] = mapped_column(String(50), nullable=True)
    severity: Mapped[str] = mapped_column(String(10), nullable=True)
    casualties_estimated: Mapped[int] = mapped_column(Integer, nullable=True)
    hazards_detected: Mapped[str] = mapped_column(Text, nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)
    location_description: Mapped[str] = mapped_column(Text, nullable=True)
    dispatched_hospital_id: Mapped[str] = mapped_column(String(36), ForeignKey("hospitals.id"), nullable=True)
    dispatched_at: Mapped[str] = mapped_column(String(30), nullable=True)
    hospital_acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)
    auto_message: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="RECEIVED")
