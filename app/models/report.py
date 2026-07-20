import uuid
from sqlalchemy import String, Integer, Date, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel

class Report(BaseModel):
    __tablename__ = "reports"

    hospital_id: Mapped[str] = mapped_column(String(36), ForeignKey("hospitals.id"), nullable=True)
    county_id: Mapped[str] = mapped_column(String(36), ForeignKey("counties.id"), nullable=True)
    report_type: Mapped[str] = mapped_column(String(30), nullable=False)
    report_date: Mapped[str] = mapped_column(String(10), nullable=False)
    ai_summary: Mapped[str] = mapped_column(Text, nullable=True)
    ai_score: Mapped[int] = mapped_column(Integer, nullable=True)
    ai_alerts: Mapped[dict] = mapped_column(JSON, nullable=True)
    ai_recommendations: Mapped[dict] = mapped_column(JSON, nullable=True)
    ai_full_report: Mapped[dict] = mapped_column(JSON, nullable=True)
