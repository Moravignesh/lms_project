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
- DATABASE_URL: mysql://root:---@db:3306/lms_project
- JWT_SECRET: set on API service

## Database Schema
- Managed by Django migrations in lms_admin/core/migrations
- Tables: users, courses, lessons, enrollments, progress

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
- POST /activity/
- GET /analytics/overview (admin)
- GET /analytics/monthly (admin)

## Postman
- Import postman_collection.json and set baseUrl=http://localhost:8002

## Docker
- Services: db (MySQL), admin (Django), api (FastAPI)
- Ports: 3306, 8001, 8002

## Screenshots
- After running, capture Admin dashboard and API responses via browser and Postman

## Email & Notifications
- In-app notifications are created for enrollments, progress updates, and subscriptions
- For email notifications, set environment variables:
  - EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_USE_TLS
  - Do NOT hardcode secrets; use env-config or Docker secrets
