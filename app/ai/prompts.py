"""Prompt templates for all Gemma 4 interactions."""

DIAGNOSIS_PROMPT = """You are a medical AI. Output ONLY a JSON object. No explanations, no markdown, no text before or after the JSON.

Patient: {age}y/o {gender}
Symptoms: {symptoms}
Location: Coastal Kenya

Output this exact structure:
{{"diagnosis":[{{"disease":"name","confidence":0.0}}],"triage_level":"EMERGENCY|URGENT|ROUTINE","tests":["test"],"treatment":[{{"medicine":"name","dosage":"instructions"}}],"self_care":["advice"]}}

JSON:"""

EMERGENCY_TEXT_PROMPT = """You are an emergency dispatcher AI. Output ONLY a JSON object. No explanations.

Emergency ({language}): {text}
GPS: {latitude}, {longitude}

Output:
{{"emergency_type":"ROAD_ACCIDENT|FIRE|MEDICAL|OBSTETRIC|OTHER","severity":"CRITICAL|SEVERE|MODERATE","casualties_estimated":0,"hazards_detected":"description","auto_message":"dispatch message"}}

JSON:"""

EMERGENCY_PHOTO_PROMPT = """Analyze this emergency photo. Output ONLY JSON. No explanations.

Scene: {photo_description}
GPS: {latitude}, {longitude}

Output:
{{"emergency_type":"type","severity":"CRITICAL|SEVERE|MODERATE","casualties_estimated":0,"hazards_detected":"description","auto_message":"message in {language}"}}

JSON:"""

STOCK_FORECAST_PROMPT = """Analyze inventory. Output ONLY JSON. No explanations.

Medicine: {medicine_name} | Stock: {current_stock} {unit} | Daily use: {daily_rate} | Threshold: {threshold}

Output:
{{"days_until_stockout":0,"severity":"CRITICAL|WARNING|OK","recommended_action":"action","suggested_quantity":0,"ai_message":"summary"}}

JSON:"""

HOSPITAL_RANKING_PROMPT = """Rank hospitals for a patient. Output ONLY JSON. No explanations.

Patient at ({patient_lat},{patient_lng}). Needs: {required_tests}, {required_medicines}
Hospitals: {hospitals_json}

Output:
{{"ranked_hospitals":[{{"name":"hospital","score":0,"reason":"reason"}}],"recommendation":"best choice"}}

JSON:"""

DAILY_SUMMARY_PROMPT = """Generate hospital report. Output ONLY JSON. No explanations.

Hospital: {hospital_name} | Date: {date}
Patients: {total_patients} | Admissions: {admissions} | Discharges: {discharges}
Alerts: {alerts} | Beds: {bed_percent}% | Staff: {staff_count}/{total_staff}

Output:
{{"summary":"report","recommendations":["action"],"prediction":"forecast"}}

JSON:"""

ATTENDANCE_ANOMALY_PROMPT = """Analyze attendance. Output ONLY JSON. No explanations.

Staff: {staff_name} ({role})
Records: {attendance_data}

Output:
{{"pattern_detected":true|false,"pattern_description":"description","impact":"impact","recommendation":"action"}}

JSON:"""

REDISTRIBUTION_PROMPT = """Recommend redistribution. Output ONLY JSON. No explanations.

{resource} at {hospital_name}: {current} units, {daily_rate}/day, {hours}h until out.
Nearby: {nearby_json}

Output:
{{"suggested_source":"hospital","suggested_quantity":0,"ai_message":"recommendation"}}

JSON:"""
