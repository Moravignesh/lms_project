from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..schemas import PlanOut
from ..models import Plan
from ..deps import get_db

router = APIRouter()


@router.get("/plans/", response_model=list[PlanOut])
def list_plans(db: Session = Depends(get_db)):
    return db.query(Plan).all()
