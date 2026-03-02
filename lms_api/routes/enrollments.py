from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..schemas import EnrollmentRequest, CourseOut
from ..models import Enrollment, Progress, Course, UserProfile, ActivityLog, Notification
from ..deps import get_db, get_current_user

router = APIRouter()


@router.post("/enroll/")
def enroll(payload: EnrollmentRequest, user: UserProfile = Depends(get_current_user), db: Session = Depends(get_db)):
    existing = db.query(Enrollment).filter(Enrollment.user_id == user.id, Enrollment.course_id == payload.course_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already enrolled")
    enrollment = Enrollment(user_id=user.id, course_id=payload.course_id, enrolled_on=db.bind.execute("SELECT NOW()").scalar())
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    prog = Progress(enrollment_id=enrollment.id, completed_lessons=0, progress_percent=0.0)
    db.add(prog)
    db.commit()
    db.add(ActivityLog(user_id=user.id, action_type="enroll", action_detail=f"course_id={payload.course_id}"))
    db.add(Notification(user_id=user.id, message=f"Enrolled in course #{payload.course_id}"))
    db.commit()
    return {"status": "enrolled"}


@router.get("/my-courses/", response_model=list[CourseOut])
def my_courses(user: UserProfile = Depends(get_current_user), db: Session = Depends(get_db)):
    q = (
        db.query(Course)
        .join(Enrollment, Enrollment.course_id == Course.id)
        .filter(Enrollment.user_id == user.id)
    )
    return q.all()
