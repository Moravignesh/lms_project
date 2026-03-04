from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random
import os
import smtplib
from email.message import EmailMessage
from urllib.parse import quote
from ..deps import get_db
from ..models import UserProfile, OTPLog
from ..auth import create_access_token, hash_password

router = APIRouter()


@router.post("/auth/otp/send")
def otp_send(email: str, purpose: str = "login", db: Session = Depends(get_db)):
    code = f"{random.randint(100000, 999999)}"
    now = datetime.utcnow()
    exp = now + timedelta(minutes=10)
    log = OTPLog(email=email, code=code, purpose=purpose, is_used=False, created_at=now, expires_at=exp)
    db.add(log)
    db.commit()
    base_api = os.getenv("BASE_API_URL", "http://localhost:8002")
    redirect_url = os.getenv("OTP_REDIRECT_URL", "http://localhost:8001/authui/login/")
    verify_link = f"{base_api}/auth/otp/verify-link?email={quote(email)}&code={quote(code)}&purpose={quote(purpose)}&redirect_url={quote(redirect_url)}"
    host = os.getenv("EMAIL_HOST")
    user = os.getenv("EMAIL_HOST_USER")
    pwd = os.getenv("EMAIL_HOST_PASSWORD")
    port = int(os.getenv("EMAIL_PORT", "587"))
    use_tls = os.getenv("EMAIL_USE_TLS", "true").lower() in ("1", "true", "yes")
    if host and user and pwd:
        try:
            msg = EmailMessage()
            msg["Subject"] = f"Your {purpose.upper()} OTP Code"
            msg["From"] = user
            msg["To"] = email
            msg.set_content(f"Your OTP code is {code}. It expires in 10 minutes.\n\nClick to verify: {verify_link}")
            with smtplib.SMTP(host, port, timeout=10) as smtp:
                if use_tls:
                    smtp.starttls()
                smtp.login(user, pwd)
                smtp.send_message(msg)
        except Exception:
            pass
    return {"status": "sent"}


@router.post("/auth/otp/verify")
def otp_verify(email: str, code: str, purpose: str = "login", name: str | None = None, db: Session = Depends(get_db)):
    now = datetime.utcnow()
    log = (
        db.query(OTPLog)
        .filter(OTPLog.email == email, OTPLog.code == code, OTPLog.purpose == purpose, OTPLog.is_used == False, OTPLog.expires_at >= now)
        .order_by(OTPLog.created_at.desc())
        .first()
    )
    if not log:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    log.is_used = True
    user = db.query(UserProfile).filter(UserProfile.email == email).first()
    if not user:
        user = UserProfile(name=name or email.split("@")[0], email=email, role="student", password_hash=hash_password("otp-login"))
        db.add(user)
        db.commit()
        db.refresh(user)
    db.commit()
    token = create_access_token(subject=user.email)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/auth/otp/verify-link", response_class=HTMLResponse)
def otp_verify_link(email: str, code: str, purpose: str = "login", redirect_url: str | None = None, db: Session = Depends(get_db)):
    now = datetime.utcnow()
    log = (
        db.query(OTPLog)
        .filter(OTPLog.email == email, OTPLog.code == code, OTPLog.purpose == purpose, OTPLog.is_used == False, OTPLog.expires_at >= now)
        .order_by(OTPLog.created_at.desc())
        .first()
    )
    if not log:
        return HTMLResponse("<h3>Invalid or expired OTP</h3>", status_code=400)
    log.is_used = True
    user = db.query(UserProfile).filter(UserProfile.email == email).first()
    if not user:
        user = UserProfile(name=email.split("@")[0], email=email, role="student", password_hash=hash_password("otp-login"))
        db.add(user)
        db.commit()
        db.refresh(user)
    db.commit()
    token = create_access_token(subject=user.email)
    target = redirect_url or os.getenv("OTP_REDIRECT_URL", "http://localhost:8001/authui/login/")
    html = f"""<html><body>
    <script>
      const token = "{token}";
      const url = new URL("{target}");
      url.searchParams.set("token", token);
      window.location.replace(url.toString());
    </script>
    Redirecting...
    </body></html>"""
    return HTMLResponse(html)
