from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_, func
from sqlalchemy.orm import Session
from ..schemas import CourseOut, CourseCreate
from ..models import Course, UserProfile, Subscription, CourseMeta
from ..deps import get_db, get_current_user

router = APIRouter()


@router.get("/courses/", response_model=list[CourseOut])
def list_courses(user: UserProfile = Depends(get_current_user), db: Session = Depends(get_db)):
    active = db.query(Subscription).filter(
        Subscription.user_id == user.id,
        Subscription.status == "active",
        Subscription.end_date >= func.now(),
    ).first()
    q = db.query(Course).filter(Course.status == "published")
    if not active:
        q = (
            q.outerjoin(CourseMeta, CourseMeta.course_id == Course.id)
            .filter(or_(CourseMeta.is_premium == False, CourseMeta.id == None))
        )
    return q.all()


@router.get("/courses/{course_id}", response_model=CourseOut)
def course_detail(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.post("/instructor/courses/", response_model=CourseOut)
def create_course(payload: CourseCreate, user: UserProfile = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != "instructor":
        raise PermissionError("Only instructors can create courses")
    course = Course(title=payload.title, description=payload.description, status=payload.status, instructor_id=user.id)
    db.add(course)
    db.commit()
    db.refresh(course)
    return course
