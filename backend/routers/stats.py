from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import schemas
import crud
from database import get_db

router = APIRouter(prefix="/api/stats", tags=["资产看板"])


@router.get("/dashboard", response_model=schemas.DashboardStats)
def get_dashboard(db: Session = Depends(get_db)):
    return crud.get_dashboard_stats(db)
