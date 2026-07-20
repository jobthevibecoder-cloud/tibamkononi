from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, time


class AppointmentBookRequest(BaseModel):
    hospital_slug: str = Field(..., description="Hospital slug (e.g., 'mama-ngina-hospital')")
    department: str = Field(..., description="Department (GENERAL_OPD, MATERNITY, PAEDIATRIC, DENTAL)")
    appointment_date: str = Field(..., description="Date in YYYY-MM-DD format")
    appointment_time: str = Field(..., description="Time in HH:MM format (24h)")
    doctor_id: Optional[str] = Field(None, description="Specific doctor ID, or leave empty for any available")
    patient_name: str = Field(..., description="Patient full name")
    patient_phone: str = Field(..., description="Patient phone number")
    patient_nhif: Optional[str] = Field(None, description="NHIF number")
    reason: Optional[str] = Field(None, description="Reason for visit")
    pre_filled_from_triage: bool = Field(False, description="Whether this came from triage")


class AppointmentResponse(BaseModel):
    id: str
    hospital_name: str
    department: str
    doctor_name: str
    appointment_date: str
    appointment_time: str
    patient_name: str
    status: str
    booking_reference: str


class AvailableSlot(BaseModel):
    time: str
    doctor_id: str
    doctor_name: str
    available: bool


class AvailableSlotsResponse(BaseModel):
    hospital_name: str
    date: str
    department: str
    slots: list[AvailableSlot]
