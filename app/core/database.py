from sqlalchemy import create_engine
from sqlalchemy.orm import Session, DeclarativeBase
from app.config import settings

DATABASE_URL = "sqlite:///./tiba_mkononi.db"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dependency injection for database sessions."""
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


def init_db():
    """Create all tables for development."""
    from app.models import (
        County, SubCounty, Ward,
        Hospital, Building, HospitalWard, Bed, Amenity,
        Supplier, InventoryCategory, Medicine, StockMovement,
        Patient, Diagnosis, Prescription,
        Staff, Attendance, Appointment,
        Emergency, TriageLog, DistressSignal,
        Announcement, Report, User
    )
    Base.metadata.create_all(bind=engine)
    print("All database tables created successfully.")


def close_db():
    """Dispose engine."""
    engine.dispose()
