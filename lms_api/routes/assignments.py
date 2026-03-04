from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from datetime import datetime
import os
import uuid
from ..deps import get_db, get_current_user
from ..models import Assignment, Submission, Course, Enrollment, UserProfile, Notification
from ..schemas import AssignmentCreateResponse, SubmissionResponse

router = APIRouter()


def _save_upload(file: UploadFile, subdir: str) -> str:
    base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads", subdir)
    os.makedirs(base_dir, exist_ok=True)
    ext = os.path.splitext(file.filename)[1]
    name = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(base_dir, name)
    with open(path, "wb") as f:
        f.write(file.file.read())
    return f"/files/{subdir}/{name}"


@router.post("/assignments/create", response_model=AssignmentCreateResponse)
def create_assignment(
    course_id: int = Form(...),
    title: str = Form(...),
    description: str = Form(""),
    deadline: str = Form(...),
    file: UploadFile | None = File(None),
    user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user.role != "instructor":
        raise HTTPException(status_code=403, detail="Only instructors can create assignments")
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.instructor_id != user.id:
        raise HTTPException(status_code=403, detail="Only course instructor can create assignments")
    try:
        dl = datetime.strptime(deadline, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid deadline format, expected YYYY-MM-DD")
    url = None
    if file:
        url = _save_upload(file, "assignments")
    a = Assignment(course_id=course.id, title=title, description=description, deadline=dl, file_url=url, created_by=user.id)
    db.add(a)
    db.commit()
    db.refresh(a)
    db.add(Notification(user_id=user.id, message=f"New assignment created for course #{course.id}: {title}"))
    db.commit()
    return a


@router.post("/assignments/submit", response_model=SubmissionResponse)
def submit_assignment(
    assignment_id: int = Form(...),
    student_id: int = Form(...),
    file: UploadFile = File(...),
    user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    a = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Assignment not found")
    now = datetime.utcnow()
    if now > a.deadline:
        raise HTTPException(status_code=400, detail="Deadline passed")
    course = db.query(Course).filter(Course.id == a.course_id).first()
    enr = db.query(Enrollment).filter(Enrollment.user_id == student_id, Enrollment.course_id == course.id).first()
    if not enr:
        raise HTTPException(status_code=400, detail="Student not enrolled in course")
    existing = db.query(Submission).filter(Submission.assignment_id == a.id, Submission.student_id == student_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Submission already exists")
    url = _save_upload(file, "submissions")
    s = Submission(assignment_id=a.id, student_id=student_id, file_url=url, submitted_at=now)
    db.add(s)
    db.commit()
    db.refresh(s)
    db.add(Notification(user_id=a.created_by, message=f"New submission for assignment #{a.id} from student #{student_id}"))
    db.commit()
    return s


@router.put("/assignments/grade")
def grade_submission(
    submission_id: int,
    grade: float,
    remarks: str = "",
    user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user.role != "instructor":
        raise HTTPException(status_code=403, detail="Only instructors can grade")
    s = db.query(Submission).filter(Submission.id == submission_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Submission not found")
    a = db.query(Assignment).filter(Assignment.id == s.assignment_id).first()
    course = db.query(Course).filter(Course.id == a.course_id).first()
    if course.instructor_id != user.id:
        raise HTTPException(status_code=403, detail="Only course instructor can grade")
    s.grade = grade
    s.remarks = remarks
    db.commit()
    db.add(Notification(user_id=s.student_id, message=f"Assignment #{a.id} graded: {grade}"))
    db.commit()
    return {"status": "graded"}
