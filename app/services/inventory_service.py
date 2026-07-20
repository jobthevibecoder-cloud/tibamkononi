"""Inventory management business logic."""
from sqlalchemy.orm import Session
from app.models.inventory import Medicine, StockMovement, InventoryCategory
from app.models.hospital import Hospital
from app.ai.services import forecast_stock
from loguru import logger


def get_inventory(db: Session, hospital_slug: str, category: str = None, status: str = None) -> list:
    """Get hospital inventory with optional filters."""
    hospital = db.query(Hospital).filter(Hospital.slug == hospital_slug).first()
    if not hospital:
        return []
    
    query = db.query(Medicine).filter(Medicine.hospital_id == hospital.id)
    
    if category:
        cat = db.query(InventoryCategory).filter(InventoryCategory.name == category).first()
        if cat:
            query = query.filter(Medicine.category_id == cat.id)
    
    medicines = query.all()
    
    results = []
    for m in medicines:
        days_left = int(m.current_stock / m.daily_usage_rate) if m.daily_usage_rate > 0 else 999
        
        if m.current_stock <= (m.critical_threshold or 0):
            stock_status = "critical"
        elif m.current_stock <= (m.minimum_threshold or 0):
            stock_status = "warning"
        else:
            stock_status = "ok"
        
        # Filter by status if requested
        if status and stock_status != status:
            continue
        
        results.append({
            "id": m.id,
            "name": m.name,
            "generic_name": m.generic_name,
            "unit": m.unit,
            "current_stock": m.current_stock,
            "minimum_threshold": m.minimum_threshold,
            "critical_threshold": m.critical_threshold,
            "daily_usage_rate": m.daily_usage_rate,
            "days_left": days_left,
            "status": stock_status,
            "unit_price": m.unit_price,
            "last_restock_date": m.last_restock_date,
            "expiry_date": m.expiry_date,
        })
    
    return results


def get_stock_forecast(db: Session, hospital_slug: str) -> dict:
    """Get AI stock forecasts for all medicines."""
    hospital = db.query(Hospital).filter(Hospital.slug == hospital_slug).first()
    if not hospital:
        return {}
    
    medicines = db.query(Medicine).filter(Medicine.hospital_id == hospital.id).all()
    
    forecasts = []
    for m in medicines:
        if m.current_stock <= (m.minimum_threshold or m.current_stock + 1):
            ai_forecast = forecast_stock(
                medicine_name=m.name,
                current_stock=m.current_stock,
                daily_rate=m.daily_usage_rate,
                threshold=m.minimum_threshold or 0,
                unit=m.unit,
                last_restock=m.last_restock_date or "Unknown",
                nearby_hospitals="[]",
            )
            forecasts.append({
                "medicine": m.name,
                "current_stock": m.current_stock,
                "days_until_stockout": ai_forecast.get("days_until_stockout", "Unknown"),
                "severity": ai_forecast.get("severity", "OK"),
                "recommendation": ai_forecast.get("recommended_action"),
            })
    
    return {"hospital": hospital.name, "forecasts": forecasts, "alerts": len(forecasts)}


def update_stock(db: Session, medicine_id: str, quantity_change: float, 
                 movement_type: str = "RESTOCK", notes: str = "") -> dict:
    """Update medicine stock level."""
    medicine = db.query(Medicine).filter(Medicine.id == medicine_id).first()
    if not medicine:
        raise ValueError("Medicine not found")
    
    previous = medicine.current_stock
    medicine.current_stock += quantity_change
    
    movement = StockMovement(
        medicine_id=medicine_id,
        hospital_id=medicine.hospital_id,
        movement_type=movement_type,
        quantity=abs(quantity_change),
        previous_stock=previous,
        new_stock=medicine.current_stock,
        notes=notes,
    )
    db.add(movement)
    db.flush()
    
    logger.info(f"Stock updated: {medicine.name} {movement_type} {quantity_change} (now: {medicine.current_stock})")
    
    return {
        "medicine": medicine.name,
        "previous_stock": previous,
        "new_stock": medicine.current_stock,
        "change": quantity_change,
        "movement_type": movement_type,
    }
