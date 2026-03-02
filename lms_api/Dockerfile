FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY lms_api/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY lms_api /app/lms_api
ENV DATABASE_URL=mysql://root:vignesh@db:3306/lms_project
ENV JWT_SECRET=devsecret
EXPOSE 8002
CMD ["uvicorn", "lms_api.main:app", "--host", "0.0.0.0", "--port", "8002"]
