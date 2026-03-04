from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, date as dt_date
from typing import List
from ..deps import get_db, get_current_user
from ..models import Attendance, Course, UserProfile, Notification
from ..schemas import AttendanceMarkRequest

router = APIRouter()


@router.post("/attendance/mark")
def mark_attendance(payload: AttendanceMarkRequest, user: UserProfile = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != "instructor":
        raise HTTPException(status_code=403, detail="Only instructors can mark attendance")
    course = db.query(Course).filter(Course.id == payload.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.instructor_id != user.id:
        raise HTTPException(status_code=403, detail="Only course instructor can mark attendance")
    try:
        d = datetime.strptime(payload.date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format, expected YYYY-MM-DD")
    for rec in payload.records:
        existing = (
            db.query(Attendance)
            .filter(Attendance.student_id == rec.student_id, Attendance.course_id == course.id, Attendance.date == d)
            .first()
        )
        if existing:
            raise HTTPException(status_code=400, detail=f"Duplicate attendance for student_id={rec.student_id} on {payload.date}")
        att = Attendance(student_id=rec.student_id, course_id=course.id, date=d, status=rec.status)
        db.add(att)
    db.add(Notification(user_id=user.id, message=f"Attendance marked for course #{course.id} on {payload.date}"))
    db.commit()
    return {"status": "marked", "count": len(payload.records)}


@router.get("/attendance/student/{student_id}")
def get_student_attendance(student_id: int, course_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(Attendance).filter(Attendance.student_id == student_id)
    if course_id:
        q = q.filter(Attendance.course_id == course_id)
    items = q.order_by(Attendance.date.desc()).all()
    total = len(items)
    present = sum(1 for r in items if r.status.lower() == "present")
    percent = (present / total * 100.0) if total > 0 else 0.0
    return {"total": total, "present": present, "percent": round(percent, 2), "records": [{"course_id": r.course_id, "date": r.date.isoformat(), "status": r.status} for r in items]}


@router.get("/attendance/course/{course_id}")
def get_course_attendance(
    course_id: int,
    from_date: str | None = Query(None, alias="from"),
    to: str | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(Attendance).filter(Attendance.course_id == course_id)
    if from_date:
        try:
            f = datetime.strptime(from_date, "%Y-%m-%d").date()
            q = q.filter(Attendance.date >= f)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid 'from' date")
    if to:
        try:
            t = datetime.strptime(to, "%Y-%m-%d").date()
            q = q.filter(Attendance.date <= t)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid 'to' date")
    items = q.order_by(Attendance.date.desc()).all()
    total = len(items)
    present = sum(1 for r in items if r.status.lower() == "present")
    percent = (present / total * 100.0) if total > 0 else 0.0
    return {"total": total, "present": present, "percent": round(percent, 2), "records": [{"student_id": r.student_id, "date": r.date.isoformat(), "status": r.status} for r in items]}
