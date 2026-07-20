"""Seed the database with test data for Mombasa County."""
from app.core.database import Session, engine
from app.models.county import County, SubCounty, Ward
from app.models.hospital import Hospital, Building, HospitalWard, Bed, Amenity
from app.models.staff import Staff
from app.models.inventory import InventoryCategory, Medicine
from app.models.supplier import Supplier

def seed():
    with Session(engine) as db:
        # Check if data already exists
        existing = db.query(County).filter(County.code == "MSA").first()
        if existing:
            print("Test data already exists. Skipping seed.")
            return
        
        # ---- County ----
        mombasa = County(name="Mombasa", code="MSA", capital="Mombasa City")
        db.add(mombasa)
        db.flush()
        
        # Sub-counties
        likoni = SubCounty(name="Likoni", county_id=mombasa.id)
        kisauni = SubCounty(name="Kisauni", county_id=mombasa.id)
        changamwe = SubCounty(name="Changamwe", county_id=mombasa.id)
        db.add_all([likoni, kisauni, changamwe])
        db.flush()
        
        # Wards
        db.add_all([
            Ward(name="Likoni Central", sub_county_id=likoni.id),
            Ward(name="Shika Adabu", sub_county_id=likoni.id),
            Ward(name="Mtongwe", sub_county_id=likoni.id),
            Ward(name="Kisauni Central", sub_county_id=kisauni.id),
            Ward(name="Changamwe Central", sub_county_id=changamwe.id),
        ])
        db.flush()
        
        # ---- Mama Ngina Hospital ----
        mama_ngina = Hospital(
            slug="mama-ngina-hospital",
            name="Mama Ngina Hospital",
            license_number="MOH/MSA/2024/001",
            type="DISTRICT_HOSPITAL",
            status="APPROVED",
            county_id=mombasa.id,
            sub_county_id=likoni.id,
            physical_address="Likoni, next to Ferry Terminal, Mombasa",
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
        opd_block = Building(name="Outpatient Block", hospital_id=mama_ngina.id, floors=2)
        maternity = Building(name="Maternity Wing", hospital_id=mama_ngina.id, floors=1)
        inpatient = Building(name="Inpatient Block", hospital_id=mama_ngina.id, floors=3)
        db.add_all([opd_block, maternity, inpatient])
        db.flush()
        
        # Wards
        db.add_all([
            HospitalWard(name="General Ward A", type="GENERAL", total_beds=25, occupied_beds=18, building_id=inpatient.id, hospital_id=mama_ngina.id),
            HospitalWard(name="General Ward B", type="GENERAL", total_beds=20, occupied_beds=15, building_id=inpatient.id, hospital_id=mama_ngina.id),
            HospitalWard(name="Maternity Ward", type="MATERNITY", total_beds=25, occupied_beds=22, building_id=maternity.id, hospital_id=mama_ngina.id),
            HospitalWard(name="Paediatric Ward", type="PAEDIATRIC", total_beds=20, occupied_beds=14, building_id=inpatient.id, hospital_id=mama_ngina.id),
            HospitalWard(name="ICU", type="ICU", total_beds=8, occupied_beds=6, building_id=inpatient.id, hospital_id=mama_ngina.id),
            HospitalWard(name="Isolation Ward", type="ISOLATION", total_beds=10, occupied_beds=3, building_id=inpatient.id, hospital_id=mama_ngina.id),
        ])
        db.flush()
        
        # Amenities
        db.add_all([
            Amenity(name="Operating Theatre", quantity=2, hospital_id=mama_ngina.id),
            Amenity(name="Laboratory", quantity=1, hospital_id=mama_ngina.id),
            Amenity(name="Pharmacy", quantity=1, hospital_id=mama_ngina.id),
            Amenity(name="X-Ray", quantity=1, hospital_id=mama_ngina.id),
            Amenity(name="Ambulance Bay", quantity=1, hospital_id=mama_ngina.id),
        ])
        
        # ---- Coast General Hospital ----
        coast_gen = Hospital(
            slug="coast-general-hospital",
            name="Coast General Hospital",
            license_number="MOH/MSA/2020/005",
            type="DISTRICT_HOSPITAL",
            status="APPROVED",
            county_id=mombasa.id,
            sub_county_id=kisauni.id,
            physical_address="Kisauni Road, Mombasa",
            latitude=-4.0435,
            longitude=39.6745,
            phone="+254 720 123 456",
            email="info@coastgeneral.go.ke",
            director_name="Dr. Salim Omar",
            director_email="director@coastgeneral.go.ke",
            director_phone="+254 733 111 222",
            performance_score=89,
        )
        db.add(coast_gen)
        db.flush()
        
        # Likoni PHC
        likoni_phc = Hospital(
            slug="likoni-phc",
            name="Likoni PHC",
            license_number="MOH/MSA/2022/012",
            type="PHC",
            status="APPROVED",
            county_id=mombasa.id,
            sub_county_id=likoni.id,
            physical_address="Likoni Main Road, Mombasa",
            latitude=-4.0880,
            longitude=39.6650,
            phone="+254 711 987 654",
            email="info@likoniphc.go.ke",
            director_name="Dr. Fatma Ali",
            performance_score=45,
        )
        db.add(likoni_phc)
        
        # ---- Staff (Doctors) ----
        db.add_all([
            Staff(
                hospital_id=mama_ngina.id,
                full_name="Dr. Wanjiku Muthoka",
                role="DOCTOR",
                specialization="General Practitioner",
                phone="+254 722 111 001",
                email="wanjiku@mamanginahealth.go.ke",
                is_active=True,
            ),
            Staff(
                hospital_id=mama_ngina.id,
                full_name="Dr. Otieno Omondi",
                role="DOCTOR",
                specialization="Paediatrician",
                phone="+254 722 111 002",
                email="otieno@mamanginahealth.go.ke",
                is_active=True,
            ),
            Staff(
                hospital_id=mama_ngina.id,
                full_name="Nurse Amina Bakari",
                role="NURSE",
                specialization="Head Nurse",
                phone="+254 722 111 003",
                is_active=True,
            ),
            Staff(
                hospital_id=mama_ngina.id,
                full_name="John Mwakio",
                role="PHARMACIST",
                phone="+254 722 111 004",
                is_active=True,
            ),
            Staff(
                hospital_id=coast_gen.id,
                full_name="Dr. Abdi Hassan",
                role="DOCTOR",
                specialization="General Surgeon",
                phone="+254 733 222 001",
                is_active=True,
            ),
            Staff(
                hospital_id=coast_gen.id,
                full_name="Dr. Zainab Mwangi",
                role="DOCTOR",
                specialization="Obstetrician",
                phone="+254 733 222 002",
                is_active=True,
            ),
        ])
        
        # ---- Inventory Categories ----
        db.add_all([
            InventoryCategory(name="MEDICINE", display_name="Medicines"),
            InventoryCategory(name="BEDDING", display_name="Bedding & Linen"),
            InventoryCategory(name="LAB_SUPPLIES", display_name="Laboratory Supplies"),
            InventoryCategory(name="SURGICAL", display_name="Surgical Equipment"),
            InventoryCategory(name="PPE", display_name="Personal Protective Equipment"),
        ])
        db.flush()
        
        # ---- Suppliers ----
        kemsa = Supplier(
            hospital_id=mama_ngina.id,
            name="KEMSA",
            contact_person="Supply Manager",
            phone="+254 20 123 4567",
            email="orders@kemsa.go.ke",
            supplies_description="General medicines, vaccines, PPE",
        )
        db.add(kemsa)
        db.flush()
        
        # ---- Medicines ----
        med_cat = db.query(InventoryCategory).filter(InventoryCategory.name == "MEDICINE").first()
        db.add_all([
            Medicine(
                hospital_id=mama_ngina.id, category_id=med_cat.id,
                name="Paediatric Amoxicillin Suspension", generic_name="Amoxicillin",
                unit="bottle", current_stock=12, minimum_threshold=50, critical_threshold=20,
                daily_usage_rate=15, unit_price=250, supplier_id=kemsa.id,
                last_restock_date="2026-07-10",
            ),
            Medicine(
                hospital_id=mama_ngina.id, category_id=med_cat.id,
                name="ACT (Artemether-Lumefantrine)", generic_name="Artemether",
                unit="dose", current_stock=144, minimum_threshold=100, critical_threshold=50,
                daily_usage_rate=12, unit_price=120, supplier_id=kemsa.id,
                last_restock_date="2026-07-15",
            ),
            Medicine(
                hospital_id=mama_ngina.id, category_id=med_cat.id,
                name="Paracetamol 500mg", generic_name="Paracetamol",
                unit="tablet", current_stock=2500, minimum_threshold=500, critical_threshold=200,
                daily_usage_rate=55, unit_price=5, supplier_id=kemsa.id,
                last_restock_date="2026-07-01",
            ),
            Medicine(
                hospital_id=mama_ngina.id, category_id=med_cat.id,
                name="ORS Sachets", generic_name="Oral Rehydration Salts",
                unit="sachet", current_stock=200, minimum_threshold=100, critical_threshold=50,
                daily_usage_rate=25, unit_price=15, supplier_id=kemsa.id,
                last_restock_date="2026-07-20",
            ),
        ])
        
        db.commit()
        print("Test data seeded successfully!")
        print(f"  County: Mombasa (MSA)")
        print(f"  Hospitals: Mama Ngina, Coast General, Likoni PHC")
        print(f"  Doctors: 4")
        print(f"  Medicines: 4")

if __name__ == "__main__":
    seed()
