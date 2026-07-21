"""Prompt templates - simplified for Gemma 4 JSON output."""

DIAGNOSIS_PROMPT = """Patient: {age}y/o {gender}
Symptoms: {symptoms}
Location: Coastal Kenya, Mombasa

Fill in this JSON exactly. Replace the placeholders with your analysis:
{{"diagnosis":[{{"disease":"DISEASE1","confidence":0.0}},{{"disease":"DISEASE2","confidence":0.0}}],"triage_level":"LEVEL","tests":["TEST1","TEST2"],"treatment":[{{"medicine":"MED1","dosage":"DOSE1"}},{{"medicine":"MED2","dosage":"DOSE2"}}],"self_care":["ADVICE1","ADVICE2"]}}

Return ONLY the filled JSON. No other text."""

EMERGENCY_TEXT_PROMPT = """Emergency report: {text}
GPS: {latitude}, {longitude}

Fill in this JSON exactly:
{{"emergency_type":"TYPE","severity":"LEVEL","casualties_estimated":0,"hazards_detected":"HAZARDS","auto_message":"DISPATCH MESSAGE"}}

Return ONLY the filled JSON. No other text."""

STOCK_FORECAST_PROMPT = """Medicine: {medicine_name}
Stock: {current_stock} {unit} | Daily use: {daily_rate} | Threshold: {threshold} | Last restock: {last_restock}
Nearby hospitals: {nearby_hospitals}

Fill in this JSON exactly:
{{"days_until_stockout":0,"severity":"LEVEL","recommended_action":"ACTION","suggested_quantity":0,"ai_message":"MESSAGE"}}

Return ONLY the filled JSON. No other text."""

HOSPITAL_RANKING_PROMPT = """Patient at ({patient_lat},{patient_lng}). Needs {required_tests}, {required_medicines}.
Hospitals: {hospitals_json}

Fill in this JSON exactly:
{{"ranked_hospitals":[{{"name":"HOSP1","score":0,"reason":"WHY"}},{{"name":"HOSP2","score":0,"reason":"WHY"}}],"recommendation":"BEST CHOICE"}}

Return ONLY the filled JSON. No other text."""

DAILY_SUMMARY_PROMPT = """{hospital_name} report for {date}:
Patients: {total_patients} | Admissions: {admissions} | Discharges: {discharges}
Alerts: {alerts} | Beds: {bed_percent}% | Staff: {staff_count}/{total_staff}

Fill in this JSON exactly:
{{"summary":"REPORT","recommendations":["REC1","REC2"],"prediction":"FORECAST"}}

Return ONLY the filled JSON. No other text."""

ATTENDANCE_ANOMALY_PROMPT = """Staff: {staff_name} ({role}). Recent attendance: {attendance_data}

Fill in this JSON exactly:
{{"pattern_detected":true,"pattern_description":"DESCRIPTION","impact":"IMPACT","recommendation":"ACTION"}}

Return ONLY the filled JSON. No other text."""

REDISTRIBUTION_PROMPT = """{resource} at {hospital_name}: {current} units, using {daily_rate}/day, {hours}h until gone.
Nearby: {nearby_json}

Fill in this JSON exactly:
{{"suggested_source":"HOSPITAL","suggested_quantity":0,"ai_message":"RECOMMENDATION"}}

Return ONLY the filled JSON. No other text."""
