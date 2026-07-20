from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.services.inventory_service import get_inventory, get_stock_forecast, update_stock

router = APIRouter()


class StockUpdateRequest(BaseModel):
    quantity_change: float
    movement_type: str = "RESTOCK"
    notes: Optional[str] = None


@router.get("/{hospital_slug}/inventory")
async def view_inventory(
    hospital_slug: str,
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """View hospital inventory."""
    try:
        items = get_inventory(db, hospital_slug, category, status)
        critical = sum(1 for i in items if i["status"] == "critical")
        warnings = sum(1 for i in items if i["status"] == "warning")
        return {
            "items": items,
            "total": len(items),
            "critical": critical,
            "warnings": warnings,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{hospital_slug}/inventory/forecast")
async def inventory_forecast(hospital_slug: str, db: Session = Depends(get_db)):
    """Get AI stock forecasts."""
    try:
        forecast = get_stock_forecast(db, hospital_slug)
        return forecast
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{hospital_slug}/inventory/{medicine_id}/update")
async def update_medicine_stock(
    hospital_slug: str,
    medicine_id: str,
    request: StockUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update medicine stock level."""
    try:
        result = update_stock(
            db, medicine_id, request.quantity_change,
            request.movement_type, request.notes or ""
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
