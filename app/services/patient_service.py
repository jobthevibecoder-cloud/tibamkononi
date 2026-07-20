"""Patient management business logic."""
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.patient import Patient, Diagnosis, Prescription
from app.models.inventory import Medicine, StockMovement
from app.ai.services import analyze_symptoms
from loguru import logger


def register_patient(db: Session, hospital_id: str, data: dict, registered_by: str) -> Patient:
    """Register a new patient."""
    patient = Patient(
        hospital_id=hospital_id,
        full_name=data["full_name"],
        id_number=data.get("id_number"),
        nhif_number=data.get("nhif_number"),
        age=data.get("age"),
        gender=data.get("gender"),
        phone=data.get("phone"),
        address=data.get("address"),
        emergency_contact_name=data.get("emergency_contact_name"),
        emergency_contact_phone=data.get("emergency_contact_phone"),
        blood_pressure=data.get("blood_pressure"),
        pulse=data.get("pulse"),
        temperature=data.get("temperature"),
        spo2=data.get("spo2"),
        registered_by=registered_by,
    )
    db.add(patient)
    db.flush()
    logger.info(f"Patient registered: {patient.full_name} at hospital {hospital_id}")
    return patient


def create_ai_diagnosis(db: Session, patient_id: str, hospital_id: str, 
                        symptoms_text: str, language: str, age: int, gender: str) -> Diagnosis:
    """Create AI-assisted diagnosis."""
    # Get AI analysis
    ai_result = analyze_symptoms(symptoms_text, language, age, gender)
    
    diagnosis = Diagnosis(
        patient_id=patient_id,
        hospital_id=hospital_id,
        symptoms_text=symptoms_text,
        symptoms_language=language,
        ai_diagnosis=ai_result.get("diagnosis", []),
        ai_recommended_tests=ai_result.get("tests", []),
        ai_recommended_treatment=ai_result.get("treatment", []),
        ai_triage_level=ai_result.get("triage_level", "ROUTINE"),
        ai_confidence=0.85,
    )
    db.add(diagnosis)
    db.flush()
    logger.info(f"AI diagnosis created for patient {patient_id}: {ai_result.get('triage_level')}")
    return diagnosis


def confirm_diagnosis(db: Session, diagnosis_id: str, doctor_id: str, final_diagnosis: str) -> Diagnosis:
    """Doctor confirms the diagnosis."""
    diagnosis = db.query(Diagnosis).filter(Diagnosis.id == diagnosis_id).first()
    if diagnosis:
        diagnosis.doctor_id = doctor_id
        diagnosis.final_diagnosis = final_diagnosis
        diagnosis.confirmed = True
    return diagnosis


def prescribe_medicine(db: Session, diagnosis_id: str, patient_id: str, hospital_id: str,
                       doctor_id: str, medicine_id: str, medicine_name: str,
                       dosage: str, quantity: float, duration_days: int) -> Prescription:
    """Prescribe medicine and auto-deduct from stock."""
    prescription = Prescription(
        diagnosis_id=diagnosis_id,
        patient_id=patient_id,
        hospital_id=hospital_id,
        doctor_id=doctor_id,
        medicine_id=medicine_id,
        medicine_name=medicine_name,
        dosage=dosage,
        quantity_prescribed=quantity,
        duration_days=duration_days,
    )
    db.add(prescription)
    
    # Auto-deduct from inventory
    medicine = db.query(Medicine).filter(Medicine.id == medicine_id).first()
    if medicine:
        previous_stock = medicine.current_stock
        medicine.current_stock -= quantity
        
        # Log stock movement
        movement = StockMovement(
            medicine_id=medicine_id,
            hospital_id=hospital_id,
            movement_type="DEDUCTION",
            quantity=quantity,
            previous_stock=previous_stock,
            new_stock=medicine.current_stock,
            patient_id=patient_id,
            prescription_id=prescription.id,
        )
        db.add(movement)
        
        logger.info(f"Stock deducted: {medicine_name} -{quantity} (remaining: {medicine.current_stock})")
    
    return prescription
