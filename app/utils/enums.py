from enum import Enum


class HospitalType(str, Enum):
    PHC = "PHC"
    CHC = "CHC"
    DISTRICT_HOSPITAL = "DISTRICT_HOSPITAL"
    PRIVATE_CLINIC = "PRIVATE_CLINIC"


class HospitalStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SUSPENDED = "SUSPENDED"


class WardType(str, Enum):
    GENERAL = "GENERAL"
    MATERNITY = "MATERNITY"
    PAEDIATRIC = "PAEDIATRIC"
    ICU = "ICU"
    ISOLATION = "ISOLATION"
    PRIVATE = "PRIVATE"


class BedStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    OCCUPIED = "OCCUPIED"
    RESERVED = "RESERVED"
    MAINTENANCE = "MAINTENANCE"


class StaffRole(str, Enum):
    DIRECTOR = "DIRECTOR"
    DOCTOR = "DOCTOR"
    NURSE = "NURSE"
    PHARMACIST = "PHARMACIST"
    LAB_TECH = "LAB_TECH"
    RECEPTIONIST = "RECEPTIONIST"
    CLEANER = "CLEANER"
    AMBULANCE_DRIVER = "AMBULANCE_DRIVER"


class AttendanceStatus(str, Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    LATE = "LATE"
    ON_LEAVE = "ON_LEAVE"
    SICK = "SICK"


class EmergencySeverity(str, Enum):
    CRITICAL = "CRITICAL"
    SEVERE = "SEVERE"
    MODERATE = "MODERATE"


class TriageLevel(str, Enum):
    EMERGENCY = "EMERGENCY"
    URGENT = "URGENT"
    ROUTINE = "ROUTINE"


class AnnouncementType(str, Enum):
    MEDICINE_DELIVERY = "MEDICINE_DELIVERY"
    FUNDING = "FUNDING"
    INSPECTION = "INSPECTION"
    HEALTH_ALERT = "HEALTH_ALERT"
    TRAINING = "TRAINING"
    GENERAL = "GENERAL"
