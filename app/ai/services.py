"""AI service functions - robust JSON parser."""
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
    """Extract JSON from Gemma response, fixing common issues."""
    cleaned = response.strip()
    
    # Remove markdown code blocks
    cleaned = re.sub(r'```(?:json)?\s*', '', cleaned)
    cleaned = cleaned.replace('```', '')
    
    # Remove leading asterisks/bullets from explanations
    cleaned = re.sub(r'^\*\s*', '', cleaned, flags=re.MULTILINE)
    
    # Try to find complete JSON object first
    start = cleaned.find('{')
    end = cleaned.rfind('}') + 1
    
    if start >= 0 and end > start:
        json_str = cleaned[start:end]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.warning(f"Initial parse failed: {e}")
            # Try to fix common issues
            json_str = _fix_json(json_str)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
    
    # If all parsing fails, extract what we can
    logger.warning(f"Could not parse JSON. Raw: {cleaned[:200]}")
    return _extract_fields_manually(cleaned)


def _fix_json(json_str: str) -> str:
    """Fix common JSON issues from LLM output."""
    # Fix missing commas between objects
    json_str = re.sub(r'}\s*{', '},{', json_str)
    
    # Fix unquoted keys
    json_str = re.sub(r'(\w+):', r'"\1":', json_str)
    
    # Fix single quotes
    json_str = json_str.replace("'", '"')
    
    # Ensure arrays have proper brackets
    if '"diagnosis":' in json_str and not '"diagnosis":[' in json_str:
        json_str = json_str.replace('"diagnosis":', '"diagnosis":[')
        # Find where diagnosis array should end
        tests_pos = json_str.find('"tests"')
        if tests_pos > 0:
            json_str = json_str[:tests_pos] + '],' + json_str[tests_pos:]
    
    if '"tests":' in json_str and not '"tests":[' in json_str:
        json_str = json_str.replace('"tests":', '"tests":[')
        treatment_pos = json_str.find('"treatment"')
        if treatment_pos > 0:
            json_str = json_str[:treatment_pos] + '],' + json_str[treatment_pos:]
    
    if '"treatment":' in json_str and not '"treatment":[' in json_str:
        json_str = json_str.replace('"treatment":', '"treatment":[')
        self_care_pos = json_str.find('"self_care"')
        if self_care_pos > 0:
            json_str = json_str[:self_care_pos] + '],' + json_str[self_care_pos:]
    
    if '"self_care":' in json_str and not '"self_care":[' in json_str:
        json_str = json_str.replace('"self_care":', '"self_care":[')
        json_str = json_str.rstrip() + ']}'
    
    return json_str


def _extract_fields_manually(text: str) -> dict:
    """Extract key fields using regex when JSON parsing fails."""
    result = {"diagnosis": [], "triage_level": "ROUTINE", "tests": [], "treatment": [], "self_care": []}
    
    # Extract triage level
    triage_match = re.search(r'triage_level["\s:]*([A-Z]+)', text, re.IGNORECASE)
    if triage_match:
        result["triage_level"] = triage_match.group(1).upper()
    
    # Extract diseases with confidence
    disease_matches = re.findall(r'"disease"\s*:\s*"([^"]+)".*?"confidence"\s*:\s*([0-9.]+)', text)
    for disease, confidence in disease_matches:
        result["diagnosis"].append({"disease": disease, "confidence": float(confidence)})
    
    # Extract tests
    test_matches = re.findall(r'"tests"\s*:\s*\[(.*?)\]', text, re.DOTALL)
    if test_matches:
        tests = re.findall(r'"([^"]+)"', test_matches[0])
        result["tests"] = tests
    
    # Extract treatments
    treatment_matches = re.findall(r'"medicine"\s*:\s*"([^"]+)".*?"dosage"\s*:\s*"([^"]+)"', text)
    for med, dosage in treatment_matches:
        result["treatment"].append({"medicine": med, "dosage": dosage})
    
    # Extract self care
    care_matches = re.findall(r'"self_care"\s*:\s*\[(.*?)\]', text, re.DOTALL)
    if care_matches:
        advice = re.findall(r'"([^"]+)"', care_matches[0])
        result["self_care"] = advice
    
    logger.info(f"Manually extracted: {result}")
    return result


def analyze_symptoms(symptoms_text: str, language: str, age: int, gender: str) -> dict:
    prompt = DIAGNOSIS_PROMPT.format(age=age, gender=gender, symptoms=symptoms_text)
    response = gemma.generate(prompt, max_tokens=400)
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
