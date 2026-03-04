from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import requests
from datetime import datetime
from ..deps import get_db
from ..models import UserProfile, SocialAccount
from ..auth import create_access_token, hash_password

router = APIRouter()


@router.post("/auth/google/callback")
def google_callback(id_token: str, db: Session = Depends(get_db)):
    r = requests.get("https://oauth2.googleapis.com/tokeninfo", params={"id_token": id_token}, timeout=10)
    if r.status_code != 200:
        raise HTTPException(status_code=400, detail="Invalid id_token")
    data = r.json()
    email = data.get("email")
    name = data.get("name") or email.split("@")[0]
    sub = data.get("sub")
    if not email or not sub:
        raise HTTPException(status_code=400, detail="Missing user info")
    user = db.query(UserProfile).filter(UserProfile.email == email).first()
    if not user:
        user = UserProfile(name=name, email=email, role="student", password_hash=hash_password("oauth-login"))
        db.add(user)
        db.commit()
        db.refresh(user)
    sa = db.query(SocialAccount).filter(SocialAccount.provider == "google", SocialAccount.provider_user_id == sub, SocialAccount.user_id == user.id).first()
    if not sa:
        sa = SocialAccount(user_id=user.id, provider="google", provider_user_id=sub, created_at=datetime.utcnow())
        db.add(sa)
        db.commit()
    token = create_access_token(subject=user.email)
    return {"access_token": token, "token_type": "bearer"}
