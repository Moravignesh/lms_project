from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..schemas import ProgressUpdate
from ..models import Progress, Enrollment, UserProfile, ActivityLog, Notification
from ..deps import get_db, get_current_user

router = APIRouter()


@router.post("/progress/update/")
def update_progress(payload: ProgressUpdate, user: UserProfile = Depends(get_current_user), db: Session = Depends(get_db)):
    enrollment = db.query(Enrollment).filter(Enrollment.id == payload.enrollment_id, Enrollment.user_id == user.id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    prog = db.query(Progress).filter(Progress.enrollment_id == enrollment.id).first()
    if not prog:
        prog = Progress(enrollment_id=enrollment.id, completed_lessons=payload.completed_lessons, progress_percent=payload.progress_percent)
        db.add(prog)
    else:
        prog.completed_lessons = payload.completed_lessons
        prog.progress_percent = payload.progress_percent
    db.commit()
    db.add(ActivityLog(user_id=user.id, action_type="progress_update", action_detail=f"enrollment_id={enrollment.id}"))
    db.add(Notification(user_id=user.id, message=f"Progress updated for enrollment #{enrollment.id}"))
    db.commit()
    return {"status": "updated"}


@router.get("/progress/view/")
def view_progress(user: UserProfile = Depends(get_current_user), db: Session = Depends(get_db)):
    q = (
        db.query(Progress)
        .join(Enrollment, Enrollment.id == Progress.enrollment_id)
        .filter(Enrollment.user_id == user.id)
    )
    return [
        {
            "enrollment_id": p.enrollment_id,
            "completed_lessons": p.completed_lessons,
            "progress_percent": p.progress_percent,
        }
        for p in q.all()
    ]
