import uuid
from sqlalchemy import String, Integer, Boolean, Date, Time, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel

class Staff(BaseModel):
    __tablename__ = "staff"

    hospital_id: Mapped[str] = mapped_column(String(36), ForeignKey("hospitals.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    role: Mapped[str] = mapped_column(String(30), nullable=False)
    specialization: Mapped[str] = mapped_column(String(200), nullable=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    email: Mapped[str] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    attendance_records: Mapped[list["Attendance"]] = relationship(back_populates="staff", lazy="selectin")


class Attendance(BaseModel):
    __tablename__ = "attendance"

    staff_id: Mapped[str] = mapped_column(String(36), ForeignKey("staff.id"), nullable=False)
    hospital_id: Mapped[str] = mapped_column(String(36), ForeignKey("hospitals.id"), nullable=False)
    date: Mapped[str] = mapped_column(String(10), nullable=False)
    clock_in: Mapped[str] = mapped_column(String(10), nullable=True)
    clock_out: Mapped[str] = mapped_column(String(10), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="PRESENT")
    notes: Mapped[str] = mapped_column(String(300), nullable=True)

    staff: Mapped["Staff"] = relationship(back_populates="attendance_records")
