import uuid
from sqlalchemy import String, Boolean, Date, Time, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel

class Appointment(BaseModel):
    __tablename__ = "appointments"

    hospital_id: Mapped[str] = mapped_column(String(36), ForeignKey("hospitals.id"), nullable=False)
    doctor_id: Mapped[str] = mapped_column(String(36), ForeignKey("staff.id"), nullable=False)
    patient_id: Mapped[str] = mapped_column(String(36), ForeignKey("patients.id"), nullable=True)
    patient_name: Mapped[str] = mapped_column(String(200), nullable=True)
    patient_phone: Mapped[str] = mapped_column(String(20), nullable=True)
    patient_nhif: Mapped[str] = mapped_column(String(30), nullable=True)
    department: Mapped[str] = mapped_column(String(50), nullable=True)
    appointment_date: Mapped[str] = mapped_column(String(10), nullable=False)
    appointment_time: Mapped[str] = mapped_column(String(10), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=True)
    pre_filled_from_triage: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(20), default="CONFIRMED")
    reminder_sent: Mapped[bool] = mapped_column(Boolean, default=False)
