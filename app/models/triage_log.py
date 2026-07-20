from sqlalchemy import String, Integer, Float, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel

class TriageLog(BaseModel):
    __tablename__ = "triage_logs"

    symptoms_text: Mapped[str] = mapped_column(Text, nullable=False)
    symptoms_language: Mapped[str] = mapped_column(String(10), default="sw")
    patient_age: Mapped[int] = mapped_column(Integer, nullable=True)
    patient_gender: Mapped[str] = mapped_column(String(10), nullable=True)
    patient_location_lat: Mapped[float] = mapped_column(Float, nullable=True)
    patient_location_lng: Mapped[float] = mapped_column(Float, nullable=True)
    ai_triage_level: Mapped[str] = mapped_column(String(20), nullable=True)
    ai_diagnosis: Mapped[dict] = mapped_column(JSON, nullable=True)
    ai_recommended_hospitals: Mapped[dict] = mapped_column(JSON, nullable=True)
    ai_recommendation_text: Mapped[str] = mapped_column(Text, nullable=True)
    ai_self_care_advice: Mapped[dict] = mapped_column(JSON, nullable=True)
