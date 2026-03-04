from pydantic import BaseModel, EmailStr
from typing import Optional, List


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    role: str
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class CourseOut(BaseModel):
    id: int
    title: str
    description: str
    instructor_id: int
    status: str

    class Config:
        from_attributes = True


class CourseCreate(BaseModel):
    title: str
    description: str
    status: str = "draft"


class EnrollmentRequest(BaseModel):
    course_id: int


class ProgressUpdate(BaseModel):
    enrollment_id: int
    completed_lessons: int
    progress_percent: float


class PlanOut(BaseModel):
    id: int
    name: str
    price: float
    duration_days: int

    class Config:
        from_attributes = True


class SubscribeRequest(BaseModel):
    plan_id: int


class PaymentOut(BaseModel):
    id: int
    plan_id: Optional[int]
    amount: float
    payment_date: str

    class Config:
        from_attributes = True


class AttendanceRecordInput(BaseModel):
    student_id: int
    status: str


class AttendanceMarkRequest(BaseModel):
    course_id: int
    date: str
    records: List[AttendanceRecordInput]


class AssignmentCreateResponse(BaseModel):
    id: int
    course_id: int
    title: str
    description: Optional[str]
    deadline: str
    file_url: Optional[str]

    class Config:
        from_attributes = True


class SubmissionResponse(BaseModel):
    id: int
    assignment_id: int
    student_id: int
    file_url: str
    submitted_at: str
    grade: Optional[float]
    remarks: Optional[str]

    class Config:
        from_attributes = True
