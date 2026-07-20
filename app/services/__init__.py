from app.services.hospital_service import (
    register_hospital, approve_hospital, reject_hospital,
    get_hospitals_by_county, get_hospital_by_slug
)
from app.services.patient_service import (
    register_patient, create_ai_diagnosis, confirm_diagnosis, prescribe_medicine
)
from app.services.emergency_service import process_emergency
from app.services.appointment_service import (
    get_available_slots, book_appointment, get_hospital_appointments, cancel_appointment
)
from app.services.county_service import (
    get_county_overview, get_hospital_list_atoz,
    get_hospital_deep_dive, generate_weekly_watchlist
)

__all__ = [
    "register_hospital", "approve_hospital", "reject_hospital",
    "get_hospitals_by_county", "get_hospital_by_slug",
    "register_patient", "create_ai_diagnosis", "confirm_diagnosis", "prescribe_medicine",
    "process_emergency",
    "get_available_slots", "book_appointment", "get_hospital_appointments", "cancel_appointment",
    "get_county_overview", "get_hospital_list_atoz",
    "get_hospital_deep_dive", "generate_weekly_watchlist",
]
