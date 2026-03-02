from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Float, UniqueConstraint, Boolean, Numeric, Table
from sqlalchemy.orm import relationship
from .database import Base


class UserProfile(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    role = Column(String(20), nullable=False)
    password_hash = Column(String(255), nullable=False)

    courses = relationship("Course", back_populates="instructor")
    enrollments = relationship("Enrollment", back_populates="user")
    subscriptions = relationship("Subscription", back_populates="user")
    payments = relationship("Payment", back_populates="user")


class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    instructor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(20), nullable=False, default="draft")

    instructor = relationship("UserProfile", back_populates="courses")
    lessons = relationship("Lesson", back_populates="course", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="course")


class Lesson(Base):
    __tablename__ = "lessons"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=True)
    video_url = Column(String(500), nullable=True)

    course = relationship("Course", back_populates="lessons")


class Enrollment(Base):
    __tablename__ = "enrollments"
    __table_args__ = (UniqueConstraint("user_id", "course_id", name="uq_user_course"),)
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    enrolled_on = Column(DateTime, nullable=False)

    user = relationship("UserProfile", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")
    progress = relationship("Progress", back_populates="enrollment", uselist=False)


class Progress(Base):
    __tablename__ = "progress"
    id = Column(Integer, primary_key=True, index=True)
    enrollment_id = Column(Integer, ForeignKey("enrollments.id"), unique=True, nullable=False)
    completed_lessons = Column(Integer, nullable=False, default=0)
    progress_percent = Column(Float, nullable=False, default=0.0)

    enrollment = relationship("Enrollment", back_populates="progress")


class Plan(Base):
    __tablename__ = "plans"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    duration_days = Column(Integer, nullable=False)

    subscriptions = relationship("Subscription", back_populates="plan")
    payments = relationship("Payment", back_populates="plan")


class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=False, default="active")

    user = relationship("UserProfile", back_populates="subscriptions")
    plan = relationship("Plan", back_populates="subscriptions")


class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_date = Column(DateTime, nullable=False)

    user = relationship("UserProfile", back_populates="payments")
    plan = relationship("Plan", back_populates="payments")


class CourseMeta(Base):
    __tablename__ = "course_meta"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), unique=True, nullable=False)
    is_premium = Column(Boolean, nullable=False, default=False)
    price = Column(Numeric(10, 2), nullable=False, default=0.00)

    course = relationship("Course", backref="meta", uselist=False)


class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False)

    user = relationship("UserProfile")


class ActivityLog(Base):
    __tablename__ = "activity_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action_type = Column(String(50), nullable=False)
    action_detail = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False)

    user = relationship("UserProfile")


chat_room_members = Table(
    "chat_room_members",
    Base.metadata,
    Column("chatroom_id", Integer, ForeignKey("chat_rooms.id"), primary_key=True),
    Column("userprofile_id", Integer, ForeignKey("users.id"), primary_key=True),
)


class ChatRoom(Base):
    __tablename__ = "chat_rooms"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=True)
    is_group = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False)

    members = relationship("UserProfile", secondary=chat_room_members, backref="chat_rooms")
    messages = relationship("ChatMessage", back_populates="room", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("chat_rooms.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=True)
    file_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, nullable=False)

    room = relationship("ChatRoom", back_populates="messages")
    sender = relationship("UserProfile")


class UserStatus(Base):
    __tablename__ = "user_status"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    is_online = Column(Boolean, default=False)
    last_seen = Column(DateTime, nullable=False)

    user = relationship("UserProfile", backref="status")
