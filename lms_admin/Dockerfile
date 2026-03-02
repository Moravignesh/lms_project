FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY lms_admin/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY lms_admin /app
ENV DATABASE_URL=mysql://root:vignesh@db:3306/lms_project
EXPOSE 8001
CMD ["python", "manage.py", "runserver", "0.0.0.0:8001"]
