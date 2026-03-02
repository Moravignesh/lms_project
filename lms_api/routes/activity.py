from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..deps import get_db, get_current_user
from ..models import ActivityLog, UserProfile

router = APIRouter()


@router.post("/activity/")
def log_activity(action_type: str, action_detail: str = "", user: UserProfile = Depends(get_current_user), db: Session = Depends(get_db)):
    log = ActivityLog(user_id=user.id, action_type=action_type, action_detail=action_detail)
    db.add(log)
    db.commit()
    return {"status": "logged"}
