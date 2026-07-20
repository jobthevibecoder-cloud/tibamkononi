import uuid
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class County(BaseModel):
    __tablename__ = "counties"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    capital: Mapped[str] = mapped_column(String(100), nullable=True)

    sub_counties: Mapped[list["SubCounty"]] = relationship(
        back_populates="county", 
        lazy="selectin",
        foreign_keys="SubCounty.county_id"
    )
    hospitals: Mapped[list["Hospital"]] = relationship(
        back_populates="county", 
        lazy="selectin",
        foreign_keys="Hospital.county_id"
    )


class SubCounty(BaseModel):
    __tablename__ = "sub_counties"

    county_id: Mapped[str] = mapped_column(String(36), ForeignKey("counties.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    county: Mapped["County"] = relationship(back_populates="sub_counties", foreign_keys=[county_id])
    wards: Mapped[list["Ward"]] = relationship(back_populates="sub_county", lazy="selectin", foreign_keys="Ward.sub_county_id")


class Ward(BaseModel):
    __tablename__ = "wards"

    sub_county_id: Mapped[str] = mapped_column(String(36), ForeignKey("sub_counties.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    sub_county: Mapped["SubCounty"] = relationship(back_populates="wards", foreign_keys=[sub_county_id])
