import uuid
from sqlalchemy import String, Integer, Float, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class Hospital(BaseModel):
    __tablename__ = "hospitals"

    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    license_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="PENDING", index=True)

    county_id: Mapped[str] = mapped_column(String(36), ForeignKey("counties.id"), nullable=True)
    sub_county_id: Mapped[str] = mapped_column(String(36), ForeignKey("sub_counties.id"), nullable=True)
    ward_id: Mapped[str] = mapped_column(String(36), ForeignKey("wards.id"), nullable=True)

    physical_address: Mapped[str] = mapped_column(Text, nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)

    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    email: Mapped[str] = mapped_column(String(255), nullable=True)
    website: Mapped[str] = mapped_column(String(255), nullable=True)

    director_name: Mapped[str] = mapped_column(String(200), nullable=True)
    director_email: Mapped[str] = mapped_column(String(255), nullable=True)
    director_phone: Mapped[str] = mapped_column(String(20), nullable=True)

    approved_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[str] = mapped_column(nullable=True)
    rejection_reason: Mapped[str] = mapped_column(Text, nullable=True)

    performance_score: Mapped[int] = mapped_column(Integer, default=0)
    last_report_at: Mapped[str] = mapped_column(nullable=True)

    county: Mapped["County"] = relationship(back_populates="hospitals", foreign_keys=[county_id])
    buildings: Mapped[list["Building"]] = relationship(back_populates="hospital", lazy="selectin", cascade="all, delete-orphan", foreign_keys="Building.hospital_id")
    amenities: Mapped[list["Amenity"]] = relationship(back_populates="hospital", lazy="selectin", cascade="all, delete-orphan", foreign_keys="Amenity.hospital_id")


class Building(BaseModel):
    __tablename__ = "buildings"

    hospital_id: Mapped[str] = mapped_column(String(36), ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    floors: Mapped[int] = mapped_column(Integer, default=1)

    hospital: Mapped["Hospital"] = relationship(back_populates="buildings", foreign_keys=[hospital_id])
    wards: Mapped[list["HospitalWard"]] = relationship(back_populates="building", lazy="selectin", cascade="all, delete-orphan", foreign_keys="HospitalWard.building_id")


class HospitalWard(BaseModel):
    __tablename__ = "hospital_wards"

    building_id: Mapped[str] = mapped_column(String(36), ForeignKey("buildings.id", ondelete="CASCADE"), nullable=False)
    hospital_id: Mapped[str] = mapped_column(String(36), ForeignKey("hospitals.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[str] = mapped_column(String(30), nullable=False)
    total_beds: Mapped[int] = mapped_column(Integer, default=0)
    occupied_beds: Mapped[int] = mapped_column(Integer, default=0)

    building: Mapped["Building"] = relationship(back_populates="wards", foreign_keys=[building_id])
    beds: Mapped[list["Bed"]] = relationship(back_populates="ward", lazy="selectin", cascade="all, delete-orphan", foreign_keys="Bed.ward_id")


class Bed(BaseModel):
    __tablename__ = "beds"

    ward_id: Mapped[str] = mapped_column(String(36), ForeignKey("hospital_wards.id", ondelete="CASCADE"), nullable=False)
    hospital_id: Mapped[str] = mapped_column(String(36), ForeignKey("hospitals.id"), nullable=False)
    bed_number: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="AVAILABLE")
    current_patient_id: Mapped[str] = mapped_column(String(36), ForeignKey("patients.id"), nullable=True)
    occupied_since: Mapped[str] = mapped_column(nullable=True)

    ward: Mapped["HospitalWard"] = relationship(back_populates="beds", foreign_keys=[ward_id])


class Amenity(BaseModel):
    __tablename__ = "amenities"

    hospital_id: Mapped[str] = mapped_column(String(36), ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1)

    hospital: Mapped["Hospital"] = relationship(back_populates="amenities", foreign_keys=[hospital_id])
