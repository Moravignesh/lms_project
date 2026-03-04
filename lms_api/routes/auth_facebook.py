from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import requests
from datetime import datetime
from ..deps import get_db
from ..models import UserProfile, SocialAccount
from ..auth import create_access_token, hash_password

router = APIRouter()


@router.post("/auth/facebook/callback")
def facebook_callback(access_token: str, db: Session = Depends(get_db)):
    r = requests.get("https://graph.facebook.com/me", params={"access_token": access_token, "fields": "id,name,email"}, timeout=10)
    if r.status_code != 200:
        raise HTTPException(status_code=400, detail="Invalid access_token")
    data = r.json()
    fid = data.get("id")
    name = data.get("name") or "facebook_user"
    email = data.get("email") or f"{fid}@facebook.local"
    if not fid:
        raise HTTPException(status_code=400, detail="Missing user info")
    user = db.query(UserProfile).filter(UserProfile.email == email).first()
    if not user:
        user = UserProfile(name=name, email=email, role="student", password_hash=hash_password("oauth-login"))
        db.add(user)
        db.commit()
        db.refresh(user)
    sa = db.query(SocialAccount).filter(SocialAccount.provider == "facebook", SocialAccount.provider_user_id == fid, SocialAccount.user_id == user.id).first()
    if not sa:
        sa = SocialAccount(user_id=user.id, provider="facebook", provider_user_id=fid, created_at=datetime.utcnow())
        db.add(sa)
        db.commit()
    token = create_access_token(subject=user.email)
    return {"access_token": token, "token_type": "bearer"}
