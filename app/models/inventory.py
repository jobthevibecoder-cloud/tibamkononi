import uuid
from decimal import Decimal
from sqlalchemy import String, Integer, Float, Boolean, Text, Date, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel

class InventoryCategory(BaseModel):
    __tablename__ = "inventory_categories"

    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=True)

    medicines: Mapped[list["Medicine"]] = relationship(back_populates="category", lazy="selectin")


class Medicine(BaseModel):
    __tablename__ = "medicines"

    hospital_id: Mapped[str] = mapped_column(String(36), ForeignKey("hospitals.id"), nullable=False)
    category_id: Mapped[str] = mapped_column(String(36), ForeignKey("inventory_categories.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    generic_name: Mapped[str] = mapped_column(String(200), nullable=True)
    unit: Mapped[str] = mapped_column(String(20), nullable=False, default="tablet")
    current_stock: Mapped[float] = mapped_column(Float, default=0)
    minimum_threshold: Mapped[float] = mapped_column(Float, nullable=True)
    critical_threshold: Mapped[float] = mapped_column(Float, nullable=True)
    daily_usage_rate: Mapped[float] = mapped_column(Float, default=0)
    unit_price: Mapped[float] = mapped_column(Float, nullable=True)
    supplier_id: Mapped[str] = mapped_column(String(36), ForeignKey("suppliers.id"), nullable=True)
    last_restock_date: Mapped[str] = mapped_column(String(20), nullable=True)
    last_restock_quantity: Mapped[float] = mapped_column(Float, nullable=True)
    expiry_date: Mapped[str] = mapped_column(String(20), nullable=True)

    category: Mapped["InventoryCategory"] = relationship(back_populates="medicines")
    supplier: Mapped["Supplier"] = relationship(back_populates="medicines")
    stock_movements: Mapped[list["StockMovement"]] = relationship(back_populates="medicine", lazy="selectin")


class StockMovement(BaseModel):
    __tablename__ = "stock_movements"

    medicine_id: Mapped[str] = mapped_column(String(36), ForeignKey("medicines.id"), nullable=False)
    hospital_id: Mapped[str] = mapped_column(String(36), ForeignKey("hospitals.id"), nullable=False)
    movement_type: Mapped[str] = mapped_column(String(20), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    previous_stock: Mapped[float] = mapped_column(Float, nullable=True)
    new_stock: Mapped[float] = mapped_column(Float, nullable=True)
    patient_id: Mapped[str] = mapped_column(String(36), ForeignKey("patients.id"), nullable=True)
    prescription_id: Mapped[str] = mapped_column(String(36), ForeignKey("prescriptions.id"), nullable=True)
    from_hospital_id: Mapped[str] = mapped_column(String(36), ForeignKey("hospitals.id"), nullable=True)
    to_hospital_id: Mapped[str] = mapped_column(String(36), ForeignKey("hospitals.id"), nullable=True)
    performed_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)

    medicine: Mapped["Medicine"] = relationship(back_populates="stock_movements")
