# Learning Management Platform

## Overview
- Admin Panel: Django with Bootstrap dashboard and CRUD via Django Admin
- User Panel: FastAPI with JWT authentication and REST APIs
- Database: MySQL shared by both services

## Prerequisites
- Docker Desktop

## Quick Start
- docker compose up -d --build
- Access Admin Panel: http://localhost:8001/dashboard/
- Access Django Admin: http://localhost:8001/admin/
- Access API Docs: http://localhost:8002/docs

## Initial Setup
- Exec into admin container: docker compose exec admin python manage.py migrate
- Create superuser: docker compose exec admin python manage.py createsuperuser
- Login at /admin and manage users, courses, lessons, enrollments, progress

## Environment
- DATABASE_URL: mysql://root:vignesh@db:3306/lms_project
- JWT_SECRET: set on API service

## Database Schema
- Managed by Django migrations in lms_admin/core/migrations
- Tables: users, courses, lessons, enrollments, progress
- Additional tables (created via SQLAlchemy): attendance, assignments, submissions

## API Endpoints
- POST /register/
- POST /login/
- GET /courses/
- GET /courses/{id}
- POST /enroll/
- GET /my-courses/
- POST /progress/update/
- GET /progress/view/
- GET /plans/
- POST /subscribe/
- GET /payments/
- GET /notifications/
- POST /notifications/mark-read/
- GET /notifications/{user_id}/
- POST /activity/
- GET /analytics/dashboard/?course_id={id} (Django, JSON)

### Attendance (FastAPI)
- POST /attendance/mark
  - Body: { course_id, date(YYYY-MM-DD), records: [{student_id, status}] }
  - Rules: Only course instructor; no duplicates per student/course/date
- GET /attendance/student/{student_id}?course_id={course_id}
- GET /attendance/course/{course_id}?from=YYYY-MM-DD&to=YYYY-MM-DD

### Assignments (FastAPI)
- POST /assignments/create (multipart/form-data)
  - Fields: course_id, title, description, deadline(YYYY-MM-DD), file(optional)
  - Rules: Instructor-only; file stored securely
- POST /assignments/submit (multipart/form-data)
  - Fields: assignment_id, student_id, file
  - Rules: Prevent late submissions; one submission per student
- PUT /assignments/grade
  - Body: { submission_id, grade, remarks }
  - Rules: Instructor-only (course owner)

## Postman
- Import postman_collection.json and set:
  - baseUrl=http://localhost:8002
  - adminUrl=http://localhost:8001
  - token=<JWT after login>
- Includes negative tests: duplicate attendance and late submission

## Docker
- Services: db (MySQL), admin (Django), api (FastAPI)
- Ports: 3306, 8001, 8002

## Screenshots
- After running, capture Admin dashboard and API responses via browser and Postman

## Email & Notifications
- In-app notifications are created for enrollments, progress updates, subscriptions, attendance marking, assignment creation, grading
- For email notifications, set environment variables:
  - EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_USE_TLS
  - Do NOT hardcode secrets; use env-config or Docker secrets
 
 ## Today’s Additions: Social Login + OTP
 - Endpoints (FastAPI):
   - POST /auth/google/callback  (expects id_token from Google Sign-In)
   - POST /auth/facebook/callback  (expects user access_token from Graph API)
   - POST /auth/github/callback  (expects user access_token; user:email scope recommended)
   - POST /auth/otp/send  (email, purpose=login|signup, returns status)
   - POST /auth/otp/verify  (email, code, purpose, optional name; returns JWT)
 - Models:
   - SQLAlchemy: social_accounts, otp_logs
   - Django Admin: SocialAccount, OTPLog (monitor linked accounts and OTP events)
 - Postman:
   - Import postman_collection_full.json; set:
     - baseUrl=http://localhost:8002
     - adminUrl=http://localhost:8001
     - token=<JWT after login>
   - Social and OTP requests included; responses logged in Console for full visibility
 - Setup Notes:
   - Obtain provider tokens client-side and pass to callbacks; backend verifies tokens and issues JWT
   - No provider secrets stored server-side in this setup
   - GitHub requires user:email scope to read email when not present on primary profile
 
## Social Auth & OTP
- Social callbacks:
  - POST /auth/google/callback (id_token)
  - POST /auth/facebook/callback (access_token)
  - POST /auth/github/callback (access_token)
- OTP:
  - POST /auth/otp/send (email, purpose)
  - POST /auth/otp/verify (email, code, purpose, name?)
- Postman:
  - Import postman_collection_full.json and set baseUrl/adminUrl/token
  - Responses are logged in Console to show complete output
- OAuth tokens:
  - Obtain provider tokens client-side and send to backend callbacks
  - GitHub requires user:email scope to read email
 
## Register Endpoint Troubleshooting
- Endpoint: POST /register/
- Payload example:
  - { "name": "Test User", "email": "test@example.com", "role": "student", "password": "Pass123!" }
- If you see 500:
  - Ensure MySQL is running and DATABASE_URL is set for API
  - Run Django migrations so the users table exists: cd lms_admin && python manage.py migrate
  - Use a unique email (duplicate emails are rejected)
  - Include all fields: name, email, role, password; role must be student or instructor
  - Check API logs for DB connection errors
 - Quick test in Postman:
   - Use item "Auth - Register" in postman_collection_full.json
   - Expect 200 with created user payload
