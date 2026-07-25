"""Seed database with comprehensive demo data for Tiba Mkononi hackathon."""
from app.core.database import engine, init_db
from app.core.database import Session
from app.models.county import County, SubCounty, Ward
from app.models.hospital import Hospital, Building, HospitalWard, Bed, Amenity
from app.models.staff import Staff, Attendance
from app.models.inventory import InventoryCategory, Medicine, StockMovement
from app.models.supplier import Supplier
from app.models.patient import Patient, Diagnosis, Prescription
from app.models.user import User
from app.core.security import hash_password
from loguru import logger


def clear_and_seed():
    """Clear all data and seed fresh demo data."""
    init_db()
    
    with Session(engine) as db:
        # ---- CLEAR ALL EXISTING DATA ----
        logger.info("Clearing old seed data...")
        db.query(Diagnosis).delete()
        db.query(Prescription).delete()
        db.query(StockMovement).delete()
        db.query(Medicine).delete()
        db.query(InventoryCategory).delete()
        db.query(Supplier).delete()
        db.query(Attendance).delete()
        db.query(Staff).delete()
        db.query(Bed).delete()
        db.query(HospitalWard).delete()
        db.query(Building).delete()
        db.query(Amenity).delete()
        db.query(Hospital).delete()
        db.query(Ward).delete()
        db.query(SubCounty).delete()
        db.query(County).delete()
        db.query(User).delete()
        db.commit()
        logger.info("Old data cleared.")
        
        # ---- COUNTY ----
        mombasa = County(name="Mombasa", code="MSA", capital="Mombasa City")
        db.add(mombasa)
        db.flush()
        
        likoni = SubCounty(name="Likoni", county_id=mombasa.id)
        kisauni = SubCounty(name="Kisauni", county_id=mombasa.id)
        changamwe = SubCounty(name="Changamwe", county_id=mombasa.id)
        nyali = SubCounty(name="Nyali", county_id=mombasa.id)
        mvita = SubCounty(name="Mvita", county_id=mombasa.id)
        jomvu = SubCounty(name="Jomvu", county_id=mombasa.id)
        db.add_all([likoni, kisauni, changamwe, nyali, mvita, jomvu])
        db.flush()
        
        # ---- HOSPITAL: Mama Ngina Hospital ----
        mama_ngina = Hospital(
            slug="mama-ngina-hospital",
            name="Mama Ngina Hospital",
            license_number="MOH/MSA/2024/001",
            type="DISTRICT_HOSPITAL",
            status="APPROVED",
            county_id=mombasa.id,
            sub_county_id=likoni.id,
            physical_address="Next to Ferry Terminal, Likoni, Mombasa",
            latitude=-4.0845,
            longitude=39.6672,
            phone="+254 712 345 678",
            email="admin@mamanginahealth.go.ke",
            director_name="Dr. Hassan Mohamed",
            director_email="director@mamanginahealth.go.ke",
            director_phone="+254 722 000 001",
            performance_score=72,
        )
        db.add(mama_ngina)
        db.flush()
        
        # Buildings
        outpatient = Building(name="Outpatient Block", hospital_id=mama_ngina.id, floors=2)
        maternity = Building(name="Maternity Wing", hospital_id=mama_ngina.id, floors=1)
        inpatient = Building(name="Inpatient Block", hospital_id=mama_ngina.id, floors=3)
        admin_block = Building(name="Administration Block", hospital_id=mama_ngina.id, floors=1)
        db.add_all([outpatient, maternity, inpatient, admin_block])
        db.flush()
        
        # Wards
        wards_data = [
            ("General Ward A", "GENERAL", 25, 18, inpatient.id),
            ("General Ward B", "GENERAL", 20, 15, inpatient.id),
            ("Maternity Ward", "MATERNITY", 25, 22, maternity.id),
            ("Paediatric Ward", "PAEDIATRIC", 20, 14, inpatient.id),
            ("ICU", "ICU", 8, 6, inpatient.id),
            ("Isolation Ward", "ISOLATION", 10, 3, inpatient.id),
            ("Private Wing", "PRIVATE", 12, 8, inpatient.id),
        ]
        for name, wtype, total, occupied, bid in wards_data:
            ward = HospitalWard(
                name=name, type=wtype, total_beds=total, occupied_beds=occupied,
                building_id=bid, hospital_id=mama_ngina.id
            )
            db.add(ward)
        db.flush()
        
        # Amenities
        amenities_list = [
            "Operating Theatre", "Laboratory", "Pharmacy", "X-Ray",
            "Ultrasound", "Ambulance Bay", "Blood Bank", "Mortuary"
        ]
        for a in amenities_list:
            db.add(Amenity(name=a, hospital_id=mama_ngina.id))
        db.flush()
        
        # ---- USERS (All Hospital Roles) ----
        # Passwords are: password123 for everyone
        default_password = hash_password("password123")
        
        users_data = [
            # (email, full_name, role, hospital_id)
            ("director@mamanginahealth.go.ke", "Dr. Hassan Mohamed", "HOSPITAL_DIRECTOR", mama_ngina.id),
            ("wanjiku@mamanginahealth.go.ke", "Dr. Wanjiku Muthoka", "DOCTOR", mama_ngina.id),
            ("otieno@mamanginahealth.go.ke", "Dr. Otieno Omondi", "DOCTOR", mama_ngina.id),
            ("amina@mamanginahealth.go.ke", "Nurse Amina Bakari", "NURSE", mama_ngina.id),
            ("zawadi@mamanginahealth.go.ke", "Nurse Zawadi Juma", "NURSE", mama_ngina.id),
            ("john@mamanginahealth.go.ke", "John Mwakio", "PHARMACIST", mama_ngina.id),
            ("mary@mamanginahealth.go.ke", "Mary Akinyi", "RECEPTIONIST", mama_ngina.id),
            ("ali@mamanginahealth.go.ke", "Ali Hassan", "AMBULANCE_DRIVER", mama_ngina.id),
        ]
        
        for email, name, role, hid in users_data:
            user = User(
                email=email,
                hashed_password=default_password,
                full_name=name,
                role=role,
                hospital_id=hid,
                is_active=True,
            )
            db.add(user)
        db.flush()
        
        # ---- COUNTY DIRECTOR USER ----
        county_director = User(
            email="director@mombasahealth.go.ke",
            hashed_password=hash_password("password123"),
            full_name="Dr. Salim Omar",
            role="COUNTY_DIRECTOR",
            county_id=mombasa.id,
            is_active=True,
        )
        db.add(county_director)
        db.flush()
        
        # ---- STAFF RECORDS ----
        staff_data = [
            ("Dr. Hassan Mohamed", "DIRECTOR", "Hospital Administration"),
            ("Dr. Wanjiku Muthoka", "DOCTOR", "General Practitioner"),
            ("Dr. Otieno Omondi", "DOCTOR", "Paediatrician"),
            ("Nurse Amina Bakari", "NURSE", "Head Nurse"),
            ("Nurse Zawadi Juma", "NURSE", "General Nursing"),
            ("John Mwakio", "PHARMACIST", "Pharmacy Management"),
            ("Mary Akinyi", "RECEPTIONIST", "Patient Registration"),
            ("Ali Hassan", "AMBULANCE_DRIVER", "Emergency Transport"),
        ]
        for name, role, spec in staff_data:
            db.add(Staff(
                hospital_id=mama_ngina.id,
                full_name=name,
                role=role,
                specialization=spec,
                is_active=True,
                phone="+254 722 000 000",
                email=f"{name.lower().replace(' ', '.').replace('dr.', '')}@mamanginahealth.go.ke",
            ))
        db.flush()
        
        # ---- INVENTORY CATEGORIES ----
        categories = [
            ("MEDICINE", "Medicines"),
            ("BEDDING", "Bedding & Linen"),
            ("LAB_SUPPLIES", "Laboratory Supplies"),
            ("SURGICAL", "Surgical Equipment"),
            ("PPE", "Personal Protective Equipment"),
        ]
        for name, display in categories:
            db.add(InventoryCategory(name=name, display_name=display))
        db.flush()
        
        med_cat = db.query(InventoryCategory).filter(InventoryCategory.name == "MEDICINE").first()
        bedding_cat = db.query(InventoryCategory).filter(InventoryCategory.name == "BEDDING").first()
        lab_cat = db.query(InventoryCategory).filter(InventoryCategory.name == "LAB_SUPPLIES").first()
        surgical_cat = db.query(InventoryCategory).filter(InventoryCategory.name == "SURGICAL").first()
        ppe_cat = db.query(InventoryCategory).filter(InventoryCategory.name == "PPE").first()
        
        # ---- SUPPLIERS ----
        suppliers_data = [
            ("KEMSA", "+254 20 123 4567", "orders@kemsa.go.ke", "General medicines, vaccines, PPE"),
            ("MedSource Kenya Ltd", "+254 711 987 654", "orders@medsource.co.ke", "Surgical equipment, lab reagents"),
            ("PharmaCare Distributors", "+254 722 333 444", "sales@pharmacare.co.ke", "Specialty medicines, cold chain"),
        ]
        for name, phone, email, supplies in suppliers_data:
            db.add(Supplier(
                hospital_id=mama_ngina.id,
                name=name,
                contact_person="Supply Manager",
                phone=phone,
                email=email,
                supplies_description=supplies,
                is_active=True,
            ))
        db.flush()
        
        # ---- MEDICINES ----
        medicines_data = [
            # (name, generic, unit, stock, min_thresh, crit_thresh, daily_use, price, category, supplier_idx)
            ("Paediatric Amoxicillin Suspension", "Amoxicillin", "bottle", 12, 50, 20, 15, 250, med_cat, 0),
            ("ACT (Artemether-Lumefantrine)", "Artemether", "dose", 144, 100, 50, 12, 120, med_cat, 0),
            ("Paracetamol 500mg", "Paracetamol", "tablet", 2500, 500, 200, 55, 5, med_cat, 0),
            ("ORS Sachets", "Oral Rehydration Salts", "sachet", 200, 100, 50, 25, 15, med_cat, 0),
            ("Insulin Regular", "Insulin", "vial", 15, 30, 10, 5, 450, med_cat, 2),
            ("Coartem 80/480", "Artemether/Lumefantrine", "tablet", 340, 200, 100, 18, 180, med_cat, 0),
            ("Metformin 500mg", "Metformin", "tablet", 890, 300, 150, 22, 8, med_cat, 0),
            ("Oxytocin 10IU", "Oxytocin", "vial", 45, 30, 15, 3, 120, med_cat, 2),
            ("BCG Vaccine", "BCG", "vial", 120, 50, 20, 8, 0, med_cat, 0),
            ("Surgical Gloves (Sterile)", "Latex Gloves", "pair", 1200, 300, 150, 40, 25, ppe_cat, 1),
            ("Surgical Masks", "Face Mask", "piece", 3000, 500, 200, 60, 3, ppe_cat, 1),
            ("Syringes 5ml", "Syringe", "piece", 500, 200, 100, 30, 10, lab_cat, 1),
            ("Blood Culture Bottles", "Culture Bottle", "piece", 40, 30, 15, 5, 350, lab_cat, 1),
            ("MRDT Kits", "Malaria RDT", "kit", 85, 60, 30, 12, 80, lab_cat, 0),
            ("Surgical Sutures", "Suture Kit", "pack", 200, 100, 50, 8, 150, surgical_cat, 1),
            ("Bed Sheets (Cotton)", "Bed Sheet", "piece", 180, 100, 60, 4, 400, bedding_cat, 0),
            ("Patient Gowns", "Hospital Gown", "piece", 200, 100, 50, 5, 350, bedding_cat, 0),
            ("Mosquito Nets (Treated)", "Mosquito Net", "piece", 45, 80, 40, 3, 200, bedding_cat, 0),
            ("Blankets (Fleece)", "Blanket", "piece", 95, 80, 40, 2, 550, bedding_cat, 0),
        ]
        
        for med in medicines_data:
            name, generic, unit, stock, min_t, crit_t, daily, price, cat, supp_idx = med
            db.add(Medicine(
                hospital_id=mama_ngina.id,
                category_id=cat.id,
                name=name,
                generic_name=generic,
                unit=unit,
                current_stock=stock,
                minimum_threshold=min_t,
                critical_threshold=crit_t,
                daily_usage_rate=daily,
                unit_price=price,
                supplier_id=None,  # Will be set if needed
                last_restock_date="2026-07-15",
            ))
        db.flush()
        
        # ---- PATIENTS ----
        patients_data = [
            ("Fatuma Juma", 34, "Female", "+254 712 345 678", "NHIF/2024/987654", "Kibarani, Mombasa",
             "Fever, severe headache, vomiting since yesterday", "Malaria confirmed positive via MRDT", "ADMITTED"),
            ("Hassan Ali", 45, "Male", "+254 722 111 222", "NHIF/2023/456789", "Likoni, Mombasa",
             "Diabetes follow-up, blood sugar fluctuations", "Type 2 Diabetes - routine checkup", "DISCHARGED"),
            ("Amina Bakari", 28, "Female", "+254 733 333 444", "NHIF/2025/123456", "Kisauni, Mombasa",
             "Antenatal visit, 32 weeks pregnant", "Normal pregnancy progression", "WITH_DOCTOR"),
            ("Baby Mwende", 1, "Female", "+254 711 999 888", "NHIF/2026/555555", "Changamwe, Mombasa",
             "Cough, difficulty breathing, fever", "Pneumonia suspected", "ADMITTED"),
            ("Joseph Otieno", 62, "Male", "+254 720 444 555", "NHIF/2022/111222", "Nyali, Mombasa",
             "Chest pain, shortness of breath", "Hypertension with cardiac concerns", "WITH_DOCTOR"),
        ]
        
        for name, age, gender, phone, nhif, address, symptoms, diagnosis, status in patients_data:
            patient = Patient(
                hospital_id=mama_ngina.id,
                full_name=name,
                age=age,
                gender=gender,
                phone=phone,
                nhif_number=nhif,
                address=address,
                visit_type="OUTPATIENT" if status == "DISCHARGED" else "INPATIENT",
                status=status,
                blood_pressure="120/80",
                pulse=72 + age % 20,
                temperature=36.5 + (0.5 if "fever" in symptoms.lower() or "homa" in symptoms.lower() else 0),
                spo2=97,
                registered_by=None,
            )
            db.add(patient)
            db.flush()
            
            # Add diagnosis record
            db.add(Diagnosis(
                patient_id=patient.id,
                hospital_id=mama_ngina.id,
                symptoms_text=symptoms,
                symptoms_language="sw" if "homa" in symptoms.lower() else "en",
                ai_diagnosis=[{"disease": "Malaria", "confidence": 0.78}] if "malaria" in diagnosis.lower() else [],
                ai_triage_level="URGENT" if "fever" in symptoms.lower() else "ROUTINE",
                final_diagnosis=diagnosis,
                confirmed=True,
            ))
        
        db.commit()
        
        # ---- PRINT SUMMARY ----
        logger.info("=" * 60)
        logger.info("DEMO DATA SEEDED SUCCESSFULLY")
        logger.info("=" * 60)
        logger.info(f"County: Mombasa (MSA)")
        logger.info(f"Hospital: Mama Ngina Hospital (mama-ngina-hospital)")
        logger.info(f"  - Status: APPROVED")
        logger.info(f"  - Beds: 120 total, 86 occupied")
        logger.info(f"  - Medicines: {len(medicines_data)} items")
        logger.info(f"  - Suppliers: {len(suppliers_data)}")
        logger.info(f"  - Patients: {len(patients_data)}")
        logger.info(f"")
        logger.info("USER ACCOUNTS (all passwords: password123)")
        logger.info("-" * 40)
        for email, name, role, hid in users_data:
            logger.info(f"  {role:20s} | {email:45s} | {name}")
        logger.info(f"  {'COUNTY_DIRECTOR':20s} | {'director@mombasahealth.go.ke':45s} | Dr. Salim Omar")
        logger.info("")
        logger.info("LOGIN FLOW:")
        logger.info("  1. Hospital Staff: http://localhost:3000/login")
        logger.info("     - Select 'Mama Ngina Hospital'")
        logger.info("     - Use any email above + password: password123")
        logger.info("  2. County Director: http://localhost:3000/county-login")
        logger.info("     - County: Mombasa")
        logger.info("     - Email: director@mombasahealth.go.ke")
        logger.info("     - Password: password123")
        logger.info("=" * 60)


if __name__ == "__main__":
    clear_and_seed()
