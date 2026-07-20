from fastapi import APIRouter
from app.api.v1 import hospitals, emergency, triage, auth, appointments, county, distress, inventory, staff, announcements

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(hospitals.router, prefix="/hospitals", tags=["Hospitals"])
api_router.include_router(emergency.router, prefix="/emergency", tags=["Emergency"])
api_router.include_router(triage.router, prefix="/triage", tags=["Triage"])
api_router.include_router(appointments.router, prefix="/appointments", tags=["Appointments"])
api_router.include_router(county.router, prefix="/county", tags=["County Director"])
api_router.include_router(distress.router, prefix="/hospitals", tags=["Distress Signals"])
api_router.include_router(inventory.router, prefix="/hospitals", tags=["Inventory"])
api_router.include_router(staff.router, prefix="/hospitals", tags=["Staff"])
api_router.include_router(announcements.router, prefix="/announcements", tags=["Announcements"])
