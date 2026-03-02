from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..schemas import SubscribeRequest
from ..models import Subscription, Payment, Plan, UserProfile, ActivityLog, Notification
from ..deps import get_db, get_current_user

router = APIRouter()


@router.post("/subscribe/")
def subscribe(payload: SubscribeRequest, user: UserProfile = Depends(get_current_user), db: Session = Depends(get_db)):
    plan = db.query(Plan).filter(Plan.id == payload.plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    start = datetime.utcnow()
    end = start + timedelta(days=int(plan.duration_days))
    sub = Subscription(user_id=user.id, plan_id=plan.id, start_date=start, end_date=end, status="active")
    db.add(sub)
    pay = Payment(user_id=user.id, plan_id=plan.id, amount=plan.price, payment_date=start)
    db.add(pay)
    db.commit()
    db.add(ActivityLog(user_id=user.id, action_type="subscribe", action_detail=f"plan_id={plan.id}"))
    db.add(Notification(user_id=user.id, message=f"Subscribed to {plan.name}"))
    db.commit()
    return {"status": "subscribed", "plan_id": plan.id}
