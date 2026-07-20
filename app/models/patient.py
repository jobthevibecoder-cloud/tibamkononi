import uuid
from sqlalchemy import String, Integer, Float, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel

class Patient(BaseModel):
    __tablename__ = "patients"

    hospital_id: Mapped[str] = mapped_column(String(36), ForeignKey("hospitals.id"), nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    id_number: Mapped[str] = mapped_column(String(20), nullable=True)
    nhif_number: Mapped[str] = mapped_column(String(30), nullable=True)
    age: Mapped[int] = mapped_column(Integer, nullable=True)
    gender: Mapped[str] = mapped_column(String(10), nullable=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    address: Mapped[str] = mapped_column(Text, nullable=True)
    emergency_contact_name: Mapped[str] = mapped_column(String(200), nullable=True)
    emergency_contact_phone: Mapped[str] = mapped_column(String(20), nullable=True)
    visit_type: Mapped[str] = mapped_column(String(20), default="OUTPATIENT")
    admission_date: Mapped[str] = mapped_column(String(30), nullable=True)
    discharge_date: Mapped[str] = mapped_column(String(30), nullable=True)
    blood_pressure: Mapped[str] = mapped_column(String(10), nullable=True)
    pulse: Mapped[int] = mapped_column(Integer, nullable=True)
    temperature: Mapped[float] = mapped_column(Float, nullable=True)
    spo2: Mapped[int] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="REGISTERED")
    registered_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)

    diagnoses: Mapped[list["Diagnosis"]] = relationship(back_populates="patient", lazy="selectin")
    prescriptions: Mapped[list["Prescription"]] = relationship(back_populates="patient", lazy="selectin")


class Diagnosis(BaseModel):
    __tablename__ = "diagnoses"

    patient_id: Mapped[str] = mapped_column(String(36), ForeignKey("patients.id"), nullable=False)
    hospital_id: Mapped[str] = mapped_column(String(36), ForeignKey("hospitals.id"), nullable=False)
    symptoms_text: Mapped[str] = mapped_column(Text, nullable=False)
    symptoms_language: Mapped[str] = mapped_column(String(10), default="sw")
    ai_diagnosis: Mapped[dict] = mapped_column(JSON, nullable=True)
    ai_recommended_tests: Mapped[dict] = mapped_column(JSON, nullable=True)
    ai_recommended_treatment: Mapped[dict] = mapped_column(JSON, nullable=True)
    ai_triage_level: Mapped[str] = mapped_column(String(20), nullable=True)
    ai_confidence: Mapped[float] = mapped_column(Float, nullable=True)
    doctor_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    final_diagnosis: Mapped[str] = mapped_column(String(300), nullable=True)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)

    patient: Mapped["Patient"] = relationship(back_populates="diagnoses")
    prescriptions: Mapped[list["Prescription"]] = relationship(back_populates="diagnosis", lazy="selectin")


class Prescription(BaseModel):
    __tablename__ = "prescriptions"

    diagnosis_id: Mapped[str] = mapped_column(String(36), ForeignKey("diagnoses.id"), nullable=False)
    patient_id: Mapped[str] = mapped_column(String(36), ForeignKey("patients.id"), nullable=False)
    hospital_id: Mapped[str] = mapped_column(String(36), ForeignKey("hospitals.id"), nullable=False)
    doctor_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    medicine_id: Mapped[str] = mapped_column(String(36), ForeignKey("medicines.id"), nullable=False)
    medicine_name: Mapped[str] = mapped_column(String(200), nullable=True)
    dosage: Mapped[str] = mapped_column(String(100), nullable=True)
    quantity_prescribed: Mapped[float] = mapped_column(Float, nullable=True)
    duration_days: Mapped[int] = mapped_column(Integer, nullable=True)
    dispensed: Mapped[bool] = mapped_column(Boolean, default=False)
    dispensed_at: Mapped[str] = mapped_column(String(30), nullable=True)
    dispensed_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)

    diagnosis: Mapped["Diagnosis"] = relationship(back_populates="prescriptions")
    patient: Mapped["Patient"] = relationship(back_populates="prescriptions")
