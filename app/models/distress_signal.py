import uuid
from sqlalchemy import String, Float, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel

class DistressSignal(BaseModel):
    __tablename__ = "distress_signals"

    from_hospital_id: Mapped[str] = mapped_column(String(36), ForeignKey("hospitals.id"), nullable=False)
    requested_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    resource_type: Mapped[str] = mapped_column(String(30), nullable=False)
    urgency: Mapped[str] = mapped_column(String(10), nullable=False)
    medicine_name: Mapped[str] = mapped_column(String(200), nullable=True)
    quantity_needed: Mapped[float] = mapped_column(Float, nullable=True)
    current_stock: Mapped[float] = mapped_column(Float, nullable=True)
    hours_until_stockout: Mapped[float] = mapped_column(Float, nullable=True)
    reason: Mapped[str] = mapped_column(Text, nullable=True)
    ai_suggested_source: Mapped[str] = mapped_column(String(36), ForeignKey("hospitals.id"), nullable=True)
    ai_message: Mapped[str] = mapped_column(Text, nullable=True)
    sent_to_county: Mapped[bool] = mapped_column(Boolean, default=True)
    sent_to_hospitals: Mapped[dict] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="OPEN")
    resolved_by: Mapped[str] = mapped_column(String(36), ForeignKey("hospitals.id"), nullable=True)
    resolved_at: Mapped[str] = mapped_column(String(30), nullable=True)
