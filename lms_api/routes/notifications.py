from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models import Notification, UserProfile
from ..schemas import PaymentOut
from ..deps import get_db, get_current_user

router = APIRouter()


@router.get("/notifications/")
def list_notifications(user: UserProfile = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Notification).filter(Notification.user_id == user.id).order_by(Notification.created_at.desc()).all()


@router.post("/notifications/mark-read/")
def mark_read(notification_id: int, user: UserProfile = Depends(get_current_user), db: Session = Depends(get_db)):
    notif = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == user.id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.is_read = True
    db.commit()
    return {"status": "ok"}


@router.get("/notifications/{user_id}/")
def list_user_notifications(user_id: int, user: UserProfile = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != "instructor" and user.id != user_id:
        raise HTTPException(status_code=403, detail="Not permitted")
    return db.query(Notification).filter(Notification.user_id == user_id).order_by(Notification.created_at.desc()).all()
