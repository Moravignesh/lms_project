from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..schemas import PaymentOut
from ..models import Payment, UserProfile
from ..deps import get_db, get_current_user

router = APIRouter()


@router.get("/payments/", response_model=list[PaymentOut])
def list_payments(user: UserProfile = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Payment).filter(Payment.user_id == user.id).order_by(Payment.payment_date.desc()).all()
