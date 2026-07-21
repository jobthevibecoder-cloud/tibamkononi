"""AI service functions - fixed diagnosis extraction."""
import json
import re
from app.ai.engine import gemma
from app.ai.prompts import (
    DIAGNOSIS_PROMPT, EMERGENCY_TEXT_PROMPT, EMERGENCY_PHOTO_PROMPT,
    STOCK_FORECAST_PROMPT, HOSPITAL_RANKING_PROMPT, DAILY_SUMMARY_PROMPT,
    ATTENDANCE_ANOMALY_PROMPT, REDISTRIBUTION_PROMPT
)
from loguru import logger


def _parse_json_response(response: str) -> dict:
    """Extract structured data from Gemma 4 output."""
    cleaned = response.strip()
    
    # Strategy 1: Try complete JSON object
    start = cleaned.find('{')
    end = cleaned.rfind('}') + 1
    if start >= 0 and end > start:
        try:
            return json.loads(cleaned[start:end])
        except json.JSONDecodeError:
            pass
    
    # Strategy 2: Extract from backtick-enclosed values
    return _parse_backtick_format(cleaned)


def _parse_backtick_format(text: str) -> dict:
    """Parse Gemma 4's `key`: `value` format."""
    result = {"diagnosis": [], "triage_level": "ROUTINE", "tests": [], "treatment": [], "self_care": []}
    
    # Extract triage_level
    triage = re.search(r'`triage_level`\s*:\s*`"?(\w+)', text)
    if triage:
        result["triage_level"] = triage.group(1).upper()
    
    # Extract diagnosis - find the array between backticks after "diagnosis"
    diag_match = re.search(r'`diagnosis`\s*:\s*`(\[.*?\])`', text, re.DOTALL)
    if not diag_match:
        # Try without backticks around the value
        diag_match = re.search(r'"diagnosis"\s*:\s*(\[.*?\])', text, re.DOTALL)
    if diag_match:
        try:
            diag_str = diag_match.group(1)
            # Clean any trailing commas or whitespace
            diag_str = diag_str.strip()
            result["diagnosis"] = json.loads(diag_str)
        except json.JSONDecodeError as e:
            logger.warning(f"Diagnosis parse failed: {e} for: {diag_match.group(1)[:100]}")
    
    # Extract tests
    tests_match = re.search(r'`tests`\s*:\s*`(\[.*?\])`', text, re.DOTALL)
    if not tests_match:
        tests_match = re.search(r'"tests"\s*:\s*(\[.*?\])', text, re.DOTALL)
    if tests_match:
        try:
            result["tests"] = json.loads(tests_match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Extract treatment
    treatment_match = re.search(r'`treatment`\s*:\s*`(\[.*?\])`', text, re.DOTALL)
    if not treatment_match:
        treatment_match = re.search(r'"treatment"\s*:\s*(\[.*?\])', text, re.DOTALL)
    if treatment_match:
        try:
            result["treatment"] = json.loads(treatment_match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Extract self_care
    care_match = re.search(r'`self_care`\s*:\s*`(\[.*?\])`', text, re.DOTALL)
    if not care_match:
        care_match = re.search(r'"self_care"\s*:\s*(\[.*?\])', text, re.DOTALL)
    if care_match:
        try:
            result["self_care"] = json.loads(care_match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Fallback: extract diagnosis from natural language if regex failed
    if not result["diagnosis"]:
        diseases = re.findall(r'"disease"\s*:\s*"([^"]+)".*?"confidence"\s*:\s*([0-9.]+)', text)
        for disease, confidence in diseases:
            result["diagnosis"].append({"disease": disease, "confidence": float(confidence)})
    
    return result


def analyze_symptoms(symptoms_text: str, language: str, age: int, gender: str) -> dict:
    prompt = DIAGNOSIS_PROMPT.format(age=age, gender=gender, symptoms=symptoms_text)
    response = gemma.generate(prompt, max_tokens=600)
    return _parse_json_response(response)


def analyze_emergency_text(text: str, language: str, lat: float, lng: float) -> dict:
    prompt = EMERGENCY_TEXT_PROMPT.format(language=language, text=text, latitude=lat, longitude=lng)
    response = gemma.generate(prompt, max_tokens=400)
    return _parse_json_response(response)


def analyze_emergency_photo(photo_description: str, language: str, lat: float, lng: float) -> dict:
    prompt = EMERGENCY_PHOTO_PROMPT.format(photo_description=photo_description, language=language, latitude=lat, longitude=lng)
    response = gemma.generate(prompt, max_tokens=400)
    return _parse_json_response(response)


def forecast_stock(medicine_name: str, current_stock: float, daily_rate: float, threshold: float, unit: str, last_restock: str, nearby_hospitals: str) -> dict:
    prompt = STOCK_FORECAST_PROMPT.format(medicine_name=medicine_name, current_stock=current_stock, daily_rate=daily_rate, threshold=threshold, unit=unit, last_restock=last_restock, nearby_hospitals=nearby_hospitals)
    response = gemma.generate(prompt, max_tokens=300)
    return _parse_json_response(response)


def rank_hospitals(patient_lat: float, patient_lng: float, required_tests: list, required_medicines: list, hospitals_json: str, language: str = "sw") -> dict:
    prompt = HOSPITAL_RANKING_PROMPT.format(patient_lat=patient_lat, patient_lng=patient_lng, required_tests=json.dumps(required_tests), required_medicines=json.dumps(required_medicines), hospitals_json=hospitals_json, language=language)
    response = gemma.generate(prompt, max_tokens=500)
    return _parse_json_response(response)


def generate_daily_summary(hospital_name: str, date: str, total_patients: int, admissions: int, discharges: int, alerts: str, bed_percent: float, staff_count: int, total_staff: int, language: str = "en") -> dict:
    prompt = DAILY_SUMMARY_PROMPT.format(hospital_name=hospital_name, date=date, total_patients=total_patients, admissions=admissions, discharges=discharges, alerts=alerts, bed_percent=bed_percent, staff_count=staff_count, total_staff=total_staff, language=language)
    response = gemma.generate(prompt, max_tokens=400)
    return _parse_json_response(response)


def detect_attendance_anomaly(staff_name: str, role: str, attendance_data: str) -> dict:
    prompt = ATTENDANCE_ANOMALY_PROMPT.format(staff_name=staff_name, role=role, attendance_data=attendance_data)
    response = gemma.generate(prompt, max_tokens=300)
    return _parse_json_response(response)


def recommend_redistribution(hospital_name: str, resource: str, current: float, daily_rate: float, hours: float, nearby_json: str) -> dict:
    prompt = REDISTRIBUTION_PROMPT.format(hospital_name=hospital_name, resource=resource, current=current, daily_rate=daily_rate, hours=hours, nearby_json=nearby_json)
    response = gemma.generate(prompt, max_tokens=300)
    return _parse_json_response(response)


logger.info("AI services ready")
