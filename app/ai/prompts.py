"""Prompt templates for all Gemma 4 interactions."""

DIAGNOSIS_PROMPT = """You are a medical AI at a Kenyan hospital. Analyze these symptoms.

Patient: {age}y/o {gender}
Symptoms ({language}): {symptoms}
Location: Coastal Kenya (consider malaria, typhoid, dengue)

Output JSON with:
- diagnosis: top 3 diseases with confidence scores (0-1)
- triage_level: EMERGENCY/URGENT/ROUTINE
- recommended_tests: list of tests needed
- recommended_treatment: list with medicine name and dosage
- self_care_advice: what patient can do now

JSON:"""

EMERGENCY_PHOTO_PROMPT = """Analyze this emergency scene photo from Mombasa, Kenya.

Scene description: {photo_description}
GPS Location: {latitude}, {longitude}

Output JSON with:
- emergency_type: ROAD_ACCIDENT/FIRE/MEDICAL/OBSTETRIC/OTHER
- severity: CRITICAL/SEVERE/MODERATE
- casualties_estimated: number
- hazards_detected: any dangers
- auto_message: dispatch message in {language}

JSON:"""

EMERGENCY_TEXT_PROMPT = """Analyze this emergency report from Mombasa, Kenya.

Emergency description ({language}): {text}
GPS Location: {latitude}, {longitude}

Output JSON with:
- emergency_type: ROAD_ACCIDENT/FIRE/MEDICAL/OBSTETRIC/OTHER
- severity: CRITICAL/SEVERE/MODERATE
- casualties_estimated: number
- hazards_detected: any dangers
- auto_message: professional dispatch message in {language}

JSON:"""

STOCK_FORECAST_PROMPT = """Analyze inventory and predict stock depletion.

Medicine: {medicine_name}
Current stock: {current_stock} {unit}
Daily usage rate: {daily_rate} {unit}/day
Minimum threshold: {threshold}
Last restock: {last_restock}

Nearby hospitals with this medicine: {nearby_hospitals}

Output JSON with:
- days_until_stockout: number
- severity: CRITICAL/WARNING/OK
- recommended_action: transfer or order
- suggested_source: best hospital to transfer from
- suggested_quantity: how much to transfer
- ai_message: summary for distress signal

JSON:"""

HOSPITAL_RANKING_PROMPT = """Rank hospitals for a patient based on multiple factors.

Patient location: {patient_lat}, {patient_lng}
Required tests: {required_tests}
Required medicines: {required_medicines}

Available hospitals: {hospitals_json}

Consider: distance, test availability, medicine stock, doctor presence, wait time.
Output JSON with ranked list and recommendation in {language}.

JSON:"""

OUTBREAK_DETECTION_PROMPT = """Analyze recent patient data for disease clustering.

Recent patients (24h): {patients_json}

Look for: common symptoms, geographic clustering, unusual frequency.
Output JSON with:
- outbreak_detected: true/false
- disease_suspected: name
- confidence: 0-1
- affected_area: location
- recommended_action: what to do

JSON:"""

DAILY_SUMMARY_PROMPT = """Generate a daily hospital report.

Hospital: {hospital_name}
Date: {date}
Patients seen: {total_patients}
Admissions: {admissions}
Discharges: {discharges}
Stock alerts: {alerts}
Bed occupancy: {bed_percent}%
Staff present: {staff_count}/{total_staff}

Write a concise summary in {language}. Include predictions for tomorrow.
Output JSON with summary and recommendations.

JSON:"""

ATTENDANCE_ANOMALY_PROMPT = """Analyze staff attendance patterns.

Staff member: {staff_name}, Role: {role}
Attendance last 30 days: {attendance_data}

Detect patterns, calculate impact on patient care, recommend action.
Output JSON.

JSON:"""

REDISTRIBUTION_PROMPT = """Recommend resource redistribution between hospitals.

Requesting hospital: {hospital_name}
Resource needed: {resource}
Current stock: {current} units
Daily usage: {daily_rate}
Hours until depletion: {hours}

Nearby hospitals with surplus: {nearby_json}

Consider: distance, surplus quantity, each hospital's own usage rate.
Output JSON with recommended transfer plan.

JSON:"""
