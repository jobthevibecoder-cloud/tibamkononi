"""Auto-seed database on first run."""
from app.core.database import engine, init_db
from app.core.database import Session
from app.models.county import County, SubCounty, Ward
from app.models.hospital import Hospital, Building, HospitalWard, Amenity
from app.models.staff import Staff
from app.models.inventory import InventoryCategory, Medicine
from app.models.supplier import Supplier
from loguru import logger


def seed_if_empty():
    """Seed database if no data exists."""
    init_db()
    
    with Session(engine) as db:
        existing = db.query(County).filter(County.code == "MSA").first()
        if existing:
            logger.info("Database already seeded")
            return
        
        logger.info("Seeding database...")
        
        mombasa = County(name="Mombasa", code="MSA", capital="Mombasa City")
        db.add(mombasa)
        db.flush()
        
        likoni = SubCounty(name="Likoni", county_id=mombasa.id)
        kisauni = SubCounty(name="Kisauni", county_id=mombasa.id)
        changamwe = SubCounty(name="Changamwe", county_id=mombasa.id)
        db.add_all([likoni, kisauni, changamwe])
        db.flush()
        
        db.add_all([
            Ward(name="Likoni Central", sub_county_id=likoni.id),
            Ward(name="Shika Adabu", sub_county_id=likoni.id),
            Ward(name="Kisauni Central", sub_county_id=kisauni.id),
        ])
        db.flush()
        
        mama_ngina = Hospital(
            slug="mama-ngina-hospital",
            name="Mama Ngina Hospital",
            license_number="MOH/MSA/2024/001",
            type="DISTRICT_HOSPITAL",
            status="APPROVED",
            county_id=mombasa.id,
            sub_county_id=likoni.id,
            physical_address="Likoni, next to Ferry Terminal, Mombasa",
            latitude=-4.0845, longitude=39.6672,
            phone="+254 712 345 678",
            email="admin@mamanginahealth.go.ke",
            director_name="Dr. Hassan Mohamed",
            performance_score=72,
        )
        db.add(mama_ngina)
        db.flush()
        
        inpatient = Building(name="Inpatient Block", hospital_id=mama_ngina.id, floors=3)
        maternity = Building(name="Maternity Wing", hospital_id=mama_ngina.id, floors=1)
        db.add_all([inpatient, maternity])
        db.flush()
        
        db.add_all([
            HospitalWard(name="General Ward A", type="GENERAL", total_beds=25, occupied_beds=18, building_id=inpatient.id, hospital_id=mama_ngina.id),
            HospitalWard(name="Maternity Ward", type="MATERNITY", total_beds=25, occupied_beds=22, building_id=maternity.id, hospital_id=mama_ngina.id),
            HospitalWard(name="Paediatric Ward", type="PAEDIATRIC", total_beds=20, occupied_beds=14, building_id=inpatient.id, hospital_id=mama_ngina.id),
            HospitalWard(name="ICU", type="ICU", total_beds=8, occupied_beds=6, building_id=inpatient.id, hospital_id=mama_ngina.id),
        ])
        
        coast_gen = Hospital(
            slug="coast-general-hospital",
            name="Coast General Hospital",
            license_number="MOH/MSA/2020/005",
            type="DISTRICT_HOSPITAL",
            status="APPROVED",
            county_id=mombasa.id,
            sub_county_id=kisauni.id,
            physical_address="Kisauni Road, Mombasa",
            latitude=-4.0435, longitude=39.6745,
            director_name="Dr. Salim Omar",
            performance_score=89,
        )
        db.add(coast_gen)
        db.flush()
        
        likoni_phc = Hospital(
            slug="likoni-phc",
            name="Likoni PHC",
            license_number="MOH/MSA/2022/012",
            type="PHC",
            status="APPROVED",
            county_id=mombasa.id,
            sub_county_id=likoni.id,
            physical_address="Likoni Main Road, Mombasa",
            latitude=-4.0880, longitude=39.6650,
            director_name="Dr. Fatma Ali",
            performance_score=45,
        )
        db.add(likoni_phc)
        
        db.add_all([
            Staff(hospital_id=mama_ngina.id, full_name="Dr. Wanjiku Muthoka", role="DOCTOR", specialization="General Practitioner", is_active=True),
            Staff(hospital_id=mama_ngina.id, full_name="Dr. Otieno Omondi", role="DOCTOR", specialization="Paediatrician", is_active=True),
            Staff(hospital_id=mama_ngina.id, full_name="Nurse Amina Bakari", role="NURSE", specialization="Head Nurse", is_active=True),
            Staff(hospital_id=mama_ngina.id, full_name="John Mwakio", role="PHARMACIST", is_active=True),
            Staff(hospital_id=coast_gen.id, full_name="Dr. Abdi Hassan", role="DOCTOR", specialization="General Surgeon", is_active=True),
        ])
        
        db.add_all([
            InventoryCategory(name="MEDICINE", display_name="Medicines"),
            InventoryCategory(name="BEDDING", display_name="Bedding & Linen"),
            InventoryCategory(name="LAB_SUPPLIES", display_name="Laboratory Supplies"),
        ])
        db.flush()
        
        med_cat = db.query(InventoryCategory).filter(InventoryCategory.name == "MEDICINE").first()
        kemsa = Supplier(hospital_id=mama_ngina.id, name="KEMSA", phone="+254 20 123 4567", email="orders@kemsa.go.ke")
        db.add(kemsa)
        db.flush()
        
        db.add_all([
            Medicine(hospital_id=mama_ngina.id, category_id=med_cat.id, name="Paediatric Amoxicillin", generic_name="Amoxicillin", unit="bottle", current_stock=12, minimum_threshold=50, critical_threshold=20, daily_usage_rate=15, unit_price=250, supplier_id=kemsa.id),
            Medicine(hospital_id=mama_ngina.id, category_id=med_cat.id, name="ACT Malaria", generic_name="Artemether", unit="dose", current_stock=144, minimum_threshold=100, critical_threshold=50, daily_usage_rate=12, unit_price=120, supplier_id=kemsa.id),
            Medicine(hospital_id=mama_ngina.id, category_id=med_cat.id, name="Paracetamol 500mg", generic_name="Paracetamol", unit="tablet", current_stock=2500, minimum_threshold=500, critical_threshold=200, daily_usage_rate=55, unit_price=5, supplier_id=kemsa.id),
            Medicine(hospital_id=mama_ngina.id, category_id=med_cat.id, name="ORS Sachets", generic_name="Oral Rehydration Salts", unit="sachet", current_stock=200, minimum_threshold=100, critical_threshold=50, daily_usage_rate=25, unit_price=15, supplier_id=kemsa.id),
        ])
        
        db.commit()
        logger.info("Database seeded successfully with 3 hospitals, 5 staff, 4 medicines")


if __name__ == "__main__":
    seed_if_empty()
