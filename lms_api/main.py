import uvicorn
from fastapi import FastAPI
from .database import Base, engine
from .routes import users, courses, enrollments, progress, plans, subscriptions, payments, notifications, activity, chat, attendance, assignments, auth_google, auth_facebook, auth_github, auth_otp

try:
    if engine.url.get_backend_name() == "sqlite":
        Base.metadata.create_all(bind=engine)
except Exception:
    pass

app = FastAPI(
    title="LMS API",
    description="Professional Learning Management System API with Real-Time Chat and Analytics",
    version="1.0.0",
)

app.include_router(users.router, tags=["Authentication"])
app.include_router(courses.router, tags=["Courses"])
app.include_router(enrollments.router, tags=["Enrollments"])
app.include_router(progress.router, tags=["Learning Progress"])
app.include_router(plans.router, tags=["Subscription Plans"])
app.include_router(subscriptions.router, tags=["Subscriptions"])
app.include_router(payments.router, tags=["Payments"])
app.include_router(notifications.router, tags=["Notifications"])
app.include_router(activity.router, tags=["Activity Logs"])
app.include_router(chat.router, tags=["Real-Time Chat"])
app.include_router(attendance.router, tags=["Attendance"])
app.include_router(assignments.router, tags=["Assignments"])
app.include_router(auth_google.router, tags=["Auth Google"])
app.include_router(auth_facebook.router, tags=["Auth Facebook"])
app.include_router(auth_github.router, tags=["Auth GitHub"])
app.include_router(auth_otp.router, tags=["Auth OTP"])


if __name__ == "__main__":
    uvicorn.run("lms_api.main:app", host="127.0.0.1", port=8002, reload=True)
